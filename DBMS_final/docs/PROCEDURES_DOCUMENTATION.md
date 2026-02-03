# Stored Procedures Documentation

## Overview
This document provides comprehensive documentation for all stored procedures defined in `01_schema_and_logic_fixed.sql`. These procedures implement critical business logic for product batch creation, product recall traceability, and regulatory compliance checking.

---

## Procedure Summary

| Procedure Name | Purpose | Parameters | Returns |
|----------------|---------|------------|---------|
| `sp_record_product_batch` | Creates product batches with ingredient consumption | 5 input parameters | Batch details |
| `sp_trace_recall` | Product recall traceability | 3 input parameters | Affected batches |
| `sp_compare_products_incompatibility` | Check ingredient compatibility | 2 input parameters | Conflict list |

---

## Detailed Procedure Documentation

### 1. sp_record_product_batch

**Purpose**: Core procedure for creating product batches with automatic ingredient consumption, cost calculation, and inventory management.

**Signature**:
```sql
CALL sp_record_product_batch(
    IN p_token VARCHAR(64),          -- Session token for staging isolation
    IN p_product_type_id INT,        -- Product type to produce
    IN p_recipe_plan_id INT,         -- Recipe plan (for future use)
    IN p_produced_units INT,         -- Number of units to produce
    IN p_manufacturer_id VARCHAR(32) -- Manufacturing company
);
```

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `p_token` | VARCHAR(64) | Yes | Session token for staging_consumption isolation |
| `p_product_type_id` | INT | Yes | Target product type to manufacture |
| `p_recipe_plan_id` | INT | Yes | Recipe plan ID (reserved for future use) |
| `p_produced_units` | INT | Yes | Number of product units to create |
| `p_manufacturer_id` | VARCHAR(32) | Yes | Manufacturer identifier |

**Return Values**:
```sql
SELECT product_batch_id, product_lot_number, batch_cost, unit_cost 
FROM product_batch WHERE product_batch_id = v_pb_id;
```

**Pre-Conditions**:
1. **Staging Data**: staging_consumption must contain ingredient allocations for p_token
2. **Valid Product**: p_product_type_id must exist and belong to p_manufacturer_id
3. **Batch Multiple**: p_produced_units must be multiple of standard_batch_units
4. **Sufficient Inventory**: All ingredient batches must have adequate on_hand quantities

**Business Logic Flow**:

1. **Input Validation**:
   ```sql
   -- Validate produced units > 0
   IF p_produced_units <= 0 THEN
       SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'produced_units must be > 0';
   END IF;

   -- Validate product type exists and check standard batch units
   SELECT standard_batch_units INTO v_standard_units FROM product_type 
   WHERE product_type_id = p_product_type_id FOR UPDATE;
   
   -- Enforce batch multiples
   IF (p_produced_units MOD v_standard_units) <> 0 THEN
       SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'produced_units must be an integer multiple of standard_batch_units';
   END IF;
   ```

2. **Safety Checks**:
   ```sql
   -- Check for expired lots
   SELECT COUNT(*) INTO v_expired_count
   FROM staging_consumption sc
   JOIN ingredient_batch ib ON sc.ingredient_batch_id = ib.ingredient_batch_id
   WHERE sc.session_token = p_token AND ib.expiration_date < CURDATE();

   -- Check sufficient inventory
   SELECT COUNT(*) INTO v_insufficient_count FROM (
       SELECT sc.ingredient_batch_id, SUM(sc.qty_oz) AS required_qty, ib.on_hand_oz
       FROM staging_consumption sc
       JOIN ingredient_batch ib ON sc.ingredient_batch_id = ib.ingredient_batch_id
       WHERE sc.session_token = p_token
       GROUP BY sc.ingredient_batch_id
       HAVING required_qty > ib.on_hand_oz
   ) t;
   ```

3. **Regulatory Compliance**:
   ```sql
   -- Check do-not-combine conflicts
   SELECT COUNT(*) INTO v_conflict_count
   FROM do_not_combine d
   WHERE EXISTS (SELECT 1 FROM staging_consumption sc
                 JOIN ingredient_batch ib ON sc.ingredient_batch_id = ib.ingredient_batch_id
                 WHERE sc.session_token = p_token AND ib.ingredient_id = d.ingredient_a)
     AND EXISTS (SELECT 1 FROM staging_consumption sc2
                 JOIN ingredient_batch ib2 ON sc2.ingredient_batch_id = ib2.ingredient_batch_id
                 WHERE sc2.session_token = p_token AND ib2.ingredient_id = d.ingredient_b);
   ```

