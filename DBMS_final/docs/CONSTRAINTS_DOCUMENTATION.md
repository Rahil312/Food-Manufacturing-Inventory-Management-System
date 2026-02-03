# Database Constraints Documentation

## Overview
This document provides comprehensive documentation for all database constraints defined in `01_schema_and_logic_fixed.sql`. These constraints ensure data integrity, enforce business rules, and maintain referential consistency across the food manufacturing inventory system.

---

## Constraint Categories

| Constraint Type | Purpose | Count | Examples |
|-----------------|---------|-------|----------|
| **Primary Keys** | Unique record identification | 15 | manufacturer_id, product_batch_id |
| **Foreign Keys** | Referential integrity | 20 | manufacturer_id → manufacturer(manufacturer_id) |
| **Unique Constraints** | Business uniqueness | 4 | lot_number, product_lot_number |
| **Check Constraints** | Value validation | 8 | qty_oz > 0, unit_price >= 0 |
| **Not Null Constraints** | Required fields | 25+ | name, created_at, is_compound |

---

## Primary Key Constraints

Primary keys ensure unique identification and prevent duplicate records.

### Business ID Primary Keys (Manual Assignment)
```sql
-- Core reference entities use business-meaningful IDs
manufacturer (manufacturer_id VARCHAR(32))     -- e.g., 'MFG001', 'MFG002'
supplier (supplier_id VARCHAR(32))             -- e.g., '20', '21' 
user_account (user_id VARCHAR(32))             -- e.g., 'MFG001', 'SUP020'
ingredient (ingredient_id INT)                 -- e.g., 101, 201, 301
product_type (product_type_id INT AUTO_INCREMENT) -- System-generated
```

### System-Generated Primary Keys (Auto-Increment)
```sql
-- Transactional entities use auto-increment
category (category_id INT AUTO_INCREMENT)
supplier_formulation (formulation_id INT AUTO_INCREMENT)
recipe_plan (recipe_plan_id INT AUTO_INCREMENT)
recipe_plan_item (recipe_plan_item_id INT AUTO_INCREMENT)
ingredient_batch (ingredient_batch_id INT AUTO_INCREMENT)
product_batch (product_batch_id INT AUTO_INCREMENT)
product_batch_consumption (product_batch_consumption_id INT AUTO_INCREMENT)
```

### Composite Primary Keys
```sql
-- Many-to-many relationships
supplier_ingredient (supplier_id, ingredient_id)
ingredient_material (parent_ingredient_id, material_ingredient_id)
supplier_formulation_material (formulation_id, material_ingredient_id)
do_not_combine (ingredient_a, ingredient_b)
```

**Business Rules**:
- Business IDs allow meaningful references in reports and user interfaces
- Auto-increment IDs ensure uniqueness without business logic dependency
- Composite keys enforce unique relationships in junction tables

---

## Foreign Key Constraints

Foreign keys maintain referential integrity and enforce valid relationships.

### Core Reference Relationships

#### User Account Associations
```sql
-- Users can be associated with manufacturers or suppliers
CONSTRAINT fk_user_manufacturer 
  FOREIGN KEY (manufacturer_id) REFERENCES manufacturer(manufacturer_id) 
  ON DELETE SET NULL

CONSTRAINT fk_user_supplier 
  FOREIGN KEY (supplier_id) REFERENCES supplier(supplier_id) 
  ON DELETE SET NULL
```

**Business Rule**: User accounts remain valid even if associated companies are removed.

#### Product Type Ownership
```sql
-- Products belong to specific manufacturers and categories
CONSTRAINT fk_pt_manufacturer 
  FOREIGN KEY (manufacturer_id) REFERENCES manufacturer(manufacturer_id) 
  ON DELETE CASCADE

CONSTRAINT fk_pt_category 
  FOREIGN KEY (category_id) REFERENCES category(category_id) 
  ON DELETE RESTRICT
```

**Business Rules**:
- Products are deleted when manufacturer is removed (CASCADE)
- Categories cannot be deleted if products exist (RESTRICT)

