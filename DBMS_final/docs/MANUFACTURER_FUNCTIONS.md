# Manufacturer Functions Documentation

## Overview
This document provides comprehensive documentation for all manufacturer-specific functionality implemented in `manufacturer_actions.py`. Manufacturers have full control over their product catalog, recipe management, production operations, and reporting capabilities.

---

## Function Categories

| Category | Functions | Purpose |
|----------|-----------|---------|
| **Product Type Management** | 4 functions | Create, view, update, delete product definitions |
| **Recipe Plan Management** | 5 functions | Manage versioned BOMs and ingredient specifications |
| **Production Operations** | 1 critical function | Create product batches with FEFO auto-selection |
| **Reporting & Analytics** | 5 functions | Inventory monitoring, cost analysis, traceability |
| **Menu System** | 1 function | Sub-menu for reports organization |

---

## Product Type Management

### 1. view_my_product_types(user)

**Purpose**: Display all product types owned by the logged-in manufacturer.

**Parameters**:
- `user` (dict): User session containing manufacturer_id

**Database Query**:
```sql
SELECT 
    pt.product_type_id,
    pt.name as product_name,
    c.name as category,
    pt.product_code,
    DATE_FORMAT(pt.created_at, '%Y-%m-%d') as created_date
FROM product_type pt
JOIN category c ON pt.category_id = c.category_id
WHERE pt.manufacturer_id = %s
ORDER BY c.name, pt.name
```

**Output Format**:
```
┌─────┬──────────────┬──────────┬──────────────┬─────────────┐
│ ID  │ Product Name │ Category │ Product Code │ Created     │
├─────┼──────────────┼──────────┼──────────────┼─────────────┤
│ 100 │ Steak Dinner │ Dinners  │ P-100        │ 2025-09-15  │
└─────┴──────────────┴──────────┴──────────────┴─────────────┘
```

**Business Rules**:
- Only shows products owned by current manufacturer
- Sorted by category then product name for easy browsing

---

### 2. create_product_type(user)

**Purpose**: Create new product types with category assignment and batch size specification.

**Interactive Flow**:
1. Display available categories
2. Collect product information:
   - Product Name (required)
   - Product Code (required, unique within manufacturer)
   - Category ID (must exist)
   - Standard Batch Units (positive integer)

**Database Query**:
```sql
INSERT INTO product_type (manufacturer_id, product_code, name, category_id, standard_batch_units)
VALUES (%s, %s, %s, %s, %s)
```

**Validation Rules**:
- Product name cannot be empty
- Product code cannot be empty
- Category ID must exist in database
- Standard batch units must be positive integer
- Product code must be unique within manufacturer (enforced by database)

**Example Usage**:
```
Product Name: Premium Beef Stew
Product Code: P-105
Category ID: 2
Standard Batch Units: 300

✅ Product type created successfully!
   Product ID: 105
   Product Code: P-105
```

---

### 3. update_product_type(user)

**Purpose**: Modify existing product type properties.

**Interactive Flow**:
1. Display manufacturer's product types
2. Select product to update
3. Show current values
4. Allow modification of each field (press Enter to keep current)

**Updateable Fields**:
- Product Name
- Product Code  
- Category ID
- Standard Batch Units

**Database Query**:
```sql
UPDATE product_type 
SET name = %s, product_code = %s, category_id = %s, standard_batch_units = %s
WHERE product_type_id = %s AND manufacturer_id = %s
```

**Business Rules**:
- Only manufacturer can update their own products
- All uniqueness constraints still apply
- Empty input preserves current value

---

### 4. delete_product_type(user)

**Purpose**: Remove product type with safety checks.

**Safety Validations**:
1. **Recipe Plan Check**: Prevent deletion if recipe plans exist
2. **Product Batch Check**: Prevent deletion if batches exist
3. **Confirmation Required**: User must type "yes" to confirm

**Database Queries**:
```sql
-- Check for recipe plans
SELECT COUNT(*) as count FROM recipe_plan WHERE product_type_id = %s

-- Check for product batches  
SELECT COUNT(*) as count FROM product_batch WHERE product_type_id = %s

-- Delete if safe
DELETE FROM product_type WHERE product_type_id = %s AND manufacturer_id = %s
```

