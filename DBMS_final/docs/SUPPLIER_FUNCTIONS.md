# Supplier Functions Documentation

## Overview
This document provides comprehensive documentation for all supplier-specific functionality implemented in `supplier_actions.py`. Suppliers manage their ingredient portfolios, formulation specifications, inventory batches, and delivery operations within the food manufacturing supply chain.

---

## Function Categories

| Category | Functions | Purpose |
|----------|-----------|---------|
| **Ingredient Management** | 3 functions | Manage ingredient supply portfolio |
| **Formulation Management** | 5 functions | Create and maintain product formulations with materials |
| **Batch Operations** | 2 functions | Receive and track ingredient inventory batches |
| **Compliance & Safety** | 1 function | Monitor do-not-combine rules for safety |

---

## Core Helper Functions

### _print_table(rows, message="Results")

**Purpose**: Standardized table formatting for all supplier operations.

**Features**:
- Uses `tabulate` library with grid format
- Handles empty result sets gracefully
- Provides consistent user experience across all functions

### _get_supplier_id(user)

**Purpose**: Extract and validate supplier identity from user session.

**Security**: Ensures only authenticated suppliers can access supplier functions.

---

## Ingredient Management

### 1. view_my_ingredients(user)

**Purpose**: Display complete ingredient portfolio for the logged-in supplier.

**Database Query**:
```sql
SELECT 
    i.ingredient_id,
    i.name AS ingredient_name,
    i.is_compound,
    CASE 
        WHEN i.is_compound THEN 'Compound'
        ELSE 'Atomic'
    END AS ingredient_type
FROM supplier_ingredient si
JOIN ingredient i ON i.ingredient_id = si.ingredient_id
WHERE si.supplier_id = %s
ORDER BY i.ingredient_id
```

**Output Format**:
```
┌──────────────┬──────────────────┬─────────────┬──────────────────┐
│ ingredient_  │ ingredient_name  │ is_compound │ ingredient_type  │
│ id           │                  │             │                  │
├──────────────┼──────────────────┼─────────────┼──────────────────┤
│           15 │ Garlic Powder    │           0 │ Atomic           │
│           20 │ Mixed Vegetables │           1 │ Compound         │
└──────────────┴──────────────────┴─────────────┴──────────────────┘
```

**Business Value**:
- Portfolio visibility for business planning
- Ingredient type differentiation (atomic vs compound)
- Foundation for formulation and batch management

---

### 2. add_ingredient_to_supply(user) ⭐ **MOST COMPLEX FUNCTION**

**Purpose**: Comprehensive ingredient addition with automatic formulation creation for compound ingredients.

#### **Two Addition Approaches**

**Approach A: Existing Ingredient Addition**
```python
# Interactive flow for existing ingredients
if choice == '1':
    # Display all available ingredients
    # Validate ingredient exists and not already supplied
    # Add to supplier_ingredient table
    # Auto-handle compound ingredient materials
    # Optional formulation creation
```

**Approach B: New Ingredient Creation**
```python
# Complete ingredient creation workflow
elif choice == '2':
    # Create new ingredient record
    # Auto-add to supplier portfolio
    # Optional material definition for compounds
    # Integrated formulation setup
```

#### **Advanced Compound Ingredient Logic**

**Automatic Material Addition**:
```python
# For compound ingredients, auto-add all materials
if is_compound:
    materials_sql = """
    SELECT im.material_ingredient_id, i.name as material_name, im.qty_oz
    FROM ingredient_material im
    JOIN ingredient i ON i.ingredient_id = im.material_ingredient_id
    WHERE im.parent_ingredient_id = %s
    """
```

**Smart Duplication Prevention**:
- Checks existing supply relationships before adding materials
- Reports materials already in portfolio vs newly added
- Prevents redundant supplier_ingredient records

#### **Integrated Formulation Creation**

**Workflow Integration**:
1. Ingredient addition (existing or new)
2. For compounds: automatic material discovery
3. Auto-addition of materials to supplier portfolio
4. Optional formulation creation with all materials included
5. Material quantity preservation from ingredient_material table