### Ingredient Composition Relationships

#### Ingredient Materials (Compound Ingredients)
```sql
-- Compound ingredients made from atomic materials
CONSTRAINT fk_im_parent 
  FOREIGN KEY (parent_ingredient_id) REFERENCES ingredient(ingredient_id) 
  ON DELETE CASCADE

CONSTRAINT fk_im_material 
  FOREIGN KEY (material_ingredient_id) REFERENCES ingredient(ingredient_id) 
  ON DELETE RESTRICT
```

**Business Rules**:
- Remove composition when compound ingredient deleted (CASCADE)
- Prevent deletion of materials used in compounds (RESTRICT)

#### Supplier Ingredient Capabilities
```sql
-- Track which ingredients suppliers can provide
CONSTRAINT fk_si_supplier 
  FOREIGN KEY (supplier_id) REFERENCES supplier(supplier_id) 
  ON DELETE CASCADE

CONSTRAINT fk_si_ingredient 
  FOREIGN KEY (ingredient_id) REFERENCES ingredient(ingredient_id) 
  ON DELETE CASCADE
```

**Business Rule**: Supplier capabilities removed when either supplier or ingredient deleted.

### Inventory & Production Relationships

#### Ingredient Batches (Received Inventory)
```sql
-- Ingredient lots received from suppliers
CONSTRAINT fk_ib_ingredient 
  FOREIGN KEY (ingredient_id) REFERENCES ingredient(ingredient_id) 
  ON DELETE RESTRICT

CONSTRAINT fk_ib_supplier 
  FOREIGN KEY (supplier_id) REFERENCES supplier(supplier_id) 
  ON DELETE RESTRICT
```

**Business Rule**: Prevent deletion of ingredients/suppliers with existing inventory.

#### Product Batch Consumption (Usage Tracking)
```sql
-- Track ingredient usage in product batches
CONSTRAINT fk_pbc_pb 
  FOREIGN KEY (product_batch_id) REFERENCES product_batch(product_batch_id) 
  ON DELETE CASCADE

CONSTRAINT fk_pbc_ib 
  FOREIGN KEY (ingredient_batch_id) REFERENCES ingredient_batch(ingredient_batch_id) 
  ON DELETE RESTRICT
```

**Business Rules**:
- Remove consumption records when product batch deleted (CASCADE)
- Preserve ingredient batch history (RESTRICT)

### Recipe Management Relationships

#### Recipe Plans (Versioned BOMs)
```sql
-- Recipe plans belong to specific products
CONSTRAINT fk_rp_product 
  FOREIGN KEY (product_type_id) REFERENCES product_type(product_type_id) 
  ON DELETE CASCADE

-- Recipe items reference ingredients
CONSTRAINT fk_rpi_plan 
  FOREIGN KEY (recipe_plan_id) REFERENCES recipe_plan(recipe_plan_id) 
  ON DELETE CASCADE

CONSTRAINT fk_rpi_ingredient 
  FOREIGN KEY (ingredient_id) REFERENCES ingredient(ingredient_id) 
  ON DELETE RESTRICT
```

**Business Rules**:
- Recipe plans removed with product (CASCADE)
- Ingredients preserved for historical recipes (RESTRICT)

---

## Unique Constraints

Unique constraints enforce business uniqueness rules beyond primary keys.

### System-Generated Unique Identifiers
```sql
-- Auto-generated lot numbers must be globally unique
ingredient_batch.lot_number VARCHAR(128) UNIQUE
product_batch.product_lot_number VARCHAR(128) UNIQUE
```

**Business Rule**: Lot numbers provide unique traceability across entire system.

### Business Uniqueness Rules
```sql
-- Suppliers have unique business codes
supplier.supplier_code VARCHAR(32) UNIQUE

-- Product codes unique within manufacturer
product_type: UNIQUE KEY ux_manufacturer_product_code (manufacturer_id, product_code)
```

