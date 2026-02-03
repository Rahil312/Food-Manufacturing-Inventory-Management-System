# Database Schema Documentation (DDL)

## Overview
This document provides comprehensive documentation for all database objects defined in `01_schema_and_logic_fixed.sql`. The database implements a food manufacturing inventory management system with role-based access control.

## Database Configuration
- **Database Name**: `dbms_project`
- **Character Set**: `utf8mb4`
- **Collation**: `utf8mb4_general_ci`
- **Target DBMS**: MySQL 8.0+ / MariaDB 10.4+

---

## Table Documentation

### 1. Core Reference Tables

#### manufacturer
Stores manufacturing company information.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| manufacturer_id | VARCHAR(32) | PRIMARY KEY | Unique manufacturer identifier |
| name | VARCHAR(255) | NOT NULL | Company name |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |

**Business Rules:**
- Each manufacturer has a unique alphanumeric ID
- Used for role-based access control in application

---

#### supplier
Stores supplier company information.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| supplier_id | VARCHAR(32) | PRIMARY KEY | Unique supplier identifier |
| supplier_code | VARCHAR(32) | UNIQUE | Business-friendly supplier code |
| name | VARCHAR(255) | NOT NULL | Supplier company name |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |

**Business Rules:**
- Each supplier has unique ID and code for different identification needs
- Used for role-based access control in application

---

#### category
Product categorization (Dinners, Sides, Beverages, etc.).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| category_id | INT | PRIMARY KEY, AUTO_INCREMENT | System-generated category ID |
| name | VARCHAR(128) | NOT NULL, UNIQUE | Category name |

**Business Rules:**
- Categories are shared across all manufacturers
- Used for product classification and reporting

---

### 2. User Management

#### user_account
Application-level user authentication and role assignment.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| user_id | VARCHAR(32) | PRIMARY KEY | Unique user identifier |
| username | VARCHAR(64) | | Login username |
| password_hash | VARCHAR(255) | | Hashed password (use bcrypt in production) |
| first_name | VARCHAR(64) | | User's first name |
| last_name | VARCHAR(64) | | User's last name |
| role | ENUM('MANUFACTURER','SUPPLIER','VIEWER') | NOT NULL | User's system role |
| manufacturer_id | VARCHAR(32) | FK to manufacturer | Associated manufacturer (if role=MANUFACTURER) |
| supplier_id | VARCHAR(32) | FK to supplier | Associated supplier (if role=SUPPLIER) |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Account creation timestamp |

**Foreign Key Constraints:**
- `fk_user_manufacturer`: manufacturer_id → manufacturer(manufacturer_id) ON DELETE SET NULL
- `fk_user_supplier`: supplier_id → supplier(supplier_id) ON DELETE SET NULL

**Business Rules:**
- One role per user (no role inheritance)
- MANUFACTURER users must have manufacturer_id
- SUPPLIER users must have supplier_id  
- VIEWER users have no company association

---

### 3. Ingredient Management

#### ingredient
Master list of all ingredients (atomic and compound).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| ingredient_id | INT | PRIMARY KEY | Unique ingredient identifier |
| name | VARCHAR(255) | NOT NULL | Ingredient name |
| is_compound | BOOLEAN | NOT NULL, DEFAULT FALSE | TRUE if made from other ingredients |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |

**Business Rules:**
- ingredient_id is manually assigned (not auto-increment) for business control
- is_compound=FALSE: atomic ingredient (salt, pepper)
- is_compound=TRUE: compound ingredient (seasoning blend)

---

#### ingredient_material
Composition of compound ingredients (one level only).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| parent_ingredient_id | INT | PRIMARY KEY (composite), FK to ingredient | Compound ingredient ID |
| material_ingredient_id | INT | PRIMARY KEY (composite), FK to ingredient | Component ingredient ID |
| qty_oz | DECIMAL(12,3) | NOT NULL, CHECK (qty_oz > 0) | Quantity of material in ounces |

**Foreign Key Constraints:**
- `fk_im_parent`: parent_ingredient_id → ingredient(ingredient_id) ON DELETE CASCADE
- `fk_im_material`: material_ingredient_id → ingredient(ingredient_id) ON DELETE RESTRICT

