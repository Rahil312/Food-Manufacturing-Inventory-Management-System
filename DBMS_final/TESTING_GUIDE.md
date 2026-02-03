# Quick Start Testing Guide

## Prerequisites
1. MySQL server running on localhost
2. Database `dbms_project` created and populated:
   ```bash
   mysql -u root -p < sql/QUICK_START.sql
   ```
3. Python dependencies installed:
   ```bash
   pip install -r requirements.txt
   ```

## Start the Application
```bash
python -m app.main
```

---

## Test Scenario 1: Supplier Workflow

### Login
```
Username: jdoe
Password: password123
Role: SUPPLIER (Supplier 20 - Jane Doe)
```

### Test Steps
1. **View My Ingredients** (Option 1)
   - Should see list of ingredients Supplier 20 (Jane Doe) supplies:
     - 101: Salt
     - 102: Pepper
     - 106: Beef Steak
     - 108: Pasta
     - 201: Seasoning Blend (compound)
   - Verify data from `supplier_ingredient` table

2. **View My Ingredient Batches** (Option 10)
   - Should see existing batches with status indicators
   - Expected batches for Supplier 20:
     - Salt (101): 4 batches (B0001, B0002, B0003)
     - Pepper (102): 1 batch (B0001)
     - Beef Steak (106): 2 batches (B0005, B0006)
     - Pasta (108): 2 batches (B0001, B0003)
     - Seasoning Blend (201): 2 batches (B0001, B0002)
   - Look for: lot numbers, on-hand quantities (some partially consumed), expiration dates

3. **Receive Ingredient Batch** (Option 9) ⭐ **DEMO TRIGGERS**
   - Choose an ingredient from your supply list (e.g., Salt: 101)
   - Enter test data:
     ```
     Ingredient ID: 101
     Quantity (oz): 500
     Unit Cost ($/oz): 0.10
     Receive Date: 2025-11-15
     Expire Date: 2026-02-20 (or later, must be >= receive_date + 90 days)
     Supplier Batch ID: B9999
     ```
   - **TRIGGER DEMO**: System automatically generates lot_number (format: `{ing_id}-{supplier_id}-{batch_id}`)
   - **TRIGGER DEMO**: System validates expiration date is within 90 days from receive date
   - Check the new batch appears in "View My Ingredient Batches"

4. **View Do-Not-Combine Rules** (Option 11)
   - Should display 2 incompatible ingredient pairs:
     - 104 (Sodium Phosphate) ⚠️ 201 (Seasoning Blend)
     - 104 (Sodium Phosphate) ⚠️ 106 (Beef Steak)
   - Data from `do_not_combine` table

5. **Additional Supplier Features** (Optional Testing):
   - **Add Ingredient to Supply List** (Option 2): Add existing or create new ingredients
   - **Remove Ingredient from Supply List** (Option 3): Stop supplying specific ingredients
   - **View My Formulations** (Option 4): See pricing and pack sizes for supplied ingredients
   - **Create New Formulation** (Option 5): Set up pricing for compound ingredients with materials
   - **View/Update/Delete Formulations** (Options 6-8): Manage formulation details
   - These demonstrate complex ingredient-supplier relationships and pricing structures

---

## Test Scenario 2: Manufacturer Workflow

### Login
```
Username: jsmith
Password: password123
Role: MANUFACTURER (MFG001 - Premier Foods Manufacturing)
```

### Test Steps
1. **View My Product Types** (Option 1)
   - Should see 1 product for MFG001 (Premier Foods Manufacturing):
     - Product ID: 100
     - Name: "Steak Dinner"
     - Category: Dinners (category_id: 2)
     - Product Code: P-100

2. **View My Recipe Plans** (Option 5)
   - Should see 1 recipe plan:
     - Recipe Plan ID: 1
     - Product: Steak Dinner
     - Notes: "Recipe for Steak Dinner - includes beef and seasoning"
     - Ingredients: 2 (Beef Steak, Seasoning Blend)

3. **View Recipe Plan Details** (Option 6)
   - Enter recipe_plan_id: 1
   - Should see detailed ingredient list:
     - 106: Beef Steak - 6.0 oz per unit
     - 201: Seasoning Blend - 0.2 oz per unit
   - Standard batch: 500 units

