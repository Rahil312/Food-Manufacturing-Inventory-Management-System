"""supplier_actions.py
All supplier-specific functionality:
- Manage ingredients supplied
- Maintain formulations (with materials)
- Receive ingredient batches
"""
from app.db import run_query, call_proc
from tabulate import tabulate
from datetime import datetime, timedelta


def _print_table(rows, message="Results"):
    """Helper to print results in a nice table format"""
    if not rows:
        print(f'ℹ️  {message}: No data found.')
        return
    print(f'\n{message}:')
    print(tabulate(rows, headers='keys', tablefmt='grid'))


def _get_supplier_id(user):
    """Extract supplier_id from user object"""
    supplier_id = user.get('supplier_id')
    if not supplier_id:
        print('❌ Error: You are not associated with a supplier.')
        return None
    return supplier_id


# ============================================================================
# 1. VIEW MY INGREDIENTS
# ============================================================================
def view_my_ingredients(user):
    """Show all ingredients this supplier can provide"""
    supplier_id = _get_supplier_id(user)
    if not supplier_id:
        return
    
    print(f'\n📦 Ingredients supplied by you (Supplier {supplier_id}):')
    
    sql = """
    SELECT 
        i.ingredient_id,
        i.name AS ingredient_name,
        i.is_compound,
        CASE 
            WHEN i.is_compound THEN 'Compound'
            ELSE 'Atomic'
        END AS ingredient_type
    FROM supplier_ingredient si
    JOIN ingredient i ON i.ingredient_id = si.ingredient_id
    WHERE si.supplier_id = %s
    ORDER BY i.ingredient_id
    """
    
    rows = run_query(sql, (supplier_id,))
    _print_table(rows, f"Ingredients you supply")
    
    if rows:
        print(f'\n✅ Total: {len(rows)} ingredient(s)')