**Database Operations**:
```sql
-- Add ingredient to supply list
INSERT INTO supplier_ingredient (supplier_id, ingredient_id) VALUES (%s, %s)

-- Create formulation
INSERT INTO supplier_formulation 
(supplier_id, ingredient_id, pack_size_oz, unit_price, effective_from, effective_to)
VALUES (%s, %s, %s, %s, %s, %s)

-- Add formulation materials
INSERT INTO supplier_formulation_material 
(formulation_id, material_ingredient_id, qty_oz)
VALUES (%s, %s, %s)
```

**Error Handling**:
- Validates ingredient existence before addition
- Prevents duplicate supplier_ingredient entries
- Handles formulation creation failures gracefully
- Maintains transaction integrity across complex operations

**Business Benefits**:
- Streamlined onboarding for compound ingredients
- Automatic compliance with BOM specifications
- Reduced manual data entry errors
- Integrated supply chain setup

---

### 3. remove_ingredient_from_supply(user)

**Purpose**: Safe removal of ingredients from supplier portfolio with cascade protection.

**Safety Validations**:

**Formulation Impact Check**:
```sql
SELECT COUNT(*) as count
FROM supplier_formulation
WHERE supplier_id = %s AND ingredient_id = %s
```

**Cascade Preview**:
- Shows number of formulations that will be deleted
- Lists formulation materials that will be removed
- Requires explicit confirmation before deletion

**Database Operations**:
```sql
-- Delete formulations (CASCADE deletes materials)
DELETE FROM supplier_formulation
WHERE supplier_id = %s AND ingredient_id = %s

-- Remove from supply list
DELETE FROM supplier_ingredient
WHERE supplier_id = %s AND ingredient_id = %s
```

**Business Protection**:
- Prevents accidental data loss
- Maintains referential integrity
- Provides clear impact assessment before deletion

---

## Formulation Management

### 4. view_my_formulations(user)

**Purpose**: Display all active formulations with status indicators.

**Database Query**:
```sql
SELECT 
    sf.formulation_id,
    sf.ingredient_id,
    i.name AS ingredient_name,
    sf.pack_size_oz,
    sf.unit_price,
    sf.effective_from,
    sf.effective_to,
    CASE 
        WHEN CURDATE() BETWEEN sf.effective_from AND COALESCE(sf.effective_to, '9999-12-31')
        THEN 'Active'
        ELSE 'Inactive'
    END AS status
FROM supplier_formulation sf
JOIN ingredient i ON i.ingredient_id = sf.ingredient_id
WHERE sf.supplier_id = %s
ORDER BY sf.formulation_id DESC
```

**Business Insights**:
- **Active/Inactive Status**: Based on effective date ranges
- **Price Evolution**: Historical pricing through versioned formulations
- **Portfolio Coverage**: Shows formulation coverage across ingredients

---

### 5. create_formulation(user)

**Purpose**: Create new formulations with automatic material addition for compound ingredients.

**Interactive Workflow**:
1. Display supplier's ingredient portfolio
2. Select ingredient for formulation
3. Collect pricing and packaging information
4. Define effective date range
5. For compounds: automated material addition via `_add_formulation_materials()`

**Date Range Logic**:
```python
effective_to = effective_to_input if effective_to_input else None
# Supports both fixed and open-ended formulations
```

**Material Addition Helper**:
```python
def _add_formulation_materials(formulation_id, parent_ingredient_id):
    # Shows available atomic ingredients
    # Interactive material selection with quantities
    # Validates material types (atomic only)
    # Supports multiple material addition
```

---

### 6. view_formulation_details(user)

**Purpose**: Comprehensive formulation inspection with complete material breakdown.

**Database Queries**:
```sql
-- Formulation header
SELECT 
    sf.formulation_id, sf.supplier_id, s.name AS supplier_name,
    sf.ingredient_id, i.name AS ingredient_name, i.is_compound,
    sf.pack_size_oz, sf.unit_price, sf.effective_from, sf.effective_to
FROM supplier_formulation sf
JOIN supplier s ON s.supplier_id = sf.supplier_id
JOIN ingredient i ON i.ingredient_id = sf.ingredient_id
WHERE sf.formulation_id = %s AND sf.supplier_id = %s

-- Material details (for compounds)
SELECT 
    sfm.material_ingredient_id, i.name AS material_name, sfm.qty_oz
FROM supplier_formulation_material sfm
JOIN ingredient i ON i.ingredient_id = sfm.material_ingredient_id
WHERE sfm.formulation_id = %s
ORDER BY sfm.material_ingredient_id
```

