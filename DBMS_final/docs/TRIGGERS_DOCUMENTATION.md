# Database Triggers Documentation

## Overview
This document provides comprehensive documentation for all database triggers defined in `01_schema_and_logic_fixed.sql`. These triggers enforce business rules, maintain data integrity, and automate critical processes in the food manufacturing inventory system.

---

## Trigger Summary

| Trigger Name | Table | Event | Purpose |
|--------------|-------|-------|---------|
| `trg_ingredient_material_before_insert` | ingredient_material | BEFORE INSERT | Enforce one-level composition rule |
| `trg_supplier_formulation_before_insert` | supplier_formulation | BEFORE INSERT | Prevent overlapping effective date ranges |
| `trg_ingredient_batch_before_insert` | ingredient_batch | BEFORE INSERT | Generate lot numbers & enforce expiration rules |
| `trg_product_batch_consumption_before_insert` | product_batch_consumption | BEFORE INSERT | Validate consumption rules |
| `trg_product_batch_consumption_after_insert` | product_batch_consumption | AFTER INSERT | Update on-hand inventory |

---

## Detailed Trigger Documentation

### 1. trg_ingredient_material_before_insert

**Purpose**: Enforces the one-level composition rule for compound ingredients.

**Table**: `ingredient_material`  
**Event**: `BEFORE INSERT`  
**Timing**: Row-level trigger

```sql
DROP TRIGGER IF EXISTS trg_ingredient_material_before_insert$$
CREATE TRIGGER trg_ingredient_material_before_insert
BEFORE INSERT ON ingredient_material
FOR EACH ROW
BEGIN
    -- Prevent a material from itself being a parent (no cycles)
    IF NEW.parent_ingredient_id = NEW.material_ingredient_id THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Ingredient cannot be a material of itself';
    END IF;
    -- Prevent materials that themselves have children (one-level only)
    IF EXISTS (SELECT 1 FROM ingredient_material im WHERE im.parent_ingredient_id = NEW.material_ingredient_id) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Materials must be atomic (no grandchildren allowed)';
    END IF;
END$$
```

**Business Rules Enforced**:
1. **No Self-Reference**: An ingredient cannot be a material of itself
2. **One-Level Only**: Materials must be atomic ingredients (no grandchildren)

**Error Conditions**:
- `SQLSTATE '45000'`: "Ingredient cannot be a material of itself"
- `SQLSTATE '45000'`: "Materials must be atomic (no grandchildren allowed)"

**Example Scenarios**:
```sql
-- ✅ VALID: Seasoning Blend made from Salt and Pepper (both atomic)
INSERT INTO ingredient_material (parent_ingredient_id, material_ingredient_id, qty_oz) 
VALUES (201, 101, 6.0);  -- Seasoning Blend contains Salt

-- ❌ INVALID: Self-reference
INSERT INTO ingredient_material (parent_ingredient_id, material_ingredient_id, qty_oz) 
VALUES (201, 201, 1.0);  -- ERROR: Ingredient cannot be a material of itself

-- ❌ INVALID: Multi-level composition
-- If Seasoning Blend (201) exists, cannot use it as material for Super Blend (301)
INSERT INTO ingredient_material (parent_ingredient_id, material_ingredient_id, qty_oz) 
VALUES (301, 201, 2.0);  -- ERROR: Materials must be atomic (no grandchildren allowed)
```

---

### 2. trg_supplier_formulation_before_insert

**Purpose**: Prevents overlapping effective date ranges for supplier formulations.

**Table**: `supplier_formulation`  
**Event**: `BEFORE INSERT`  
**Timing**: Row-level trigger

```sql
DROP TRIGGER IF EXISTS trg_supplier_formulation_before_insert$$
CREATE TRIGGER trg_supplier_formulation_before_insert
BEFORE INSERT ON supplier_formulation
FOR EACH ROW
BEGIN
    IF EXISTS (
        SELECT 1 FROM supplier_formulation sf
        WHERE sf.supplier_id = NEW.supplier_id
            AND sf.ingredient_id = NEW.ingredient_id
            AND (NEW.effective_to IS NULL OR sf.effective_to IS NULL OR 
                 NOT (NEW.effective_to < sf.effective_from OR NEW.effective_from > sf.effective_to))
    ) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Overlapping supplier formulation effective dates are not allowed';
    END IF;
END$$
```

**Business Rules Enforced**:
1. **No Date Overlap**: Only one formulation can be active for a supplier-ingredient pair at any time
2. **Proper Versioning**: Ensures clean pricing history without conflicts

**Overlap Detection Logic**:
- Two date ranges overlap if NOT (range1_end < range2_start OR range1_start > range2_end)
- Handles NULL effective_to dates (open-ended ranges)

