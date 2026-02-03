"""manufacturer_actions.py
All actions for MANUFACTURER role.
"""
from tabulate import tabulate
from app.db import run_query


def _print_table(rows, headers):
    """Print rows as a formatted table"""
    if not rows:
        print("No data to display.")
        return
    # Convert dict rows to list of lists for tabulate
    data = [[row.get(h, '') for h in headers] for row in rows]
    print(tabulate(data, headers=headers, tablefmt='grid'))


def _get_manufacturer_id(user):
    """Get manufacturer_id from user object"""
    return user.get('manufacturer_id')


# ============================================================================
# PRODUCT TYPE MANAGEMENT
# ============================================================================

def view_my_product_types(user):
    """View all product types for this manufacturer"""
    print('\n' + '='*70)
    print('MY PRODUCT TYPES')
    print('='*70)
    
    mfg_id = _get_manufacturer_id(user)
    if not mfg_id:
        print("❌ Error: No manufacturer_id associated with your account")
        return
    
    query = """
        SELECT 
            pt.product_type_id,
            pt.name as product_name,
            c.name as category,
            pt.product_code,
            DATE_FORMAT(pt.created_at, '%Y-%m-%d') as created_date
        FROM product_type pt
        JOIN category c ON pt.category_id = c.category_id
        WHERE pt.manufacturer_id = %s
        ORDER BY c.name, pt.name
    """
    
    rows = run_query(query, (mfg_id,))
    
    if not rows:
        print(f"📦 No product types found for manufacturer {mfg_id}")
        print("   Use option 2 to create your first product type.")
        return
    
    headers = ['product_type_id', 'product_name', 'category', 'product_code', 'created_date']
    print(tabulate([[row.get(h, '') for h in headers] for row in rows], 
                   headers=['ID', 'Product Name', 'Category', 'Product Code', 'Created'], 
                   tablefmt='grid'))
    print(f"\n✅ Found {len(rows)} product type(s)")


def create_product_type(user):
    """Create a new product type"""
    print('\n' + '='*70)
    print('CREATE PRODUCT TYPE')
    print('='*70)
    
    mfg_id = _get_manufacturer_id(user)
    if not mfg_id:
        print("❌ Error: No manufacturer_id associated with your account")
        return
    
    # Show available categories
    categories = run_query("SELECT category_id, name FROM category ORDER BY name", ())
    if categories:
        print("\nAvailable Categories:")
        for cat in categories:
            print(f"  {cat['category_id']}: {cat['name']}")
    
    # Gather inputs
    product_name = input("\nProduct Name: ").strip()
    if not product_name:
        print("❌ Product name is required")
        return
    
    product_code = input("Product Code: ").strip()
    if not product_code:
        print("❌ Product code is required")
        return
    
    category_id = input("Category ID: ").strip()
    if not category_id:
        print("❌ Category ID is required")
        return
    
    standard_batch_units = input("Standard Batch Units: ").strip()
    if not standard_batch_units or not standard_batch_units.isdigit():
        print("❌ Standard batch units must be a positive integer")
        return
    
    # Insert into database
    query = """
        INSERT INTO product_type (manufacturer_id, product_code, name, category_id, standard_batch_units)
        VALUES (%s, %s, %s, %s, %s)
    """
    
    try:
        run_query(query, (mfg_id, product_code, product_name, category_id, standard_batch_units), fetch=False)
        print(f"\n✅ Product type '{product_name}' created successfully!")
        print(f"   Product Code: {product_code}")
        print(f"   Standard Batch: {standard_batch_units} units")
    except Exception as e:
        print(f"❌ Error creating product type: {e}")


def update_product_type(user):
    """Update an existing product type"""
    print('\n' + '='*70)
    print('UPDATE PRODUCT TYPE')
    print('='*70)
    
    mfg_id = _get_manufacturer_id(user)
    if not mfg_id:
        print("❌ Error: No manufacturer_id associated with your account")
        return
    
    # Show available product types
    print("\n--- Your Product Types ---")
    view_my_product_types(user)
    
    product_type_id = input("\nEnter Product Type ID to update: ").strip()
    if not product_type_id:
        return
    
    # Validate product type belongs to this manufacturer
    check = run_query(
        "SELECT product_type_id, name, product_code, category_id, standard_batch_units FROM product_type WHERE product_type_id = %s AND manufacturer_id = %s",
        (product_type_id, mfg_id)
    )
    if not check:
        print(f"❌ Product type {product_type_id} not found or doesn't belong to you")
        return
    
    current = check[0]
    print(f"\n📦 Current values for Product Type {product_type_id}:")
    print(f"   Name: {current['name']}")
    print(f"   Product Code: {current['product_code']}")
    print(f"   Category ID: {current['category_id']}")
    print(f"   Standard Batch Units: {current['standard_batch_units']}")
    
    # Show available categories
    categories = run_query("SELECT category_id, name FROM category ORDER BY name", ())
    if categories:
        print("\nAvailable Categories:")
        for cat in categories:
            print(f"  {cat['category_id']}: {cat['name']}")
    
    # Gather new inputs (press Enter to keep current value)
    print("\n📝 Enter new values (press Enter to keep current value):")
    
    product_name = input(f"Product Name [{current['name']}]: ").strip()
    product_name = product_name if product_name else current['name']
    
    product_code = input(f"Product Code [{current['product_code']}]: ").strip()
    product_code = product_code if product_code else current['product_code']
    
    category_id = input(f"Category ID [{current['category_id']}]: ").strip()
    category_id = category_id if category_id else current['category_id']
    
    standard_batch_units = input(f"Standard Batch Units [{current['standard_batch_units']}]: ").strip()
    standard_batch_units = standard_batch_units if standard_batch_units else current['standard_batch_units']
    
    # Update database
    query = """
        UPDATE product_type 
        SET name = %s, product_code = %s, category_id = %s, standard_batch_units = %s
        WHERE product_type_id = %s AND manufacturer_id = %s
    """
    
    try:
        run_query(query, (product_name, product_code, category_id, standard_batch_units, product_type_id, mfg_id), fetch=False)
        print(f"\n✅ Product type '{product_name}' updated successfully!")
    except Exception as e:
        print(f"❌ Error updating product type: {e}")