4. **Create Product Batch** (Option 10) ⭐ **DEMO sp_record_product_batch & FEFO**
   
   **NEW FEATURE**: This now supports FEFO (First Expired, First Out) auto-selection!
   
   **Two approaches:**
   
   **Approach A: FEFO Auto-Selection (RECOMMENDED)**
   - Select recipe plan ID: 1 (Steak Dinner)
   - Enter batch quantity: 100 (units)
   - Choose Option 1: "Auto-select using FEFO"
   - System automatically selects ingredient lots based on expiration dates
   - Review auto-selected lots with expiry information
   - Confirm creation
   
   **Approach B: Manual Staging (Traditional)**
   ```sql
   USE dbms_project;
   
   -- Clear any existing staging
   DELETE FROM staging_consumption;
   
   -- Insert staging consumption for Steak Dinner batch
   -- Need: 6 oz Beef per unit * 100 units = 600 oz Beef
   --       0.2 oz Seasoning per unit * 100 units = 20 oz Seasoning
   
   -- Get ingredient_batch_ids (check what's available)
   SELECT ingredient_batch_id, lot_number, ingredient_id, on_hand_oz 
   FROM ingredient_batch 
   WHERE (ingredient_id = 106 OR ingredient_id = 201) 
     AND on_hand_oz > 0
   ORDER BY ingredient_id;
   
   -- Insert staging (use actual batch IDs from query above)
   -- Example with typical IDs (adjust based on your results):
   INSERT INTO staging_consumption (ingredient_batch_id, qty_oz)
   VALUES 
   (7, 600),  -- Beef Steak batch (adjust ID)
   (11, 20);  -- Seasoning Blend batch (adjust ID)
   ```
   
   **Then in the CLI:**
   - Select recipe plan ID: 1 (Steak Dinner)
   - Enter batch quantity: 100 (units)
   - Choose Option 2: "Use existing staging_consumption records"
   - Review staging consumption (should show 2 records: Beef 600oz, Seasoning 20oz)
   - Confirm creation
   
   **STORED PROCEDURE DEMO**: sp_record_product_batch will:
   - ✅ Create product_batch record with auto-generated lot_number
   - ✅ Insert product_batch_consumption records (2 ingredients)
   - ✅ Update ingredient_batch.on_hand quantities (reduce by consumed amounts)
   - ✅ Clear staging_consumption table
   
   - Verify new batch created with lot number format: `{product_type_id}-{mfg_id}-B####`
   - Check ingredient batches have reduced on_hand (600 oz and 20 oz consumed)

5. **Reports Menu** (Option 11)
   - **On-Hand Inventory Report** (Option 1): View current stock levels
     - Should show 1 product: Steak Dinner with remaining inventory
   - **Nearly Out of Stock** (Option 2): Products < 100 oz
     - May show products if on-hand is low
   - **Almost Expired Ingredient Batches** (Option 3): Expiring in next 7 days
     - Database has expiration dates in 2026, so may be empty unless you add near-expiry batches
   - **Product Batch Cost Report** (Option 4): See cost breakdown
     - Should show existing batch: 100-MFG001-B0901 (100 units, $650.00 total, $6.50/unit)
     - Plus any new batches you created
   - **🔍 Product Recall Traceability** (Option 5) ⭐ **DEMO sp_trace_recall**
     - Enter a product batch ID to trace all ingredient lots used
     - Shows full supply chain for recall purposes
     - Demonstrates stored procedure sp_trace_recall

---

## Test Scenario 3: Viewer Workflow

### Login
```
Username: bjohnson
Password: password123
Role: VIEWER (Read-Only Access)
```

### Test Steps
1. **Browse All Products** (Option 1)
   - Should see 2 products from 2 manufacturers:
     - Product 100: Steak Dinner (MFG001 - Premier Foods Manufacturing, Category: Dinners)
     - Product 101: Mac & Cheese (MFG002 - Quality Meals Corp, Category: Sides)
   - Shows batches and on-hand quantities

2. **Browse by Manufacturer** (Option 2)
   - Available manufacturers:
     - MFG001: Premier Foods Manufacturing
     - MFG002: Quality Meals Corp
   - Select MFG001: Should see Steak Dinner
   - Select MFG002: Should see Mac & Cheese

3. **View Product Ingredient List** (Option 4)
   - Enter product_type_id: 100 (Steak Dinner)
   - Should see flattened BOM:
     - 106: Beef Steak - 6.0 oz per unit
     - 201: Seasoning Blend - 0.2 oz per unit
   - OR Enter product_type_id: 101 (Mac & Cheese)
   - Should see:
     - 108: Pasta - 7.0 oz per unit
     - 101: Salt - 0.5 oz per unit
     - 102: Pepper - 2.0 oz per unit