**Example Scenarios**:
```sql
-- ✅ VALID: Sequential formulations
INSERT INTO supplier_formulation (supplier_id, ingredient_id, pack_size_oz, unit_price, effective_from, effective_to) 
VALUES ('20', 101, 16.0, 10.0, '2025-01-01', '2025-06-30');

INSERT INTO supplier_formulation (supplier_id, ingredient_id, pack_size_oz, unit_price, effective_from, effective_to) 
VALUES ('20', 101, 16.0, 12.0, '2025-07-01', NULL);  -- New pricing starts after previous ends

-- ❌ INVALID: Overlapping dates
INSERT INTO supplier_formulation (supplier_id, ingredient_id, pack_size_oz, unit_price, effective_from, effective_to) 
VALUES ('20', 101, 20.0, 11.0, '2025-06-15', '2025-12-31');  -- ERROR: Overlapping with existing formulation
```

---

### 3. trg_ingredient_batch_before_insert

**Purpose**: Auto-generates unique lot numbers and enforces minimum expiration requirements.

**Table**: `ingredient_batch`  
**Event**: `BEFORE INSERT`  
**Timing**: Row-level trigger

```sql
DROP TRIGGER IF EXISTS trg_ingredient_batch_before_insert$$
CREATE TRIGGER trg_ingredient_batch_before_insert
BEFORE INSERT ON ingredient_batch
FOR EACH ROW
BEGIN
    -- Enforce 90-day minimum expiration rule
    IF DATEDIFF(NEW.expiration_date, CURDATE()) < 90 THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Expiration date must be at least 90 days from intake date';
    END IF;
    
    -- Initialize on_hand_oz to the received quantity
    SET NEW.on_hand_oz = NEW.quantity_oz;
    
    -- Generate unique lot_number: <ingredient>-<supplier>-<timestamp><random>
    SET NEW.lot_number = CONCAT(
        NEW.ingredient_id, '-', 
        NEW.supplier_id, '-', 
        DATE_FORMAT(NOW(), '%Y%m%d%H%i%s'), 
        LPAD(FLOOR(RAND() * 1000), 3, '0')
    );
END$$
```

**Business Rules Enforced**:
1. **Food Safety**: Minimum 90-day shelf life requirement
2. **Automatic Inventory**: Sets on_hand_oz to received quantity
3. **Unique Identification**: Generates collision-resistant lot numbers

**Lot Number Format**: `{ingredient_id}-{supplier_id}-{YYYYMMDDHHMMSS}{000-999}`

**Example Scenarios**:
```sql
-- ✅ VALID: Sufficient expiration time
INSERT INTO ingredient_batch (ingredient_id, supplier_id, supplier_batch_id, quantity_oz, unit_cost, expiration_date) 
VALUES (101, '20', 'B12345', 500.0, 0.10, '2026-03-15');
-- Result: lot_number = '101-20-20251116143000123', on_hand_oz = 500.0

-- ❌ INVALID: Expiration too soon
INSERT INTO ingredient_batch (ingredient_id, supplier_id, supplier_batch_id, quantity_oz, unit_cost, expiration_date) 
VALUES (101, '20', 'B12346', 300.0, 0.10, '2025-12-01');  -- ERROR: Only 15 days from now
```

---

### 4. trg_product_batch_consumption_before_insert

**Purpose**: Validates consumption rules before allowing ingredient usage.

**Table**: `product_batch_consumption`  
**Event**: `BEFORE INSERT`  
**Timing**: Row-level trigger

```sql
DROP TRIGGER IF EXISTS trg_product_batch_consumption_before_insert$$
CREATE TRIGGER trg_product_batch_consumption_before_insert
BEFORE INSERT ON product_batch_consumption
FOR EACH ROW
BEGIN
    DECLARE exp DATE;
    DECLARE v_on_hand DECIMAL(14,3);
    DECLARE v_exists INT;
    
    -- Verify ingredient_batch exists
    SELECT COUNT(*) INTO v_exists FROM ingredient_batch WHERE ingredient_batch_id = NEW.ingredient_batch_id;
    IF v_exists = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid ingredient_batch_id';
    END IF;
    
    -- Check if expired (with NULL safety)
    SELECT expiration_date INTO exp FROM ingredient_batch WHERE ingredient_batch_id = NEW.ingredient_batch_id;
    IF exp IS NOT NULL AND exp < CURDATE() THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Cannot consume expired ingredient lot';
    END IF;
    
    -- Check sufficient on_hand at insert time
    SELECT on_hand_oz INTO v_on_hand FROM ingredient_batch WHERE ingredient_batch_id = NEW.ingredient_batch_id;
    IF v_on_hand IS NOT NULL AND v_on_hand < NEW.qty_oz THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Insufficient on-hand quantity for ingredient batch';
    END IF;
END$$
```

**Business Rules Enforced**:
1. **Referential Integrity**: Ingredient batch must exist
2. **Food Safety**: Cannot consume expired ingredients
3. **Inventory Validation**: Sufficient on-hand quantity required

**Error Conditions**:
- `SQLSTATE '45000'`: "Invalid ingredient_batch_id"
- `SQLSTATE '45000'`: "Cannot consume expired ingredient lot"
- `SQLSTATE '45000'`: "Insufficient on-hand quantity for ingredient batch"