# ============================================================================
# 2. ADD INGREDIENT TO SUPPLY LIST
# ============================================================================
def add_ingredient_to_supply(user):
    """Add an ingredient to this supplier's supply list (can create new ingredients)"""
    supplier_id = _get_supplier_id(user)
    if not supplier_id:
        return
    
    print('\n➕ Add Ingredient to Your Supply List')
    print('-' * 60)
    
    # First, show all available ingredients
    sql = """
    SELECT ingredient_id, name, is_compound
    FROM ingredient
    ORDER BY ingredient_id
    """
    all_ingredients = run_query(sql)
    _print_table(all_ingredients, "Available Ingredients")
    
    # Give user choice: add existing or create new
    print("\n📝 Options:")
    print("1. Add existing ingredient from the list above")
    print("2. Create a completely new ingredient")
    print("0. Cancel")
    
    choice = input("\nChoose an option: ").strip()
    
    if choice == '0':
        print('❌ Cancelled.')
        return
    
    elif choice == '1':
        # Add existing ingredient
        if not all_ingredients:
            print('❌ No ingredients found in the system.')
            return
        
        valid_ids = [ing['ingredient_id'] for ing in all_ingredients]
        print(f"\n💡 Valid Ingredient IDs: {', '.join(map(str, valid_ids))}")
        
        # Get ingredient_id from user (with retry loop)
        while True:
            ingredient_id_input = input('\nEnter Ingredient ID to add (or 0 to cancel): ').strip()
            
            if ingredient_id_input == '0':
                print('❌ Cancelled.')
                return
            
            try:
                ingredient_id = int(ingredient_id_input)
            except ValueError:
                print('❌ Invalid input. Please enter a number.')
                continue
            
            # Check if ingredient exists
            check_sql = "SELECT name, is_compound FROM ingredient WHERE ingredient_id = %s"
            check_result = run_query(check_sql, (ingredient_id,))
            if not check_result:
                print(f'❌ Ingredient ID {ingredient_id} does not exist. Please choose from the list above.')
                continue
            
            ingredient_name = check_result[0]['name']
            is_compound = check_result[0]['is_compound']
            
            # Check if already supplying
            check_supply_sql = """
            SELECT 1 FROM supplier_ingredient 
            WHERE supplier_id = %s AND ingredient_id = %s
            """
            already_exists = run_query(check_supply_sql, (supplier_id, ingredient_id))
            if already_exists:
                print(f'⚠️  You are already supplying {ingredient_name} (ID: {ingredient_id})')
                retry = input('Would you like to add a different ingredient? (yes/no): ').strip().lower()
                if retry != 'yes':
                    return
                continue
            
            # Valid ingredient, not already in list - proceed with insert
            break
        
        # Insert into supplier_ingredient
        insert_sql = """
        INSERT INTO supplier_ingredient (supplier_id, ingredient_id)
        VALUES (%s, %s)
        """
        
        try:
            run_query(insert_sql, (supplier_id, ingredient_id), fetch=False)
            print(f'✅ Successfully added {ingredient_name} (ID: {ingredient_id}) to your supply list!')
            
            # If compound ingredient, automatically add all material ingredients
            if is_compound:
                print(f'\n📦 {ingredient_name} is a compound ingredient.')
                print('   Automatically adding its material ingredients to your supply list...')
                
                # Get all materials for this compound ingredient with quantities
                materials_sql = """
                SELECT im.material_ingredient_id, i.name as material_name, im.qty_oz
                FROM ingredient_material im
                JOIN ingredient i ON i.ingredient_id = im.material_ingredient_id
                WHERE im.parent_ingredient_id = %s
                """
                materials = run_query(materials_sql, (ingredient_id,))
                
                if materials:
                    added_materials = []
                    already_had_materials = []
                    
                    for material in materials:
                        material_id = material['material_ingredient_id']
                        material_name = material['material_name']
                        
                        # Check if already supplying this material
                        check_material = run_query(check_supply_sql, (supplier_id, material_id))
                        
                        if not check_material:
                            # Add material to supply list
                            try:
                                run_query(insert_sql, (supplier_id, material_id), fetch=False)
                                added_materials.append(f"{material_name} (ID: {material_id})")
                            except Exception as e:
                                print(f'   ⚠️  Could not add material {material_name}: {e}')
                        else:
                            already_had_materials.append(f"{material_name} (ID: {material_id})")
                    
                    # Report what was added
                    if added_materials:
                        print(f'\n   ✅ Added {len(added_materials)} material ingredient(s):')
                        for mat in added_materials:
                            print(f'      • {mat}')
                    
                    if already_had_materials:
                        print(f'\n   ℹ️  Already supplying {len(already_had_materials)} material(s):')
                        for mat in already_had_materials:
                            print(f'      • {mat}')
                    
                    # Ask if user wants to create a formulation
                    print(f'\n💡 Would you like to create a formulation for {ingredient_name}?')
                    create_form = input('   This will include all the material ingredients. (yes/no): ').strip().lower()
                    
                    if create_form == 'yes':
                        print(f'\n➕ Creating Formulation for {ingredient_name}')
                        print('-' * 60)
                        
                        try:
                            # Get formulation details
                            pack_size = float(input('Pack size (oz): ').strip())
                            unit_price = float(input('Unit price ($): ').strip())
                            
                            print('\nEffective Date Range:')
                            effective_from = input('Effective from (YYYY-MM-DD, or press Enter for today): ').strip()
                            if not effective_from:
                                effective_from = datetime.now().strftime('%Y-%m-%d')
                            
                            effective_to_input = input('Effective to (YYYY-MM-DD, or leave blank for open-ended): ').strip()
                            effective_to = effective_to_input if effective_to_input else None
                            
                            # Insert formulation
                            insert_formulation_sql = """
                            INSERT INTO supplier_formulation 
                            (supplier_id, ingredient_id, pack_size_oz, unit_price, effective_from, effective_to)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            """
                            
                            run_query(insert_formulation_sql, (supplier_id, ingredient_id, pack_size, unit_price, 
                                                               effective_from, effective_to), fetch=False)
                            
                            # Get the formulation_id by querying the most recent formulation for this supplier+ingredient
                            get_formulation_id_sql = """
                            SELECT formulation_id 
                            FROM supplier_formulation 
                            WHERE supplier_id = %s AND ingredient_id = %s
                            ORDER BY formulation_id DESC
                            LIMIT 1
                            """
                            formulation_result = run_query(get_formulation_id_sql, (supplier_id, ingredient_id))
                            
                            if not formulation_result:
                                print('❌ Error: Could not retrieve formulation ID')
                                return
                            
                            formulation_id = formulation_result[0]['formulation_id']
                            
                            print(f'\n✅ Formulation created with ID: {formulation_id}')
                            
                            # Add all materials to the formulation
                            print(f'   Adding {len(materials)} material(s) to formulation...')
                            
                            insert_material_sql = """
                            INSERT INTO supplier_formulation_material 
                            (formulation_id, material_ingredient_id, qty_oz)
                            VALUES (%s, %s, %s)
                            """
                            
                            for material in materials:
                                material_id = material['material_ingredient_id']
                                material_qty = material['qty_oz']
                                material_name = material['material_name']
                                
                                try:
                                    run_query(insert_material_sql, (formulation_id, material_id, material_qty), fetch=False)
                                    print(f'      ✅ {material_name}: {material_qty} oz')
                                except Exception as e:
                                    print(f'      ⚠️  Could not add {material_name}: {e}')
                            
                            print(f'\n✅ Formulation with materials created successfully!')
                            print(f'   You can view it with "View Formulation Details" (Option 6)')
                            
                        except ValueError as e:
                            print(f'❌ Invalid input for formulation: {e}')
                        except Exception as e:
                            print(f'❌ Error creating formulation: {e}')
                else:
                    print('   ⚠️  No materials defined for this compound ingredient.')
            
        except Exception as e:
            print(f'❌ Error adding ingredient: {e}')
    
    elif choice == '2':
        # Create new ingredient
        print("\n🆕 Create New Ingredient")
        print('-' * 60)
        
        # Get new ingredient ID
        ingredient_id_input = input('Enter new Ingredient ID (must be unique): ').strip()
        try:
            ingredient_id = int(ingredient_id_input)
        except ValueError:
            print('❌ Invalid ingredient ID. Must be a number.')
            return
        
        # Check if ID already exists
        check_sql = "SELECT ingredient_id FROM ingredient WHERE ingredient_id = %s"
        if run_query(check_sql, (ingredient_id,)):
            print(f'❌ Ingredient ID {ingredient_id} already exists!')
            return
        
        # Get ingredient details
        ingredient_name = input('Enter ingredient name: ').strip()
        if not ingredient_name:
            print('❌ Ingredient name cannot be empty.')
            return
        
        is_compound_input = input('Is this a compound ingredient? (yes/no): ').strip().lower()
        is_compound = 1 if is_compound_input == 'yes' else 0
        
        # Create the ingredient
        insert_ingredient_sql = """
        INSERT INTO ingredient (ingredient_id, name, is_compound)
        VALUES (%s, %s, %s)
        """
        
        try:
            run_query(insert_ingredient_sql, (ingredient_id, ingredient_name, is_compound), fetch=False)
            print(f'✅ Successfully created ingredient: {ingredient_name} (ID: {ingredient_id})')
            
            # Automatically add to supplier's supply list
            insert_supply_sql = """
            INSERT INTO supplier_ingredient (supplier_id, ingredient_id)
            VALUES (%s, %s)
            """
            run_query(insert_supply_sql, (supplier_id, ingredient_id), fetch=False)
            print(f'✅ Automatically added to your supply list!')
            
            # If compound, ask if they want to add materials now
            if is_compound:
                materials_added = []
                
                add_materials = input('\n💡 Would you like to add materials for this compound ingredient now? (yes/no): ').strip().lower()
                if add_materials == 'yes':
                    print("\n--- Adding Materials ---")
                    print("Available simple ingredients:")
                    simple_ingredients = run_query(
                        "SELECT ingredient_id, name FROM ingredient WHERE is_compound = FALSE ORDER BY name",
                        ()
                    )
                    if simple_ingredients:
                        _print_table(simple_ingredients, "Simple Ingredients")
                        
                        while True:
                            material_id_input = input('\nMaterial Ingredient ID to add (or 0 to finish): ').strip()
                            if material_id_input == '0':
                                break
                            
                            try:
                                material_id = int(material_id_input)
                                qty = float(input('Quantity (oz): ').strip())
                                
                                insert_material_sql = """
                                INSERT INTO ingredient_material (parent_ingredient_id, material_ingredient_id, qty_oz)
                                VALUES (%s, %s, %s)
                                """
                                run_query(insert_material_sql, (ingredient_id, material_id, qty), fetch=False)
                                print(f'✅ Material added successfully!')
                                
                                # Store material info for formulation
                                materials_added.append({'material_id': material_id, 'qty': qty})
                                
                            except ValueError:
                                print('❌ Invalid input.')
                            except Exception as e:
                                print(f'❌ Error adding material: {e}')
                
                # Ask if user wants to create formulation
                if materials_added:
                    print(f'\n💡 Would you like to create a formulation for {ingredient_name}?')
                    create_form = input('   This will include all the material ingredients you just added. (yes/no): ').strip().lower()
                    
                    if create_form == 'yes':
                        print(f'\n➕ Creating Formulation for {ingredient_name}')
                        print('-' * 60)
                        
                        try:
                            # Get formulation details
                            pack_size = float(input('Pack size (oz): ').strip())
                            unit_price = float(input('Unit price ($): ').strip())
                            
                            print('\nEffective Date Range:')
                            effective_from = input('Effective from (YYYY-MM-DD, or press Enter for today): ').strip()
                            if not effective_from:
                                effective_from = datetime.now().strftime('%Y-%m-%d')
                            
                            effective_to_input = input('Effective to (YYYY-MM-DD, or leave blank for open-ended): ').strip()
                            effective_to = effective_to_input if effective_to_input else None
                            
                            # Insert formulation
                            insert_formulation_sql = """
                            INSERT INTO supplier_formulation 
                            (supplier_id, ingredient_id, pack_size_oz, unit_price, effective_from, effective_to)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            """
                            
                            run_query(insert_formulation_sql, (supplier_id, ingredient_id, pack_size, unit_price, 
                                                               effective_from, effective_to), fetch=False)
                            
                            # Get the formulation_id
                            get_formulation_id_sql = """
                            SELECT formulation_id 
                            FROM supplier_formulation 
                            WHERE supplier_id = %s AND ingredient_id = %s
                            ORDER BY formulation_id DESC
                            LIMIT 1
                            """
                            formulation_result = run_query(get_formulation_id_sql, (supplier_id, ingredient_id))
                            
                            if formulation_result:
                                formulation_id = formulation_result[0]['formulation_id']
                                print(f'\n✅ Formulation created with ID: {formulation_id}')
                                
                                # Add all materials to the formulation
                                print(f'   Adding {len(materials_added)} material(s) to formulation...')
                                
                                insert_material_sql = """
                                INSERT INTO supplier_formulation_material 
                                (formulation_id, material_ingredient_id, qty_oz)
                                VALUES (%s, %s, %s)
                                """
                                
                                for material in materials_added:
                                    try:
                                        run_query(insert_material_sql, (formulation_id, material['material_id'], material['qty']), fetch=False)
                                        print(f'      ✅ Material ID {material["material_id"]}: {material["qty"]} oz')
                                    except Exception as e:
                                        print(f'      ⚠️  Could not add material {material["material_id"]}: {e}')
                                
                                print(f'\n✅ Formulation with materials created successfully!')
                                print(f'   You can view it with "View Formulation Details" (Option 6)')
                            else:
                                print('❌ Error: Could not retrieve formulation ID')
                            
                        except ValueError as e:
                            print(f'❌ Invalid input for formulation: {e}')
                        except Exception as e:
                            print(f'❌ Error creating formulation: {e}')
                    
        except Exception as e:
            print(f'❌ Error creating ingredient: {e}')
    
    else:
        print('❌ Invalid choice.')


