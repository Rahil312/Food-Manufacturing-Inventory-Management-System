-- Fix for sp_compare_products_incompatibility
-- Run this to update the stored procedure

USE dbms_project;

DROP PROCEDURE IF EXISTS sp_compare_products_incompatibility;

DELIMITER //

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
END//

DELIMITER ;

SELECT 'Stored procedure sp_compare_products_incompatibility updated successfully!' AS status;