**Error Prevention**:
- Cannot delete products with production history
- Cannot delete products with active recipes
- Prevents accidental data loss

---

## Recipe Plan Management

### 5. view_my_recipe_plans(user)

**Purpose**: Display all recipe plans (versioned BOMs) for manufacturer's products.

**Database Query**:
```sql
SELECT 
    rp.recipe_plan_id,
    pt.name as product_name,
    DATE_FORMAT(rp.created_at, '%Y-%m-%d') as created,
    COALESCE(rp.notes, '') as notes,
    COUNT(rpi.ingredient_id) as num_ingredients
FROM recipe_plan rp
JOIN product_type pt ON rp.product_type_id = pt.product_type_id
LEFT JOIN recipe_plan_item rpi ON rp.recipe_plan_id = rpi.recipe_plan_id
WHERE pt.manufacturer_id = %s
GROUP BY rp.recipe_plan_id
ORDER BY pt.name, rp.created_at DESC
```

**Output Features**:
- Shows ingredient count per recipe
- Displays creation dates for version tracking
- Includes optional notes for recipe documentation

---

### 6. view_recipe_plan_details(user)

**Purpose**: Show detailed ingredient list and quantities for a specific recipe plan.

**Interactive Flow**:
1. Display available recipe plans
2. User selects recipe plan ID
3. Show complete ingredient breakdown

**Database Queries**:
```sql
-- Recipe header information
SELECT rp.recipe_plan_id, pt.name as product_name, pt.standard_batch_units, rp.notes
FROM recipe_plan rp
JOIN product_type pt ON rp.product_type_id = pt.product_type_id
WHERE rp.recipe_plan_id = %s AND pt.manufacturer_id = %s

-- Ingredient details
SELECT i.ingredient_id, i.name as ingredient_name, rpi.qty_oz_per_unit
FROM recipe_plan_item rpi
JOIN ingredient i ON rpi.ingredient_id = i.ingredient_id
WHERE rpi.recipe_plan_id = %s
ORDER BY rpi.qty_oz_per_unit DESC
```

**Calculation Features**:
- Shows quantity per unit
- Calculates total batch requirements
- Displays ingredient hierarchy (atomic vs compound)

---

### 7. create_recipe_plan(user)

**Purpose**: Create new versioned recipe plans with ingredient specifications.

**Interactive Flow**:
1. Display manufacturer's products
2. Select product for recipe
3. Add ingredients with quantities
4. Confirm and save recipe

**Implementation**:
- Creates recipe_plan record with product association
- Calls `_add_recipe_ingredients()` helper for ingredient entry
- Supports multiple ingredients per recipe
- Validates ingredient existence and positive quantities

**Database Operations**:
```sql
-- Create recipe plan
INSERT INTO recipe_plan (product_type_id, notes) VALUES (%s, %s)

-- Add ingredients
INSERT INTO recipe_plan_item (recipe_plan_id, ingredient_id, qty_oz_per_unit)
VALUES (%s, %s, %s)
```

---

### 8. update_recipe_plan(user)

**Purpose**: Modify existing recipe plans (add, remove, or update ingredients).

**Advanced Features**:
1. **Add Ingredients**: Expand recipe with new ingredients
2. **Remove Ingredients**: Delete specific ingredients from recipe
3. **Update Quantities**: Modify ingredient quantities
4. **Update Notes**: Change recipe documentation

**Complex Logic**:
- Maintains recipe versioning through modification tracking
- Prevents removal of ingredients if production batches exist using that recipe
- Validates all ingredient and quantity changes

---

### 9. delete_recipe_plan(user)

**Purpose**: Remove entire recipe plans with production history validation.

**Safety Checks**:
```sql
-- Check for product batches using this recipe
SELECT COUNT(*) as count 
FROM product_batch pb
WHERE EXISTS (
    SELECT 1 FROM recipe_plan rp 
    WHERE rp.recipe_plan_id = %s 
    AND rp.product_type_id = pb.product_type_id
)
```