# ============================================================================
# 3. REMOVE INGREDIENT FROM SUPPLY LIST
# ============================================================================
def remove_ingredient_from_supply(user):
    """Remove an ingredient from this supplier's supply list"""
    supplier_id = _get_supplier_id(user)
    if not supplier_id:
        return
    
    print('\n➖ Remove Ingredient from Your Supply List')
    print('-' * 60)
    
    # Show current ingredients
    view_my_ingredients(user)
    
    # Get ingredient_id from user
    try:
        ingredient_id = int(input('\nEnter Ingredient ID to remove: ').strip())
    except ValueError:
        print('❌ Invalid ingredient ID.')
        return
    
    # Check if currently supplying
    check_sql = """
    SELECT i.name, i.is_compound
    FROM supplier_ingredient si
    JOIN ingredient i ON i.ingredient_id = si.ingredient_id
    WHERE si.supplier_id = %s AND si.ingredient_id = %s
    """
    result = run_query(check_sql, (supplier_id, ingredient_id))
    if not result:
        print(f'⚠️  You are not currently supplying ingredient ID {ingredient_id}')
        return
    
    ingredient_name = result[0]['name']
    is_compound = result[0]['is_compound']
    
    # Check if there are formulations for this ingredient
    formulation_check_sql = """
    SELECT COUNT(*) as count
    FROM supplier_formulation
    WHERE supplier_id = %s AND ingredient_id = %s
    """
    formulation_result = run_query(formulation_check_sql, (supplier_id, ingredient_id))
    formulation_count = formulation_result[0]['count'] if formulation_result else 0
    
    # Show warning about what will be deleted
    print(f'\n⚠️  Warning: Removing {ingredient_name} (ID: {ingredient_id}) will:')
    print(f'   • Remove it from your supply list')
    if formulation_count > 0:
        print(f'   • Delete {formulation_count} formulation(s) for this ingredient')
        print(f'   • Delete all formulation materials associated with these formulations')
    
    # Confirm deletion
    confirm = input(f'\nAre you sure you want to stop supplying {ingredient_name}? (yes/no): ').strip().lower()
    if confirm != 'yes':
        print('❌ Cancelled.')
        return
    
    try:
        # First, delete formulations (which will CASCADE delete formulation_materials)
        if formulation_count > 0:
            delete_formulations_sql = """
            DELETE FROM supplier_formulation
            WHERE supplier_id = %s AND ingredient_id = %s
            """
            run_query(delete_formulations_sql, (supplier_id, ingredient_id), fetch=False)
            print(f'   ✅ Deleted {formulation_count} formulation(s)')
        
        # Then delete from supplier_ingredient
        delete_sql = """
        DELETE FROM supplier_ingredient
        WHERE supplier_id = %s AND ingredient_id = %s
        """
        run_query(delete_sql, (supplier_id, ingredient_id), fetch=False)
        print(f'✅ Successfully removed {ingredient_name} from your supply list!')
        
    except Exception as e:
        print(f'❌ Error removing ingredient: {e}')


