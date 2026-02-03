from db import run_query

def check_all_tables():
    """Check if there's any data in all database tables"""
    
    tables = [
        'manufacturer', 'supplier', 'category', 'user_account', 'ingredient',
        'ingredient_material', 'supplier_ingredient', 'supplier_formulation',
        'supplier_formulation_material', 'do_not_combine', 'product_type',
        'recipe_plan', 'recipe_plan_item', 'ingredient_batch', 'staging_consumption',
        'product_batch', 'product_batch_consumption'
    ]
    
    print("Checking all database tables for data:")
    print("=" * 50)
    
    total_records = 0
    tables_with_data = []
    
    for table in tables:
        try:
            result = run_query(f"SELECT COUNT(*) as count FROM {table}")
            count = result[0]['count'] if result else 0
            total_records += count
            
            if count > 0:
                print(f"📊 {table}: {count} records")
                tables_with_data.append((table, count))
            else:
                print(f"🈳 {table}: empty")
                
        except Exception as e:
            print(f"❌ {table}: Error - {e}")
    
    print("\n" + "=" * 50)
    
    if total_records == 0:
        print("✅ DATABASE IS COMPLETELY EMPTY")
        print("All tables are clean and ready for fresh data ingestion.")
    else:
        print(f"⚠️  DATABASE CONTAINS {total_records} TOTAL RECORDS")
        print("\nTables with data:")
        for table, count in tables_with_data:
            print(f"  • {table}: {count} records")
        print("\nTo clear all data, run: python clear_data.py")
    
    return total_records == 0

if __name__ == "__main__":
    check_all_tables()