**Business Rules**:
- Supplier codes enable external system integration
- Product codes prevent manufacturer internal duplication

---

## Check Constraints

Check constraints validate data values according to business rules.

### Quantity Validations
```sql
-- All quantities must be positive
ingredient_material.qty_oz DECIMAL(12,3) CHECK (qty_oz > 0)
recipe_plan_item.qty_oz_per_unit DECIMAL(12,4) CHECK (qty_oz_per_unit > 0)
staging_consumption.qty_oz DECIMAL(14,3) CHECK (qty_oz > 0)
product_batch_consumption.qty_oz DECIMAL(14,3) CHECK (qty_oz > 0)
ingredient_batch.quantity_oz DECIMAL(14,3) CHECK (quantity_oz >= 0)
```

**Business Rule**: Negative quantities are not allowed in food manufacturing.

### Financial Validations
```sql
-- Prices and costs must be non-negative
supplier_formulation.unit_price DECIMAL(12,4) CHECK (unit_price >= 0)
ingredient_batch.unit_cost DECIMAL(12,4) CHECK (unit_cost >= 0)
```

**Business Rule**: Free ingredients allowed (cost = 0) but negative costs prohibited.

### Production Validations
```sql
-- Production quantities must be positive
product_type.standard_batch_units INT CHECK (standard_batch_units > 0)
product_batch.produced_units INT CHECK (produced_units > 0)
```

**Business Rule**: All production must result in measurable output.

---

## Not Null Constraints

Not null constraints ensure required data is always present.

### Required Business Identifiers
```sql
-- Core identifiers cannot be empty
manufacturer.name VARCHAR(255) NOT NULL
supplier.name VARCHAR(255) NOT NULL
ingredient.name VARCHAR(255) NOT NULL
ingredient.is_compound BOOLEAN NOT NULL DEFAULT FALSE
user_account.role ENUM('MANUFACTURER','SUPPLIER','VIEWER') NOT NULL
```

### Required Relationships
```sql
-- Essential foreign key relationships
product_type.manufacturer_id VARCHAR(32) NOT NULL
product_type.category_id INT NOT NULL
ingredient_batch.ingredient_id INT NOT NULL
ingredient_batch.supplier_id VARCHAR(32) NOT NULL
product_batch.product_type_id INT NOT NULL
product_batch.manufacturer_id VARCHAR(32) NOT NULL
```

### Required Operational Data
```sql
-- Critical operational values
ingredient_batch.expiration_date DATE NOT NULL
product_batch.expiration_date DATE NOT NULL
supplier_formulation.effective_from DATE NOT NULL
staging_consumption.session_token VARCHAR(64) NOT NULL
```

---

## Constraint Implementation Patterns

### Cascading Delete Hierarchy
```
manufacturer
  └─ CASCADE → product_type
      └─ CASCADE → recipe_plan
          └─ CASCADE → recipe_plan_item

supplier
  └─ CASCADE → supplier_ingredient
  └─ CASCADE → supplier_formulation
      └─ CASCADE → supplier_formulation_material
```

### Restrict Delete Protection
```
category (protected by product_type)
ingredient (protected by recipe_plan_item, ingredient_batch)
ingredient_batch (protected by product_batch_consumption)
```

### Null-Tolerant Relationships
```
user_account.manufacturer_id (can be NULL for non-manufacturers)
user_account.supplier_id (can be NULL for non-suppliers)
supplier_formulation.effective_to (NULL = open-ended)
```

---

## Constraint Validation Examples

### Valid Operations
```sql
-- ✅ Valid ingredient material composition
INSERT INTO ingredient_material (parent_ingredient_id, material_ingredient_id, qty_oz) 
VALUES (201, 101, 6.0);  -- Positive quantity

-- ✅ Valid product batch
INSERT INTO product_batch (product_type_id, manufacturer_id, produced_units, expiration_date)
VALUES (100, 'MFG001', 500, '2026-01-15');  -- All required fields

-- ✅ Valid supplier formulation
INSERT INTO supplier_formulation (supplier_id, ingredient_id, pack_size_oz, unit_price, effective_from)
VALUES ('20', 101, 16.0, 12.50, '2025-01-01');  -- Non-negative price
```