**Output Features**:
- Complete formulation metadata
- Material breakdown with quantities
- Effective date range analysis
- Security validation (supplier ownership)

---

### 7. update_formulation(user)

**Purpose**: Advanced formulation modification with granular update options.

#### **Three Update Categories**

**Category 1: Pricing & Packaging**
```python
if choice == '1':
    # Update pack_size_oz and unit_price
    # Preserves current values if input empty
    # Immediate database update
```

**Category 2: Effective Date Management**
```python
elif choice == '2':
    # Modify effective_from and effective_to
    # Supports open-ended dates (None for effective_to)
    # Version control for pricing history
```

**Category 3: Material Management (Compound Only)**
```python
elif choice == '3':
    # Add new materials
    # Update material quantities  
    # Remove existing materials
    # Live material list refresh
```

#### **Dynamic Material Management**

**Add Materials**:
- Shows available atomic ingredients
- Prevents duplicate material addition
- Live formulation refresh after each operation

**Update Quantities**:
- Shows current quantity before update
- Validates material existence in formulation
- Immediate feedback on changes

**Remove Materials**:
- Confirmation required for deletion
- Maintains formulation integrity
- Updates display after removal

**Live Refresh Logic**:
```python
# After each operation, refresh the materials display
materials = run_query(materials_sql, (formulation_id,))
print('\n--- Updated Materials ---')
if materials:
    _print_table(materials, "Updated Materials")
```

---

### 8. delete_formulation(user)

**Purpose**: Safe formulation deletion with material cascade handling.

**Impact Assessment**:
```sql
SELECT COUNT(*) as count
FROM supplier_formulation_material
WHERE formulation_id = %s
```

**Deletion Preview**:
- Shows formulation to be deleted
- Counts associated materials
- Explains cascade effects
- Requires explicit confirmation

**Database Operation**:
```sql
DELETE FROM supplier_formulation
WHERE formulation_id = %s AND supplier_id = %s
-- CASCADE automatically deletes supplier_formulation_material records
```

---

## Batch Operations

### 9. receive_ingredient_batch(user)

**Purpose**: Create inventory lots from received ingredient shipments.

**Validation Workflow**:
1. **Supplier Authorization**: Verify supplier can provide the ingredient
2. **Expiration Compliance**: Enforce 90-day minimum expiration requirement
3. **Data Collection**: Gather all batch metadata
4. **Lot Generation**: Trigger automatic lot number generation

**Database Operation**:
```sql
INSERT INTO ingredient_batch 
(ingredient_id, supplier_id, supplier_batch_id, quantity_oz, unit_cost, expiration_date)
VALUES (%s, %s, %s, %s, %s, %s)
```

**Auto-Generated Fields** (via triggers):
- `lot_number`: System-generated unique identifier
- `received_at`: Automatic timestamp
- `on_hand_oz`: Initially equals `quantity_oz`

**Expiration Logic**:
```python
min_expiration = datetime.now() + timedelta(days=90)
print(f'Minimum expiration date: {min_expiration.strftime("%Y-%m-%d")}')
```

**Lot Number Retrieval**:
```sql
SELECT lot_number, ingredient_batch_id
FROM ingredient_batch
WHERE ingredient_id = %s AND supplier_id = %s AND supplier_batch_id = %s
ORDER BY received_at DESC LIMIT 1
```

**Business Benefits**:
- **Traceability**: Complete lot tracking from receipt
- **Quality Control**: Expiration date enforcement
- **Inventory Management**: Automatic on-hand quantity initialization
- **Cost Tracking**: Unit cost recording for financial analysis

---

### 10. view_my_batches(user)

**Purpose**: Comprehensive batch inventory monitoring with status intelligence.

