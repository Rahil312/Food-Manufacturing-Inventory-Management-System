"""Run basic integration tests for the DB schema, triggers and sp_record_product_batch.

This script will:
- Connect to MySQL server using credentials in app/db.py (DB_NAME optional)
- Execute sql/01_schema_and_logic.sql to create schema
- Insert minimal test data
- Insert an ingredient batch, stage consumption, call sp_record_product_batch and verify results

Adjust DB credentials in `app/db.py` or set environment variables DB_HOST, DB_PORT, DB_USER, DB_PASS.
"""
import os
import sys
import time
import mysql.connector
from mysql.connector import Error

# import database config from app.db if available
try:
    from app.db import DB_CONFIG
except Exception:
    DB_CONFIG = {
        'host': os.getenv('DB_HOST','localhost'),
        'port': int(os.getenv('DB_PORT',3306)),
        'user': os.getenv('DB_USER','root'),
        'password': os.getenv('DB_PASS',''),
        'database': os.getenv('DB_NAME','dbms_project')
    }

ROOT = os.path.dirname(os.path.dirname(__file__))
SQL_FILE = os.path.join(ROOT, 'sql', '01_schema_and_logic.sql')


def run_sql_file(conn, path):
    with open(path, 'r', encoding='utf8') as f:
        sql = f.read()
    cur = conn.cursor()
    try:
        for result in cur.execute(sql, multi=True):
            # consume any result
            pass
        conn.commit()
    finally:
        cur.close()


def connect_without_db(cfg):
    cfg_copy = dict(cfg)
    cfg_copy.pop('database', None)
    return mysql.connector.connect(**cfg_copy)


def run_tests():
    print('Using DB config:', {k: v for k, v in DB_CONFIG.items() if k != 'password'})
    # 1) connect without database to create it
    try:
        conn = connect_without_db(DB_CONFIG)
    except Error as e:
        print('ERROR: could not connect to MySQL server:', e)
        sys.exit(1)

    try:
        print('Executing DDL file:', SQL_FILE)
        run_sql_file(conn, SQL_FILE)
    except Exception as e:
        print('ERROR executing DDL:', e)
        conn.close()
        sys.exit(1)
    conn.close()

    # 2) connect to the created database
    try:
        DB_CONFIG_WITH_DB = dict(DB_CONFIG)
        DB_CONFIG_WITH_DB.setdefault('database', 'dbms_project')
        conn = mysql.connector.connect(**DB_CONFIG_WITH_DB)
    except Error as e:
        print('ERROR: could not connect to database:', e)
        sys.exit(1)

    cur = conn.cursor()
    try:
        # Minimal seed data: manufacturer, supplier, category, ingredient, product type, recipe plan, ingredient batch
        print('Inserting minimal seed data...')
        cur.execute("INSERT IGNORE INTO manufacturer (manufacturer_id, name) VALUES ('MFG001','Test Manufacturer')")
        cur.execute("INSERT IGNORE INTO supplier (supplier_id, supplier_code, name) VALUES (21,'SUP21','Supplier B')")
        cur.execute("INSERT IGNORE INTO category (category_id, name) VALUES (1,'Dinners')")
        cur.execute("INSERT IGNORE INTO ingredient (ingredient_id, name, is_compound) VALUES ('ING001','Beef',FALSE)")
        cur.execute("INSERT IGNORE INTO ingredient (ingredient_id, name, is_compound) VALUES ('ING002','Salt',FALSE)")
        cur.execute("INSERT IGNORE INTO product_type (product_type_id, manufacturer_id, product_code, name, category_id, standard_batch_units) VALUES (100,'MFG001','100','Steak Dinner',1,500)")
        cur.execute("INSERT IGNORE INTO recipe_plan (recipe_plan_id, product_type_id) VALUES (10,100)")
        # recipe items: per unit assume small qty
        cur.execute("INSERT IGNORE INTO recipe_plan_item (recipe_plan_item_id, recipe_plan_id, ingredient_id, qty_oz_per_unit) VALUES (1000,10,'ING001',8.0)")
        cur.execute("INSERT IGNORE INTO recipe_plan_item (recipe_plan_item_id, recipe_plan_id, ingredient_id, qty_oz_per_unit) VALUES (1001,10,'ING002',0.5)")
        conn.commit()

        # Create an ingredient batch with enough quantity and future expiration
        cur.execute("INSERT INTO ingredient_batch (ingredient_batch_id, ingredient_id, supplier_id, supplier_batch_id, quantity_oz, unit_cost, expiration_date) VALUES (9001,'ING001',21,'B0901',10000,0.50, DATE_ADD(CURDATE(), INTERVAL 180 DAY))")
        cur.execute("INSERT INTO ingredient_batch (ingredient_batch_id, ingredient_id, supplier_id, supplier_batch_id, quantity_oz, unit_cost, expiration_date) VALUES (9002,'ING002',21,'B0902',1000,0.10, DATE_ADD(CURDATE(), INTERVAL 180 DAY))")
        conn.commit()

        # Stage consumption to produce 500 units (standard batch 500): compute required qty per ingredient = qty_per_unit * produced_units
        token = 'test-session-1'
        produced_units = 500
        # For ingredient ING001: 8 oz per unit * 500 = 4000 oz
        cur.execute("INSERT INTO staging_consumption (session_token, ingredient_batch_id, qty_oz) VALUES (%s, %s, %s)", (token, 9001, 8.0 * produced_units))
        # For ING002: 0.5 * 500 = 250 oz
        cur.execute("INSERT INTO staging_consumption (session_token, ingredient_batch_id, qty_oz) VALUES (%s, %s, %s)", (token, 9002, 0.5 * produced_units))
        conn.commit()

        print('Calling stored procedure sp_record_product_batch...')
        # Call the stored procedure
        cur.callproc('sp_record_product_batch', [token, 100, 10, produced_units, 'MFG001'])
        # fetch resultset(s)
        # mysql-connector stores results on cursor.stored_results()
        for result in cur.stored_results():
            rows = result.fetchall()
            print('sp_record_product_batch result:')
            for r in rows:
                print(r)

        # Verify on_hand decreased
        cur.execute('SELECT on_hand_oz FROM ingredient_batch WHERE ingredient_batch_id = %s', (9001,))
        onhand1 = cur.fetchone()[0]
        cur.execute('SELECT on_hand_oz FROM ingredient_batch WHERE ingredient_batch_id = %s', (9002,))
        onhand2 = cur.fetchone()[0]
        print('Remaining on_hand for ING001 (9001):', onhand1)
        print('Remaining on_hand for ING002 (9002):', onhand2)

        # Check product_batch exists
        cur.execute("SELECT product_batch_id, product_lot_number, unit_cost FROM product_batch WHERE product_type_id = 100 AND manufacturer_id = 'MFG001' ORDER BY created_at DESC LIMIT 1")
        pb = cur.fetchone()
        if pb is None:
            print('ERROR: product_batch was not created')
            sys.exit(2)
        else:
            print('Product batch created:', pb)

        print('Test completed successfully.')

    except Exception as e:
        print('TEST ERROR:', e)
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == '__main__':
    run_tests()
