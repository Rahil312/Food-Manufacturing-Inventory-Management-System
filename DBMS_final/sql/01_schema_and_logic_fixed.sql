-- 01_schema_and_logic.sql
-- Full DDL for the dbms_project project. Designed for MySQL/MariaDB.

-- NOTE: This file creates a database `dbms_project` and builds objects inside it.
-- It contains tables, constraints, triggers, and a stored procedure `sp_record_product_batch`.

CREATE DATABASE IF NOT EXISTS dbms_project CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE dbms_project;

-- ------------------------------------------------------------------
-- Core reference tables
-- ------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS manufacturer (
    manufacturer_id VARCHAR(32) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS supplier (
    supplier_id VARCHAR(32) PRIMARY KEY,
    supplier_code VARCHAR(32) UNIQUE,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS category (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(128) NOT NULL UNIQUE
);

-- Users: simple application-level auth (one role per user)
CREATE TABLE IF NOT EXISTS user_account (
    user_id VARCHAR(32) PRIMARY KEY,
    username VARCHAR(64),
    password_hash VARCHAR(255),
    first_name VARCHAR(64),
    last_name VARCHAR(64),
    role ENUM('MANUFACTURER','SUPPLIER','VIEWER') NOT NULL,
    manufacturer_id VARCHAR(32),
    supplier_id VARCHAR(32),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_user_manufacturer FOREIGN KEY (manufacturer_id) REFERENCES manufacturer(manufacturer_id) ON DELETE SET NULL,
    CONSTRAINT fk_user_supplier FOREIGN KEY (supplier_id) REFERENCES supplier(supplier_id) ON DELETE SET NULL
);

-- ------------------------------------------------------------------
-- Ingredients, composition (one-level), suppliers and formulations
-- ------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ingredient (
    ingredient_id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    is_compound BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Materials for compound ingredients (one-level only)
CREATE TABLE IF NOT EXISTS ingredient_material (
    parent_ingredient_id INT NOT NULL,
    material_ingredient_id INT NOT NULL,
    qty_oz DECIMAL(12,3) NOT NULL CHECK (qty_oz > 0),
    PRIMARY KEY (parent_ingredient_id, material_ingredient_id),
    CONSTRAINT fk_im_parent FOREIGN KEY (parent_ingredient_id) REFERENCES ingredient(ingredient_id) ON DELETE CASCADE,
    CONSTRAINT fk_im_material FOREIGN KEY (material_ingredient_id) REFERENCES ingredient(ingredient_id) ON DELETE RESTRICT
);

-- Which ingredients a supplier can provide
CREATE TABLE IF NOT EXISTS supplier_ingredient (
    supplier_id VARCHAR(32) NOT NULL,
    ingredient_id INT NOT NULL,
    PRIMARY KEY (supplier_id, ingredient_id),
    CONSTRAINT fk_si_supplier FOREIGN KEY (supplier_id) REFERENCES supplier(supplier_id) ON DELETE CASCADE,
    CONSTRAINT fk_si_ingredient FOREIGN KEY (ingredient_id) REFERENCES ingredient(ingredient_id) ON DELETE CASCADE
);

-- Supplier formulations (versioned ranges). effective_to can be NULL for open-ended.
CREATE TABLE IF NOT EXISTS supplier_formulation (
    formulation_id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_id VARCHAR(32) NOT NULL,
    ingredient_id INT NOT NULL,
    pack_size_oz DECIMAL(12,3) NOT NULL,
    unit_price DECIMAL(12,4) NOT NULL CHECK (unit_price >= 0),
    effective_from DATE NOT NULL,
    effective_to DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_sf_supplier FOREIGN KEY (supplier_id) REFERENCES supplier(supplier_id) ON DELETE CASCADE,
    CONSTRAINT fk_sf_ingredient FOREIGN KEY (ingredient_id) REFERENCES ingredient(ingredient_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS supplier_formulation_material (
    formulation_id INT NOT NULL,
    material_ingredient_id INT NOT NULL,
    qty_oz DECIMAL(12,3) NOT NULL CHECK (qty_oz > 0),
    PRIMARY KEY (formulation_id, material_ingredient_id),
    CONSTRAINT fk_sfm_formulation FOREIGN KEY (formulation_id) REFERENCES supplier_formulation(formulation_id) ON DELETE CASCADE,
    CONSTRAINT fk_sfm_material FOREIGN KEY (material_ingredient_id) REFERENCES ingredient(ingredient_id) ON DELETE RESTRICT
);

-- A global list of incompatible ingredient pairs (do-not-combine). Enforce uniqueness by ordering smaller id first.
CREATE TABLE IF NOT EXISTS do_not_combine (
    ingredient_a INT NOT NULL,
    ingredient_b INT NOT NULL,
    PRIMARY KEY (ingredient_a, ingredient_b),
    CONSTRAINT fk_dnc_a FOREIGN KEY (ingredient_a) REFERENCES ingredient(ingredient_id) ON DELETE CASCADE,
    CONSTRAINT fk_dnc_b FOREIGN KEY (ingredient_b) REFERENCES ingredient(ingredient_id) ON DELETE CASCADE
);

-- ------------------------------------------------------------------
-- Products, recipe plans (versioned), batches and consumption
-- ------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS product_type (
    product_type_id INT AUTO_INCREMENT PRIMARY KEY,
    manufacturer_id VARCHAR(32) NOT NULL,
    product_code VARCHAR(64) NOT NULL,
    name VARCHAR(255) NOT NULL,
    category_id INT NOT NULL,
    standard_batch_units INT NOT NULL CHECK (standard_batch_units > 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_pt_manufacturer FOREIGN KEY (manufacturer_id) REFERENCES manufacturer(manufacturer_id) ON DELETE CASCADE,
    CONSTRAINT fk_pt_category FOREIGN KEY (category_id) REFERENCES category(category_id) ON DELETE RESTRICT,
    UNIQUE KEY ux_manufacturer_product_code (manufacturer_id, product_code)
);

CREATE TABLE IF NOT EXISTS recipe_plan (
    recipe_plan_id INT AUTO_INCREMENT PRIMARY KEY,
    product_type_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    CONSTRAINT fk_rp_product FOREIGN KEY (product_type_id) REFERENCES product_type(product_type_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS recipe_plan_item (
    recipe_plan_item_id INT AUTO_INCREMENT PRIMARY KEY,
    recipe_plan_id INT NOT NULL,
    ingredient_id INT NOT NULL,
    qty_oz_per_unit DECIMAL(12,4) NOT NULL CHECK (qty_oz_per_unit > 0),
    CONSTRAINT fk_rpi_plan FOREIGN KEY (recipe_plan_id) REFERENCES recipe_plan(recipe_plan_id) ON DELETE CASCADE,
    CONSTRAINT fk_rpi_ingredient FOREIGN KEY (ingredient_id) REFERENCES ingredient(ingredient_id) ON DELETE RESTRICT
);

-- Ingredient batches (received lots from suppliers)
CREATE TABLE IF NOT EXISTS ingredient_batch (
    ingredient_batch_id INT AUTO_INCREMENT PRIMARY KEY,
    ingredient_id INT NOT NULL,
    supplier_id VARCHAR(32) NOT NULL,
    supplier_batch_id VARCHAR(64) NOT NULL,
    lot_number VARCHAR(128) UNIQUE,
    quantity_oz DECIMAL(14,3) NOT NULL CHECK (quantity_oz >= 0),
    on_hand_oz DECIMAL(14,3) NOT NULL DEFAULT 0,
    unit_cost DECIMAL(12,4) NOT NULL CHECK (unit_cost >= 0),
    expiration_date DATE NOT NULL,
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_ib_ingredient FOREIGN KEY (ingredient_id) REFERENCES ingredient(ingredient_id) ON DELETE RESTRICT,
    CONSTRAINT fk_ib_supplier FOREIGN KEY (supplier_id) REFERENCES supplier(supplier_id) ON DELETE RESTRICT
);

-- Staging table for product batch consumption prior to calling sp_record_product_batch
CREATE TABLE IF NOT EXISTS staging_consumption (
    session_token VARCHAR(64) NOT NULL,
    ingredient_batch_id INT NOT NULL,
    qty_oz DECIMAL(14,3) NOT NULL CHECK (qty_oz > 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_staging_token (session_token),
    CONSTRAINT fk_staging_ib FOREIGN KEY (ingredient_batch_id) REFERENCES ingredient_batch(ingredient_batch_id) ON DELETE RESTRICT
);

-- Finished product batches
CREATE TABLE IF NOT EXISTS product_batch (
    product_batch_id INT AUTO_INCREMENT PRIMARY KEY,
    product_type_id INT NOT NULL,
    manufacturer_id VARCHAR(32) NOT NULL,
    product_lot_number VARCHAR(128) UNIQUE,
    produced_units INT NOT NULL CHECK (produced_units > 0),
    batch_cost DECIMAL(14,4) NOT NULL DEFAULT 0,
    unit_cost DECIMAL(12,4) NOT NULL DEFAULT 0,
    expiration_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_pb_product FOREIGN KEY (product_type_id) REFERENCES product_type(product_type_id) ON DELETE RESTRICT,
    CONSTRAINT fk_pb_manufacturer FOREIGN KEY (manufacturer_id) REFERENCES manufacturer(manufacturer_id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS product_batch_consumption (
    product_batch_consumption_id INT AUTO_INCREMENT PRIMARY KEY,
    product_batch_id INT NOT NULL,
    ingredient_batch_id INT NOT NULL,
    qty_oz DECIMAL(14,3) NOT NULL CHECK (qty_oz > 0),
    CONSTRAINT fk_pbc_pb FOREIGN KEY (product_batch_id) REFERENCES product_batch(product_batch_id) ON DELETE CASCADE,
    CONSTRAINT fk_pbc_ib FOREIGN KEY (ingredient_batch_id) REFERENCES ingredient_batch(ingredient_batch_id) ON DELETE RESTRICT
);

-- ------------------------------------------------------------------
-- Triggers and procedural enforcement
-- ------------------------------------------------------------------

DELIMITER $$

-- 1) Ensure ingredient_material enforces one-level composition
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

-- 2) Prevent overlapping supplier_formulation effective ranges for the same supplier+ingredient
DROP TRIGGER IF EXISTS trg_supplier_formulation_before_insert$$
CREATE TRIGGER trg_supplier_formulation_before_insert
BEFORE INSERT ON supplier_formulation
FOR EACH ROW
BEGIN
    IF EXISTS (
        SELECT 1 FROM supplier_formulation sf
        WHERE sf.supplier_id = NEW.supplier_id
            AND sf.ingredient_id = NEW.ingredient_id
            AND (NEW.effective_to IS NULL OR sf.effective_to IS NULL OR NOT (NEW.effective_to < sf.effective_from OR NEW.effective_from > sf.effective_to))
    ) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Overlapping supplier formulation effective dates are not allowed';
    END IF;
END$$

-- 3) Set lot_number and initialize on_hand on ingredient_batch insert
-- Fixed: Use BEFORE INSERT to avoid "can't update table in trigger" error
-- Generate lot_number using timestamp + random to ensure uniqueness without needing auto-increment ID
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
    -- This avoids the need for the auto-increment ID and prevents collisions
    SET NEW.lot_number = CONCAT(
        NEW.ingredient_id, '-', 
        NEW.supplier_id, '-', 
        DATE_FORMAT(NOW(), '%Y%m%d%H%i%s'), 
        LPAD(FLOOR(RAND() * 1000), 3, '0')
    );
END$$

-- 4) Prevent expired consumption and validate on_hand (when a consumption row is inserted)
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
    
    -- Check sufficient on_hand at insert time (this will race in multi-user env; sp_record_product_batch does stronger checks)
    SELECT on_hand_oz INTO v_on_hand FROM ingredient_batch WHERE ingredient_batch_id = NEW.ingredient_batch_id;
    IF v_on_hand IS NOT NULL AND v_on_hand < NEW.qty_oz THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Insufficient on-hand quantity for ingredient batch';
    END IF;
END$$

-- 5) Maintain on_hand when product_batch_consumption inserted: decrement
DROP TRIGGER IF EXISTS trg_product_batch_consumption_after_insert$$
CREATE TRIGGER trg_product_batch_consumption_after_insert
AFTER INSERT ON product_batch_consumption
FOR EACH ROW
BEGIN
    UPDATE ingredient_batch
    SET on_hand_oz = on_hand_oz - NEW.qty_oz
    WHERE ingredient_batch_id = NEW.ingredient_batch_id;
END$$

DELIMITER ;

-- ------------------------------------------------------------------
-- Stored procedure: sp_record_product_batch
-- Inputs:
-- IN p_token VARCHAR(64)  -- session token for staging_consumption
-- IN p_product_type_id INT
-- IN p_recipe_plan_id INT
-- IN p_produced_units INT
-- IN p_manufacturer_id VARCHAR(32)
-- ------------------------------------------------------------------

DELIMITER $$

DROP PROCEDURE IF EXISTS sp_record_product_batch$$
CREATE PROCEDURE sp_record_product_batch(
    IN p_token VARCHAR(64),
    IN p_product_type_id INT,
    IN p_recipe_plan_id INT,
    IN p_produced_units INT,
    IN p_manufacturer_id VARCHAR(32)
)
BEGIN
    DECLARE v_standard_units INT;
    DECLARE v_batch_cost DECIMAL(14,4) DEFAULT 0;
    DECLARE v_insufficient_count INT DEFAULT 0;
    DECLARE v_expired_count INT DEFAULT 0;
    DECLARE v_conflict_count INT DEFAULT 0;
    DECLARE v_pb_id INT;
    DECLARE v_unit_cost DECIMAL(12,4) DEFAULT 0;
    DECLARE v_earliest_expiry DATE;

    -- Basic checks
    IF p_produced_units <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'produced_units must be > 0';
    END IF;

    SELECT standard_batch_units INTO v_standard_units FROM product_type WHERE product_type_id = p_product_type_id FOR UPDATE;
    IF v_standard_units IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid product_type_id';
    END IF;
    IF (p_produced_units MOD v_standard_units) <> 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'produced_units must be an integer multiple of standard_batch_units';
    END IF;

    START TRANSACTION;

    -- Check: no expired lots in staging
    SELECT COUNT(*) INTO v_expired_count
    FROM staging_consumption sc
    JOIN ingredient_batch ib ON sc.ingredient_batch_id = ib.ingredient_batch_id
    WHERE sc.session_token = p_token AND ib.expiration_date < CURDATE();
    IF v_expired_count > 0 THEN
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Staging contains expired ingredient lots';
    END IF;

    -- Check: sufficient on-hand per ingredient_batch
    SELECT COUNT(*) INTO v_insufficient_count FROM (
        SELECT sc.ingredient_batch_id, SUM(sc.qty_oz) AS required_qty, ib.on_hand_oz
        FROM staging_consumption sc
        JOIN ingredient_batch ib ON sc.ingredient_batch_id = ib.ingredient_batch_id
        WHERE sc.session_token = p_token
        GROUP BY sc.ingredient_batch_id
        HAVING required_qty > ib.on_hand_oz
    ) t;
    IF v_insufficient_count > 0 THEN
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Insufficient on-hand for one or more ingredient batches in staging';
    END IF;

    -- Do-not-combine check: check for conflicts directly without temporary table
    -- Only check if the do_not_combine table has any records
    -- This check is optional and non-critical to batch creation
    SET v_conflict_count = 0;
    
    -- Check if there are any do_not_combine rules to enforce
    IF EXISTS (SELECT 1 FROM do_not_combine LIMIT 1) THEN
        SELECT COUNT(*) INTO v_conflict_count
        FROM do_not_combine d
        WHERE EXISTS (
            SELECT 1 FROM staging_consumption sc
            JOIN ingredient_batch ib ON sc.ingredient_batch_id = ib.ingredient_batch_id
            WHERE sc.session_token = p_token AND ib.ingredient_id = d.ingredient_a
        )
        AND EXISTS (
            SELECT 1 FROM staging_consumption sc2
            JOIN ingredient_batch ib2 ON sc2.ingredient_batch_id = ib2.ingredient_batch_id
            WHERE sc2.session_token = p_token AND ib2.ingredient_id = d.ingredient_b
        );
        
        IF v_conflict_count > 0 THEN
            ROLLBACK;
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Do-not-combine conflict detected among the chosen ingredient lots';
        END IF;
    END IF;

    -- Compute batch cost
    SELECT IFNULL(SUM(sc.qty_oz * ib.unit_cost),0) INTO v_batch_cost
    FROM staging_consumption sc
    JOIN ingredient_batch ib ON sc.ingredient_batch_id = ib.ingredient_batch_id
    WHERE sc.session_token = p_token;

    -- Compute product expiration date (earliest expiry of consumed ingredients)
    SELECT MIN(ib.expiration_date) INTO v_earliest_expiry
    FROM staging_consumption sc
    JOIN ingredient_batch ib ON sc.ingredient_batch_id = ib.ingredient_batch_id
    WHERE sc.session_token = p_token;

    -- Create product_batch (insert minimal first to get id)
    INSERT INTO product_batch (product_type_id, manufacturer_id, produced_units, batch_cost, unit_cost, expiration_date)
    VALUES (p_product_type_id, p_manufacturer_id, p_produced_units, v_batch_cost, 0, v_earliest_expiry);
    SET v_pb_id = LAST_INSERT_ID();

    -- Set product lot number and unit cost
    UPDATE product_batch
    SET product_lot_number = CONCAT(p_product_type_id,'-',p_manufacturer_id,'-',LPAD(v_pb_id,6,'0')),
            unit_cost = CASE WHEN p_produced_units > 0 THEN v_batch_cost / p_produced_units ELSE 0 END
    WHERE product_batch_id = v_pb_id;

    -- Insert consumption rows (copy from staging)
    -- Note: The trigger trg_product_batch_consumption_after_insert will automatically decrement on_hand
    INSERT INTO product_batch_consumption (product_batch_id, ingredient_batch_id, qty_oz)
        SELECT v_pb_id, sc.ingredient_batch_id, sc.qty_oz FROM staging_consumption sc WHERE sc.session_token = p_token;

    -- Final safety: ensure no on_hand negative (should not happen with proper checks above)
    IF (SELECT COUNT(*) FROM ingredient_batch WHERE on_hand_oz < 0) > 0 THEN
        -- revert
        DELETE FROM product_batch_consumption WHERE product_batch_id = v_pb_id;
        DELETE FROM product_batch WHERE product_batch_id = v_pb_id;
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Operation would cause negative on_hand for a batch';
    END IF;

    -- Clear staging for this token
    DELETE FROM staging_consumption WHERE session_token = p_token;

    COMMIT;

    -- Return created product batch id and lot number to caller
    SELECT product_batch_id, product_lot_number, batch_cost, unit_cost FROM product_batch WHERE product_batch_id = v_pb_id;
END$$

DELIMITER ;

-- ------------------------------------------------------------------
-- Stored procedure: sp_trace_recall
-- Inputs:
-- IN p_ingredient_id INT  -- ingredient to trace (nullable)
-- IN p_lot_number VARCHAR(128)     -- specific lot to trace (nullable)
-- IN p_days_window INT             -- how many days back to search (default 20)
-- ------------------------------------------------------------------

DELIMITER $$

DROP PROCEDURE IF EXISTS sp_trace_recall$$
CREATE PROCEDURE sp_trace_recall(
    IN p_ingredient_id INT,
    IN p_lot_number VARCHAR(128),
    IN p_days_window INT
)
BEGIN
    DECLARE v_start_date DATE;
    SET v_start_date = DATE_SUB(CURDATE(), INTERVAL COALESCE(p_days_window, 20) DAY);
    
    -- Find affected product batches
    SELECT DISTINCT 
           pb.product_batch_id, 
           pb.product_lot_number, 
           pb.product_type_id, 
           pt.name AS product_name,
           pb.manufacturer_id, 
           m.name AS manufacturer_name,
           pb.produced_units, 
           pb.created_at,
           ib.lot_number AS ingredient_lot_number,
           ib.ingredient_id, 
           ing.name AS ingredient_name,
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

DELIMITER ;

-- ------------------------------------------------------------------
-- Stored procedure: sp_compare_products_incompatibility
-- Inputs:
-- IN p_product_type_id_1 INT
-- IN p_product_type_id_2 INT
-- Returns: List of incompatible ingredient pairs found in the two products
-- ------------------------------------------------------------------

DELIMITER $$

DROP PROCEDURE IF EXISTS sp_compare_products_incompatibility$$
CREATE PROCEDURE sp_compare_products_incompatibility(
    IN p_product_type_id_1 INT,
    IN p_product_type_id_2 INT
)
BEGIN
    -- Get flattened ingredients from both products
    CREATE TEMPORARY TABLE IF NOT EXISTS tmp_product1_ings (ingredient_id INT PRIMARY KEY);
    CREATE TEMPORARY TABLE IF NOT EXISTS tmp_product2_ings (ingredient_id INT PRIMARY KEY);
    
    DELETE FROM tmp_product1_ings;
    DELETE FROM tmp_product2_ings;
    
    -- Get ingredients from product 1 (from latest recipe plan)
    INSERT IGNORE INTO tmp_product1_ings (ingredient_id)
    SELECT DISTINCT rpi.ingredient_id
    FROM recipe_plan_item rpi
    WHERE rpi.recipe_plan_id = (
        SELECT recipe_plan_id 
        FROM recipe_plan 
        WHERE product_type_id = p_product_type_id_1
        ORDER BY created_at DESC
        LIMIT 1
    );
    
    -- Get ingredients from product 2 (from latest recipe plan)
    INSERT IGNORE INTO tmp_product2_ings (ingredient_id)
    SELECT DISTINCT rpi.ingredient_id
    FROM recipe_plan_item rpi
    WHERE rpi.recipe_plan_id = (
        SELECT recipe_plan_id 
        FROM recipe_plan 
        WHERE product_type_id = p_product_type_id_2
        ORDER BY created_at DESC
        LIMIT 1
    );
    
    -- Find do-not-combine conflicts between the two products
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
    
    DROP TEMPORARY TABLE IF EXISTS tmp_product1_ings;
    DROP TEMPORARY TABLE IF EXISTS tmp_product2_ings;
END$$

DELIMITER ;

-- ------------------------------------------------------------------
-- Views (examples)
-- ------------------------------------------------------------------
DROP VIEW IF EXISTS v_report_onhand;
CREATE VIEW v_report_onhand AS
SELECT ib.ingredient_batch_id, ib.lot_number, ib.ingredient_id, ib.supplier_id, ib.on_hand_oz, ib.expiration_date
FROM ingredient_batch ib;

DROP VIEW IF EXISTS v_nearly_out_of_stock;
CREATE VIEW v_nearly_out_of_stock AS
SELECT pt.product_type_id, pt.name AS product_name, pt.manufacturer_id, pt.standard_batch_units,
    IFNULL(SUM(ib.on_hand_oz),0) AS total_on_hand_oz
FROM product_type pt
LEFT JOIN recipe_plan rp ON rp.product_type_id = pt.product_type_id
LEFT JOIN recipe_plan_item rpi ON rpi.recipe_plan_id = rp.recipe_plan_id
LEFT JOIN ingredient_batch ib ON ib.ingredient_id = rpi.ingredient_id
GROUP BY pt.product_type_id
HAVING total_on_hand_oz < pt.standard_batch_units;

-- Almost-expired ingredient lots (within 10-day window)
DROP VIEW IF EXISTS v_almost_expired;
CREATE VIEW v_almost_expired AS
SELECT ib.ingredient_batch_id, ib.lot_number, ib.ingredient_id, i.name AS ingredient_name,
       ib.supplier_id, s.name AS supplier_name, ib.on_hand_oz, ib.expiration_date,
       DATEDIFF(ib.expiration_date, CURDATE()) AS days_until_expiry
FROM ingredient_batch ib
JOIN ingredient i ON i.ingredient_id = ib.ingredient_id
JOIN supplier s ON s.supplier_id = ib.supplier_id
WHERE ib.expiration_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 10 DAY)
  AND ib.on_hand_oz > 0
ORDER BY ib.expiration_date;

-- Active supplier formulations (currently valid)
DROP VIEW IF EXISTS v_active_formulations;
CREATE VIEW v_active_formulations AS
SELECT sf.formulation_id, sf.supplier_id, s.name AS supplier_name,
       sf.ingredient_id, i.name AS ingredient_name,
       sf.pack_size_oz, sf.unit_price, sf.effective_from, sf.effective_to
FROM supplier_formulation sf
JOIN supplier s ON s.supplier_id = sf.supplier_id
JOIN ingredient i ON i.ingredient_id = sf.ingredient_id
WHERE CURDATE() BETWEEN sf.effective_from AND COALESCE(sf.effective_to, '9999-12-31');

-- Health-risk violations in product batches (last 30 days)
DROP VIEW IF EXISTS v_health_risk_violations;
CREATE VIEW v_health_risk_violations AS
SELECT pb.product_batch_id, pb.product_lot_number, pb.created_at,
       pt.name AS product_name, pb.manufacturer_id,
       dnc.ingredient_a, ia.name AS ingredient_a_name,
       dnc.ingredient_b, ib.name AS ingredient_b_name
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

-- End of 01_schema_and_logic.sql