**Database Query**:
```sql
SELECT 
    ib.ingredient_batch_id, ib.lot_number, ib.ingredient_id,
    i.name AS ingredient_name, ib.supplier_batch_id,
    ib.quantity_oz, ib.on_hand_oz, ib.unit_cost, ib.expiration_date,
    ib.received_at, DATEDIFF(ib.expiration_date, CURDATE()) AS days_until_expiry,
    CASE 
        WHEN ib.on_hand_oz = 0 THEN 'Depleted'
        WHEN DATEDIFF(ib.expiration_date, CURDATE()) < 10 THEN 'Expiring Soon'
        WHEN DATEDIFF(ib.expiration_date, CURDATE()) < 0 THEN 'Expired'
        ELSE 'Available'
    END AS status
FROM ingredient_batch ib
JOIN ingredient i ON i.ingredient_id = ib.ingredient_id
WHERE ib.supplier_id = %s
ORDER BY ib.received_at DESC
```

**Intelligent Status Logic**:
- **Depleted**: `on_hand_oz = 0` (fully consumed)
- **Expiring Soon**: Less than 10 days until expiration
- **Expired**: Past expiration date
- **Available**: Normal inventory status

**Summary Analytics**:
```python
total_batches = len(rows)
available = sum(1 for r in rows if r['status'] == 'Available')
expiring = sum(1 for r in rows if r['status'] == 'Expiring Soon')
expired = sum(1 for r in rows if r['status'] == 'Expired')
depleted = sum(1 for r in rows if r['status'] == 'Depleted')
```

**Business Intelligence**:
- **Inventory Health**: Quick assessment of batch status distribution
- **Expiration Management**: Early warning for waste prevention
- **Consumption Tracking**: Depletion analysis for demand forecasting
- **Financial Analysis**: Cost tracking across all batches

---

## Compliance & Safety

### 11. view_do_not_combine(user)

**Purpose**: Display global ingredient incompatibility rules for safety compliance.

**Database Query**:
```sql
SELECT 
    dnc.ingredient_a, ia.name AS ingredient_a_name,
    dnc.ingredient_b, ib.name AS ingredient_b_name
FROM do_not_combine dnc
JOIN ingredient ia ON ia.ingredient_id = dnc.ingredient_a
JOIN ingredient ib ON ib.ingredient_id = dnc.ingredient_b
ORDER BY dnc.ingredient_a, dnc.ingredient_b
```

**Compliance Features**:
- **Global Rules**: System-wide incompatibility enforcement
- **Safety First**: Critical for food safety and regulatory compliance
- **Formulation Guidance**: Helps suppliers design safe formulations
- **Regulatory Support**: Aids in FDA and food safety compliance

**Business Application**:
- Formulation design constraints
- Quality assurance reference
- Supplier education on safety requirements
- Risk management for food production

---

## Integration Features

### Database Integration
- **Parameterized Queries**: Complete SQL injection protection
- **Transaction Safety**: All operations maintain ACID properties
- **Foreign Key Enforcement**: Referential integrity across all operations
- **Cascade Handling**: Proper cleanup of related records during deletions

### User Experience Design
- **Consistent Formatting**: Standardized table output across all functions
- **Interactive Workflows**: Step-by-step guidance for complex operations
- **Input Validation**: Comprehensive validation before database operations
- **Error Messages**: User-friendly error reporting with actionable guidance

### Advanced Features
- **Date Range Management**: Flexible effective date handling for formulations
- **Status Intelligence**: Dynamic status calculation based on business rules
- **Automatic Material Handling**: Smart compound ingredient material management
- **Live Data Refresh**: Real-time display updates during multi-step operations

### Business Logic
- **Portfolio Management**: Complete ingredient supply chain control
- **Version Control**: Historical formulation tracking through effective dates
- **Safety Compliance**: Integration with do-not-combine rules
- **Cost Management**: Unit cost tracking and financial analysis support

### Security Model
- **Supplier Isolation**: All operations filtered by supplier_id
- **Data Ownership**: Suppliers can only modify their own records
- **Authentication Required**: All functions require valid supplier session
- **Authorization Validation**: Consistent permission checking

### Performance Optimization
- **Efficient Queries**: Optimized JOIN operations with proper indexing
- **Minimal Data Transfer**: Only essential data retrieved and displayed
- **Bulk Operations**: Efficient handling of multiple material additions
- **Smart Caching**: Reuse of supplier_id throughout sessions

This comprehensive supplier function suite enables complete supply chain management from ingredient portfolio development through formulation creation, batch receiving, and compliance monitoring, supporting both simple atomic ingredients and complex compound formulations with full traceability and safety compliance.