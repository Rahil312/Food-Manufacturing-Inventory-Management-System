from db import run_query

def execute_test_queries():
    """Execute a series of test queries to validate database functionality"""
    
    print("EXECUTING TEST QUERIES ON DATABASE")
    print("=" * 60)
    
    # First, let's check if we have any data to work with
    print("1. CHECKING DATA AVAILABILITY...")
    try:
        result = run_query("SELECT COUNT(*) as count FROM product_batch")
        pb_count = result[0]['count'] if result else 0
        result = run_query("SELECT COUNT(*) as count FROM ingredient_batch")  
        ib_count = result[0]['count'] if result else 0
        
        print(f"   Product batches: {pb_count}")
        print(f"   Ingredient batches: {ib_count}")
        
        if pb_count == 0:
            print("   ⚠️  No product batches found - need to create some test production data first")
            return
            
    except Exception as e:
        print(f"   ❌ Error checking data: {e}")
        return
    
    # Query 1: Most recent Steak Dinner batch and its ingredients
    print("\n2. QUERY 1: Most recent Steak Dinner batch ingredients")
    print("-" * 50)
    try:
        query1 = """
        WITH last_pb AS (
          SELECT pb.product_batch_id, pb.product_lot_number
          FROM product_batch pb
          JOIN product_type pt
            ON pt.product_type_id = pb.product_type_id
          WHERE pt.manufacturer_id = 'MFG001'
            AND (pt.product_code = 'P-100' OR pt.name = 'Steak Dinner')
          ORDER BY pb.created_at DESC, pb.product_batch_id DESC
          LIMIT 1
        )
        SELECT l.product_lot_number AS product_lot,
               i.ingredient_id,
               i.name AS ingredient_name
        FROM last_pb l
        JOIN product_batch_consumption pbc
          ON pbc.product_batch_id = l.product_batch_id
        JOIN ingredient_batch ib
          ON ib.ingredient_batch_id = pbc.ingredient_batch_id
        JOIN ingredient i
          ON i.ingredient_id = ib.ingredient_id
        ORDER BY i.name
        """
        
        result = run_query(query1)
        if result:
            print("   Results:")
            for row in result:
                print(f"     Lot: {row['product_lot']}, Ingredient: {row['ingredient_id']} ({row['ingredient_name']})")
        else:
            print("   No results found - may need production data")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Query 2: MFG002 supplier spending
    print("\n3. QUERY 2: MFG002 supplier spending analysis")
    print("-" * 50)
    try:
        query2 = """
        SELECT s.supplier_id,
               s.name AS supplier_name,
               ROUND(SUM(pbc.qty_oz * ib.unit_cost), 4) AS total_spent
        FROM product_batch pb
        JOIN product_batch_consumption pbc
          ON pbc.product_batch_id = pb.product_batch_id
        JOIN ingredient_batch ib
          ON ib.ingredient_batch_id = pbc.ingredient_batch_id
        JOIN supplier s
          ON s.supplier_id = ib.supplier_id
        WHERE pb.manufacturer_id = 'MFG002'
        GROUP BY s.supplier_id, s.name
        ORDER BY total_spent DESC
        """
        
        result = run_query(query2)
        if result:
            print("   Results:")
            for row in result:
                print(f"     Supplier {row['supplier_id']} ({row['supplier_name']}): ${row['total_spent']}")
        else:
            print("   No results found - MFG002 may not have production data")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Query 3: Unit cost lookup
    print("\n4. QUERY 3: Unit cost for specific product lot")
    print("-" * 50)
    try:
        query3 = """
        SELECT unit_cost
        FROM product_batch
        WHERE product_lot_number = '100-MFG001-B0901'
        """
        
        result = run_query(query3)
        if result:
            print("   Results:")
            for row in result:
                print(f"     Unit cost for lot '100-MFG001-B0901': ${row['unit_cost']}")
        else:
            print("   No results found - specific lot number may not exist")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Query 4: Conflict analysis
    print("\n5. QUERY 4: Ingredient conflicts for specific lot")
    print("-" * 50)
    try:
        query4 = """
        WITH used AS (
          SELECT DISTINCT ib.ingredient_id
          FROM product_batch pb
          JOIN product_batch_consumption pbc
            ON pbc.product_batch_id = pb.product_batch_id
          JOIN ingredient_batch ib
            ON ib.ingredient_batch_id = pbc.ingredient_batch_id
          WHERE pb.product_lot_number = '100-MFG001-B0901'
        ),
        conflicts AS (
          SELECT dnc.ingredient_b AS conflict_id
          FROM do_not_combine dnc
          JOIN used u ON u.ingredient_id = dnc.ingredient_a
          UNION
          SELECT dnc.ingredient_a AS conflict_id
          FROM do_not_combine dnc
          JOIN used u ON u.ingredient_id = dnc.ingredient_b
        )
        SELECT i.ingredient_id, i.name AS ingredient_name
        FROM conflicts c
        JOIN ingredient i
          ON i.ingredient_id = c.conflict_id
        LEFT JOIN used u
          ON u.ingredient_id = c.conflict_id
        WHERE u.ingredient_id IS NULL
        ORDER BY i.name
        """
        
        result = run_query(query4)
        if result:
            print("   Results:")
            for row in result:
                print(f"     Conflicting ingredient: {row['ingredient_id']} ({row['ingredient_name']})")
        else:
            print("   No conflicts found or lot doesn't exist")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Query 5: Manufacturers not supplied by James Miller
    print("\n6. QUERY 5: Manufacturers NOT supplied by James Miller")
    print("-" * 50)
    try:
        query5 = """
        SELECT m.manufacturer_id, m.name AS manufacturer_name
        FROM manufacturer m
        WHERE m.manufacturer_id NOT IN (
          SELECT DISTINCT pb.manufacturer_id
          FROM product_batch pb
          JOIN product_batch_consumption pbc
            ON pbc.product_batch_id = pb.product_batch_id
          JOIN ingredient_batch ib
            ON ib.ingredient_batch_id = pbc.ingredient_batch_id
          JOIN supplier s
            ON s.supplier_id = ib.supplier_id
          WHERE s.supplier_id = '21'
            AND s.name = 'James Miller'
        )
        ORDER BY m.manufacturer_id
        """
        
        result = run_query(query5)
        if result:
            print("   Results:")
            for row in result:
                print(f"     Not supplied: {row['manufacturer_id']} ({row['manufacturer_name']})")
        else:
            print("   All manufacturers have been supplied by James Miller")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("QUERY TESTING COMPLETED")

if __name__ == "__main__":
    execute_test_queries()