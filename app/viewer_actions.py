"""viewer_actions.py
All actions for VIEWER role - read-only browsing and product comparison.
"""
from tabulate import tabulate
from app.db import run_query


def _print_table(rows, column_keys, display_headers=None):
    """Print rows as a formatted table
    
    Args:
        rows: List of dictionary rows from database
        column_keys: List of dictionary keys to extract from rows
        display_headers: Optional list of header names to display (defaults to column_keys)
    """
    if not rows:
        print("No data to display.")
        return
    
    # Use column_keys as headers if display_headers not provided
    if display_headers is None:
        display_headers = column_keys
    
    # Convert dict rows to list of lists for tabulate
    data = [[row.get(key, '') for key in column_keys] for row in rows]
    print(tabulate(data, headers=display_headers, tablefmt='grid'))


# ============================================================================
# BROWSE PRODUCTS
# ============================================================================

def browse_all_products():
    """Browse all product types in the system"""
    print('\n' + '='*70)
    print('BROWSE ALL PRODUCTS')
    print('='*70)
    
    query = """
        SELECT 
            pt.product_type_id,
            m.name as manufacturer_name,
            pt.name as product_name,
            c.name as category,
            COUNT(DISTINCT pb.product_batch_id) as num_batches,
            COALESCE(SUM(pb.produced_units), 0) as total_units
        FROM product_type pt
        JOIN manufacturer m ON pt.manufacturer_id = m.manufacturer_id
        JOIN category c ON pt.category_id = c.category_id
        LEFT JOIN product_batch pb ON pt.product_type_id = pb.product_type_id
        GROUP BY pt.product_type_id, m.name, pt.name, c.name
        ORDER BY c.name, pt.name
    """
    
    rows = run_query(query, ())
    
    if not rows:
        print("📦 No products found in the system")
        return
    
    column_keys = ['product_type_id', 'manufacturer_name', 'product_name', 'category', 'num_batches', 'total_units']
    display_headers = ['Product ID', 'Manufacturer', 'Product Name', 'Category', '# Batches', 'Total Units']
    _print_table(rows, column_keys, display_headers)
    
    print(f"\n✅ Total: {len(rows)} product(s)")


def browse_products_by_manufacturer():
    """Browse products filtered by manufacturer"""
    print('\n' + '='*70)
    print('BROWSE BY MANUFACTURER')
    print('='*70)
    
    # Show available manufacturers
    manufacturers = run_query(
        "SELECT manufacturer_id, name as manufacturer_name FROM manufacturer ORDER BY name",
        ()
    )
    
    if not manufacturers:
        print("❌ No manufacturers found")
        return
    
    print("\nAvailable Manufacturers:")
    column_keys = ['manufacturer_id', 'manufacturer_name']
    display_headers = ['ID', 'Name']
    _print_table(manufacturers, column_keys, display_headers)
    
    mfg_id = input("\nEnter Manufacturer ID (or press Enter to view all): ").strip()
    
    if not mfg_id:
        browse_all_products()
        return
    
    # Query products for this manufacturer
    query = """
        SELECT 
            pt.product_type_id,
            pt.name as product_name,
            c.name as category,
            pt.product_code,
            COUNT(DISTINCT pb.product_batch_id) as num_batches,
            COALESCE(SUM(pb.produced_units), 0) as total_units
        FROM product_type pt
        JOIN category c ON pt.category_id = c.category_id
        LEFT JOIN product_batch pb ON pt.product_type_id = pb.product_type_id
        WHERE pt.manufacturer_id = %s
        GROUP BY pt.product_type_id, pt.name, c.name, pt.product_code
        ORDER BY c.name, pt.name
    """
    
    rows = run_query(query, (mfg_id,))
    
    if not rows:
        print(f"📦 No products found for manufacturer {mfg_id}")
        return
    
    # Get manufacturer name
    mfg_name = next((m['manufacturer_name'] for m in manufacturers if str(m['manufacturer_id']) == mfg_id), mfg_id)
    
    print(f"\n{'='*70}")
    print(f"Products from: {mfg_name}")
    print(f"{'='*70}")
    
    column_keys = ['product_type_id', 'product_name', 'category', 'product_code', 'num_batches', 'total_units']
    display_headers = ['Product ID', 'Name', 'Category', 'Product Code', '# Batches', 'Total Units']
    _print_table(rows, column_keys, display_headers)
    
    print(f"\n✅ {len(rows)} product(s) from {mfg_name}")


