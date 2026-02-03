# Database Views Documentation

## Overview
This document provides comprehensive documentation for all database views defined in `01_schema_and_logic_fixed.sql`. These views provide simplified access to complex data relationships and support reporting, monitoring, and business intelligence functions.

---

## View Summary

| View Name | Purpose | Primary Use Case |
|-----------|---------|------------------|
| `v_report_onhand` | Current inventory status | Real-time inventory monitoring |
| `v_nearly_out_of_stock` | Low inventory products | Procurement planning |
| `v_almost_expired` | Soon-to-expire batches | Waste prevention & FEFO management |
| `v_active_formulations` | Current supplier pricing | Cost analysis & supplier selection |
| `v_health_risk_violations` | Regulatory compliance issues | Quality assurance & risk management |

---

## Detailed View Documentation

### 1. v_report_onhand

**Purpose**: Provides a simplified view of current ingredient inventory status across all batches.

```sql
DROP VIEW IF EXISTS v_report_onhand;
CREATE VIEW v_report_onhand AS
SELECT 
    ib.ingredient_batch_id, 
    ib.lot_number, 
    ib.ingredient_id, 
    ib.supplier_id, 
    ib.on_hand_oz, 
    ib.expiration_date
FROM ingredient_batch ib;
```

**Columns**:
- `ingredient_batch_id` (INT): Unique batch identifier
- `lot_number` (VARCHAR): Human-readable lot identifier  
- `ingredient_id` (INT): Type of ingredient
- `supplier_id` (VARCHAR): Source supplier
- `on_hand_oz` (DECIMAL): Current available quantity
- `expiration_date` (DATE): Expiration date

**Business Use Cases**:
- Real-time inventory dashboards
- Daily inventory reports
- FEFO (First Expired, First Out) lot selection
- Audit trail for inventory levels

**Example Queries**:
```sql
-- View all available inventory
SELECT * FROM v_report_onhand WHERE on_hand_oz > 0;

-- Check specific ingredient availability
SELECT * FROM v_report_onhand 
WHERE ingredient_id = 101 AND on_hand_oz > 0
ORDER BY expiration_date;

-- Inventory by supplier
SELECT supplier_id, SUM(on_hand_oz) as total_inventory
FROM v_report_onhand 
GROUP BY supplier_id;
```

---

### 2. v_nearly_out_of_stock

**Purpose**: Identifies products that may face production shortages based on ingredient availability.

```sql
DROP VIEW IF EXISTS v_nearly_out_of_stock;
CREATE VIEW v_nearly_out_of_stock AS
SELECT 
    pt.product_type_id, 
    pt.name AS product_name, 
    pt.manufacturer_id, 
    pt.standard_batch_units,
    IFNULL(SUM(ib.on_hand_oz),0) AS total_on_hand_oz
FROM product_type pt
LEFT JOIN recipe_plan rp ON rp.product_type_id = pt.product_type_id
LEFT JOIN recipe_plan_item rpi ON rpi.recipe_plan_id = rp.recipe_plan_id
LEFT JOIN ingredient_batch ib ON ib.ingredient_id = rpi.ingredient_id
GROUP BY pt.product_type_id
HAVING total_on_hand_oz < pt.standard_batch_units;
```

**Columns**:
- `product_type_id` (INT): Product identifier
- `product_name` (VARCHAR): Product name
- `manufacturer_id` (VARCHAR): Manufacturing company
- `standard_batch_units` (INT): Standard production batch size
- `total_on_hand_oz` (DECIMAL): Total available ingredient inventory

**Business Logic**:
- Aggregates all ingredient inventory for each product
- Compares against standard batch requirements
- Flags products where total ingredient availability is insufficient

**Business Use Cases**:
- Production planning alerts
- Procurement requirement forecasting
- Supply chain risk management
- Manufacturing scheduling optimization

**Example Queries**:
```sql
-- Critical shortage alerts
SELECT * FROM v_nearly_out_of_stock 
ORDER BY total_on_hand_oz;

-- Shortages by manufacturer
SELECT manufacturer_id, COUNT(*) as products_at_risk
FROM v_nearly_out_of_stock 
GROUP BY manufacturer_id;

-- Detailed shortage analysis
SELECT v.*, pt.category_id, c.name as category_name
FROM v_nearly_out_of_stock v
JOIN product_type pt ON v.product_type_id = pt.product_type_id
JOIN category c ON pt.category_id = c.category_id;
```

---

### 3. v_almost_expired

**Purpose**: Monitors ingredient batches approaching expiration for waste prevention and FEFO optimization.

```sql
DROP VIEW IF EXISTS v_almost_expired;
CREATE VIEW v_almost_expired AS
SELECT 
    ib.ingredient_batch_id, 
    ib.lot_number, 
    ib.ingredient_id, 
    i.name AS ingredient_name,
    ib.supplier_id, 
    s.name AS supplier_name, 
    ib.on_hand_oz, 
    ib.expiration_date,
    DATEDIFF(ib.expiration_date, CURDATE()) AS days_until_expiry
FROM ingredient_batch ib
JOIN ingredient i ON i.ingredient_id = ib.ingredient_id
JOIN supplier s ON s.supplier_id = ib.supplier_id
WHERE ib.expiration_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 10 DAY)
  AND ib.on_hand_oz > 0
ORDER BY ib.expiration_date;
```

