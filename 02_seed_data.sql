-- 02_seed_data.sql
-- Comprehensive seed data for dbms_project database
-- Based on Sample Data - Public.txt and compatible with 01_schema_and_logic.sql schema

USE dbms_project;

-- Disable safe update mode and foreign key checks for clean insertion
SET SQL_SAFE_UPDATES = 0;
SET FOREIGN_KEY_CHECKS = 0;

-- Clear existing data (if any) in reverse dependency order
DELETE FROM product_batch_consumption;
DELETE FROM product_batch;
DELETE FROM staging_consumption;
DELETE FROM ingredient_batch;
DELETE FROM recipe_plan_item;
DELETE FROM recipe_plan;
DELETE FROM product_type;
DELETE FROM supplier_formulation_material;
DELETE FROM supplier_formulation;
DELETE FROM do_not_combine;
DELETE FROM supplier_ingredient;
DELETE FROM ingredient_material;
DELETE FROM ingredient;
DELETE FROM user_account;
DELETE FROM category;
DELETE FROM supplier;
DELETE FROM manufacturer;

-- Reset auto-increment counters
ALTER TABLE category AUTO_INCREMENT = 1;
ALTER TABLE supplier_formulation AUTO_INCREMENT = 1;
ALTER TABLE product_type AUTO_INCREMENT = 1;
ALTER TABLE recipe_plan AUTO_INCREMENT = 1;
ALTER TABLE recipe_plan_item AUTO_INCREMENT = 1;
ALTER TABLE ingredient_batch AUTO_INCREMENT = 1;
ALTER TABLE product_batch AUTO_INCREMENT = 1;
ALTER TABLE product_batch_consumption AUTO_INCREMENT = 1;

-- Re-enable foreign key checks and safe updates
SET FOREIGN_KEY_CHECKS = 1;
SET SQL_SAFE_UPDATES = 1;

-- 1. MANUFACTURERS

INSERT INTO manufacturer (manufacturer_id, name) VALUES
('MFG001', 'Premier Foods Manufacturing'),
('MFG002', 'Quality Meals Corp');

-- 2. SUPPLIERS

INSERT INTO supplier (supplier_id, supplier_code, name) VALUES
('20', 'SUP-020', 'Jane Doe'),
('21', 'SUP-021', 'James Miller');

-- 3. CATEGORIES

INSERT INTO category (category_id, name) VALUES
(2, 'Dinners'),
(3, 'Sides');

-- 4. USERS (all roles represented)

INSERT INTO user_account (user_id, username, password_hash, first_name, last_name, role, manufacturer_id, supplier_id) VALUES
('MFG001', 'jsmith', 'HASH_password123', 'John', 'Smith', 'MANUFACTURER', 'MFG001', NULL),
('MFG002', 'alee', 'HASH_password123', 'Alice', 'Lee', 'MANUFACTURER', 'MFG002', NULL),
('SUP020', 'jdoe', 'HASH_password123', 'Jane', 'Doe', 'SUPPLIER', NULL, '20'),
('SUP021', 'jmiller', 'HASH_password123', 'James', 'Miller', 'SUPPLIER', NULL, '21'),
('VIEW001', 'bjohnson', 'HASH_password123', 'Bob', 'Johnson', 'VIEWER', NULL, NULL);

-- 5. INGREDIENTS (atomic and compound)

INSERT INTO ingredient (ingredient_id, name, is_compound) VALUES
(101, 'Salt', FALSE),
(102, 'Pepper', FALSE),
(104, 'Sodium Phosphate', FALSE),
(106, 'Beef Steak', FALSE),
(108, 'Pasta', FALSE),
(201, 'Seasoning Blend', TRUE),
(301, 'Super Seasoning', TRUE);

-- 6. INGREDIENT MATERIALS (compound ingredient compositions)

-- Seasoning Blend (201) is made from Salt (101) and Pepper (102)
INSERT INTO ingredient_material (parent_ingredient_id, material_ingredient_id, qty_oz) VALUES
(201, 101, 6.0),   -- Seasoning Blend contains 6 oz Salt
(201, 102, 2.0);   -- Seasoning Blend contains 2 oz Pepper

-- Super Seasoning (301) is made from Salt (101) and Sodium Phosphate (104)
INSERT INTO ingredient_material (parent_ingredient_id, material_ingredient_id, qty_oz) VALUES
(301, 101, 4.0),   -- Super Seasoning contains 4 oz Salt
(301, 104, 1.0);   -- Super Seasoning contains 1 oz Sodium Phosphate

-- 7. SUPPLIER-INGREDIENT RELATIONSHIPS