def browse_products_by_category():
    """Browse products filtered by category"""
    print('\n' + '='*70)
    print('BROWSE BY CATEGORY')
    print('='*70)
    
    # Show available categories
    categories = run_query(
        "SELECT DISTINCT c.name as category FROM product_type pt JOIN category c ON pt.category_id = c.category_id ORDER BY c.name",
        ()
    )
    
    if not categories:
        print("❌ No categories found")
        return
    
    print("\nAvailable Categories:")
    for i, cat in enumerate(categories, 1):
        print(f"  {i}. {cat['category']}")
    
    cat_name = input("\nEnter Category name: ").strip()
    if not cat_name:
        return
    
    # Query products in this category
    query = """
        SELECT 
            pt.product_type_id,
            m.name as manufacturer_name,
            pt.name as product_name,
            pt.product_code,
            COUNT(DISTINCT pb.product_batch_id) as num_batches,
            COALESCE(SUM(pb.produced_units), 0) as total_units
        FROM product_type pt
        JOIN manufacturer m ON pt.manufacturer_id = m.manufacturer_id
        JOIN category c ON pt.category_id = c.category_id
        LEFT JOIN product_batch pb ON pt.product_type_id = pb.product_type_id
        WHERE c.name = %s
        GROUP BY pt.product_type_id, m.name, pt.name, pt.product_code
        ORDER BY m.name, pt.name
    """
    
    rows = run_query(query, (cat_name,))
    
    if not rows:
        print(f"📦 No products found in category '{cat_name}'")
        return
    
    print(f"\n{'='*70}")
    print(f"Products in Category: {cat_name}")
    print(f"{'='*70}")
    
    column_keys = ['product_type_id', 'manufacturer_name', 'product_name', 'product_code', 'num_batches', 'total_units']
    display_headers = ['Product ID', 'Manufacturer', 'Name', 'Product Code', '# Batches', 'Total Units']
    _print_table(rows, column_keys, display_headers)
    
    print(f"\n✅ {len(rows)} product(s) in {cat_name}")


# ============================================================================
# PRODUCT INGREDIENT LIST
# ============================================================================

def view_product_ingredients():
    """
    View flattened ingredient list for a product.
    Shows all ingredients used in the active recipe plan.
    """
    print('\n' + '='*70)
    print('PRODUCT INGREDIENT LIST')
    print('='*70)
    
    # First show available products
    browse_all_products()
    
    product_id = input("\nEnter Product Type ID: ").strip()
    if not product_id:
        return
    
    # Get product info
    product_query = """
        SELECT pt.name as product_name, m.name as manufacturer_name, c.name as category
        FROM product_type pt
        JOIN manufacturer m ON pt.manufacturer_id = m.manufacturer_id
        JOIN category c ON pt.category_id = c.category_id
        WHERE pt.product_type_id = %s
    """
    
    product = run_query(product_query, (product_id,))
    
    if not product:
        print(f"❌ Product {product_id} not found")
        return
    
    p = product[0]
    
    print(f"\n{'='*70}")
    print(f"Product: {p['product_name']}")
    print(f"Manufacturer: {p['manufacturer_name']}")
    print(f"Category: {p['category']}")
    print(f"{'='*70}\n")
    
    # Get ingredient list from active recipe plan
    ingredients_query = """
        SELECT 
            i.ingredient_id,
            i.name as ingredient_name,
            rpi.qty_oz_per_unit,
            pt.standard_batch_units
        FROM recipe_plan rp
        JOIN recipe_plan_item rpi ON rp.recipe_plan_id = rpi.recipe_plan_id
        JOIN ingredient i ON rpi.ingredient_id = i.ingredient_id
        JOIN product_type pt ON rp.product_type_id = pt.product_type_id
        WHERE rp.product_type_id = %s
        ORDER BY rpi.qty_oz_per_unit DESC
    """
    
    ingredients = run_query(ingredients_query, (product_id,))
    
    if not ingredients:
        print("⚠️  No recipe plan or ingredients found for this product")
        return
    
    standard_batch = ingredients[0]['standard_batch_units']
    
    print(f"Standard Batch Size: {standard_batch} units\n")
    
    headers = ['Ingredient ID', 'Ingredient Name', 'Qty per Unit (oz)']
    display_headers = ['ingredient_id', 'ingredient_name', 'qty_oz_per_unit']
    
    data = [[row.get(h, '') for h in display_headers] for row in ingredients]
    print(tabulate(data, headers=headers, tablefmt='grid'))
    
    print(f"\n✅ Total: {len(ingredients)} ingredient(s)")


# ============================================================================
# COMPARE PRODUCTS FOR INCOMPATIBILITIES
# ============================================================================