# ============================================================================
# 4. VIEW MY FORMULATIONS
# ============================================================================
def view_my_formulations(user):
    """Show all formulations for this supplier"""
    supplier_id = _get_supplier_id(user)
    if not supplier_id:
        return
    
    print(f'\n📋 Your Formulations (Supplier {supplier_id}):')
    
    sql = """
    SELECT 
        sf.formulation_id,
        sf.ingredient_id,
        i.name AS ingredient_name,
        sf.pack_size_oz,
        sf.unit_price,
        sf.effective_from,
        sf.effective_to,
        CASE 
            WHEN CURDATE() BETWEEN sf.effective_from AND COALESCE(sf.effective_to, '9999-12-31')
            THEN 'Active'
            ELSE 'Inactive'
        END AS status
    FROM supplier_formulation sf
    JOIN ingredient i ON i.ingredient_id = sf.ingredient_id
    WHERE sf.supplier_id = %s
    ORDER BY sf.formulation_id DESC
    """
    
    rows = run_query(sql, (supplier_id,))
    _print_table(rows, "Your Formulations")
    
    if rows:
        print(f'\n✅ Total: {len(rows)} formulation(s)')


# ============================================================================
# 5. CREATE NEW FORMULATION
# ============================================================================
def create_formulation(user):
    """Create a new supplier formulation with materials"""
    supplier_id = _get_supplier_id(user)
    if not supplier_id:
        return
    
    print('\n➕ Create New Formulation')
    print('-' * 60)
    
    # Show supplier's ingredients
    view_my_ingredients(user)
    
    try:
        # Get formulation details
        ingredient_id = int(input('\nEnter Ingredient ID for this formulation: ').strip())
        
        # Verify supplier supplies this ingredient
        check_sql = """
        SELECT i.name, i.is_compound
        FROM supplier_ingredient si
        JOIN ingredient i ON i.ingredient_id = si.ingredient_id
        WHERE si.supplier_id = %s AND si.ingredient_id = %s
        """
        result = run_query(check_sql, (supplier_id, ingredient_id))
        if not result:
            print(f'❌ You do not supply ingredient ID {ingredient_id}')
            return
        
        ingredient_name = result[0]['name']
        is_compound = result[0]['is_compound']
        
        print(f'\n📦 Creating formulation for: {ingredient_name} (ID: {ingredient_id})')
        print(f'   Type: {"Compound" if is_compound else "Atomic"}')
        
        pack_size = float(input('Pack size (oz): ').strip())
        unit_price = float(input('Unit price ($): ').strip())
        
        print('\nEffective Date Range:')
        effective_from = input('Effective from (YYYY-MM-DD): ').strip()
        effective_to_input = input('Effective to (YYYY-MM-DD, or leave blank for open-ended): ').strip()
        effective_to = effective_to_input if effective_to_input else None
        
        # Insert formulation
        insert_sql = """
        INSERT INTO supplier_formulation 
        (supplier_id, ingredient_id, pack_size_oz, unit_price, effective_from, effective_to)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        run_query(insert_sql, (supplier_id, ingredient_id, pack_size, unit_price, 
                               effective_from, effective_to), fetch=False)
        
        # Get the formulation_id
        formulation_id_sql = "SELECT LAST_INSERT_ID() as formulation_id"
        formulation_result = run_query(formulation_id_sql)
        formulation_id = formulation_result[0]['formulation_id']
        
        print(f'\n✅ Formulation created with ID: {formulation_id}')
        
        # If compound ingredient, add materials
        if is_compound:
            print('\n📦 This is a compound ingredient. Add materials:')
            add_materials = input('Add materials now? (yes/no): ').strip().lower()
            
            if add_materials == 'yes':
                _add_formulation_materials(formulation_id, ingredient_id)
        
        print(f'\n✅ Formulation created successfully!')
        
    except ValueError as e:
        print(f'❌ Invalid input: {e}')
    except Exception as e:
        print(f'❌ Error creating formulation: {e}')


def _add_formulation_materials(formulation_id, parent_ingredient_id):
    """Helper to add materials to a formulation"""
    # Show available materials (atomic ingredients)
    print('\nAvailable materials (atomic ingredients):')
    sql = """
    SELECT ingredient_id, name
    FROM ingredient
    WHERE is_compound = FALSE
    ORDER BY ingredient_id
    """
    materials = run_query(sql)
    _print_table(materials, "Available Materials")
    
    while True:
        try:
            material_id = input('\nEnter material ingredient ID (or "done" to finish): ').strip()
            if material_id.lower() == 'done':
                break
            
            material_id = int(material_id)
            qty_oz = float(input('Quantity (oz): ').strip())
            
            insert_sql = """
            INSERT INTO supplier_formulation_material 
            (formulation_id, material_ingredient_id, qty_oz)
            VALUES (%s, %s, %s)
            """
            run_query(insert_sql, (formulation_id, material_id, qty_oz), fetch=False)
            print(f'✅ Added material {material_id} ({qty_oz} oz)')
            
        except ValueError:
            print('❌ Invalid input.')
        except Exception as e:
            print(f'❌ Error adding material: {e}')


# ============================================================================
# 6. VIEW FORMULATION DETAILS
# ============================================================================
def view_formulation_details(user):
    """View detailed information about a specific formulation including materials"""
    supplier_id = _get_supplier_id(user)
    if not supplier_id:
        return
    
    print('\n🔍 View Formulation Details')
    print('-' * 60)
    
    # Show formulations first
    view_my_formulations(user)
    
    try:
        formulation_id = int(input('\nEnter Formulation ID to view details: ').strip())
        
        # Get formulation info
        sql = """
        SELECT 
            sf.formulation_id,
            sf.supplier_id,
            s.name AS supplier_name,
            sf.ingredient_id,
            i.name AS ingredient_name,
            i.is_compound,
            sf.pack_size_oz,
            sf.unit_price,
            sf.effective_from,
            sf.effective_to
        FROM supplier_formulation sf
        JOIN supplier s ON s.supplier_id = sf.supplier_id
        JOIN ingredient i ON i.ingredient_id = sf.ingredient_id
        WHERE sf.formulation_id = %s AND sf.supplier_id = %s
        """
        
        formulation = run_query(sql, (formulation_id, supplier_id))
        if not formulation:
            print(f'❌ Formulation ID {formulation_id} not found or does not belong to you.')
            return
        
        info = formulation[0]
        print(f'\n📋 Formulation #{info["formulation_id"]}')
        print('=' * 60)
        print(f'Ingredient: {info["ingredient_name"]} (ID: {info["ingredient_id"]})')
        print(f'Type: {"Compound" if info["is_compound"] else "Atomic"}')
        print(f'Pack Size: {info["pack_size_oz"]} oz')
        print(f'Unit Price: ${info["unit_price"]}')
        print(f'Effective From: {info["effective_from"]}')
        print(f'Effective To: {info["effective_to"] if info["effective_to"] else "Open-ended"}')
        
        # If compound, show materials
        if info['is_compound']:
            materials_sql = """
            SELECT 
                sfm.material_ingredient_id,
                i.name AS material_name,
                sfm.qty_oz
            FROM supplier_formulation_material sfm
            JOIN ingredient i ON i.ingredient_id = sfm.material_ingredient_id
            WHERE sfm.formulation_id = %s
            ORDER BY sfm.material_ingredient_id
            """
            materials = run_query(materials_sql, (formulation_id,))
            
            if materials:
                print('\n📦 Materials:')
                _print_table(materials, "Formulation Materials")
            else:
                print('\n⚠️  No materials defined for this compound ingredient.')
        
    except ValueError:
        print('❌ Invalid formulation ID.')
    except Exception as e:
        print(f'❌ Error: {e}')


# ============================================================================
# 6a. UPDATE FORMULATION
# ============================================================================
def update_formulation(user):
    """Update an existing formulation"""
    supplier_id = _get_supplier_id(user)
    if not supplier_id:
        return
    
    print('\n✏️  Update Formulation')
    print('-' * 60)
    
    # Show formulations first
    view_my_formulations(user)
    
    try:
        formulation_id = int(input('\nEnter Formulation ID to update: ').strip())
        
        # Get formulation info
        sql = """
        SELECT 
            sf.formulation_id,
            sf.ingredient_id,
            i.name AS ingredient_name,
            i.is_compound,
            sf.pack_size_oz,
            sf.unit_price,
            sf.effective_from,
            sf.effective_to
        FROM supplier_formulation sf
        JOIN ingredient i ON i.ingredient_id = sf.ingredient_id
        WHERE sf.formulation_id = %s AND sf.supplier_id = %s
        """
        
        formulation = run_query(sql, (formulation_id, supplier_id))
        if not formulation:
            print(f'❌ Formulation ID {formulation_id} not found or does not belong to you.')
            return
        
        info = formulation[0]
        print(f'\n📋 Current Formulation #{info["formulation_id"]}')
        print('=' * 60)
        print(f'Ingredient: {info["ingredient_name"]} (ID: {info["ingredient_id"]})')
        print(f'Pack Size: {info["pack_size_oz"]} oz')
        print(f'Unit Price: ${info["unit_price"]}')
        print(f'Effective From: {info["effective_from"]}')
        print(f'Effective To: {info["effective_to"] if info["effective_to"] else "Open-ended"}')
        
        # Update options
        print("\n📝 What would you like to update?")
        print("1. Update pack size and price")
        print("2. Update effective date range")
        print("3. Update materials (for compound ingredients)")
        print("0. Cancel")
        
        choice = input("\nChoose an option: ").strip()
        
        if choice == '0':
            print('❌ Cancelled.')
            return
        
        elif choice == '1':
            # Update pack size and price
            print(f'\nCurrent pack size: {info["pack_size_oz"]} oz')
            new_pack_size = input('New pack size (oz) [press Enter to keep current]: ').strip()
            
            print(f'Current unit price: ${info["unit_price"]}')
            new_unit_price = input('New unit price ($) [press Enter to keep current]: ').strip()
            
            if new_pack_size or new_unit_price:
                pack_size = float(new_pack_size) if new_pack_size else info["pack_size_oz"]
                unit_price = float(new_unit_price) if new_unit_price else info["unit_price"]
                
                update_sql = """
                UPDATE supplier_formulation
                SET pack_size_oz = %s, unit_price = %s
                WHERE formulation_id = %s
                """
                run_query(update_sql, (pack_size, unit_price, formulation_id), fetch=False)
                print('✅ Pack size and price updated successfully!')
            else:
                print('ℹ️  No changes made.')
        
        elif choice == '2':
            # Update effective dates
            print(f'\nCurrent effective from: {info["effective_from"]}')
            new_from = input('New effective from (YYYY-MM-DD) [press Enter to keep current]: ').strip()
            
            print(f'Current effective to: {info["effective_to"] if info["effective_to"] else "Open-ended"}')
            new_to = input('New effective to (YYYY-MM-DD, or "none" for open-ended) [press Enter to keep current]: ').strip()
            
            if new_from or new_to:
                effective_from = new_from if new_from else info["effective_from"]
                
                if new_to.lower() == 'none':
                    effective_to = None
                elif new_to:
                    effective_to = new_to
                else:
                    effective_to = info["effective_to"]
                
                update_sql = """
                UPDATE supplier_formulation
                SET effective_from = %s, effective_to = %s
                WHERE formulation_id = %s
                """
                run_query(update_sql, (effective_from, effective_to, formulation_id), fetch=False)
                print('✅ Effective date range updated successfully!')
            else:
                print('ℹ️  No changes made.')
        
        elif choice == '3':
            # Update materials
            if not info['is_compound']:
                print('❌ This is not a compound ingredient. Materials can only be added to compound ingredients.')
                return
            
            # Show current materials
            materials_sql = """
            SELECT 
                sfm.material_ingredient_id,
                i.name AS material_name,
                sfm.qty_oz
            FROM supplier_formulation_material sfm
            JOIN ingredient i ON i.ingredient_id = sfm.material_ingredient_id
            WHERE sfm.formulation_id = %s
            ORDER BY sfm.material_ingredient_id
            """
            materials = run_query(materials_sql, (formulation_id,))
            
            print('\n--- Current Materials ---')
            if materials:
                _print_table(materials, "Current Materials")
            else:
                print('No materials currently defined.')
            
            print("\n📝 Material Management:")
            print("1. Add new material")
            print("2. Update material quantity")
            print("3. Remove material")
            print("0. Done")
            
            while True:
                sub_choice = input("\nChoose an option: ").strip()
                
                if sub_choice == '0':
                    break
                elif sub_choice == '1':
                    # Add material
                    print("\n--- Available Simple Ingredients ---")
                    simple_ingredients = run_query(
                        "SELECT ingredient_id, name FROM ingredient WHERE is_compound = FALSE ORDER BY name",
                        ()
                    )
                    if simple_ingredients:
                        _print_table(simple_ingredients, "Simple Ingredients")
                        
                        material_id = input('\nMaterial Ingredient ID to add: ').strip()
                        if not material_id:
                            continue
                        
                        try:
                            material_id = int(material_id)
                            
                            # Check if already exists
                            check_sql = """
                            SELECT 1 FROM supplier_formulation_material
                            WHERE formulation_id = %s AND material_ingredient_id = %s
                            """
                            if run_query(check_sql, (formulation_id, material_id)):
                                print(f'❌ Material {material_id} is already in this formulation!')
                                continue
                            
                            qty = float(input('Quantity (oz): ').strip())
                            
                            insert_sql = """
                            INSERT INTO supplier_formulation_material (formulation_id, material_ingredient_id, qty_oz)
                            VALUES (%s, %s, %s)
                            """
                            run_query(insert_sql, (formulation_id, material_id, qty), fetch=False)
                            print(f'✅ Material {material_id} added successfully!')
                            
                            # Refresh display
                            materials = run_query(materials_sql, (formulation_id,))
                            print('\n--- Updated Materials ---')
                            if materials:
                                _print_table(materials, "Updated Materials")
                        except ValueError:
                            print('❌ Invalid input.')
                        except Exception as e:
                            print(f'❌ Error adding material: {e}')
                
                elif sub_choice == '2':
                    # Update quantity
                    if not materials:
                        print('❌ No materials to update!')
                        continue
                    
                    material_id = input('\nMaterial Ingredient ID to update: ').strip()
                    if not material_id:
                        continue
                    
                    try:
                        material_id = int(material_id)
                        
                        # Check if exists
                        check_sql = """
                        SELECT qty_oz FROM supplier_formulation_material
                        WHERE formulation_id = %s AND material_ingredient_id = %s
                        """
                        result = run_query(check_sql, (formulation_id, material_id))
                        if not result:
                            print(f'❌ Material {material_id} not found in this formulation!')
                            continue
                        
                        current_qty = result[0]['qty_oz']
                        print(f'Current quantity: {current_qty} oz')
                        
                        qty = float(input('New quantity (oz): ').strip())
                        
                        update_sql = """
                        UPDATE supplier_formulation_material
                        SET qty_oz = %s
                        WHERE formulation_id = %s AND material_ingredient_id = %s
                        """
                        run_query(update_sql, (qty, formulation_id, material_id), fetch=False)
                        print(f'✅ Quantity updated successfully!')
                        
                        # Refresh display
                        materials = run_query(materials_sql, (formulation_id,))
                        print('\n--- Updated Materials ---')
                        if materials:
                            _print_table(materials, "Updated Materials")
                    except ValueError:
                        print('❌ Invalid input.')
                    except Exception as e:
                        print(f'❌ Error updating quantity: {e}')
                
                elif sub_choice == '3':
                    # Remove material
                    if not materials:
                        print('❌ No materials to remove!')
                        continue
                    
                    material_id = input('\nMaterial Ingredient ID to remove: ').strip()
                    if not material_id:
                        continue
                    
                    try:
                        material_id = int(material_id)
                        
                        # Check if exists
                        check_sql = """
                        SELECT 1 FROM supplier_formulation_material
                        WHERE formulation_id = %s AND material_ingredient_id = %s
                        """
                        if not run_query(check_sql, (formulation_id, material_id)):
                            print(f'❌ Material {material_id} not found in this formulation!')
                            continue
                        
                        confirm = input(f'⚠️  Are you sure you want to remove material {material_id}? (yes/no): ').strip().lower()
                        if confirm == 'yes':
                            delete_sql = """
                            DELETE FROM supplier_formulation_material
                            WHERE formulation_id = %s AND material_ingredient_id = %s
                            """
                            run_query(delete_sql, (formulation_id, material_id), fetch=False)
                            print(f'✅ Material removed successfully!')
                            
                            # Refresh display
                            materials = run_query(materials_sql, (formulation_id,))
                            print('\n--- Updated Materials ---')
                            if materials:
                                _print_table(materials, "Updated Materials")
                            else:
                                print('No materials remaining.')
                    except ValueError:
                        print('❌ Invalid input.')
                    except Exception as e:
                        print(f'❌ Error removing material: {e}')
        
    except ValueError:
        print('❌ Invalid input.')
    except Exception as e:
        print(f'❌ Error: {e}')


# ============================================================================
# 6b. DELETE FORMULATION
# ============================================================================
def delete_formulation(user):
    """Delete an existing formulation"""
    supplier_id = _get_supplier_id(user)
    if not supplier_id:
        return
    
    print('\n🗑️  Delete Formulation')
    print('-' * 60)
    
    # Show formulations first
    view_my_formulations(user)
    
    try:
        formulation_id = int(input('\nEnter Formulation ID to delete: ').strip())
        
        # Get formulation info
        sql = """
        SELECT 
            sf.formulation_id,
            sf.ingredient_id,
            i.name AS ingredient_name,
            i.is_compound,
            sf.pack_size_oz,
            sf.unit_price,
            sf.effective_from,
            sf.effective_to
        FROM supplier_formulation sf
        JOIN ingredient i ON i.ingredient_id = sf.ingredient_id
        WHERE sf.formulation_id = %s AND sf.supplier_id = %s
        """
        
        formulation = run_query(sql, (formulation_id, supplier_id))
        if not formulation:
            print(f'❌ Formulation ID {formulation_id} not found or does not belong to you.')
            return
        
        info = formulation[0]
        
        # Check for materials
        materials_count_sql = """
        SELECT COUNT(*) as count
        FROM supplier_formulation_material
        WHERE formulation_id = %s
        """
        materials_result = run_query(materials_count_sql, (formulation_id,))
        materials_count = materials_result[0]['count'] if materials_result else 0
        
        # Show what will be deleted
        print(f'\n⚠️  Warning: Deleting Formulation #{formulation_id} will:')
        print(f'   • Delete formulation for {info["ingredient_name"]} (ID: {info["ingredient_id"]})')
        if materials_count > 0:
            print(f'   • Delete {materials_count} material(s) associated with this formulation')
        
        # Confirm deletion
        confirm = input(f'\nAre you sure you want to delete this formulation? (yes/no): ').strip().lower()
        if confirm != 'yes':
            print('❌ Cancelled.')
            return
        
        # Delete formulation (CASCADE will delete materials automatically)
        delete_sql = """
        DELETE FROM supplier_formulation
        WHERE formulation_id = %s AND supplier_id = %s
        """
        
        run_query(delete_sql, (formulation_id, supplier_id), fetch=False)
        print(f'✅ Formulation #{formulation_id} deleted successfully!')
        if materials_count > 0:
            print(f'   ✅ {materials_count} material(s) also deleted')
        
    except ValueError:
        print('❌ Invalid formulation ID.')
    except Exception as e:
        print(f'❌ Error deleting formulation: {e}')


# ============================================================================
# 7. RECEIVE INGREDIENT BATCH (Create Inventory Lot)
# ============================================================================
def receive_ingredient_batch(user):
    """Receive a new ingredient batch - creates a new inventory lot"""
    supplier_id = _get_supplier_id(user)
    if not supplier_id:
        return
    
    print('\n📥 Receive Ingredient Batch')
    print('-' * 60)
    
    # Show supplier's ingredients
    view_my_ingredients(user)
    
    try:
        # Get batch details
        ingredient_id = int(input('\nEnter Ingredient ID: ').strip())
        
        # Verify supplier supplies this ingredient
        check_sql = """
        SELECT i.name
        FROM supplier_ingredient si
        JOIN ingredient i ON i.ingredient_id = si.ingredient_id
        WHERE si.supplier_id = %s AND si.ingredient_id = %s
        """
        result = run_query(check_sql, (supplier_id, ingredient_id))
        if not result:
            print(f'❌ You do not supply ingredient ID {ingredient_id}')
            return
        
        ingredient_name = result[0]['name']
        print(f'\n📦 Receiving: {ingredient_name} (ID: {ingredient_id})')
        
        supplier_batch_id = input('Supplier Batch ID (your internal reference): ').strip()
        quantity_oz = float(input('Quantity (oz): ').strip())
        unit_cost = float(input('Unit cost ($/oz): ').strip())
        
        # Calculate minimum expiration date (90 days from today)
        min_expiration = datetime.now() + timedelta(days=90)
        print(f'\n⚠️  Minimum expiration date: {min_expiration.strftime("%Y-%m-%d")}')
        print('    (Must be at least 90 days from today)')
        
        expiration_date = input('Expiration date (YYYY-MM-DD): ').strip()
        
        # Insert into ingredient_batch (trigger will generate lot_number and set on_hand_oz)
        insert_sql = """
        INSERT INTO ingredient_batch 
        (ingredient_id, supplier_id, supplier_batch_id, quantity_oz, unit_cost, expiration_date)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        run_query(insert_sql, (ingredient_id, supplier_id, supplier_batch_id, 
                               quantity_oz, unit_cost, expiration_date), fetch=False)
        
        # Get the generated lot number
        lot_sql = """
        SELECT lot_number, ingredient_batch_id
        FROM ingredient_batch
        WHERE ingredient_id = %s 
          AND supplier_id = %s 
          AND supplier_batch_id = %s
        ORDER BY received_at DESC
        LIMIT 1
        """
        lot_result = run_query(lot_sql, (ingredient_id, supplier_id, supplier_batch_id))
        
        if lot_result:
            lot_number = lot_result[0]['lot_number']
            batch_id = lot_result[0]['ingredient_batch_id']
            print(f'\n✅ Ingredient batch received successfully!')
            print(f'   Batch ID: {batch_id}')
            print(f'   Lot Number: {lot_number}')
            print(f'   Quantity: {quantity_oz} oz')
            print(f'   On-hand: {quantity_oz} oz (initial)')
        
    except ValueError as e:
        print(f'❌ Invalid input: {e}')
    except Exception as e:
        print(f'❌ Error receiving batch: {e}')
        if '90 days' in str(e):
            print('💡 Tip: Expiration date must be at least 90 days from today.')