def delete_product_type(user):
    """Delete a product type"""
    print('\n' + '='*70)
    print('DELETE PRODUCT TYPE')
    print('='*70)
    
    mfg_id = _get_manufacturer_id(user)
    if not mfg_id:
        print("❌ Error: No manufacturer_id associated with your account")
        return
    
    # Show available product types
    print("\n--- Your Product Types ---")
    view_my_product_types(user)
    
    product_type_id = input("\nEnter Product Type ID to delete: ").strip()
    if not product_type_id:
        return
    
    # Validate product type belongs to this manufacturer
    check = run_query(
        "SELECT product_type_id, name FROM product_type WHERE product_type_id = %s AND manufacturer_id = %s",
        (product_type_id, mfg_id)
    )
    if not check:
        print(f"❌ Product type {product_type_id} not found or doesn't belong to you")
        return
    
    product_name = check[0]['name']
    
    # Check if there are recipe plans using this product type
    recipe_count = run_query(
        "SELECT COUNT(*) as count FROM recipe_plan WHERE product_type_id = %s",
        (product_type_id,)
    )
    if recipe_count and recipe_count[0]['count'] > 0:
        print(f"\n⚠️  Warning: This product type has {recipe_count[0]['count']} recipe plan(s).")
        print("   Deleting this product type will CASCADE delete all associated recipe plans and their items.")
    
    # Check if there are product batches
    batch_count = run_query(
        "SELECT COUNT(*) as count FROM product_batch WHERE product_type_id = %s",
        (product_type_id,)
    )
    if batch_count and batch_count[0]['count'] > 0:
        print(f"\n❌ Cannot delete: This product type has {batch_count[0]['count']} product batch(es).")
        print("   Product batches reference this product type with RESTRICT constraint.")
        return
    
    # Confirm deletion
    confirm = input(f"\n⚠️  Are you sure you want to delete product type '{product_name}'? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("❌ Cancelled.")
        return
    
    # Delete from database
    query = "DELETE FROM product_type WHERE product_type_id = %s AND manufacturer_id = %s"
    
    try:
        run_query(query, (product_type_id, mfg_id), fetch=False)
        print(f"\n✅ Product type '{product_name}' deleted successfully!")
    except Exception as e:
        print(f"❌ Error deleting product type: {e}")


# ============================================================================
# RECIPE PLAN MANAGEMENT
# ============================================================================

def view_my_recipe_plans(user):
    """View all recipe plans (versioned BOMs) for this manufacturer"""
    print('\n' + '='*70)
    print('MY RECIPE PLANS')
    print('='*70)
    
    mfg_id = _get_manufacturer_id(user)
    if not mfg_id:
        print("❌ Error: No manufacturer_id associated with your account")
        return
    
    query = """
        SELECT 
            rp.recipe_plan_id,
            pt.name as product_name,
            DATE_FORMAT(rp.created_at, '%Y-%m-%d') as created,
            COALESCE(rp.notes, '') as notes,
            COUNT(rpi.ingredient_id) as num_ingredients
        FROM recipe_plan rp
        JOIN product_type pt ON rp.product_type_id = pt.product_type_id
        LEFT JOIN recipe_plan_item rpi ON rp.recipe_plan_id = rpi.recipe_plan_id
        WHERE pt.manufacturer_id = %s
        GROUP BY rp.recipe_plan_id
        ORDER BY pt.name, rp.created_at DESC
    """
    
    rows = run_query(query, (mfg_id,))
    
    if not rows:
        print(f"📋 No recipe plans found for manufacturer {mfg_id}")
        print("   Use option 4 to create your first recipe plan.")
        return
    
    headers = ['recipe_plan_id', 'product_name', 'created', 'notes', 'num_ingredients']
    print(tabulate([[row.get(h, '') for h in headers] for row in rows],
                   headers=['Recipe ID', 'Product', 'Created', 'Notes', '# Ingredients'],
                   tablefmt='grid'))
    print(f"\n✅ Found {len(rows)} recipe plan(s)")


def view_recipe_plan_details(user):
    """View detailed ingredients for a specific recipe plan"""
    print('\n' + '='*70)
    print('RECIPE PLAN DETAILS')
    print('='*70)
    
    # First show available recipe plans
    view_my_recipe_plans(user)
    
    recipe_id = input("\nEnter Recipe Plan ID to view details: ").strip()
    if not recipe_id:
        return
    
    # Get recipe plan header
    header_query = """
        SELECT 
            rp.recipe_plan_id,
            pt.name as product_name,
            pt.standard_batch_units,
            DATE_FORMAT(rp.created_at, '%Y-%m-%d') as created,
            COALESCE(rp.notes, '') as notes
        FROM recipe_plan rp
        JOIN product_type pt ON rp.product_type_id = pt.product_type_id
        WHERE rp.recipe_plan_id = %s
    """
    
    header = run_query(header_query, (recipe_id,))
    if not header:
        print(f"❌ Recipe plan {recipe_id} not found")
        return
    
    h = header[0]
    print(f"\n{'='*70}")
    print(f"Recipe Plan: {h['product_name']}")
    print(f"Standard Batch: {h['standard_batch_units']} units")
    print(f"Created: {h['created']}")
    if h['notes']:
        print(f"Notes: {h['notes']}")
    print(f"{'='*70}\n")
    
    # Get ingredients
    ingredients_query = """
        SELECT 
            i.name as ingredient_name,
            rpi.qty_oz_per_unit
        FROM recipe_plan_item rpi
        JOIN ingredient i ON rpi.ingredient_id = i.ingredient_id
        WHERE rpi.recipe_plan_id = %s
        ORDER BY rpi.qty_oz_per_unit DESC
    """
    
    ingredients = run_query(ingredients_query, (recipe_id,))
    
    if not ingredients:
        print("⚠️  No ingredients defined for this recipe plan")
        return
    
    headers = ['ingredient_name', 'qty_oz_per_unit']
    print(tabulate([[row.get(h, '') for h in headers] for row in ingredients],
                   headers=['Ingredient', 'Qty per Unit (oz)'],
                   tablefmt='grid'))
    print(f"\n✅ Total: {len(ingredients)} ingredient(s)")


def create_recipe_plan(user):
    """Create a new recipe plan (BOM) for a product type"""
    print('\n' + '='*70)
    print('CREATE RECIPE PLAN')
    print('='*70)
    
    mfg_id = _get_manufacturer_id(user)
    if not mfg_id:
        print("❌ Error: No manufacturer_id associated with your account")
        return
    
    # Show available product types
    print("\n--- Your Product Types ---")
    view_my_product_types(user)
    
    product_type_id = input("\nEnter Product Type ID: ").strip()
    if not product_type_id:
        return
    
    # Validate product type belongs to this manufacturer
    check = run_query(
        "SELECT product_type_id FROM product_type WHERE product_type_id = %s AND manufacturer_id = %s",
        (product_type_id, mfg_id)
    )
    if not check:
        print(f"❌ Product type {product_type_id} not found or doesn't belong to you")
        return
    
    notes = input("Recipe Notes (optional): ").strip() or None
    
    # Insert recipe plan and get the ID in same connection
    try:
        from app.db import get_connection
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        
        insert_query = """
            INSERT INTO recipe_plan (product_type_id, notes)
            VALUES (%s, %s)
        """
        cur.execute(insert_query, (product_type_id, notes))
        conn.commit()
        
        # Get the newly created recipe_plan_id from same connection
        new_id = cur.lastrowid
        
        cur.close()
        conn.close()
        
        print(f"\n✅ Recipe plan created successfully! (ID: {new_id})")
        if notes:
            print(f"   Notes: {notes}")
        
        # Now add ingredients
        print("\n--- Add Ingredients to Recipe ---")
        _add_recipe_ingredients(new_id)
        
    except Exception as e:
        print(f"❌ Error creating recipe plan: {e}")


def _add_recipe_ingredients(recipe_plan_id):
    """Helper to add ingredients to a recipe plan"""
    print(f"\nAdding ingredients to recipe plan {recipe_plan_id}...")
    print("(Enter ingredient ID and quantity per unit, or press Enter to finish)\n")
    
    # Show available ingredients
    ingredients = run_query("SELECT ingredient_id, name FROM ingredient ORDER BY name", ())
    
    if ingredients:
        print("Available Ingredients:")
        headers = ['ingredient_id', 'name']
        print(tabulate([[row.get(h, '') for h in headers] for row in ingredients[:20]],
                       headers=['ID', 'Name'],
                       tablefmt='grid'))
        if len(ingredients) > 20:
            print(f"... and {len(ingredients) - 20} more")
    
    while True:
        print()
        ing_id = input("Ingredient ID (or Enter to finish): ").strip()
        if not ing_id:
            break
        
        qty = input("Quantity per unit (oz): ").strip()
        if not qty:
            continue
        
        try:
            qty = float(qty)
        except ValueError:
            print("❌ Invalid quantity")
            continue
        
        # Insert ingredient into recipe
        insert_query = """
            INSERT INTO recipe_plan_item (recipe_plan_id, ingredient_id, qty_oz_per_unit)
            VALUES (%s, %s, %s)
        """
        
        try:
            run_query(insert_query, (recipe_plan_id, ing_id, qty), fetch=False)
            
            # Get ingredient name
            ing_name = run_query("SELECT name FROM ingredient WHERE ingredient_id = %s", (ing_id,))
            name = ing_name[0]['name'] if ing_name else ing_id
            
            print(f"   ✓ Added {qty} oz/unit of {name}")
        except Exception as e:
            print(f"   ❌ Error: {e}")


def update_recipe_plan(user):
    """Update an existing recipe plan"""
    print('\n' + '='*70)
    print('UPDATE RECIPE PLAN')
    print('='*70)
    
    mfg_id = _get_manufacturer_id(user)
    if not mfg_id:
        print("❌ Error: No manufacturer_id associated with your account")
        return
    
    # Show available recipe plans
    print("\n--- Your Recipe Plans ---")
    view_my_recipe_plans(user)
    
    recipe_plan_id = input("\nEnter Recipe Plan ID to update: ").strip()
    if not recipe_plan_id:
        return
    
    # Validate recipe plan belongs to this manufacturer
    check = run_query(
        """SELECT rp.recipe_plan_id, rp.product_type_id, pt.name as product_name, rp.notes
           FROM recipe_plan rp
           JOIN product_type pt ON rp.product_type_id = pt.product_type_id
           WHERE rp.recipe_plan_id = %s AND pt.manufacturer_id = %s""",
        (recipe_plan_id, mfg_id)
    )
    if not check:
        print(f"❌ Recipe plan {recipe_plan_id} not found or doesn't belong to you")
        return
    
    current = check[0]
    print(f"\n📋 Current Recipe Plan {recipe_plan_id}:")
    print(f"   Product: {current['product_name']}")
    print(f"   Notes: {current['notes'] or '(none)'}")
    
    # Update options
    print("\n📝 What would you like to update?")
    print("1. Update Notes")
    print("2. Update Ingredients (add/remove/modify)")
    print("0. Cancel")
    
    choice = input("\nChoose an option: ").strip()
    
    if choice == '1':
        # Update notes
        new_notes = input(f"\nNew Notes [{current['notes'] or ''}]: ").strip()
        if new_notes:
            try:
                run_query("UPDATE recipe_plan SET notes = %s WHERE recipe_plan_id = %s", 
                         (new_notes, recipe_plan_id), fetch=False)
                print(f"✅ Notes updated successfully!")
            except Exception as e:
                print(f"❌ Error updating notes: {e}")
    
    elif choice == '2':
        # Update ingredients
        print("\n--- Current Ingredients ---")
        current_ingredients = run_query(
            """SELECT rpi.ingredient_id, i.name as ingredient_name, rpi.qty_oz_per_unit
               FROM recipe_plan_item rpi
               JOIN ingredient i ON rpi.ingredient_id = i.ingredient_id
               WHERE rpi.recipe_plan_id = %s
               ORDER BY i.name""",
            (recipe_plan_id,)
        )
        
        if current_ingredients:
            headers = ['ingredient_id', 'ingredient_name', 'qty_oz_per_unit']
            print(tabulate([[row.get(h, '') for h in headers] for row in current_ingredients],
                          headers=['Ingredient ID', 'Ingredient Name', 'Qty per Unit (oz)'],
                          tablefmt='grid'))
        else:
            print("No ingredients in this recipe plan.")
        
        print("\n📝 Ingredient Management:")
        print("1. Add new ingredient")
        print("2. Update ingredient quantity")
        print("3. Remove ingredient")
        print("0. Done")
        
        while True:
            sub_choice = input("\nChoose an option: ").strip()
            
            if sub_choice == '0':
                break
            elif sub_choice == '1':
                # Add ingredient - Show all available ingredients
                print("\n--- Available Ingredients ---")
                all_ingredients = run_query(
                    """SELECT ingredient_id, name, is_compound
                       FROM ingredient
                       ORDER BY name""",
                    ()
                )
                if all_ingredients:
                    headers = ['ingredient_id', 'name', 'is_compound']
                    print(tabulate([[row.get(h, '') for h in headers] for row in all_ingredients],
                                  headers=['Ingredient ID', 'Ingredient Name', 'Is Compound'],
                                  tablefmt='grid'))
                else:
                    print("No ingredients available.")
                    continue
                
                ing_id = input("\nIngredient ID to add: ").strip()
                if not ing_id:
                    continue
                    
                # Check if ingredient already in recipe
                check = run_query(
                    """SELECT ingredient_id FROM recipe_plan_item 
                       WHERE recipe_plan_id = %s AND ingredient_id = %s""",
                    (recipe_plan_id, ing_id)
                )
                if check:
                    print(f"❌ Ingredient {ing_id} is already in this recipe plan!")
                    continue
                
                qty = input("Quantity per unit (oz): ").strip()
                try:
                    qty = float(qty)
                    run_query("INSERT INTO recipe_plan_item (recipe_plan_id, ingredient_id, qty_oz_per_unit) VALUES (%s, %s, %s)",
                             (recipe_plan_id, ing_id, qty), fetch=False)
                    print(f"✅ Ingredient {ing_id} added successfully!")
                    
                    # Refresh current ingredients display
                    current_ingredients = run_query(
                        """SELECT rpi.ingredient_id, i.name as ingredient_name, rpi.qty_oz_per_unit
                           FROM recipe_plan_item rpi
                           JOIN ingredient i ON rpi.ingredient_id = i.ingredient_id
                           WHERE rpi.recipe_plan_id = %s
                           ORDER BY i.name""",
                        (recipe_plan_id,)
                    )
                    print("\n--- Updated Ingredients ---")
                    if current_ingredients:
                        headers = ['ingredient_id', 'ingredient_name', 'qty_oz_per_unit']
                        print(tabulate([[row.get(h, '') for h in headers] for row in current_ingredients],
                                      headers=['Ingredient ID', 'Ingredient Name', 'Qty per Unit (oz)'],
                                      tablefmt='grid'))
                except Exception as e:
                    print(f"❌ Error adding ingredient: {e}")
            
            elif sub_choice == '2':
                # Update quantity - Use ingredient_id
                if not current_ingredients:
                    print("❌ No ingredients to update!")
                    continue
                    
                ing_id = input("\nIngredient ID to update: ").strip()
                if not ing_id:
                    continue
                
                # Find the recipe_plan_item for this ingredient in this recipe
                item = run_query(
                    """SELECT recipe_plan_item_id, qty_oz_per_unit 
                       FROM recipe_plan_item 
                       WHERE recipe_plan_id = %s AND ingredient_id = %s""",
                    (recipe_plan_id, ing_id)
                )
                if not item:
                    print(f"❌ Ingredient {ing_id} not found in this recipe plan!")
                    continue
                
                current_qty = item[0]['qty_oz_per_unit']
                print(f"Current quantity: {current_qty} oz")
                qty = input("New Quantity per unit (oz): ").strip()
                try:
                    qty = float(qty)
                    run_query("UPDATE recipe_plan_item SET qty_oz_per_unit = %s WHERE recipe_plan_id = %s AND ingredient_id = %s",
                             (qty, recipe_plan_id, ing_id), fetch=False)
                    print(f"✅ Quantity updated successfully!")
                    
                    # Refresh current ingredients display
                    current_ingredients = run_query(
                        """SELECT rpi.ingredient_id, i.name as ingredient_name, rpi.qty_oz_per_unit
                           FROM recipe_plan_item rpi
                           JOIN ingredient i ON rpi.ingredient_id = i.ingredient_id
                           WHERE rpi.recipe_plan_id = %s
                           ORDER BY i.name""",
                        (recipe_plan_id,)
                    )
                    print("\n--- Updated Ingredients ---")
                    if current_ingredients:
                        headers = ['ingredient_id', 'ingredient_name', 'qty_oz_per_unit']
                        print(tabulate([[row.get(h, '') for h in headers] for row in current_ingredients],
                                      headers=['Ingredient ID', 'Ingredient Name', 'Qty per Unit (oz)'],
                                      tablefmt='grid'))
                except Exception as e:
                    print(f"❌ Error updating quantity: {e}")
            
            elif sub_choice == '3':
                # Remove ingredient - Use ingredient_id
                if not current_ingredients:
                    print("❌ No ingredients to remove!")
                    continue
                    
                ing_id = input("\nIngredient ID to remove: ").strip()
                if not ing_id:
                    continue
                
                # Check if ingredient exists in this recipe
                item = run_query(
                    """SELECT recipe_plan_item_id 
                       FROM recipe_plan_item 
                       WHERE recipe_plan_id = %s AND ingredient_id = %s""",
                    (recipe_plan_id, ing_id)
                )
                if not item:
                    print(f"❌ Ingredient {ing_id} not found in this recipe plan!")
                    continue
                
                confirm = input(f"⚠️  Are you sure you want to remove ingredient {ing_id}? (yes/no): ").strip().lower()
                if confirm == 'yes':
                    try:
                        run_query("DELETE FROM recipe_plan_item WHERE recipe_plan_id = %s AND ingredient_id = %s",
                                 (recipe_plan_id, ing_id), fetch=False)
                        print(f"✅ Ingredient removed successfully!")
                        
                        # Refresh current ingredients display
                        current_ingredients = run_query(
                            """SELECT rpi.ingredient_id, i.name as ingredient_name, rpi.qty_oz_per_unit
                               FROM recipe_plan_item rpi
                               JOIN ingredient i ON rpi.ingredient_id = i.ingredient_id
                               WHERE rpi.recipe_plan_id = %s
                               ORDER BY i.name""",
                            (recipe_plan_id,)
                        )
                        print("\n--- Updated Ingredients ---")
                        if current_ingredients:
                            headers = ['ingredient_id', 'ingredient_name', 'qty_oz_per_unit']
                            print(tabulate([[row.get(h, '') for h in headers] for row in current_ingredients],
                                          headers=['Ingredient ID', 'Ingredient Name', 'Qty per Unit (oz)'],
                                          tablefmt='grid'))
                        else:
                            print("No ingredients remaining in this recipe plan.")
                    except Exception as e:
                        print(f"❌ Error removing ingredient: {e}")
    
    elif choice == '0':
        print("❌ Cancelled.")
    else:
        print("❌ Invalid choice")


def delete_recipe_plan(user):
    """Delete a recipe plan"""
    print('\n' + '='*70)
    print('DELETE RECIPE PLAN')
    print('='*70)
    
    mfg_id = _get_manufacturer_id(user)
    if not mfg_id:
        print("❌ Error: No manufacturer_id associated with your account")
        return
    
    # Show available recipe plans
    print("\n--- Your Recipe Plans ---")
    view_my_recipe_plans(user)
    
    recipe_plan_id = input("\nEnter Recipe Plan ID to delete: ").strip()
    if not recipe_plan_id:
        return
    
    # Validate recipe plan belongs to this manufacturer
    check = run_query(
        """SELECT rp.recipe_plan_id, pt.name as product_name
           FROM recipe_plan rp
           JOIN product_type pt ON rp.product_type_id = pt.product_type_id
           WHERE rp.recipe_plan_id = %s AND pt.manufacturer_id = %s""",
        (recipe_plan_id, mfg_id)
    )
    if not check:
        print(f"❌ Recipe plan {recipe_plan_id} not found or doesn't belong to you")
        return
    
    product_name = check[0]['product_name']
    
    # Check if there are product batches using this recipe plan
    # Note: Based on DDL, product_batch doesn't have recipe_plan_id, so we check via product_type_id
    print(f"\n📋 Recipe Plan {recipe_plan_id} for product '{product_name}'")
    
    # Check ingredient items
    item_count = run_query(
        "SELECT COUNT(*) as count FROM recipe_plan_item WHERE recipe_plan_id = %s",
        (recipe_plan_id,)
    )
    if item_count and item_count[0]['count'] > 0:
        print(f"   Contains {item_count[0]['count']} ingredient(s)")
        print("   Deleting this recipe plan will CASCADE delete all ingredient items.")
    
    # Confirm deletion
    confirm = input(f"\n⚠️  Are you sure you want to delete this recipe plan? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("❌ Cancelled.")
        return
    
    # Delete from database (CASCADE will delete recipe_plan_item)
    query = """DELETE rp FROM recipe_plan rp
               JOIN product_type pt ON rp.product_type_id = pt.product_type_id
               WHERE rp.recipe_plan_id = %s AND pt.manufacturer_id = %s"""
    
    try:
        run_query(query, (recipe_plan_id, mfg_id), fetch=False)
        print(f"\n✅ Recipe plan {recipe_plan_id} deleted successfully!")
    except Exception as e:
        print(f"❌ Error deleting recipe plan: {e}")


# ============================================================================
# PRODUCT BATCH CREATION (MOST CRITICAL)
# ============================================================================

def auto_select_lots_fefo(recipe_plan_id, produced_units, session_token):
    """
    GRADUATE FEATURE: FEFO (First Expired, First Out) Auto-Selection
    
    Automatically populate staging_consumption by selecting ingredient lots
    with the earliest expiration dates first.
    
    Args:
        recipe_plan_id: The recipe plan to use
        produced_units: Number of units to produce
        session_token: Unique session token for staging
        
    Returns:
        (success: bool, message: str, lots_selected: int)
    """
    try:
        # Get required ingredients from recipe plan
        recipe_items = run_query(
            """SELECT 
                   rpi.ingredient_id,
                   i.name as ingredient_name,
                   rpi.qty_oz_per_unit,
                   (rpi.qty_oz_per_unit * %s) as total_qty_needed
               FROM recipe_plan_item rpi
               JOIN ingredient i ON rpi.ingredient_id = i.ingredient_id
               WHERE rpi.recipe_plan_id = %s
               ORDER BY i.name""",
            (produced_units, recipe_plan_id)
        )
        
        if not recipe_items:
            return (False, "No ingredients found in recipe plan", 0)
        
        print(f"\n🔍 Auto-selecting lots using FEFO (First Expired, First Out)...")
        print(f"   Recipe requires {len(recipe_items)} ingredient(s)\n")
        
        total_lots_selected = 0
        
        for item in recipe_items:
            ingredient_id = item['ingredient_id']
            ingredient_name = item['ingredient_name']
            qty_needed = float(item['total_qty_needed'])
            
            print(f"  📦 {ingredient_name}: need {qty_needed:.2f} oz")
            
            # Get available batches ordered by expiration date (FEFO)
            available_batches = run_query(
                """SELECT 
                       ib.ingredient_batch_id,
                       ib.lot_number,
                       ib.on_hand_oz,
                       DATE_FORMAT(ib.expiration_date, '%Y-%m-%d') as expiration_date,
                       s.name as supplier_name,
                       DATEDIFF(ib.expiration_date, CURDATE()) as days_until_expiry
                   FROM ingredient_batch ib
                   JOIN supplier s ON ib.supplier_id = s.supplier_id
                   WHERE ib.ingredient_id = %s
                     AND ib.on_hand_oz > 0
                     AND ib.expiration_date >= CURDATE()
                   ORDER BY ib.expiration_date ASC, ib.ingredient_batch_id ASC""",
                (ingredient_id,)
            )
            
            if not available_batches:
                # No lots found - provide detailed message
                all_batches = run_query(
                    """SELECT 
                           COUNT(*) as total_count,
                           SUM(CASE WHEN on_hand_oz > 0 THEN 1 ELSE 0 END) as with_stock,
                           SUM(CASE WHEN expiration_date < CURDATE() THEN 1 ELSE 0 END) as expired
                       FROM ingredient_batch 
                       WHERE ingredient_id = %s""",
                    (ingredient_id,)
                )
                if all_batches and all_batches[0]['total_count'] > 0:
                    info = all_batches[0]
                    return (False, 
                           f"No available lots for ingredient: {ingredient_name}\n"
                           f"   Total batches: {info['total_count']}, With stock: {info['with_stock']}, Expired: {info['expired']}\n"
                           f"   All available lots either have zero on-hand or are expired",
                           0)
                return (False, f"No ingredient batches exist for: {ingredient_name}", 0)
            
            print(f"     Found {len(available_batches)} available lot(s), selecting FEFO (earliest expiry first):")
            
            # Calculate total available quantity
            total_available = sum(float(batch['on_hand_oz']) for batch in available_batches)
            
            # Check if we have enough total quantity before selecting
            if total_available < qty_needed:
                return (False, 
                       f"Insufficient total quantity for {ingredient_name}:\n"
                       f"   Need: {qty_needed:.2f} oz\n"
                       f"   Available across {len(available_batches)} lot(s): {total_available:.2f} oz\n"
                       f"   Shortage: {(qty_needed - total_available):.2f} oz",
                       0)
            
            # Select lots until qty_needed is satisfied
            qty_remaining = qty_needed
            lots_for_ingredient = 0
            
            for batch in available_batches:
                if qty_remaining <= 0:
                    break
                
                batch_id = batch['ingredient_batch_id']
                lot_number = batch['lot_number']
                on_hand = float(batch['on_hand_oz'])
                days_until_expiry = batch['days_until_expiry']
                expiration_date = batch['expiration_date']
                
                # Take what we need (or all available if less than needed)
                qty_to_take = min(qty_remaining, on_hand)
                
                # Insert into staging_consumption
                run_query(
                    """INSERT INTO staging_consumption (session_token, ingredient_batch_id, qty_oz)
                       VALUES (%s, %s, %s)""",
                    (session_token, batch_id, qty_to_take),
                    fetch=False
                )
                
                print(f"     ✓ Lot {lot_number}: {qty_to_take:.2f}/{on_hand:.2f} oz (exp: {expiration_date}, {days_until_expiry} days)")
                
                qty_remaining -= qty_to_take
                lots_for_ingredient += 1
                total_lots_selected += 1
            
            if qty_remaining > 0:
                # Clean up staging for this session
                run_query("DELETE FROM staging_consumption WHERE session_token = %s", (session_token,), fetch=False)
                return (False, f"Insufficient quantity for {ingredient_name}: need {qty_remaining:.2f} more oz", 0)
            
            print(f"     ✅ Selected {lots_for_ingredient} lot(s) for {ingredient_name}\n")
        
        return (True, f"Successfully selected {total_lots_selected} lots using FEFO", total_lots_selected)
        
    except Exception as e:
        # Clean up on error
        try:
            run_query("DELETE FROM staging_consumption WHERE session_token = %s", (session_token,), fetch=False)
        except:
            pass
        return (False, f"Error during FEFO selection: {str(e)}", 0)


def create_product_batch(user):
    """
    Create a product batch using sp_record_product_batch.
    
    This is the MOST CRITICAL function for manufacturers.
    It demonstrates the stored procedure that:
    1. Creates a product_batch record
    2. Consumes ingredients from staging_consumption
    3. Generates lot_number via trigger
    4. Updates on_hand quantities
    
    GRADUATE FEATURE: Supports FEFO auto-selection of ingredient lots
    """
    print('\n' + '='*70)
    print('CREATE PRODUCT BATCH')
    print('='*70)
    print("This will create a new product batch and consume ingredients from staging.")
    
    mfg_id = _get_manufacturer_id(user)
    if not mfg_id:
        print("❌ Error: No manufacturer_id associated with your account")
        return
    
    # Show active recipe plans (all recipe plans, no status field)
    print("\n--- Your Recipe Plans ---")
    active_query = """
        SELECT 
            rp.recipe_plan_id,
            pt.name as product_name,
            pt.standard_batch_units,
            COUNT(rpi.ingredient_id) as num_ingredients
        FROM recipe_plan rp
        JOIN product_type pt ON rp.product_type_id = pt.product_type_id
        LEFT JOIN recipe_plan_item rpi ON rp.recipe_plan_id = rpi.recipe_plan_id
        WHERE pt.manufacturer_id = %s
        GROUP BY rp.recipe_plan_id
        ORDER BY pt.name
    """
    
    active_recipes = run_query(active_query, (mfg_id,))
    
    if not active_recipes:
        print("❌ No recipe plans found. Create a recipe plan first!")
        return
    
    headers = ['recipe_plan_id', 'product_name', 'standard_batch_units', 'num_ingredients']
    print(tabulate([[row.get(h, '') for h in headers] for row in active_recipes],
                   headers=['Recipe ID', 'Product', 'Std Batch Units', '# Ingredients'],
                   tablefmt='grid'))
    
    # Get recipe plan ID
    recipe_plan_id = input("\nEnter Recipe Plan ID: ").strip()
    if not recipe_plan_id:
        return
    
    # Validate recipe plan
    recipe_check = run_query(
        """SELECT rp.recipe_plan_id, pt.name as product_name, pt.standard_batch_units
           FROM recipe_plan rp
           JOIN product_type pt ON rp.product_type_id = pt.product_type_id
           WHERE rp.recipe_plan_id = %s AND pt.manufacturer_id = %s""",
        (recipe_plan_id, mfg_id)
    )
    
    if not recipe_check:
        print(f"❌ Recipe plan {recipe_plan_id} not found")
        return
    
    recipe = recipe_check[0]
    print(f"\n📦 Creating batch for: {recipe['product_name']}")
    print(f"   Standard batch size: {recipe['standard_batch_units']} units")
    
    # Get batch units
    batch_units = input("\nBatch Units to Produce: ").strip()
    if not batch_units:
        return
    
    try:
        batch_units = int(batch_units)
    except ValueError:
        print("❌ Invalid quantity")
        return
    
    # Generate unique session token for staging
    import uuid
    session_token = str(uuid.uuid4())
    
    # GRADUATE FEATURE: Offer FEFO auto-selection
    print("\n" + "="*70)
    print("INGREDIENT LOT SELECTION")
    print("="*70)
    print("Choose how to select ingredient lots:")
    print("  1. 🤖 Auto-select using FEFO (First Expired, First Out) - RECOMMENDED")
    print("  2. 📝 Use existing staging_consumption records")
    print("="*70)
    
    selection_choice = input("\nChoice (1 or 2): ").strip()
    
    if selection_choice == '1':
        # Use FEFO auto-selection
        print("\n⏳ Running FEFO auto-selection...")
        success, message, lots_selected = auto_select_lots_fefo(recipe_plan_id, batch_units, session_token)
        
        if not success:
            print(f"\n❌ FEFO selection failed: {message}")
            return
        
        print(f"\n✅ {message}")
        
        # Show what was selected
        staging = run_query(
            """SELECT 
                   i.name as ingredient_name,
                   ib.lot_number,
                   sc.qty_oz,
                   ib.on_hand_oz,
                   DATEDIFF(ib.expiration_date, CURDATE()) as days_until_expiry
               FROM staging_consumption sc
               JOIN ingredient_batch ib ON sc.ingredient_batch_id = ib.ingredient_batch_id
               JOIN ingredient i ON ib.ingredient_id = i.ingredient_id
               WHERE sc.session_token = %s
               ORDER BY i.name, ib.expiration_date""",
            (session_token,)
        )
        
        if staging:
            print("\n--- Selected Ingredient Lots (FEFO) ---")
            headers = ['ingredient_name', 'lot_number', 'qty_oz', 'on_hand_oz', 'days_until_expiry']
            print(tabulate([[row.get(h, '') for h in headers] for row in staging],
                           headers=['Ingredient', 'Lot Number', 'Qty to Use (oz)', 'Available (oz)', 'Days Until Expiry'],
                           tablefmt='grid'))
    
    elif selection_choice == '2':
        # Use existing staging (no session token needed for old approach)
        session_token = None
        
        print("\n--- Current Staging Consumption ---")
        staging = run_query(
            """SELECT 
                   i.name as ingredient_name,
                   ib.lot_number,
                   sc.qty_oz,
                   ib.on_hand_oz
               FROM staging_consumption sc
               JOIN ingredient_batch ib ON sc.ingredient_batch_id = ib.ingredient_batch_id
               JOIN ingredient i ON ib.ingredient_id = i.ingredient_id
               ORDER BY sc.consumption_id""",
            ()
        )
        
        if staging:
            headers = ['ingredient_name', 'lot_number', 'qty_oz', 'on_hand_oz']
            print(tabulate([[row.get(h, '') for h in headers] for row in staging],
                           headers=['Ingredient', 'Lot Number', 'Qty to Consume (oz)', 'Available On-Hand (oz)'],
                           tablefmt='grid'))
            print(f"\n⚠️  These {len(staging)} staged consumptions will be applied to the batch.")
        else:
            print("⚠️  No staging consumption records found!")
            print("   You may want to add consumption records to staging_consumption first.")
            proceed = input("\nProceed anyway? (y/n): ").strip().lower()
            if proceed != 'y':
                return
    else:
        print("❌ Invalid choice")
        return
    
    # Get product_type_id from recipe_plan
    product_type_result = run_query(
        "SELECT product_type_id FROM recipe_plan WHERE recipe_plan_id = %s",
        (recipe_plan_id,)
    )
    if not product_type_result:
        print("❌ Could not find product type for recipe plan")
        return
    
    product_type_id = product_type_result[0]['product_type_id']
    
    print(f"\n⏳ Preparing for batch creation...")
    print(f"   ✅ Ready to create batch")
    
    # Confirm creation
    print(f"\n{'='*70}")
    print(f"READY TO CREATE BATCH")
    print(f"Recipe: {recipe['product_name']}")
    print(f"Units: {batch_units}")
    print(f"Lots Selected: {len(staging) if staging else 0}")
    print(f"{'='*70}")
    
    confirm = input("\nConfirm batch creation? (y/n): ").strip().lower()
    if confirm != 'y':
        print("❌ Cancelled")
        
        # Clean up FEFO staging if used
        if session_token:
            run_query("DELETE FROM staging_consumption WHERE session_token = %s", (session_token,), fetch=False)
        return
    
    # Call stored procedure with correct parameters
    if session_token:
        call_query = "CALL sp_record_product_batch(%s, %s, %s, %s, %s)"
        params = (session_token, product_type_id, recipe_plan_id, batch_units, mfg_id)
    else:
        # Use empty token for old staging approach (no session filtering)
        call_query = "CALL sp_record_product_batch(%s, %s, %s, %s, %s)"
        params = ('', product_type_id, recipe_plan_id, batch_units, mfg_id)
    
    try:
        print(f"\n⏳ Creating product batch...")
        print(f"   Calling sp_record_product_batch with:")
        print(f"   - Session Token: {session_token if session_token else '(empty - using all staging)'}")
        print(f"   - Product Type ID: {product_type_id}")
        print(f"   - Recipe Plan ID: {recipe_plan_id}")
        print(f"   - Produced Units: {batch_units}")
        print(f"   - Manufacturer ID: {mfg_id}")
        
        # Execute the stored procedure
        result = run_query(call_query, params, fetch=True)
        
        # The stored procedure returns the created batch info
        if result and len(result) > 0:
            b = result[0]
            print(f"\n✅ Product batch created successfully!")
            print(f"   Batch ID: {b.get('product_batch_id')}")
            print(f"   Lot Number: {b.get('product_lot_number')}")
            print(f"   Batch Cost: ${b.get('batch_cost', 0):.2f}")
            print(f"   Unit Cost: ${b.get('unit_cost', 0):.4f}")
            print(f"\n✅ Ingredients consumed from staging and on_hand updated!")
        else:
            # Fallback: Try to get the newly created batch
            new_batch = run_query(
                """SELECT pb.product_batch_id, pb.product_lot_number, pb.produced_units, 
                          pb.batch_cost, pb.unit_cost,
                          DATE_FORMAT(pb.created_at, '%Y-%m-%d') as created_date
                   FROM product_batch pb
                   WHERE pb.product_type_id = %s
                     AND pb.manufacturer_id = %s
                   ORDER BY pb.product_batch_id DESC
                   LIMIT 1""",
                (product_type_id, mfg_id)
            )
            
            if new_batch:
                b = new_batch[0]
                print(f"\n✅ Product batch created successfully!")
                print(f"   Batch ID: {b['product_batch_id']}")
                print(f"   Lot Number: {b['product_lot_number']}")
                print(f"   Units Produced: {b['produced_units']}")
                print(f"   Batch Cost: ${b.get('batch_cost', 0):.2f}")
                print(f"   Unit Cost: ${b.get('unit_cost', 0):.4f}")
                print(f"   Created: {b['created_date']}")
                print(f"\n✅ Ingredients consumed from staging and on_hand updated!")
            else:
                print("\n✅ Batch created, but unable to retrieve details")
            
    except Exception as e:
        print(f"\n❌ Error creating batch: {e}")
        print("   Possible issues:")
        print("   - Insufficient on-hand quantity for ingredient lots")
        print("   - Expired ingredient lots in selection")
        print("   - Produced units not a multiple of standard batch size")
        # Clean up FEFO staging on error
        if session_token:
            try:
                run_query("DELETE FROM staging_consumption WHERE session_token = %s", (session_token,), fetch=False)
                print("   - Cleaned up staging consumption for this session")
            except:
                pass


# ============================================================================
# REPORTS
# ============================================================================

def view_my_inventory_report(user):
    """View on-hand inventory report for this manufacturer"""
    print('\n' + '='*70)
    print('ON-HAND INVENTORY REPORT')
    print('='*70)
    
    mfg_id = _get_manufacturer_id(user)
    if not mfg_id:
        print("❌ Error: No manufacturer_id associated with your account")
        return
    
    query = """
        SELECT 
            pt.name as product_name,
            c.name as category,
            SUM(pb.produced_units) as total_units,
            COUNT(pb.product_batch_id) as num_batches
        FROM product_type pt
        JOIN category c ON pt.category_id = c.category_id
        LEFT JOIN product_batch pb ON pt.product_type_id = pb.product_type_id
        WHERE pt.manufacturer_id = %s
        GROUP BY pt.product_type_id
        HAVING total_units > 0
        ORDER BY c.name, pt.name
    """
    
    rows = run_query(query, (mfg_id,))
    
    if not rows:
        print(f"📊 No inventory found for manufacturer {mfg_id}")
        return
    
    headers = ['Product Name', 'Category', 'Total Units', 'Num Batches']
    display_headers = ['product_name', 'category', 'total_units', 'num_batches']
    
    data = [[row.get(h, '') for h in display_headers] for row in rows]
    print(tabulate(data, headers=headers, tablefmt='grid'))
    
    total_units = sum(row.get('total_units', 0) or 0 for row in rows)
    print(f"\n✅ Total inventory: {total_units} units across {len(rows)} product(s)")


def view_nearly_out_of_stock(user):
    """View products nearly out of stock (< 100 oz)"""
    print('\n' + '='*70)
    print('NEARLY OUT OF STOCK PRODUCTS')
    print('='*70)
    
    mfg_id = _get_manufacturer_id(user)
    if not mfg_id:
        print("❌ Error: No manufacturer_id associated with your account")
        return
    
    query = """
        SELECT 
            pt.name as product_name,
            c.name as category,
            SUM(pb.produced_units) as total_units,
            COUNT(pb.product_batch_id) as num_batches
        FROM product_type pt
        JOIN category c ON pt.category_id = c.category_id
        LEFT JOIN product_batch pb ON pt.product_type_id = pb.product_type_id
        WHERE pt.manufacturer_id = %s
        GROUP BY pt.product_type_id
        HAVING total_units < 100 AND total_units > 0
        ORDER BY total_units ASC
    """
    
    rows = run_query(query, (mfg_id,))
    
    if not rows:
        print(f"✅ No products nearly out of stock! All inventory levels are healthy.")
        return
    
    headers = ['Product Name', 'Category', 'Total Units', 'Num Batches']
    display_headers = ['product_name', 'category', 'total_units', 'num_batches']
    
    data = [[row.get(h, '') for h in display_headers] for row in rows]
    print(tabulate(data, headers=headers, tablefmt='grid'))
    
    print(f"\n⚠️  {len(rows)} product(s) need restocking (< 100 units)")


def view_almost_expired_batches(user):
    """View batches expiring in next 7 days"""
    print('\n' + '='*70)
    print('ALMOST EXPIRED BATCHES (Next 7 Days)')
    print('='*70)
    
    mfg_id = _get_manufacturer_id(user)
    if not mfg_id:
        print("❌ Error: No manufacturer_id associated with your account")
        return
    
    query = """
        SELECT 
            ib.ingredient_batch_id,
            ib.lot_number,
            s.name as supplier_name,
            i.name as ingredient_name,
            ib.quantity_oz,
            ib.on_hand_oz,
            DATE_FORMAT(ib.expiration_date, '%Y-%m-%d') as expire_date,
            DATEDIFF(ib.expiration_date, CURDATE()) as days_until_expiration
        FROM ingredient_batch ib
        JOIN ingredient i ON ib.ingredient_id = i.ingredient_id
        JOIN supplier s ON ib.supplier_id = s.supplier_id
        WHERE DATEDIFF(ib.expiration_date, CURDATE()) BETWEEN 0 AND 7
          AND ib.on_hand_oz > 0
        ORDER BY days_until_expiration ASC
    """
    
    rows = run_query(query, ())
    
    if not rows:
        print(f"✅ No batches expiring soon! All ingredient batches are fresh.")
        return
    
    headers = ['Batch ID', 'Lot Number', 'Supplier', 'Ingredient', 'Original Qty', 'On-Hand', 'Expires', 'Days Left']
    display_headers = ['ingredient_batch_id', 'lot_number', 'supplier_name', 'ingredient_name', 
                       'quantity_oz', 'on_hand_oz', 'expire_date', 'days_until_expiration']
    
    data = [[row.get(h, '') for h in display_headers] for row in rows]
    print(tabulate(data, headers=headers, tablefmt='grid'))
    
    print(f"\n⚠️  {len(rows)} ingredient batch(es) expiring within 7 days")


def view_batch_cost_report(user):
    """View cost breakdown for recent product batches"""
    print('\n' + '='*70)
    print('PRODUCT BATCH COST REPORT')
    print('='*70)
    
    mfg_id = _get_manufacturer_id(user)
    if not mfg_id:
        print("❌ Error: No manufacturer_id associated with your account")
        return
    
    query = """
        SELECT 
            pb.product_batch_id,
            pb.product_lot_number,
            pt.name as product_name,
            pb.produced_units,
            DATE_FORMAT(pb.created_at, '%Y-%m-%d') as created_date,
            pb.batch_cost,
            pb.unit_cost
        FROM product_batch pb
        JOIN product_type pt ON pb.product_type_id = pt.product_type_id
        WHERE pt.manufacturer_id = %s
        ORDER BY pb.product_batch_id DESC
        LIMIT 20
    """
    
    rows = run_query(query, (mfg_id,))
    
    if not rows:
        print(f"📊 No product batches found for manufacturer {mfg_id}")
        return
    
    headers = ['Batch ID', 'Lot Number', 'Product', 'Units', 'Created', 'Total Cost', 'Cost/Unit']
    display_headers = ['product_batch_id', 'product_lot_number', 'product_name', 'produced_units', 
                       'created_date', 'batch_cost', 'unit_cost']
    
    data = [[row.get(h, '') for h in display_headers] for row in rows]
    print(tabulate(data, headers=headers, tablefmt='grid'))
    
    total_cost = sum(row.get('batch_cost', 0) or 0 for row in rows)
    print(f"\n✅ Total cost across {len(rows)} batches: ${total_cost:.2f}")


def trace_product_recall(user):
    """
    GRADUATE FEATURE: Recall & Traceability
    
    Given an ingredient or ingredient lot and date window, 
    list finished product batches that used the affected inputs.
    Calls sp_trace_recall stored procedure.
    """
    print('\n' + '='*70)
    print('PRODUCT RECALL TRACEABILITY')
    print('='*70)
    print("Track which product batches used specific ingredients or lots.")
    print("Useful for recalls, quality issues, or supply chain investigations.")
    
    # Choice: ingredient or lot
    print("\n" + "="*70)
    print("TRACE BY:")
    print("  1. Ingredient ID (all lots of an ingredient)")
    print("  2. Specific Lot Number")
    print("="*70)
    
    trace_choice = input("\nChoice (1 or 2): ").strip()
    
    ingredient_id = None
    lot_number = None
    
    if trace_choice == '1':
        # Show available ingredients
        print("\n--- Available Ingredients ---")
        ingredients = run_query(
            """SELECT ingredient_id, name, is_compound 
               FROM ingredient 
               ORDER BY name 
               LIMIT 50""",
            ()
        )
        
        if ingredients:
            headers = ['ingredient_id', 'name', 'is_compound']
            print(tabulate([[row.get(h, '') for h in headers] for row in ingredients],
                           headers=['ID', 'Ingredient Name', 'Is Compound'],
                           tablefmt='grid'))
        
        ingredient_id = input("\nEnter Ingredient ID to trace: ").strip()
        if not ingredient_id or not ingredient_id.isdigit():
            print("❌ Invalid ingredient ID")
            return
        ingredient_id = int(ingredient_id)
        
    elif trace_choice == '2':
        # Search by lot number
        lot_number = input("\nEnter Lot Number to trace: ").strip()
        if not lot_number:
            print("❌ Lot number is required")
            return
    else:
        print("❌ Invalid choice")
        return
    
    # Get time window
    print("\n📅 Time Window:")
    days_window = input("Days to look back (default 20): ").strip()
    if not days_window:
        days_window = 20
    else:
        try:
            days_window = int(days_window)
        except ValueError:
            print("❌ Invalid number of days, using default (20)")
            days_window = 20
    
    # Call stored procedure
    print(f"\n⏳ Searching for affected product batches (last {days_window} days)...\n")
    
    try:
        call_query = "CALL sp_trace_recall(%s, %s, %s)"
        results = run_query(call_query, (ingredient_id, lot_number, days_window))
        
        if not results:
            print("✅ No product batches found using the specified ingredient/lot in the time window.")
            print("   This could mean:")
            print("   - No batches were produced using this ingredient/lot recently")
            print("   - The ingredient/lot was not used in production")
            print("   - Try expanding the time window")
            return
        
        print(f"⚠️  RECALL ALERT: Found {len(results)} affected product batch(es)")
        print("="*70)
        
        # Display results
        headers = ['product_batch_id', 'product_lot_number', 'product_name', 'manufacturer_name',
                   'produced_units', 'created_at', 'ingredient_lot_number', 'ingredient_name', 'consumed_qty_oz']
        
        display_headers = ['Batch ID', 'Product Lot', 'Product', 'Manufacturer', 
                          'Units', 'Created', 'Ingredient Lot', 'Ingredient', 'Qty Used (oz)']
        
        data = [[row.get(h, '') for h in headers] for row in results]
        print(tabulate(data, headers=display_headers, tablefmt='grid'))
        
        # Summary
        total_units = sum(row.get('produced_units', 0) or 0 for row in results)
        unique_products = len(set(row.get('product_lot_number') for row in results))
        
        print(f"\n📊 RECALL SUMMARY:")
        print(f"   • Affected Product Batches: {unique_products}")
        print(f"   • Total Units Affected: {total_units}")
        print(f"   • Time Period: Last {days_window} days")
        
        if ingredient_id:
            ing_name = results[0].get('ingredient_name', 'Unknown')
            print(f"   • Traced Ingredient: {ing_name} (ID: {ingredient_id})")
        if lot_number:
            print(f"   • Traced Lot Number: {lot_number}")
        
        print("\n⚠️  Action Required: Review these batches for potential recall/quarantine")
        
    except Exception as e:
        print(f"\n❌ Error running recall trace: {e}")


# ============================================================================
# MAIN MENU
# ============================================================================

def reports_menu(user):
    """Sub-menu for manufacturer reports"""
    while True:
        print('\n' + '='*70)
        print('MANUFACTURER REPORTS')
        print('='*70)
        print('1. On-Hand Inventory Report')
        print('2. Nearly Out of Stock Products')
        print('3. Almost Expired Ingredient Batches')
        print('4. Product Batch Cost Report')
        print('5. 🔍 Product Recall Traceability (sp_trace_recall)')
        print('0. Back to Main Menu')
        print('='*70)
        
        choice = input('Choose an option: ').strip()
        
        if choice == '1':
            view_my_inventory_report(user)
        elif choice == '2':
            view_nearly_out_of_stock(user)
        elif choice == '3':
            view_almost_expired_batches(user)
        elif choice == '4':
            view_batch_cost_report(user)
        elif choice == '5':
            trace_product_recall(user)
        elif choice == '0':
            break
        else:
            print('❌ Invalid choice')