def compare_products_for_incompatibility():
    """
    Compare two products to check if they contain incompatible ingredients.
    Uses sp_compare_products_incompatibility stored procedure.
    """
    print('\n' + '='*70)
    print('COMPARE PRODUCTS FOR INCOMPATIBILITY')
    print('='*70)
    print("Check if two products contain ingredients that should not be combined.\n")
    
    # Show available products
    browse_all_products()
    
    product1_id = input("\nEnter First Product Type ID: ").strip()
    if not product1_id:
        return
    
    product2_id = input("Enter Second Product Type ID: ").strip()
    if not product2_id:
        return
    
    if product1_id == product2_id:
        print("❌ Please select two different products")
        return
    
    # Get product names
    product_names = {}
    for pid in [product1_id, product2_id]:
        name_query = "SELECT name as product_name FROM product_type WHERE product_type_id = %s"
        result = run_query(name_query, (pid,))
        if result:
            product_names[pid] = result[0]['product_name']
        else:
            print(f"❌ Product {pid} not found")
            return
    
    print(f"\n{'='*70}")
    print(f"Comparing:")
    print(f"  Product 1: {product_names[product1_id]} (ID: {product1_id})")
    print(f"  Product 2: {product_names[product2_id]} (ID: {product2_id})")
    print(f"{'='*70}\n")
    
    # Call stored procedure
    call_query = "CALL sp_compare_products_incompatibility(%s, %s)"
    
    try:
        # The procedure returns incompatible ingredient pairs
        results = run_query(call_query, (product1_id, product2_id))
        
        if not results:
            print("✅ No incompatibilities found!")
            print(f"   Products '{product_names[product1_id]}' and '{product_names[product2_id]}' can be safely combined.")
            return
        
        print("⚠️  INCOMPATIBILITIES DETECTED!\n")
        print(f"The following ingredient pairs from these products should NOT be combined:\n")
        
        headers = ['Ingredient A ID', 'Ingredient A Name', 'Ingredient B ID', 'Ingredient B Name']
        display_headers = ['ingredient_a', 'ingredient_a_name', 'ingredient_b', 'ingredient_b_name']
        
        data = [[row.get(h, '') for h in display_headers] for row in results]
        print(tabulate(data, headers=headers, tablefmt='grid'))
        
        print(f"\n⚠️  Found {len(results)} incompatible ingredient pair(s)")
        print("   These products should NOT be processed or stored together!")
        
    except Exception as e:
        print(f"❌ Error comparing products: {e}")


# ============================================================================
# HEALTH RISK VIOLATIONS
# ============================================================================

def view_health_risk_violations():
    """View current health risk violations (product batches using incompatible ingredients)"""
    print('\n' + '='*70)
    print('HEALTH RISK VIOLATIONS')
    print('='*70)
    print("Product batches created in last 30 days that contain incompatible ingredient combinations\n")
    
    query = "SELECT * FROM v_health_risk_violations ORDER BY created_at DESC"
    
    rows = run_query(query, ())
    
    if not rows:
        print("✅ No health risk violations detected!")
        print("   All recent product batches comply with do-not-combine rules.")
        return
    
    print("⚠️  HEALTH RISK VIOLATIONS DETECTED!\n")
    
    headers = ['Batch ID', 'Lot Number', 'Product', 'Manufacturer ID', 
               'Ingredient A', 'Ingredient B', 'Created']
    display_headers = ['product_batch_id', 'product_lot_number', 'product_name', 'manufacturer_id',
                       'ingredient_a_name', 'ingredient_b_name', 'created_at']
    
    data = [[row.get(h, '') for h in display_headers] for row in rows]
    print(tabulate(data, headers=headers, tablefmt='grid'))
    
    print(f"\n⚠️  {len(rows)} violation(s) detected")
    print("   ⚠️  These batches contain incompatible ingredient combinations!")


# ============================================================================
# VIEW ACTIVE FORMULATIONS
# ============================================================================

def view_all_formulations():
    """View all active supplier formulations"""
    print('\n' + '='*70)
    print('ACTIVE SUPPLIER FORMULATIONS')
    print('='*70)
    
    query = """
        SELECT * FROM v_active_formulations
        ORDER BY supplier_name, ingredient_name
    """
    
    rows = run_query(query, ())
    
    if not rows:
        print("📋 No active formulations found")
        return
    
    headers = ['Formulation ID', 'Supplier', 'Ingredient', 'Pack Size (oz)', 
               'Unit Price', 'Effective From', 'Effective To']
    display_headers = ['formulation_id', 'supplier_name', 'ingredient_name', 
                       'pack_size_oz', 'unit_price', 'effective_from', 'effective_to']
    
    data = [[row.get(h, '') for h in display_headers] for row in rows]
    print(tabulate(data, headers=headers, tablefmt='grid'))
    
    print(f"\n✅ Total: {len(rows)} active formulation(s)")
