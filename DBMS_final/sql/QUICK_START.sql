-- ==================================================================
-- QUICK START GUIDE - Run these scripts IN ORDER
-- ==================================================================

-- STEP 1: RESET (Start Fresh)
-- File: 00_drop_and_reset.sql
-- Purpose: Completely wipe and recreate empty database
-- Expected: "Database dbms_project has been completely reset and is now empty"

-- STEP 2: CREATE SCHEMA (Build Structure)
-- File: 01_schema_and_logic_fixed.sql (USE THIS ONE - IT'S FIXED!)
-- Purpose: Create all tables, triggers, procedures, views
-- Expected: 18 tables, 5 triggers, 3 procedures, 5 views created
-- Time: ~2 seconds

-- STEP 3: LOAD DATA (Populate Tables)
-- File: 02_seed_data.sql
-- Purpose: Insert 76 sample records
-- Expected: All 76 records loaded successfully
-- Time: ~1 second

-- ==================================================================
-- VERIFICATION QUERIES (Copy and run after each step)
-- ==================================================================

-- After Step 1 (should be empty):
SHOW TABLES;

-- After Step 2 (should see 18 tables):
SELECT 
    'Tables' AS object_type, 
    COUNT(*) AS count 
FROM information_schema.tables 
WHERE table_schema = 'dbms_project'
UNION ALL
SELECT 'Triggers', COUNT(*) 
FROM information_schema.triggers 
WHERE trigger_schema = 'dbms_project'
UNION ALL
SELECT 'Procedures', COUNT(*) 
FROM information_schema.routines 
WHERE routine_schema = 'dbms_project' AND routine_type = 'PROCEDURE'
UNION ALL
SELECT 'Views', COUNT(*) 
FROM information_schema.views 
WHERE table_schema = 'dbms_project';

-- Expected Results:
-- Tables: 18
-- Triggers: 5
-- Procedures: 3
-- Views: 5

-- After Step 3 (should have data):
SELECT 'Total Records' AS metric, 
(SELECT COUNT(*) FROM manufacturer) +
(SELECT COUNT(*) FROM supplier) +
(SELECT COUNT(*) FROM category) +
(SELECT COUNT(*) FROM user_account) +
(SELECT COUNT(*) FROM ingredient) +
(SELECT COUNT(*) FROM ingredient_material) +
(SELECT COUNT(*) FROM supplier_ingredient) +
(SELECT COUNT(*) FROM supplier_formulation) +
(SELECT COUNT(*) FROM supplier_formulation_material) +
(SELECT COUNT(*) FROM do_not_combine) +
(SELECT COUNT(*) FROM product_type) +
(SELECT COUNT(*) FROM recipe_plan) +
(SELECT COUNT(*) FROM recipe_plan_item) +
(SELECT COUNT(*) FROM ingredient_batch) +
(SELECT COUNT(*) FROM product_batch) +
(SELECT COUNT(*) FROM product_batch_consumption) AS total;

-- Expected: 76 records

-- ==================================================================
-- TROUBLESHOOTING
-- ==================================================================

-- If you get errors, check:
-- 1. Are you using 01_schema_and_logic_fixed.sql (NOT the original)?
-- 2. Did you run 00_drop_and_reset.sql first?
-- 3. Is MySQL Workbench connected to the correct server?
-- 4. Do you have proper permissions?

-- To see specific error details:
SHOW ERRORS;
SHOW WARNINGS;