-- Supplier 20 (Jane Doe) can provide these ingredients
INSERT INTO supplier_ingredient (supplier_id, ingredient_id) VALUES
('20', 101),  -- Salt
('20', 102),  -- Pepper
('20', 106),  -- Beef Steak
('20', 108),  -- Pasta
('20', 201);  -- Seasoning Blend

-- Supplier 21 (James Miller) can provide these ingredients
INSERT INTO supplier_ingredient (supplier_id, ingredient_id) VALUES
('21', 101),  -- Salt
('21', 102),  -- Pepper
('21', 104);  -- Sodium Phosphate

-- 8. SUPPLIER FORMULATIONS (versioned pricing and pack sizes)

-- Formulation for Seasoning Blend from Supplier 20
INSERT INTO supplier_formulation (formulation_id, supplier_id, ingredient_id, pack_size_oz, unit_price, effective_from, effective_to) VALUES
(1, '20', 201, 8.0, 20.0, '2025-01-01', '2025-06-30');

-- 9. SUPPLIER FORMULATION MATERIALS

-- Materials for formulation 1 (Seasoning Blend from Supplier 20)
INSERT INTO supplier_formulation_material (formulation_id, material_ingredient_id, qty_oz) VALUES
(1, 101, 6.0),  -- 6 oz Salt
(1, 102, 2.0);  -- 2 oz Pepper

-- 10. DO-NOT-COMBINE PAIRS (incompatible ingredients)

-- Regulatory conflicts - these ingredients should not be mixed
INSERT INTO do_not_combine (ingredient_a, ingredient_b) VALUES
(104, 201),  -- Sodium Phosphate cannot be combined with Seasoning Blend
(104, 106);  -- Sodium Phosphate cannot be combined with Beef Steak

-- 11. PRODUCT TYPES

INSERT INTO product_type (product_type_id, manufacturer_id, product_code, name, category_id, standard_batch_units) VALUES
(100, 'MFG001', 'P-100', 'Steak Dinner', 2, 500),
(101, 'MFG002', 'P-101', 'Mac & Cheese', 3, 300);

-- 12. RECIPE PLANS (Bill of Materials for products)

-- Recipe plan for Steak Dinner (product 100)
INSERT INTO recipe_plan (recipe_plan_id, product_type_id, notes) VALUES
(1, 100, 'Recipe for Steak Dinner - includes beef and seasoning');

-- Recipe plan for Mac & Cheese (product 101)
INSERT INTO recipe_plan (recipe_plan_id, product_type_id, notes) VALUES
(2, 101, 'Recipe for Mac & Cheese - pasta with seasonings');

-- 13. RECIPE PLAN ITEMS (ingredients per recipe)

-- Steak Dinner (recipe_plan_id 1) requires:
INSERT INTO recipe_plan_item (recipe_plan_id, ingredient_id, qty_oz_per_unit) VALUES
(1, 106, 6.0),    -- 6 oz Beef Steak per unit
(1, 201, 0.2);    -- 0.2 oz Seasoning Blend per unit

-- Mac & Cheese (recipe_plan_id 2) requires:
INSERT INTO recipe_plan_item (recipe_plan_id, ingredient_id, qty_oz_per_unit) VALUES
(2, 108, 7.0),    -- 7 oz Pasta per unit
(2, 101, 0.5),    -- 0.5 oz Salt per unit
(2, 102, 2.0);    -- 2 oz Pepper per unit

-- 14. INGREDIENT BATCHES (inventory lots)

-- NOTE: Trigger will auto-generate lot_number and set on_hand_oz = quantity_oz
-- We provide supplier_batch_id to match the expected lot number pattern
-- Format: ingredient_id-supplier_id-supplier_batch_id
-- All expiration dates set to at least 90 days from Nov 13, 2025 (Feb 11, 2026+)

-- Salt (ingredient 101) batches
INSERT INTO ingredient_batch (ingredient_id, supplier_id, supplier_batch_id, quantity_oz, unit_cost, expiration_date) VALUES
(101, '20', 'B0001', 1000, 0.1, '2026-03-15'),
(101, '21', 'B0001', 800, 0.08, '2026-04-30'),
(101, '20', 'B0002', 500, 0.1, '2026-05-01'),
(101, '20', 'B0003', 500, 0.1, '2026-03-20');

-- Pepper (ingredient 102) batches
INSERT INTO ingredient_batch (ingredient_id, supplier_id, supplier_batch_id, quantity_oz, unit_cost, expiration_date) VALUES
(102, '20', 'B0001', 1200, 0.3, '2026-03-15');

