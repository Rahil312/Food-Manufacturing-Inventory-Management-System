-- 00_drop_and_reset.sql
-- This script completely drops the database and recreates it empty
-- Use this to start completely fresh

-- Drop the entire database (removes everything: tables, triggers, procedures, views, data)
DROP DATABASE IF EXISTS dbms_project;

-- Recreate empty database
CREATE DATABASE dbms_project CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

-- Switch to the database
USE dbms_project;

-- Confirmation message
SELECT 'Database dbms_project has been completely reset and is now empty' AS status;