# ============================================================================
# 8. VIEW MY INGREDIENT BATCHES
# ============================================================================
def view_my_batches(user):
    """View all ingredient batches supplied by this supplier"""
    supplier_id = _get_supplier_id(user)
    if not supplier_id:
        return
    
    print(f'\n📦 Your Ingredient Batches (Supplier {supplier_id}):')
    
    sql = """
    SELECT 
        ib.ingredient_batch_id,
        ib.lot_number,
        ib.ingredient_id,
        i.name AS ingredient_name,
        ib.supplier_batch_id,
        ib.quantity_oz,
        ib.on_hand_oz,
        ib.unit_cost,
        ib.expiration_date,
        ib.received_at,
        DATEDIFF(ib.expiration_date, CURDATE()) AS days_until_expiry,
        CASE 
            WHEN ib.on_hand_oz = 0 THEN 'Depleted'
            WHEN DATEDIFF(ib.expiration_date, CURDATE()) < 10 THEN 'Expiring Soon'
            WHEN DATEDIFF(ib.expiration_date, CURDATE()) < 0 THEN 'Expired'
            ELSE 'Available'
        END AS status
    FROM ingredient_batch ib
    JOIN ingredient i ON i.ingredient_id = ib.ingredient_id
    WHERE ib.supplier_id = %s
    ORDER BY ib.received_at DESC
    """
    
    rows = run_query(sql, (supplier_id,))
    _print_table(rows, "Your Ingredient Batches")
    
    if rows:
        print(f'\n✅ Total: {len(rows)} batch(es)')
        
        # Summary statistics
        total_batches = len(rows)
        available = sum(1 for r in rows if r['status'] == 'Available')
        expiring = sum(1 for r in rows if r['status'] == 'Expiring Soon')
        expired = sum(1 for r in rows if r['status'] == 'Expired')
        depleted = sum(1 for r in rows if r['status'] == 'Depleted')
        
        print(f'\n📊 Summary:')
        print(f'   Available: {available}')
        print(f'   Expiring Soon (<10 days): {expiring}')
        print(f'   Expired: {expired}')
        print(f'   Depleted: {depleted}')


# ============================================================================
# 9. VIEW DO-NOT-COMBINE RULES
# ============================================================================
def view_do_not_combine(user):
    """View all do-not-combine ingredient pairs (global rules)"""
    print('\n⚠️  Do-Not-Combine Rules (Incompatible Ingredient Pairs):')
    
    sql = """
    SELECT 
        dnc.ingredient_a,
        ia.name AS ingredient_a_name,
        dnc.ingredient_b,
        ib.name AS ingredient_b_name
    FROM do_not_combine dnc
    JOIN ingredient ia ON ia.ingredient_id = dnc.ingredient_a
    JOIN ingredient ib ON ib.ingredient_id = dnc.ingredient_b
    ORDER BY dnc.ingredient_a, dnc.ingredient_b
    """
    
    rows = run_query(sql)
    _print_table(rows, "Do-Not-Combine Rules")
    
    if rows:
        print(f'\n✅ Total: {len(rows)} rule(s)')
        print('💡 These ingredient pairs cannot be used together in products.')
