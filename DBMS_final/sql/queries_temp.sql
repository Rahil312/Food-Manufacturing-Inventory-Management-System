-- queries_temp.sql
-- Collection of business queries for dbms_project database

USE dbms_project;

-- ============================================================================
-- QUERY 1: List the ingredients and lot numbers from the last batch of 
--          Steak Dinner (product_type_id = 100) made by manufacturer MFG001
-- ============================================================================
SELECT
    i.ingredient_id,
    i.name AS ingredient_name,
    ib.lot_number AS ingredient_lot_number
FROM product_batch pb
JOIN product_batch_consumption pbc
    ON pbc.product_batch_id = pb.product_batch_id
JOIN ingredient_batch ib
    ON ib.ingredient_batch_id = pbc.ingredient_batch_id
JOIN ingredient i
    ON i.ingredient_id = ib.ingredient_id
WHERE pb.product_type_id = 100
    AND pb.manufacturer_id = 'MFG001'
    AND pb.product_batch_id = (
        SELECT MAX(product_batch_id)
        FROM product_batch
        WHERE product_type_id = 100
            AND manufacturer_id = 'MFG001'
    )
ORDER BY i.ingredient_id;

-- ============================================================================
-- QUERY 2: For manufacturer MFG002, list all suppliers they have purchased 
--          from and the total amount of money spent with each supplier
-- ============================================================================
SELECT
    s.supplier_id,
    s.name AS supplier_name,
    COUNT(DISTINCT ib.ingredient_batch_id) AS total_batches_used,
    SUM(pbc.qty_oz * ib.unit_cost) AS total_amount_spent
FROM product_batch pb
JOIN product_batch_consumption pbc
    ON pbc.product_batch_id = pb.product_batch_id
JOIN ingredient_batch ib
    ON ib.ingredient_batch_id = pbc.ingredient_batch_id
JOIN supplier s
    ON s.supplier_id = ib.supplier_id
WHERE pb.manufacturer_id = 'MFG002'
GROUP BY s.supplier_id, s.name
ORDER BY total_amount_spent DESC;

-- ============================================================================
-- QUERY 3: For product with lot number 100-MFG001-B0901, find the unit cost
-- ============================================================================
SELECT
    pb.product_lot_number,
    pt.name AS product_name,
    pb.produced_units,
    pb.batch_cost,
    pb.unit_cost
FROM product_batch pb
JOIN product_type pt
    ON pt.product_type_id = pb.product_type_id
WHERE pb.product_lot_number = '100-MFG001-B0901';

-- ============================================================================
-- QUERY 4: Based on the ingredients in product lot 100-MFG001-B0901, 
--          find all ingredients that CANNOT be included (conflict check)
-- ============================================================================
-- First, get all ingredients used in the product lot
-- Then find all ingredients that are in do_not_combine with any of those ingredients
SELECT DISTINCT
    conflict_ing.ingredient_id,
    conflict_ing.name AS conflicting_ingredient_name,
    used_ing.ingredient_id AS conflicts_with_ingredient_id,
    used_ing.name AS conflicts_with_ingredient_name
FROM product_batch pb
JOIN product_batch_consumption pbc
    ON pbc.product_batch_id = pb.product_batch_id
JOIN ingredient_batch ib
    ON ib.ingredient_batch_id = pbc.ingredient_batch_id
JOIN ingredient used_ing
    ON used_ing.ingredient_id = ib.ingredient_id
JOIN do_not_combine dnc
    ON (dnc.ingredient_a = used_ing.ingredient_id OR dnc.ingredient_b = used_ing.ingredient_id)
JOIN ingredient conflict_ing
    ON (conflict_ing.ingredient_id = dnc.ingredient_a OR conflict_ing.ingredient_id = dnc.ingredient_b)
        AND conflict_ing.ingredient_id != used_ing.ingredient_id
WHERE pb.product_lot_number = '100-MFG001-B0901'
ORDER BY conflict_ing.ingredient_id;

-- ============================================================================
-- QUERY 5: Which manufacturers has supplier James Miller (21) NOT supplied to?
-- ============================================================================
-- Find all manufacturers that have NOT received ingredients from supplier 21
SELECT DISTINCT
    m.manufacturer_id,
    m.name AS manufacturer_name
FROM manufacturer m
WHERE m.manufacturer_id NOT IN (
    SELECT DISTINCT pb.manufacturer_id
    FROM product_batch pb
    JOIN product_batch_consumption pbc
        ON pbc.product_batch_id = pb.product_batch_id
    JOIN ingredient_batch ib
        ON ib.ingredient_batch_id = pbc.ingredient_batch_id
    WHERE ib.supplier_id = '21'
)
ORDER BY m.manufacturer_id;