**Columns**:
- `ingredient_batch_id` (INT): Batch identifier
- `lot_number` (VARCHAR): Lot identifier
- `ingredient_id` (INT): Ingredient type
- `ingredient_name` (VARCHAR): Human-readable ingredient name
- `supplier_id` (VARCHAR): Supplier identifier
- `supplier_name` (VARCHAR): Supplier company name
- `on_hand_oz` (DECIMAL): Available quantity
- `expiration_date` (DATE): Expiration date
- `days_until_expiry` (INT): Calculated days remaining

**Business Logic**:
- 10-day warning window (configurable)
- Only shows batches with available inventory
- Sorted by expiration date (most urgent first)

**Business Use Cases**:
- Daily expiration monitoring
- FEFO lot selection optimization
- Waste reduction initiatives
- Quality control alerts
- Discount/promotion planning

**Example Queries**:
```sql
-- Urgent expiration alerts (≤ 3 days)
SELECT * FROM v_almost_expired 
WHERE days_until_expiry <= 3;

-- Expiration summary by ingredient
SELECT ingredient_name, COUNT(*) as batches_expiring, SUM(on_hand_oz) as total_oz
FROM v_almost_expired 
GROUP BY ingredient_id, ingredient_name
ORDER BY total_oz DESC;

-- Supplier performance on expiration management
SELECT supplier_name, AVG(days_until_expiry) as avg_days_remaining
FROM v_almost_expired 
GROUP BY supplier_id, supplier_name;
```

---

### 4. v_active_formulations

**Purpose**: Shows currently valid supplier formulations for pricing and sourcing decisions.

```sql
DROP VIEW IF EXISTS v_active_formulations;
CREATE VIEW v_active_formulations AS
SELECT 
    sf.formulation_id, 
    sf.supplier_id, 
    s.name AS supplier_name,
    sf.ingredient_id, 
    i.name AS ingredient_name,
    sf.pack_size_oz, 
    sf.unit_price, 
    sf.effective_from, 
    sf.effective_to
FROM supplier_formulation sf
JOIN supplier s ON s.supplier_id = sf.supplier_id
JOIN ingredient i ON i.ingredient_id = sf.ingredient_id
WHERE CURDATE() BETWEEN sf.effective_from AND COALESCE(sf.effective_to, '9999-12-31');
```

**Columns**:
- `formulation_id` (INT): Formulation identifier
- `supplier_id` (VARCHAR): Supplier identifier
- `supplier_name` (VARCHAR): Supplier company name
- `ingredient_id` (INT): Ingredient type
- `ingredient_name` (VARCHAR): Ingredient name
- `pack_size_oz` (DECIMAL): Package size
- `unit_price` (DECIMAL): Price per package
- `effective_from` (DATE): Start of validity period
- `effective_to` (DATE): End of validity period (NULL = ongoing)

**Business Logic**:
- Only shows formulations valid today
- Handles open-ended formulations (effective_to = NULL)
- Includes supplier and ingredient names for readability

**Business Use Cases**:
- Supplier price comparison
- Cost analysis for production planning
- Procurement sourcing decisions
- Contract negotiation reference
- Financial reporting

**Example Queries**:
```sql
-- Compare pricing for specific ingredient
SELECT * FROM v_active_formulations 
WHERE ingredient_id = 101 
ORDER BY unit_price;

-- Supplier offering analysis
SELECT supplier_name, COUNT(*) as ingredient_count, AVG(unit_price) as avg_price
FROM v_active_formulations 
GROUP BY supplier_id, supplier_name;

-- Cost per ounce analysis
SELECT *, (unit_price / pack_size_oz) as cost_per_oz
FROM v_active_formulations 
ORDER BY cost_per_oz;
```

---

### 5. v_health_risk_violations

**Purpose**: Identifies product batches that violate do-not-combine rules for regulatory compliance.

```sql
DROP VIEW IF EXISTS v_health_risk_violations;
CREATE VIEW v_health_risk_violations AS
SELECT 
    pb.product_batch_id, 
    pb.product_lot_number, 
    pb.created_at,
    pt.name AS product_name, 
    pb.manufacturer_id,
    dnc.ingredient_a, 
    ia.name AS ingredient_a_name,
    dnc.ingredient_b, 
    ib.name AS ingredient_b_name
FROM product_batch pb
JOIN product_type pt ON pt.product_type_id = pb.product_type_id
JOIN product_batch_consumption pbc1 ON pbc1.product_batch_id = pb.product_batch_id
JOIN ingredient_batch iba ON iba.ingredient_batch_id = pbc1.ingredient_batch_id
JOIN product_batch_consumption pbc2 ON pbc2.product_batch_id = pb.product_batch_id
JOIN ingredient_batch ibb ON ibb.ingredient_batch_id = pbc2.ingredient_batch_id
JOIN do_not_combine dnc ON (
    (dnc.ingredient_a = iba.ingredient_id AND dnc.ingredient_b = ibb.ingredient_id)
)
JOIN ingredient ia ON ia.ingredient_id = dnc.ingredient_a
JOIN ingredient ib ON ib.ingredient_id = dnc.ingredient_b
WHERE pb.created_at >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
GROUP BY pb.product_batch_id, dnc.ingredient_a, dnc.ingredient_b;
```