4. **Cost Calculation**:
   ```sql
   -- Calculate total batch cost
   SELECT IFNULL(SUM(sc.qty_oz * ib.unit_cost),0) INTO v_batch_cost
   FROM staging_consumption sc
   JOIN ingredient_batch ib ON sc.ingredient_batch_id = ib.ingredient_batch_id
   WHERE sc.session_token = p_token;
   ```

5. **Product Batch Creation**:
   ```sql
   -- Create product batch record
   INSERT INTO product_batch (product_type_id, manufacturer_id, produced_units, batch_cost, unit_cost, expiration_date)
   VALUES (p_product_type_id, p_manufacturer_id, p_produced_units, v_batch_cost, 0, v_earliest_expiry);
   
   -- Generate lot number and set unit cost
   UPDATE product_batch
   SET product_lot_number = CONCAT(p_product_type_id,'-',p_manufacturer_id,'-',LPAD(v_pb_id,6,'0')),
       unit_cost = CASE WHEN p_produced_units > 0 THEN v_batch_cost / p_produced_units ELSE 0 END
   WHERE product_batch_id = v_pb_id;
   ```

6. **Ingredient Consumption**:
   ```sql
   -- Create consumption records (triggers automatically update inventory)
   INSERT INTO product_batch_consumption (product_batch_id, ingredient_batch_id, qty_oz)
   SELECT v_pb_id, sc.ingredient_batch_id, sc.qty_oz 
   FROM staging_consumption sc 
   WHERE sc.session_token = p_token;
   ```

**Error Conditions**:
- `'produced_units must be > 0'`
- `'Invalid product_type_id'`
- `'produced_units must be an integer multiple of standard_batch_units'`
- `'Staging contains expired ingredient lots'`
- `'Insufficient on-hand for one or more ingredient batches in staging'`
- `'Do-not-combine conflict detected among the chosen ingredient lots'`
- `'Operation would cause negative on_hand for a batch'`

**Usage Example**:
```sql
-- 1. Prepare staging consumption
DELETE FROM staging_consumption WHERE session_token = 'session123';
INSERT INTO staging_consumption (session_token, ingredient_batch_id, qty_oz) VALUES 
('session123', 5, 600.0),  -- Beef Steak
('session123', 11, 20.0);  -- Seasoning Blend

-- 2. Create product batch
CALL sp_record_product_batch('session123', 100, 1, 100, 'MFG001');

-- 3. Result: New batch created with auto-generated lot number
-- Example output: product_batch_id=5, product_lot_number='100-MFG001-000005', batch_cost=650.00, unit_cost=6.50
```

---

### 2. sp_trace_recall

**Purpose**: Provides comprehensive product recall traceability by identifying all product batches that used specific ingredient lots or ingredients.

**Signature**:
```sql
CALL sp_trace_recall(
    IN p_ingredient_id INT,       -- Specific ingredient to trace (optional)
    IN p_lot_number VARCHAR(128), -- Specific lot number to trace (optional)
    IN p_days_window INT          -- Days back to search (default: 20)
);
```

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `p_ingredient_id` | INT | No | Ingredient ID to trace (NULL for all ingredients) |
| `p_lot_number` | VARCHAR(128) | No | Specific ingredient lot to trace (NULL for all lots) |
| `p_days_window` | INT | No | Days back from current date (default: 20) |

**Return Columns**:
- `product_batch_id` (INT): Affected product batch
- `product_lot_number` (VARCHAR): Product lot identifier
- `product_type_id` (INT): Product type
- `product_name` (VARCHAR): Product name
- `manufacturer_id` (VARCHAR): Manufacturer
- `manufacturer_name` (VARCHAR): Manufacturer company name
- `produced_units` (INT): Units in affected batch
- `created_at` (TIMESTAMP): Production date
- `ingredient_lot_number` (VARCHAR): Source ingredient lot
- `ingredient_id` (INT): Ingredient type
- `ingredient_name` (VARCHAR): Ingredient name
- `consumed_qty_oz` (DECIMAL): Quantity consumed