**Cascading Effects**:
- Automatically removes all recipe_plan_item records
- Maintains referential integrity
- Prevents deletion if production history exists

---

## Production Operations

### 10. create_product_batch(user) ⭐ **MOST CRITICAL FUNCTION**

**Purpose**: Core production function that creates product batches using advanced FEFO (First Expired, First Out) inventory management.

**Graduate Features Implemented**:

#### FEFO Auto-Selection Algorithm
```python
def auto_select_lots_fefo(recipe_plan_id, produced_units, session_token):
    """
    Automatically selects ingredient lots based on expiration dates
    to minimize waste through First Expired, First Out logic
    """
```

**Selection Strategy**:
1. Calculate ingredient requirements from recipe plan
2. Query available lots by expiration date (earliest first)
3. Allocate quantities from expiring lots first
4. Create staging_consumption records with session isolation

#### Two Production Approaches

**Approach A: FEFO Auto-Selection (Recommended)**
```python
# Interactive flow:
selection_choice = input("\nChoice (1 or 2): ").strip()

if selection_choice == '1':
    # Use FEFO auto-selection
    success, message, lots_selected = auto_select_lots_fefo(recipe_plan_id, batch_units, session_token)
```

**Approach B: Manual Staging**
```python
elif selection_choice == '2':
    # Use existing staging_consumption records
    # Shows current staging and proceeds with manual selection
```

#### Stored Procedure Integration
```python
# Call sp_record_product_batch with session token
if session_token:
    call_query = "CALL sp_record_product_batch(%s, %s, %s, %s, %s)"
    params = (session_token, product_type_id, recipe_plan_id, batch_units, mfg_id)
```

#### Session Token Isolation
- Generates unique session tokens using `uuid.uuid4()`
- Prevents interference between concurrent batch creation sessions
- Enables safe multi-user production operations

**Complete Production Flow**:
1. Display available recipe plans
2. User selects recipe plan and batch quantity
3. Choose FEFO auto-selection or manual staging
4. Review selected ingredient lots (shows expiration info)
5. Confirm batch creation
6. Call stored procedure for atomic batch creation
7. Display created batch details (ID, lot number, costs)

**Error Handling**:
- Insufficient inventory detection
- Expired ingredient prevention
- Do-not-combine conflict checking
- Session cleanup on errors

**Example Output**:
```
✅ Product batch created successfully!
   Batch ID: 5
   Lot Number: 100-MFG001-000005
   Batch Cost: $650.00
   Unit Cost: $6.50
   
✅ Ingredients consumed from staging and on_hand updated!
```

---

## Reporting & Analytics

### 11. view_my_inventory_report(user)

**Purpose**: Current inventory status for manufacturer's products.

**Database Query**:
```sql
SELECT 
    pt.name as product_name,
    c.name as category,
    SUM(pb.produced_units) as total_units,
    COUNT(pb.product_batch_id) as num_batches
FROM product_type pt
JOIN category c ON pt.category_id = c.category_id
LEFT JOIN product_batch pb ON pt.product_type_id = pb.product_type_id
WHERE pt.manufacturer_id = %s
GROUP BY pt.product_type_id
HAVING total_units > 0
ORDER BY c.name, pt.name
```

**Business Insights**:
- Total units in inventory
- Number of production batches
- Category-based organization

---

### 12. view_nearly_out_of_stock(user)

**Purpose**: Identify products at risk of production shortages.

**Uses Database View**:
```sql
SELECT * FROM v_nearly_out_of_stock 
WHERE manufacturer_id = %s
ORDER BY total_on_hand_oz
```

**Alert Logic**:
- Compares ingredient availability vs. standard batch requirements
- Highlights critical shortages first
- Enables proactive procurement planning

---

### 13. view_almost_expired_batches(user)

**Purpose**: Monitor ingredient batches approaching expiration (waste prevention).