4. **Compare Products for Incompatibility** (Option 5) ⭐ **DEMO sp_compare_products_incompatibility**
   - Enter first product ID: 100 (Steak Dinner)
   - Enter second product ID: 101 (Mac & Cheese)
   - **STORED PROCEDURE DEMO**: Calls sp_compare_products_incompatibility
   - Expected result: May show no incompatibilities (these products don't share conflicting ingredients)
   - Note: Conflicts exist for ingredient 104 (Sodium Phosphate) with 201 (Seasoning Blend) and 106 (Beef Steak)
   - To test conflicts, would need a product containing Sodium Phosphate vs. one with Seasoning Blend or Beef

5. **View Health Risk Violations** (Option 6)
   - Shows expired ingredient batches still in inventory (on_hand > 0)
   - Should be EMPTY initially (all expiration dates are set to 2026)
   - Uses `v_health_risk_violations` view
   - To test: Would need to manually update an ingredient_batch expiration_date to the past

6. **View All Active Formulations** (Option 7)
   - Shows all active supplier formulations across the system
   - Displays: Formulation ID, Supplier, Ingredient, Pack Size, Unit Price, Effective dates
   - Uses `v_active_formulations` view
   - Read-only view of pricing and supplier capabilities

---

## Verification Checklist

### Database Integration
- [ ] Queries execute without errors
- [ ] Data from views displays correctly
- [ ] Stored procedure sp_record_product_batch works with FEFO auto-selection
- [ ] Stored procedure sp_compare_products_incompatibility works
- [ ] Stored procedure sp_trace_recall works (product traceability)
- [ ] FEFO auto-selection chooses lots by expiration date
- [ ] Trigger generates lot_number for ingredient_batch
- [ ] Trigger validates 90-day expiration rule
- [ ] Trigger updates on_hand quantities automatically
- [ ] Session tokens properly isolate staging_consumption records

### User Interface
- [ ] Tables format properly with tabulate
- [ ] Error messages display with ❌ emoji
- [ ] Success messages display with ✅ emoji
- [ ] Menus are clear and organized
- [ ] Navigation works (logout, back to menu)

### Role-Based Access
- [ ] Manufacturer sees manufacturer_id-specific data
- [ ] Supplier sees supplier_id-specific data
- [ ] Viewer has read-only access
- [ ] Each role menu has correct options

---

## Graduate Features Highlighted

### 🤖 FEFO (First Expired, First Out) Auto-Selection
- **Location**: Manufacturer Menu → Create Product Batch (Option 10) → Auto-select using FEFO (Option 1)
- **Purpose**: Automatically selects ingredient lots based on expiration dates to minimize waste
- **Demo**: When creating a product batch, choose FEFO option and system will show selected lots with days until expiry
- **Technical**: Uses session tokens to isolate staging records, complex SQL with JOINs and ORDER BY expiration dates

### 🔍 Product Recall Traceability
- **Location**: Manufacturer Menu → Reports Menu (Option 11) → Product Recall Traceability (Option 5)
- **Purpose**: Trace all ingredient lots used in a specific product batch for recall purposes
- **Demo**: Enter any product batch ID to see complete supply chain
- **Technical**: Stored procedure sp_trace_recall with recursive ingredient tracking

### 📊 Advanced Views and Reporting
- **Health Risk Violations**: Shows expired ingredients still in inventory
- **Active Formulations**: Cross-supplier pricing and availability
- **Cost Analysis**: Product batch cost breakdowns with unit costs
- **Inventory Management**: Real-time on-hand quantities with consumption tracking

---

## Common Issues & Fixes

### Import Error: "tabulate not found"
```bash
pip install tabulate
```

### Database Connection Error
1. Check MySQL is running: `mysql -u root -p`
2. Verify database exists: `SHOW DATABASES;`
3. Update connection in `app/db.py`:
   ```python
   conn = mysql.connector.connect(
       host='localhost',
       user='root',
       password='YOUR_PASSWORD',
       database='dbms_project'
   )
   ```

### "No staging_consumption records" when creating batch
**RECOMMENDED**: Use FEFO auto-selection (Option 1) which automatically selects lots based on expiration dates
**ALTERNATIVE**: Manually insert staging records in MySQL:
   ```sql
   INSERT INTO staging_consumption (ingredient_batch_id, qty_oz)
   VALUES (1, 150), (2, 2100), (3, 600);
   ```
   Then create batch in CLI and choose Option 2

### Stored Procedure Errors
- Check procedure exists: `SHOW PROCEDURE STATUS WHERE Db = 'dbms_project';`
- Verify seed data loaded: `SELECT COUNT(*) FROM ingredient_batch;`
- Check on_hand quantities sufficient: `SELECT * FROM ingredient_batch WHERE on_hand_oz > 0;`

---

## Sample Test Data

### Test Users (From Seed Data)
| Username | Password | Role | ID | Full Name |
|----------|----------|------|-----|-----------|
| jsmith | password123 | MANUFACTURER | MFG001 | John Smith (Premier Foods) |
| alee | password123 | MANUFACTURER | MFG002 | Alice Lee (Quality Meals) |
| jdoe | password123 | SUPPLIER | 20 | Jane Doe |
| jmiller | password123 | SUPPLIER | 21 | James Miller |
| bjohnson | password123 | VIEWER | - | Bob Johnson |

**Note**: Password hash in DB is `HASH_password123` but login accepts `password123`

### Manufacturers
| ID | Name |
|----|------|
| MFG001 | Premier Foods Manufacturing |
| MFG002 | Quality Meals Corp |

### Suppliers
| ID | Code | Name |
|----|------|------|
| 20 | SUP-020 | Jane Doe |
| 21 | SUP-021 | James Miller |

### Sample Product Types
| ID | Manufacturer | Product Name | Category | Product Code |
|----|--------------|--------------|----------|--------------|
| 100 | MFG001 | Steak Dinner | Dinners (2) | P-100 |
| 101 | MFG002 | Mac & Cheese | Sides (3) | P-101 |

### Sample Ingredients
| ID | Name | Type | Supplied By |
|----|------|------|-------------|
| 101 | Salt | Atomic | Supplier 20, 21 |
| 102 | Pepper | Atomic | Supplier 20, 21 |
| 104 | Sodium Phosphate | Atomic | Supplier 21 |
| 106 | Beef Steak | Atomic | Supplier 20 |
| 108 | Pasta | Atomic | Supplier 20 |
| 201 | Seasoning Blend | Compound (6oz Salt + 2oz Pepper) | Supplier 20 |
| 301 | Super Seasoning | Compound (4oz Salt + 1oz Sodium Phosphate) | - |

### Recipe Plans
| ID | Product | Ingredients | Notes |
|----|---------|-------------|-------|
| 1 | Steak Dinner (100) | 6oz Beef + 0.2oz Seasoning per unit | Standard: 500 units |
| 2 | Mac & Cheese (101) | 7oz Pasta + 0.5oz Salt + 2oz Pepper per unit | Standard: 300 units |

### Existing Product Batches
| Batch ID | Lot Number | Product | Units | Cost | Created |
|----------|------------|---------|-------|------|---------|
| 1 | 100-MFG001-B0901 | Steak Dinner | 100 | $650 ($6.50/unit) | 2025-09-26 |
| 2 | 101-MFG002-B0101 | Mac & Cheese | 300 | $861 ($2.87/unit) | 2025-09-10 |

### Sample Ingredient Batches (Supplier 20 - Jane Doe)
| Ingredient | Batches | Total Quantity | Some Consumed |
|------------|---------|----------------|---------------|
| Salt (101) | 4 (B0001-B0003) | 2800 oz total | 150 oz used in Mac & Cheese |
| Pepper (102) | 1 (B0001) | 1200 oz | 600 oz used in Mac & Cheese |
| Beef Steak (106) | 2 (B0005, B0006) | 3600 oz | 600 oz used in Steak Dinner |
| Pasta (108) | 2 (B0001, B0003) | 7300 oz | 2100 oz used in Mac & Cheese |
| Seasoning Blend (201) | 2 (B0001, B0002) | 120 oz | 20 oz used in Steak Dinner |

### Do-Not-Combine Rules
| Ingredient A | Ingredient B | Reason |
|--------------|--------------|--------|
| 104 (Sodium Phosphate) | 201 (Seasoning Blend) | Regulatory conflict |
| 104 (Sodium Phosphate) | 106 (Beef Steak) | Regulatory conflict |

---

## Success Criteria

After completing all test scenarios, you should have:
1. ✅ Successfully logged in as all 3 roles
2. ✅ Demonstrated lot_number trigger (supplier receiving batch)
3. ✅ Demonstrated 90-day expiration trigger validation
4. ✅ Demonstrated sp_record_product_batch (manufacturer creating batch)
5. ✅ Demonstrated FEFO auto-selection feature (First Expired, First Out)
6. ✅ Demonstrated sp_compare_products_incompatibility (viewer comparison)
7. ✅ Demonstrated sp_trace_recall (product traceability)
8. ✅ Viewed data from all 5+ views
9. ✅ Created new records (product type, recipe plan, batch)
10. ✅ Generated reports with aggregated data
11. ✅ Tested session token isolation in staging consumption

**If all checkboxes pass, the application is fully functional! 🎉**
