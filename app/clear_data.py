#!/usr/bin/env python3
"""
clear_data.py
Comprehensive data clearing script for DBMS project.
Safely deletes all records from every table in the correct order to respect foreign key constraints.
"""

from db import run_query

def clear_all_data():
    """
    Clear all data from all tables in the correct order to respect foreign key constraints.
    This ensures a clean slate for fresh data insertion.
    """
    
    print("CLEARING ALL DATA FROM DATABASE")
    print("=" * 60)
    
    try:
        # Step 1: Clear transaction/consumption data first (child tables)
        print("1. Clearing transaction and consumption data...")
        transaction_tables = [
            'staging_consumption',           # Staging data for product batch creation
            'product_batch_consumption',     # Product batch ingredient consumption records
            'product_batch'                  # Finished product batches
        ]
        
        for table in transaction_tables:
            result = run_query(f"SELECT COUNT(*) as count FROM {table}")
            count = result[0]['count'] if result else 0
            
            if count > 0:
                run_query(f"DELETE FROM {table}", fetch=False)
                print(f"   ✅ Cleared {count} records from {table}")
            else:
                print(f"   ⚪ {table} was already empty")
        
        # Step 2: Clear recipe and formulation data
        print("\n2. Clearing recipe and formulation data...")
        recipe_tables = [
            'recipe_plan_item',              # Recipe ingredients (BOM items)
            'recipe_plan',                   # Recipe plans for products
            'supplier_formulation_material', # Materials in supplier formulations
            'supplier_formulation'           # Supplier formulations (versioned)
        ]
        
        for table in recipe_tables:
            result = run_query(f"SELECT COUNT(*) as count FROM {table}")
            count = result[0]['count'] if result else 0
            
            if count > 0:
                run_query(f"DELETE FROM {table}", fetch=False)
                print(f"   ✅ Cleared {count} records from {table}")
            else:
                print(f"   ⚪ {table} was already empty")
        
        # Step 3: Clear inventory and ingredient data
        print("\n3. Clearing inventory and ingredient data...")
        inventory_tables = [
            'ingredient_batch',              # Ingredient inventory batches
            'do_not_combine',               # Ingredient conflict rules
            'supplier_ingredient',          # Supplier-ingredient relationships
            'ingredient_material',          # Compound ingredient compositions
            'ingredient'                    # Ingredient master data
        ]
        
        for table in inventory_tables:
            result = run_query(f"SELECT COUNT(*) as count FROM {table}")
            count = result[0]['count'] if result else 0
            
            if count > 0:
                run_query(f"DELETE FROM {table}", fetch=False)
                print(f"   ✅ Cleared {count} records from {table}")
            else:
                print(f"   ⚪ {table} was already empty")
        
        # Step 4: Clear product and category data
        print("\n4. Clearing product and category data...")
        product_tables = [
            'product_type',                  # Product type definitions
            'category'                      # Product categories
        ]
        
        for table in product_tables:
            result = run_query(f"SELECT COUNT(*) as count FROM {table}")
            count = result[0]['count'] if result else 0
            
            if count > 0:
                run_query(f"DELETE FROM {table}", fetch=False)
                print(f"   ✅ Cleared {count} records from {table}")
            else:
                print(f"   ⚪ {table} was already empty")
        
        # Step 5: Clear user accounts and authentication data
        print("\n5. Clearing user accounts...")
        auth_tables = [
            'user_account'                   # User accounts and authentication
        ]
        
        for table in auth_tables:
            result = run_query(f"SELECT COUNT(*) as count FROM {table}")
            count = result[0]['count'] if result else 0
            
            if count > 0:
                run_query(f"DELETE FROM {table}", fetch=False)
                print(f"   ✅ Cleared {count} records from {table}")
            else:
                print(f"   ⚪ {table} was already empty")
        
        # Step 6: Clear master reference data (suppliers and manufacturers)
        print("\n6. Clearing master reference data...")
        master_tables = [
            'supplier',                      # Supplier master data
            'manufacturer'                   # Manufacturer master data
        ]
        
        for table in master_tables:
            result = run_query(f"SELECT COUNT(*) as count FROM {table}")
            count = result[0]['count'] if result else 0
            
            if count > 0:
                run_query(f"DELETE FROM {table}", fetch=False)
                print(f"   ✅ Cleared {count} records from {table}")
            else:
                print(f"   ⚪ {table} was already empty")
        
        # Step 7: Reset auto-increment counters for all tables
        print("\n7. Resetting auto-increment counters...")
        auto_increment_tables = [
            'supplier',
            'category', 
            'user_account',
            'supplier_formulation',
            'product_type',
            'recipe_plan',
            'recipe_plan_item',
            'ingredient_batch',
            'product_batch',
            'product_batch_consumption'
        ]
        
        for table in auto_increment_tables:
            run_query(f"ALTER TABLE {table} AUTO_INCREMENT = 1", fetch=False)
            print(f"   🔄 Reset {table} auto-increment to 1")
        
        # Step 8: Verification - confirm all tables are empty
        print("\n8. VERIFICATION - Confirming all tables are empty...")
        all_tables = [
            'manufacturer', 'supplier', 'category', 'user_account', 'ingredient',
            'ingredient_material', 'supplier_ingredient', 'supplier_formulation',
            'supplier_formulation_material', 'do_not_combine', 'product_type',
            'recipe_plan', 'recipe_plan_item', 'ingredient_batch', 'staging_consumption',
            'product_batch', 'product_batch_consumption'
        ]
        
        all_empty = True
        for table in all_tables:
            result = run_query(f"SELECT COUNT(*) as count FROM {table}")
            count = result[0]['count'] if result else 0
            
            if count == 0:
                print(f"   ✅ {table}: EMPTY")
            else:
                print(f"   ❌ {table}: {count} records remaining!")
                all_empty = False
        
        # Final status
        print("\n" + "=" * 60)
        if all_empty:
            print("🎉 SUCCESS: ALL DATA CLEARED SUCCESSFULLY!")
            print("✅ All tables are empty")
            print("✅ All auto-increment counters reset to 1")
            print("✅ Database is ready for fresh data insertion")
        else:
            print("⚠️  WARNING: Some tables still contain data")
            print("   Check foreign key constraints or table dependencies")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ ERROR during data clearing: {e}")
        import traceback
        traceback.print_exc()
        print("\n💡 TROUBLESHOOTING:")
        print("   - Check if there are foreign key constraint violations")
        print("   - Ensure database connection is working")
        print("   - Try disabling foreign key checks temporarily:")
        print("     SET FOREIGN_KEY_CHECKS = 0;")
        print("     -- run clearing operations --")
        print("     SET FOREIGN_KEY_CHECKS = 1;")