### Constraint Violations
```sql
-- ❌ Check constraint violation
INSERT INTO ingredient_material (parent_ingredient_id, material_ingredient_id, qty_oz) 
VALUES (201, 101, -1.0);  -- ERROR: qty_oz > 0 violated

-- ❌ Foreign key violation  
INSERT INTO product_type (manufacturer_id, product_code, name, category_id, standard_batch_units)
VALUES ('MFG999', 'P-001', 'Test Product', 1, 100);  -- ERROR: MFG999 doesn't exist

-- ❌ Unique constraint violation
INSERT INTO ingredient_batch (ingredient_id, supplier_id, supplier_batch_id, lot_number, ...)
VALUES (101, '20', 'B001', '101-20-existing-lot', ...);  -- ERROR: lot_number already exists

-- ❌ Not null constraint violation
INSERT INTO manufacturer (manufacturer_id, name) VALUES ('MFG003', NULL);  -- ERROR: name cannot be NULL
```

---

## Performance Impact & Optimization

### Index Requirements for Foreign Keys
```sql
-- Foreign key columns automatically indexed by MySQL
-- Additional indexes may be needed for performance

-- Composite foreign key indexing
CREATE INDEX idx_staging_consumption_lookup ON staging_consumption(session_token, ingredient_batch_id);
CREATE INDEX idx_product_batch_consumption_batch ON product_batch_consumption(product_batch_id);
```

### Constraint Checking Performance
- **ON DELETE CASCADE**: Requires scanning related tables
- **ON DELETE RESTRICT**: Requires existence checks
- **Check Constraints**: Minimal overhead for simple validations
- **Foreign Key Checks**: Use existing indexes when possible

### Constraint Maintenance
```sql
-- Monitor constraint violations
SHOW ENGINE INNODB STATUS;  -- Check for constraint-related deadlocks

-- Disable constraints for bulk operations (use carefully)
SET FOREIGN_KEY_CHECKS=0;
-- ... bulk operations ...
SET FOREIGN_KEY_CHECKS=1;
```

---

## Error Handling & Troubleshooting

### Common Constraint Error Messages

1. **Foreign Key Violations**:
   ```
   ERROR 1452 (23000): Cannot add or update a child row: 
   a foreign key constraint fails
   ```
   **Solution**: Verify referenced record exists

2. **Check Constraint Violations**:
   ```
   ERROR 3819 (HY000): Check constraint 'chk_qty_positive' is violated
   ```
   **Solution**: Ensure values meet constraint conditions

3. **Unique Constraint Violations**:
   ```
   ERROR 1062 (23000): Duplicate entry 'value' for key 'UNIQUE_KEY_NAME'
   ```
   **Solution**: Use different value or update existing record

4. **Not Null Violations**:
   ```
   ERROR 1364 (HY000): Field 'column_name' doesn't have a default value
   ```
   **Solution**: Provide value for required field

### Constraint Analysis Queries
```sql
-- View all foreign key constraints
SELECT TABLE_NAME, CONSTRAINT_NAME, REFERENCED_TABLE_NAME 
FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
WHERE REFERENCED_TABLE_SCHEMA = 'dbms_project';

-- View check constraints
SELECT TABLE_NAME, CONSTRAINT_NAME, CHECK_CLAUSE 
FROM INFORMATION_SCHEMA.CHECK_CONSTRAINTS 
WHERE CONSTRAINT_SCHEMA = 'dbms_project';

-- View unique constraints
SELECT TABLE_NAME, CONSTRAINT_NAME, COLUMN_NAME 
FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
WHERE TABLE_SCHEMA = 'dbms_project' AND CONSTRAINT_NAME != 'PRIMARY';
```

This comprehensive constraint system ensures data integrity, enforces business rules, and maintains referential consistency throughout the food manufacturing inventory management system.