**Database Query**:
```sql
SELECT 
    ib.ingredient_batch_id,
    ib.lot_number,
    i.name AS ingredient_name,
    ib.on_hand_oz,
    ib.expiration_date,
    DATEDIFF(ib.expiration_date, CURDATE()) AS days_until_expiry
FROM ingredient_batch ib
JOIN ingredient i ON i.ingredient_id = ib.ingredient_id
JOIN recipe_plan_item rpi ON rpi.ingredient_id = ib.ingredient_id
JOIN recipe_plan rp ON rp.recipe_plan_id = rpi.recipe_plan_id
JOIN product_type pt ON pt.product_type_id = rp.product_type_id
WHERE pt.manufacturer_id = %s
  AND ib.expiration_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 7 DAY)
  AND ib.on_hand_oz > 0
ORDER BY ib.expiration_date
```

**FEFO Integration**:
- Identifies ingredients for priority usage
- Supports waste reduction initiatives
- Enables expiration-based production scheduling

---

### 14. view_batch_cost_report(user)

**Purpose**: Financial analysis of production batches with cost breakdowns.

**Database Query**:
```sql
SELECT 
    pb.product_batch_id,
    pb.product_lot_number,
    pt.name AS product_name,
    pb.produced_units,
    pb.batch_cost,
    pb.unit_cost,
    DATE_FORMAT(pb.created_at, '%Y-%m-%d') AS created_date
FROM product_batch pb
JOIN product_type pt ON pt.product_type_id = pb.product_type_id
WHERE pt.manufacturer_id = %s
ORDER BY pb.created_at DESC
```

**Financial Insights**:
- Total batch costs
- Per-unit cost analysis
- Historical cost trends
- Production efficiency metrics

---

### 15. trace_product_recall(user) ⭐ **GRADUATE FEATURE**

**Purpose**: Complete product recall traceability using stored procedure `sp_trace_recall`.

**Interactive Flow**:
1. Display manufacturer's product batches
2. User selects batch for traceability
3. Call stored procedure for comprehensive trace
4. Display complete supply chain breakdown

**Stored Procedure Call**:
```python
# Extract product_batch_id for traceability
call_query = "CALL sp_trace_recall(NULL, %s, 30)"
params = (selected_lot_number,)
result = run_query(call_query, params, fetch=True)
```

**Traceability Output**:
- All ingredient lots used in the batch
- Supplier information for each ingredient
- Quantities consumed
- Supply chain mapping
- Regulatory compliance documentation

**Critical for**:
- FDA recall requirements
- Quality control investigations
- Customer safety notifications
- Liability management

---

### 16. reports_menu(user)

**Purpose**: Organized sub-menu for all reporting functions.

**Menu Options**:
1. On-Hand Inventory Report
2. Nearly Out of Stock Products
3. Almost Expired Ingredient Batches
4. Product Batch Cost Report
5. 🔍 Product Recall Traceability

**Design Pattern**:
- Clean separation of concerns
- Intuitive navigation
- Consistent user experience

---

## Integration Features

### Database Integration
- **Parameterized Queries**: Prevents SQL injection
- **Transaction Safety**: All operations are database-transaction safe
- **Role-Based Security**: manufacturer_id filtering ensures data isolation
- **Error Handling**: Comprehensive exception handling with user-friendly messages

### User Experience
- **Tabulated Output**: Uses `tabulate` library for formatted tables
- **Interactive Prompts**: Clear instructions and input validation
- **Progress Indicators**: Status messages with emoji indicators (✅❌)
- **Data Validation**: Input validation before database operations

### Advanced Features
- **Session Management**: UUID-based session tokens for production isolation
- **FEFO Algorithm**: Sophisticated inventory selection based on expiration dates
- **Cost Calculation**: Automatic batch cost computation from ingredient costs
- **Lot Traceability**: Complete supply chain traceability for quality control

### Performance Optimization
- **Efficient Queries**: Optimized SQL with proper indexing
- **Minimal Data Transfer**: Only retrieves necessary data
- **Cached Lookups**: Reuses manufacturer_id for multiple operations

### Error Recovery
- **Graceful Degradation**: System continues operating despite individual operation failures
- **Rollback Capability**: Database transactions ensure data consistency
- **User Feedback**: Clear error messages with suggested solutions

This comprehensive manufacturer function suite provides complete control over product lifecycle management, from initial product definition through recipe development, production execution, and post-production analysis, with advanced features supporting regulatory compliance and operational efficiency.