-- Beef Steak (ingredient 106) batches
INSERT INTO ingredient_batch (ingredient_id, supplier_id, supplier_batch_id, quantity_oz, unit_cost, expiration_date) VALUES
(106, '20', 'B0005', 3000, 0.5, '2026-03-15'),
(106, '20', 'B0006', 600, 0.5, '2026-03-20');

-- Pasta (ingredient 108) batches
INSERT INTO ingredient_batch (ingredient_id, supplier_id, supplier_batch_id, quantity_oz, unit_cost, expiration_date) VALUES
(108, '20', 'B0001', 1000, 0.25, '2026-05-28'),
(108, '20', 'B0003', 6300, 0.25, '2026-04-30');

-- Seasoning Blend (ingredient 201) batches
INSERT INTO ingredient_batch (ingredient_id, supplier_id, supplier_batch_id, quantity_oz, unit_cost, expiration_date) VALUES
(201, '20', 'B0001', 100, 2.5, '2026-03-30'),
(201, '20', 'B0002', 20, 2.5, '2026-04-15');


-- 15. PRODUCT BATCHES (finished goods)

-- The trigger and stored procedure are for NEW batches created through the application

-- Steak Dinner batch produced on 2025-09-26
-- Product: 100 (Steak Dinner), Manufacturer: MFG001, 100 units produced
INSERT INTO product_batch (product_batch_id, product_type_id, manufacturer_id, product_lot_number, produced_units, batch_cost, unit_cost, expiration_date, created_at) VALUES
(1, 100, 'MFG001', '100-MFG001-B0901', 100, 650.0, 6.5, '2026-03-15', '2025-09-26 10:00:00');

-- Mac & Cheese batch produced on 2025-09-10
-- Product: 101 (Mac & Cheese), Manufacturer: MFG002, 300 units produced
INSERT INTO product_batch (product_batch_id, product_type_id, manufacturer_id, product_lot_number, produced_units, batch_cost, unit_cost, expiration_date, created_at) VALUES
(2, 101, 'MFG002', '101-MFG002-B0101', 300, 861.0, 2.87, '2026-04-30', '2025-09-10 14:30:00');


-- 16. PRODUCT BATCH CONSUMPTION (ingredient traceability)

-- We need to find the ingredient_batch_id values for our lot numbers
-- Since triggers auto-generate lot numbers, we use a temp table to avoid trigger conflicts

-- Create temporary table to store the ingredient_batch_ids we need
CREATE TEMPORARY TABLE IF NOT EXISTS tmp_consumption_data (
    product_batch_id INT,
    ingredient_batch_id INT,
    qty_oz DECIMAL(14,3)
);

-- Populate temp table with consumption data
-- Consumption for product batch 1 (Steak Dinner 100-MFG001-B0901)
INSERT INTO tmp_consumption_data (product_batch_id, ingredient_batch_id, qty_oz)
SELECT 1, ingredient_batch_id, 600
FROM ingredient_batch
WHERE ingredient_id = 106 AND supplier_id = '20' AND supplier_batch_id = 'B0006';

INSERT INTO tmp_consumption_data (product_batch_id, ingredient_batch_id, qty_oz)
SELECT 1, ingredient_batch_id, 20
FROM ingredient_batch
WHERE ingredient_id = 201 AND supplier_id = '20' AND supplier_batch_id = 'B0002';

-- Consumption for product batch 2 (Mac & Cheese 101-MFG002-B0101)
INSERT INTO tmp_consumption_data (product_batch_id, ingredient_batch_id, qty_oz)
SELECT 2, ingredient_batch_id, 150
FROM ingredient_batch
WHERE ingredient_id = 101 AND supplier_id = '20' AND supplier_batch_id = 'B0002';

INSERT INTO tmp_consumption_data (product_batch_id, ingredient_batch_id, qty_oz)
SELECT 2, ingredient_batch_id, 2100
FROM ingredient_batch
WHERE ingredient_id = 108 AND supplier_id = '20' AND supplier_batch_id = 'B0003';

INSERT INTO tmp_consumption_data (product_batch_id, ingredient_batch_id, qty_oz)
SELECT 2, ingredient_batch_id, 600
FROM ingredient_batch
WHERE ingredient_id = 102 AND supplier_id = '20' AND supplier_batch_id = 'B0001';

-- Now insert from temp table (triggers will fire and update on_hand automatically)
INSERT INTO product_batch_consumption (product_batch_id, ingredient_batch_id, qty_oz)
SELECT product_batch_id, ingredient_batch_id, qty_oz
FROM tmp_consumption_data;

-- Clean up temp table
DROP TEMPORARY TABLE IF EXISTS tmp_consumption_data;