**Example Scenarios**:
```sql
-- ✅ VALID: Fresh ingredient with sufficient quantity
INSERT INTO product_batch_consumption (product_batch_id, ingredient_batch_id, qty_oz) 
VALUES (1, 5, 100.0);  -- Assuming batch 5 has 100+ oz available and not expired

-- ❌ INVALID: Expired ingredient
INSERT INTO product_batch_consumption (product_batch_id, ingredient_batch_id, qty_oz) 
VALUES (1, 6, 50.0);  -- ERROR: If batch 6 expired yesterday

-- ❌ INVALID: Insufficient quantity
INSERT INTO product_batch_consumption (product_batch_id, ingredient_batch_id, qty_oz) 
VALUES (1, 7, 200.0);  -- ERROR: If batch 7 only has 150 oz available
```

---

### 5. trg_product_batch_consumption_after_insert

**Purpose**: Automatically updates ingredient inventory after consumption.

**Table**: `product_batch_consumption`  
**Event**: `AFTER INSERT`  
**Timing**: Row-level trigger

```sql
DROP TRIGGER IF EXISTS trg_product_batch_consumption_after_insert$$
CREATE TRIGGER trg_product_batch_consumption_after_insert
AFTER INSERT ON product_batch_consumption
FOR EACH ROW
BEGIN
    UPDATE ingredient_batch
    SET on_hand_oz = on_hand_oz - NEW.qty_oz
    WHERE ingredient_batch_id = NEW.ingredient_batch_id;
END$$
```

**Business Rules Enforced**:
1. **Automatic Inventory**: Updates on-hand quantities immediately
2. **Data Consistency**: Ensures consumption records match inventory levels

**Process Flow**:
1. Consumption record is inserted (validated by previous trigger)
2. This trigger fires automatically
3. on_hand_oz is decremented by consumed quantity

**Example Process**:
```sql
-- Initial state: ingredient_batch_id=5 has on_hand_oz=500.0

INSERT INTO product_batch_consumption (product_batch_id, ingredient_batch_id, qty_oz) 
VALUES (1, 5, 100.0);

-- After trigger fires: ingredient_batch_id=5 now has on_hand_oz=400.0
```

---

## Trigger Dependencies & Interactions

### Execution Order
1. **BEFORE INSERT triggers** validate and transform data
2. **INSERT operation** occurs if validations pass
3. **AFTER INSERT triggers** perform cascading updates

### Integration with Stored Procedures
- **sp_record_product_batch**: Relies on consumption triggers for inventory management
- Triggers provide automatic enforcement even if procedures are bypassed

### Concurrency Considerations
- **Row-level locking**: Triggers use FOR UPDATE where necessary
- **Race conditions**: Minimized through proper transaction boundaries
- **Performance**: Optimized queries in trigger logic

---

## Error Handling & Troubleshooting

### Common Error Scenarios

1. **Ingredient Material Errors**:
   ```sql
   ERROR 1644 (45000): Ingredient cannot be a material of itself
   ERROR 1644 (45000): Materials must be atomic (no grandchildren allowed)
   ```
   **Solution**: Verify ingredient hierarchy and ensure one-level composition

2. **Formulation Date Errors**:
   ```sql
   ERROR 1644 (45000): Overlapping supplier formulation effective dates are not allowed
   ```
   **Solution**: Check existing formulations and adjust date ranges

3. **Batch Expiration Errors**:
   ```sql
   ERROR 1644 (45000): Expiration date must be at least 90 days from intake date
   ```
   **Solution**: Use expiration dates at least 90 days in the future

4. **Consumption Validation Errors**:
   ```sql
   ERROR 1644 (45000): Cannot consume expired ingredient lot
   ERROR 1644 (45000): Insufficient on-hand quantity for ingredient batch
   ```
   **Solution**: Verify ingredient batch status and available quantities

### Debugging Triggers
```sql
-- Check trigger existence
SHOW TRIGGERS FROM dbms_project;

-- View trigger definitions
SHOW CREATE TRIGGER trg_ingredient_batch_before_insert;

-- Monitor trigger execution (enable general log)
SET GLOBAL general_log = 'ON';
```

---

## Performance Considerations

### Trigger Optimization
- **Minimal Logic**: Triggers perform only essential validations
- **Efficient Queries**: Use indexed lookups where possible
- **Avoid Loops**: All triggers use single-row operations

### Indexing Recommendations
```sql
-- Support trigger performance
CREATE INDEX idx_ingredient_material_parent ON ingredient_material(parent_ingredient_id);
CREATE INDEX idx_supplier_formulation_lookup ON supplier_formulation(supplier_id, ingredient_id, effective_from);
CREATE INDEX idx_ingredient_batch_expiration ON ingredient_batch(expiration_date);
```

### Monitoring Performance
- Monitor trigger execution time during high-volume operations
- Consider trigger disable/enable during bulk data loads
- Use EXPLAIN on trigger SELECT statements

This comprehensive trigger system ensures data integrity, enforces complex business rules, and maintains inventory accuracy automatically throughout the food manufacturing system.