**Business Rules:**
- One-level composition only (no grandchildren)
- Enforced by trigger `trg_ingredient_material_before_insert`
- Materials must be atomic ingredients

---

#### supplier_ingredient
Many-to-many relationship: which ingredients each supplier can provide.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| supplier_id | VARCHAR(32) | PRIMARY KEY (composite), FK to supplier | Supplier identifier |
| ingredient_id | INT | PRIMARY KEY (composite), FK to ingredient | Ingredient identifier |

**Foreign Key Constraints:**
- `fk_si_supplier`: supplier_id → supplier(supplier_id) ON DELETE CASCADE
- `fk_si_ingredient`: ingredient_id → ingredient(ingredient_id) ON DELETE CASCADE

**Business Rules:**
- Multiple suppliers can provide the same ingredient
- One supplier can provide multiple ingredients

---

### 4. Supplier Formulations & Pricing

#### supplier_formulation
Versioned pricing and packaging for supplier ingredients.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| formulation_id | INT | PRIMARY KEY, AUTO_INCREMENT | Unique formulation ID |
| supplier_id | VARCHAR(32) | NOT NULL, FK to supplier | Supplier identifier |
| ingredient_id | INT | NOT NULL, FK to ingredient | Ingredient identifier |
| pack_size_oz | DECIMAL(12,3) | NOT NULL | Package size in ounces |
| unit_price | DECIMAL(12,4) | NOT NULL, CHECK (unit_price >= 0) | Price per package |
| effective_from | DATE | NOT NULL | Start date of validity |
| effective_to | DATE | | End date of validity (NULL = open-ended) |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |

**Foreign Key Constraints:**
- `fk_sf_supplier`: supplier_id → supplier(supplier_id) ON DELETE CASCADE
- `fk_sf_ingredient`: ingredient_id → ingredient(ingredient_id) ON DELETE CASCADE

**Business Rules:**
- No overlapping effective date ranges (enforced by trigger)
- Used for cost calculations in product batches

---

#### supplier_formulation_material
Materials needed for compound ingredient formulations.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| formulation_id | INT | PRIMARY KEY (composite), FK to supplier_formulation | Formulation ID |
| material_ingredient_id | INT | PRIMARY KEY (composite), FK to ingredient | Material ingredient ID |
| qty_oz | DECIMAL(12,3) | NOT NULL, CHECK (qty_oz > 0) | Quantity of material needed |

**Foreign Key Constraints:**
- `fk_sfm_formulation`: formulation_id → supplier_formulation(formulation_id) ON DELETE CASCADE
- `fk_sfm_material`: material_ingredient_id → ingredient(ingredient_id) ON DELETE RESTRICT

**Business Rules:**
- Only applies to compound ingredients
- Used for material cost breakdown in formulations

---

### 5. Regulatory Compliance

#### do_not_combine
Global list of incompatible ingredient pairs.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| ingredient_a | INT | PRIMARY KEY (composite), FK to ingredient | First ingredient ID (smaller ID) |
| ingredient_b | INT | PRIMARY KEY (composite), FK to ingredient | Second ingredient ID (larger ID) |

**Foreign Key Constraints:**
- `fk_dnc_a`: ingredient_a → ingredient(ingredient_id) ON DELETE CASCADE
- `fk_dnc_b`: ingredient_b → ingredient(ingredient_id) ON DELETE CASCADE

**Business Rules:**
- ingredient_a must be < ingredient_b (enforced by application)
- Used to prevent hazardous ingredient combinations
- Checked during product batch creation

---

### 6. Product Management

#### product_type
Product definitions by manufacturers.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| product_type_id | INT | PRIMARY KEY, AUTO_INCREMENT | System-generated product ID |
| manufacturer_id | VARCHAR(32) | NOT NULL, FK to manufacturer | Owning manufacturer |
| product_code | VARCHAR(64) | NOT NULL | Manufacturer's product code |
| name | VARCHAR(255) | NOT NULL | Product name |
| category_id | INT | NOT NULL, FK to category | Product category |
| standard_batch_units | INT | NOT NULL, CHECK (standard_batch_units > 0) | Standard production batch size |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |

**Foreign Key Constraints:**
- `fk_pt_manufacturer`: manufacturer_id → manufacturer(manufacturer_id) ON DELETE CASCADE
- `fk_pt_category`: category_id → category(category_id) ON DELETE RESTRICT

**Unique Constraints:**
- `ux_manufacturer_product_code`: (manufacturer_id, product_code)

**Business Rules:**
- Each manufacturer controls their own product codes
- Standard batch size used for production planning

---

#### recipe_plan
Versioned bill of materials (BOM) for products.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| recipe_plan_id | INT | PRIMARY KEY, AUTO_INCREMENT | System-generated recipe ID |
| product_type_id | INT | NOT NULL, FK to product_type | Associated product |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Recipe creation timestamp |
| notes | TEXT | | Optional recipe notes |

**Foreign Key Constraints:**
- `fk_rp_product`: product_type_id → product_type(product_type_id) ON DELETE CASCADE

**Business Rules:**
- Multiple recipe plans can exist per product (versioning)
- Latest recipe plan used for production

---

#### recipe_plan_item
Individual ingredients within a recipe plan.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| recipe_plan_item_id | INT | PRIMARY KEY, AUTO_INCREMENT | System-generated item ID |
| recipe_plan_id | INT | NOT NULL, FK to recipe_plan | Parent recipe plan |
| ingredient_id | INT | NOT NULL, FK to ingredient | Required ingredient |
| qty_oz_per_unit | DECIMAL(12,4) | NOT NULL, CHECK (qty_oz_per_unit > 0) | Ounces needed per product unit |

**Foreign Key Constraints:**
- `fk_rpi_plan`: recipe_plan_id → recipe_plan(recipe_plan_id) ON DELETE CASCADE
- `fk_rpi_ingredient`: ingredient_id → ingredient(ingredient_id) ON DELETE RESTRICT

**Business Rules:**
- Defines exact ingredient quantities for production
- Used to calculate total ingredient needs for batches

---

### 7. Inventory Management

#### ingredient_batch
Individual lots/batches of ingredients received from suppliers.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| ingredient_batch_id | INT | PRIMARY KEY, AUTO_INCREMENT | System-generated batch ID |
| ingredient_id | INT | NOT NULL, FK to ingredient | Type of ingredient |
| supplier_id | VARCHAR(32) | NOT NULL, FK to supplier | Source supplier |
| supplier_batch_id | VARCHAR(64) | NOT NULL | Supplier's batch identifier |
| lot_number | VARCHAR(128) | UNIQUE | System-generated lot number |
| quantity_oz | DECIMAL(14,3) | NOT NULL, CHECK (quantity_oz >= 0) | Original received quantity |
| on_hand_oz | DECIMAL(14,3) | NOT NULL, DEFAULT 0 | Current available quantity |
| unit_cost | DECIMAL(12,4) | NOT NULL, CHECK (unit_cost >= 0) | Cost per ounce |
| expiration_date | DATE | NOT NULL | Expiration date |
| received_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Receipt timestamp |

**Foreign Key Constraints:**
- `fk_ib_ingredient`: ingredient_id → ingredient(ingredient_id) ON DELETE RESTRICT
- `fk_ib_supplier`: supplier_id → supplier(supplier_id) ON DELETE RESTRICT

**Unique Constraints:**
- `lot_number` (system-wide unique)

**Business Rules:**
- lot_number auto-generated by trigger (format: {ingredient_id}-{supplier_id}-{timestamp}{random})
- on_hand_oz automatically updated during consumption
- Minimum 90-day expiration enforced by trigger
- Used for FEFO (First Expired, First Out) inventory management

---

#### staging_consumption
Temporary table for product batch ingredient allocation.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| session_token | VARCHAR(64) | NOT NULL, INDEX | Session isolation token |
| ingredient_batch_id | INT | NOT NULL, FK to ingredient_batch | Ingredient batch to consume |
| qty_oz | DECIMAL(14,3) | NOT NULL, CHECK (qty_oz > 0) | Quantity to consume |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Staging timestamp |

**Foreign Key Constraints:**
- `fk_staging_ib`: ingredient_batch_id → ingredient_batch(ingredient_batch_id) ON DELETE RESTRICT

**Indexes:**
- `idx_staging_token` on session_token