def clear_data_with_foreign_key_disable():
    """
    Alternative clearing method that temporarily disables foreign key checks.
    Use this if the regular clear_all_data() encounters foreign key constraint issues.
    """
    
    print("CLEARING ALL DATA (WITH FOREIGN KEY CHECKS DISABLED)")
    print("=" * 60)
    
    try:
        # Disable foreign key checks
        print("1. Disabling foreign key checks...")
        run_query("SET FOREIGN_KEY_CHECKS = 0", fetch=False)
        print("   ✅ Foreign key checks disabled")
        
        # Get all table names
        all_tables = [
            'product_batch_consumption', 'product_batch', 'staging_consumption',
            'ingredient_batch', 'recipe_plan_item', 'recipe_plan', 'product_type',
            'supplier_formulation_material', 'supplier_formulation', 'do_not_combine',
            'supplier_ingredient', 'ingredient_material', 'ingredient', 'user_account',
            'category', 'supplier', 'manufacturer'
        ]
        
        # Clear all tables
        print("\n2. Clearing all tables...")
        for table in all_tables:
            result = run_query(f"SELECT COUNT(*) as count FROM {table}")
            count = result[0]['count'] if result else 0
            
            if count > 0:
                run_query(f"DELETE FROM {table}", fetch=False)
                print(f"   ✅ Cleared {count} records from {table}")
            else:
                print(f"   ⚪ {table} was already empty")
        
        # Reset auto-increment counters
        print("\n3. Resetting auto-increment counters...")
        auto_increment_tables = [
            'supplier', 'category', 'user_account', 'supplier_formulation',
            'product_type', 'recipe_plan', 'recipe_plan_item', 
            'ingredient_batch', 'product_batch', 'product_batch_consumption'
        ]
        
        for table in auto_increment_tables:
            run_query(f"ALTER TABLE {table} AUTO_INCREMENT = 1", fetch=False)
            print(f"   🔄 Reset {table} auto-increment to 1")
        
        # Re-enable foreign key checks
        print("\n4. Re-enabling foreign key checks...")
        run_query("SET FOREIGN_KEY_CHECKS = 1", fetch=False)
        print("   ✅ Foreign key checks re-enabled")
        
        print("\n🎉 SUCCESS: All data cleared with foreign key override!")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        # Make sure to re-enable foreign key checks even if there's an error
        try:
            run_query("SET FOREIGN_KEY_CHECKS = 1", fetch=False)
            print("   🔄 Foreign key checks re-enabled after error")
        except:
            print("   ⚠️  Could not re-enable foreign key checks - check manually!")
        
        import traceback
        traceback.print_exc()

def show_table_status():
    """
    Show the current record count for all tables.
    Useful for checking what data exists before clearing.
    """
    
    print("CURRENT TABLE STATUS")
    print("=" * 40)
    
    all_tables = [
        'manufacturer', 'supplier', 'category', 'user_account', 'ingredient',
        'ingredient_material', 'supplier_ingredient', 'supplier_formulation',
        'supplier_formulation_material', 'do_not_combine', 'product_type',
        'recipe_plan', 'recipe_plan_item', 'ingredient_batch', 'staging_consumption',
        'product_batch', 'product_batch_consumption'
    ]
    
    total_records = 0
    for table in all_tables:
        try:
            result = run_query(f"SELECT COUNT(*) as count FROM {table}")
            count = result[0]['count'] if result else 0
            total_records += count
            
            status = "EMPTY" if count == 0 else f"{count} records"
            print(f"{table:25} : {status}")
        except Exception as e:
            print(f"{table:25} : ERROR - {e}")
    
    print("-" * 40)
    print(f"{'TOTAL RECORDS':25} : {total_records}")
    print("=" * 40)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--force":
            print("Using force mode (disabling foreign key checks)...")
            clear_data_with_foreign_key_disable()
        elif sys.argv[1] == "--status":
            show_table_status()
        else:
            print("Usage:")
            print("  python clear_data.py           # Normal clearing (respects FK constraints)")
            print("  python clear_data.py --force   # Force clearing (disables FK checks)")
            print("  python clear_data.py --status  # Show current table status")
    else:
        # Default: show status first, then clear
        print("Showing current table status before clearing...\n")
        show_table_status()
        print("\n")
        clear_all_data()