**Business Logic**:
```sql
CREATE PROCEDURE sp_trace_recall(...)
BEGIN
    DECLARE v_start_date DATE;
    SET v_start_date = DATE_SUB(CURDATE(), INTERVAL COALESCE(p_days_window, 20) DAY);
    
    SELECT DISTINCT 
           pb.product_batch_id, pb.product_lot_number, 
           pb.product_type_id, pt.name AS product_name,
           pb.manufacturer_id, m.name AS manufacturer_name,
           pb.produced_units, pb.created_at,
           ib.lot_number AS ingredient_lot_number,
           ib.ingredient_id, ing.name AS ingredient_name,
           pbc.qty_oz AS consumed_qty_oz
    FROM product_batch pb
    JOIN product_type pt ON pt.product_type_id = pb.product_type_id
    JOIN manufacturer m ON m.manufacturer_id = pb.manufacturer_id
    JOIN product_batch_consumption pbc ON pbc.product_batch_id = pb.product_batch_id
    JOIN ingredient_batch ib ON ib.ingredient_batch_id = pbc.ingredient_batch_id
    JOIN ingredient ing ON ing.ingredient_id = ib.ingredient_id
    WHERE pb.created_at >= v_start_date
      AND (
          (p_ingredient_id IS NOT NULL AND ib.ingredient_id = p_ingredient_id)
          OR
          (p_lot_number IS NOT NULL AND ib.lot_number = p_lot_number)
      )
    ORDER BY pb.created_at DESC, pb.product_batch_id;
END$$
```

**Usage Scenarios**:

1. **Ingredient Recall**:
   ```sql
   -- Trace all products using Beef Steak (ingredient 106) in last 30 days
   CALL sp_trace_recall(106, NULL, 30);
   ```

2. **Lot-Specific Recall**:
   ```sql
   -- Trace specific ingredient lot
   CALL sp_trace_recall(NULL, '106-20-20251115143000123', 45);
   ```

3. **Recent Production Review**:
   ```sql
   -- Review last 7 days of production
   CALL sp_trace_recall(NULL, NULL, 7);
   ```

**Business Use Cases**:
- **Food Safety Recalls**: Quickly identify affected products
- **Quality Control**: Track ingredient impact on product quality
- **Supply Chain Analysis**: Understand ingredient usage patterns
- **Regulatory Compliance**: Provide audit trails for inspections
- **Customer Communication**: Identify specific batches for customer notification

---

### 3. sp_compare_products_incompatibility

**Purpose**: Analyzes two products for regulatory do-not-combine ingredient conflicts.

**Signature**:
```sql
CALL sp_compare_products_incompatibility(
    IN p_product_type_id_1 INT,  -- First product to compare
    IN p_product_type_id_2 INT   -- Second product to compare
);
```

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `p_product_type_id_1` | INT | Yes | First product type identifier |
| `p_product_type_id_2` | INT | Yes | Second product type identifier |

**Return Columns**:
- `ingredient_a` (INT): First conflicting ingredient ID
- `ingredient_a_name` (VARCHAR): First ingredient name
- `ingredient_b` (INT): Second conflicting ingredient ID
- `ingredient_b_name` (VARCHAR): Second ingredient name
- `found_in_product_1` (VARCHAR): Indicates presence in first product
- `found_in_product_2` (VARCHAR): Indicates presence in second product