**Business Rules:**
- Used by sp_record_product_batch for transactional batch creation
- session_token provides isolation between concurrent batch creations
- Cleared after successful batch creation

---

### 8. Production Management

#### product_batch
Finished product batches produced by manufacturers.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| product_batch_id | INT | PRIMARY KEY, AUTO_INCREMENT | System-generated batch ID |
| product_type_id | INT | NOT NULL, FK to product_type | Type of product produced |
| manufacturer_id | VARCHAR(32) | NOT NULL, FK to manufacturer | Producing manufacturer |
| product_lot_number | VARCHAR(128) | UNIQUE | System-generated product lot number |
| produced_units | INT | NOT NULL, CHECK (produced_units > 0) | Number of units produced |
| batch_cost | DECIMAL(14,4) | NOT NULL, DEFAULT 0 | Total production cost |
| unit_cost | DECIMAL(12,4) | NOT NULL, DEFAULT 0 | Cost per unit |
| expiration_date | DATE | NOT NULL | Product expiration date |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Production timestamp |

**Foreign Key Constraints:**
- `fk_pb_product`: product_type_id → product_type(product_type_id) ON DELETE RESTRICT
- `fk_pb_manufacturer`: manufacturer_id → manufacturer(manufacturer_id) ON DELETE RESTRICT

**Unique Constraints:**
- `product_lot_number` (system-wide unique)

**Business Rules:**
- product_lot_number auto-generated (format: {product_type_id}-{manufacturer_id}-B{sequence})
- Costs calculated from ingredient consumption
- Used for product recall traceability

---

#### product_batch_consumption
Track which ingredient batches were consumed to create each product batch.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| product_batch_consumption_id | INT | PRIMARY KEY, AUTO_INCREMENT | System-generated consumption ID |
| product_batch_id | INT | NOT NULL, FK to product_batch | Product batch created |
| ingredient_batch_id | INT | NOT NULL, FK to ingredient_batch | Ingredient batch consumed |
| qty_oz | DECIMAL(14,3) | NOT NULL, CHECK (qty_oz > 0) | Quantity consumed |

**Foreign Key Constraints:**
- `fk_pbc_pb`: product_batch_id → product_batch(product_batch_id) ON DELETE CASCADE
- `fk_pbc_ib`: ingredient_batch_id → ingredient_batch(ingredient_batch_id) ON DELETE RESTRICT

**Business Rules:**
- Critical for product recall traceability
- Created automatically by sp_record_product_batch
- Triggers automatic update of ingredient_batch.on_hand_oz

---

## Data Types & Precision

### Decimal Precision Standards
- **Quantities (oz)**: DECIMAL(12,3) - up to 999,999,999.999 oz
- **Extended Quantities**: DECIMAL(14,3) - up to 99,999,999,999.999 oz  
- **Unit Costs**: DECIMAL(12,4) - up to $99,999,999.9999
- **Extended Costs**: DECIMAL(14,4) - up to $9,999,999,999.9999

### String Length Standards
- **IDs**: VARCHAR(32) - adequate for alphanumeric business IDs
- **Names**: VARCHAR(255) - standard name length
- **Codes**: VARCHAR(64) - business codes and identifiers
- **Categories**: VARCHAR(128) - category names
- **Lot Numbers**: VARCHAR(128) - system-generated identifiers

### Date/Time Standards
- **Dates**: DATE - expiration dates, effective dates
- **Timestamps**: TIMESTAMP DEFAULT CURRENT_TIMESTAMP - audit trails

---

## Entity Relationships Summary

### One-to-Many Relationships
- manufacturer → product_type
- supplier → ingredient_batch
- product_type → recipe_plan
- recipe_plan → recipe_plan_item
- ingredient → ingredient_batch
- product_batch → product_batch_consumption

### Many-to-Many Relationships
- supplier ↔ ingredient (via supplier_ingredient)
- ingredient ↔ ingredient (via ingredient_material - hierarchical)
- ingredient_batch ↔ product_batch (via product_batch_consumption)

### Special Relationships
- user_account → manufacturer/supplier (role-based)
- ingredient → do_not_combine (regulatory constraints)
- supplier_formulation → ingredient_material (versioned composition)

This schema supports a complete food manufacturing inventory system with full traceability, cost tracking, regulatory compliance, and role-based access control.