**Columns**:
- `product_batch_id` (INT): Violating product batch
- `product_lot_number` (VARCHAR): Product lot identifier
- `created_at` (TIMESTAMP): Batch creation time
- `product_name` (VARCHAR): Product name
- `manufacturer_id` (VARCHAR): Manufacturing company
- `ingredient_a` (INT): First conflicting ingredient
- `ingredient_a_name` (VARCHAR): First ingredient name
- `ingredient_b` (INT): Second conflicting ingredient
- `ingredient_b_name` (VARCHAR): Second ingredient name

**Business Logic**:
- Scans last 30 days of production (configurable)
- Identifies products using incompatible ingredient combinations
- Cross-references consumption records with do-not-combine rules
- Groups by batch and ingredient pair to avoid duplicates

**Business Use Cases**:
- Quality control alerts
- Regulatory compliance monitoring
- Product recall preparation
- Manufacturing process audit
- Risk management reporting

**Example Queries**:
```sql
-- Recent violations summary
SELECT COUNT(*) as violation_count, 
       COUNT(DISTINCT product_batch_id) as affected_batches
FROM v_health_risk_violations;

-- Violations by manufacturer
SELECT manufacturer_id, COUNT(*) as violation_count
FROM v_health_risk_violations 
GROUP BY manufacturer_id;

-- Most common ingredient conflicts
SELECT ingredient_a_name, ingredient_b_name, COUNT(*) as occurrence_count
FROM v_health_risk_violations 
GROUP BY ingredient_a, ingredient_b 
ORDER BY occurrence_count DESC;
```

---

## View Performance Optimization

### Recommended Indexes
```sql
-- Support v_nearly_out_of_stock performance
CREATE INDEX idx_recipe_plan_product ON recipe_plan(product_type_id);
CREATE INDEX idx_recipe_plan_item_plan ON recipe_plan_item(recipe_plan_id);
CREATE INDEX idx_ingredient_batch_ingredient ON ingredient_batch(ingredient_id);

-- Support v_almost_expired performance  
CREATE INDEX idx_ingredient_batch_expiry ON ingredient_batch(expiration_date, on_hand_oz);

-- Support v_active_formulations performance
CREATE INDEX idx_supplier_formulation_dates ON supplier_formulation(effective_from, effective_to);

-- Support v_health_risk_violations performance
CREATE INDEX idx_product_batch_created ON product_batch(created_at);
CREATE INDEX idx_product_batch_consumption_batch ON product_batch_consumption(product_batch_id);
```

### Materialized View Considerations
For high-volume environments, consider materializing frequently-accessed views:

```sql
-- Example: Create materialized table for v_report_onhand
CREATE TABLE mv_report_onhand AS SELECT * FROM v_report_onhand;

-- Refresh strategy (could be triggered or scheduled)
TRUNCATE mv_report_onhand;
INSERT INTO mv_report_onhand SELECT * FROM v_report_onhand;
```

---

## Integration with Application Layer

### Python Application Usage
Views are accessed through the standard database connection:

```python
# Example: Get expiring ingredients
from app.db import run_query

expiring_items = run_query("""
    SELECT * FROM v_almost_expired 
    WHERE days_until_expiry <= 7
    ORDER BY days_until_expiry
""")

for item in expiring_items:
    print(f"URGENT: {item['ingredient_name']} expires in {item['days_until_expiry']} days")
```

### Reporting Integration
Views provide clean interfaces for business intelligence tools:
- Power BI / Tableau connectivity
- Excel pivot table data sources
- Custom dashboard applications
- Automated alert systems

### View Dependencies
- **v_nearly_out_of_stock**: Depends on product_type, recipe_plan, recipe_plan_item, ingredient_batch
- **v_almost_expired**: Depends on ingredient_batch, ingredient, supplier
- **v_active_formulations**: Depends on supplier_formulation, supplier, ingredient
- **v_health_risk_violations**: Depends on product_batch, product_type, product_batch_consumption, ingredient_batch, do_not_combine, ingredient

---

## Monitoring & Maintenance

### View Performance Monitoring
```sql
-- Monitor view execution plans
EXPLAIN SELECT * FROM v_health_risk_violations WHERE manufacturer_id = 'MFG001';

-- Monitor view usage (enable slow query log)
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 2;
```

### View Refresh Strategies
- **Real-time views**: Current implementation provides live data
- **Snapshot views**: Consider for historical reporting
- **Incremental refresh**: For large datasets with materialized views

This comprehensive view system provides powerful reporting capabilities while maintaining clean separation between business logic and data access patterns.