**Business Logic**:
```sql
CREATE PROCEDURE sp_compare_products_incompatibility(...)
BEGIN
    -- Create temporary tables for ingredient lists
    CREATE TEMPORARY TABLE IF NOT EXISTS tmp_product1_ings (ingredient_id INT PRIMARY KEY);
    CREATE TEMPORARY TABLE IF NOT EXISTS tmp_product2_ings (ingredient_id INT PRIMARY KEY);
    
    -- Get ingredients from latest recipe plans
    INSERT IGNORE INTO tmp_product1_ings (ingredient_id)
    SELECT DISTINCT rpi.ingredient_id
    FROM recipe_plan_item rpi
    WHERE rpi.recipe_plan_id = (
        SELECT recipe_plan_id FROM recipe_plan 
        WHERE product_type_id = p_product_type_id_1
        ORDER BY created_at DESC LIMIT 1
    );
    
    -- Find conflicts between the two products
    SELECT dnc.ingredient_a, ia.name AS ingredient_a_name,
           dnc.ingredient_b, ib.name AS ingredient_b_name,
           'Product 1' AS found_in_product_1,
           'Product 2' AS found_in_product_2
    FROM do_not_combine dnc
    JOIN tmp_product1_ings p1 ON (p1.ingredient_id = dnc.ingredient_a OR p1.ingredient_id = dnc.ingredient_b)
    JOIN tmp_product2_ings p2 ON (p2.ingredient_id = dnc.ingredient_a OR p2.ingredient_id = dnc.ingredient_b)
    JOIN ingredient ia ON ia.ingredient_id = dnc.ingredient_a
    JOIN ingredient ib ON ib.ingredient_id = dnc.ingredient_b
    WHERE (p1.ingredient_id = dnc.ingredient_a AND p2.ingredient_id = dnc.ingredient_b)
       OR (p1.ingredient_id = dnc.ingredient_b AND p2.ingredient_id = dnc.ingredient_a);
    
    -- Cleanup temporary tables
    DROP TEMPORARY TABLE IF EXISTS tmp_product1_ings;
    DROP TEMPORARY TABLE IF EXISTS tmp_product2_ings;
END$$
```

**Usage Examples**:
```sql
-- Compare Steak Dinner with Mac & Cheese
CALL sp_compare_products_incompatibility(100, 101);

-- Expected result if no conflicts:
-- Empty result set (no conflicting ingredients found)

-- Example result if conflicts exist:
-- ingredient_a=104, ingredient_a_name='Sodium Phosphate', 
-- ingredient_b=106, ingredient_b_name='Beef Steak',
-- found_in_product_1='Product 1', found_in_product_2='Product 2'
```

**Business Use Cases**:
- **Regulatory Compliance**: Verify products don't violate do-not-combine rules
- **Quality Assurance**: Prevent production of unsafe product combinations
- **Product Development**: Check new formulations against existing products
- **Cross-Contamination Prevention**: Identify potential manufacturing conflicts
- **Audit Preparation**: Document compliance checking procedures

---

## Procedure Integration & Dependencies

### Transaction Management
All procedures use proper transaction boundaries:
- `START TRANSACTION` for multi-step operations
- `ROLLBACK` on validation failures
- `COMMIT` on successful completion

### Trigger Integration
Procedures work seamlessly with database triggers:
- **sp_record_product_batch** relies on consumption triggers for inventory updates
- Triggers provide automatic validation and data maintenance
- Procedures focus on business logic while triggers handle data integrity

### Error Handling Strategy
```sql
-- Consistent error reporting
SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Descriptive error message';

-- Pre-condition validation
-- Business rule enforcement  
-- Post-condition verification
```

### Performance Considerations
- **Row Locking**: Critical records locked during transactions
- **Batch Processing**: Optimized for production batch sizes
- **Index Usage**: Procedures designed to leverage existing indexes

---

## Monitoring & Troubleshooting

### Procedure Performance Monitoring
```sql
-- Enable procedure logging
SET GLOBAL log_queries_not_using_indexes = ON;
SET GLOBAL slow_query_log = ON;
SET GLOBAL long_query_time = 1;

-- Monitor procedure calls
SHOW PROCEDURE STATUS WHERE Name LIKE 'sp_%';
```

### Common Issues & Solutions

1. **Session Token Conflicts**:
   ```sql
   -- Always use unique session tokens
   SELECT UUID() as session_token;
   ```

2. **Staging Data Issues**:
   ```sql
   -- Verify staging data before procedure call
   SELECT * FROM staging_consumption WHERE session_token = 'your_token';
   ```

3. **Inventory Shortfalls**:
   ```sql
   -- Check available inventory
   SELECT * FROM v_report_onhand WHERE ingredient_id IN (106, 201) AND on_hand_oz > 0;
   ```

4. **Do-Not-Combine Violations**:
   ```sql
   -- Review incompatible pairs
   SELECT * FROM do_not_combine;
   ```

This comprehensive stored procedure system provides robust, transactionally-safe business logic implementation for the food manufacturing inventory system.