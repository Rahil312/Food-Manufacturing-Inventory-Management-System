"""queries.py
Preset queries and small helpers used by menus.
Add the SQL from the project spec into these functions.
"""
from app.db import run_query
from tabulate import tabulate


def _print(rows):
    if not rows:
        print('No results')
        return
    print(tabulate(rows, headers='keys', tablefmt='psql'))


def report_onhand(user):
    # Example: simple on-hand report
    sql = "SELECT ingredient_batch_id, lot_number, ingredient_id, supplier_id, on_hand_oz, expiration_date FROM ingredient_batch ORDER BY expiration_date"
    rows = run_query(sql)
    _print(rows)

# Placeholder for the 5 sample required queries from the spec
def query_last_batch_ingredients(product_type_id, manufacturer_id):
    sql = """
    SELECT pb.product_lot_number, pbc.ingredient_batch_id, ib.lot_number
    FROM product_batch pb
    JOIN product_batch_consumption pbc ON pbc.product_batch_id = pb.product_batch_id
    JOIN ingredient_batch ib ON ib.ingredient_batch_id = pbc.ingredient_batch_id
    WHERE pb.product_type_id = %s AND pb.manufacturer_id = %s
    ORDER BY pb.created_at DESC
    LIMIT 1
    """
    return run_query(sql, (product_type_id, manufacturer_id))

# TODO: implement the other queries described in final_submission.md
