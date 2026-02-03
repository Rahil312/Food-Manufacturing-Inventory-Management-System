"""menus.py
Role-based menus. Each function should call into queries.py or call stored procedures.
"""
from app import queries
from app import supplier_actions
import app.manufacturer_actions as manufacturer_actions
import app.viewer_actions as viewer_actions


def manufacturer_menu(user):
    """Show menu for MANUFACTURER users - Full product batch creation workflow"""
    while True:
        print('\n' + '='*80)
        print('🏭 MANUFACTURER MENU')
        print('='*80)
        print('📦 Product Type Management:')
        print('  1. View My Product Types')
        print('  2. Create Product Type')
        print('  3. Update Product Type')
        print('  4. Delete Product Type')
        print()
        print('📋 Recipe Plan Management:')
        print('  5. View My Recipe Plans')
        print('  6. View Recipe Plan Details')
        print('  7. Create Recipe Plan')
        print('  8. Update Recipe Plan')
        print('  9. Delete Recipe Plan')
        print()
        print('🎯 Production:')
        print('  10. Create Product Batch (Uses sp_record_product_batch)')
        print()
        print('📊 Reports:')
        print('  11. Reports Menu (Inventory, Costs, Expiration)')
        print()
        print('  0. Logout')
        print('='*80)
        
        choice = input('Choose an option: ').strip()
        
        if choice == '1':
            manufacturer_actions.view_my_product_types(user)
        elif choice == '2':
            manufacturer_actions.create_product_type(user)
        elif choice == '3':
            manufacturer_actions.update_product_type(user)
        elif choice == '4':
            manufacturer_actions.delete_product_type(user)
        elif choice == '5':
            manufacturer_actions.view_my_recipe_plans(user)
        elif choice == '6':
            manufacturer_actions.view_recipe_plan_details(user)
        elif choice == '7':
            manufacturer_actions.create_recipe_plan(user)
        elif choice == '8':
            manufacturer_actions.update_recipe_plan(user)
        elif choice == '9':
            manufacturer_actions.delete_recipe_plan(user)
        elif choice == '10':
            manufacturer_actions.create_product_batch(user)
        elif choice == '11':
            manufacturer_actions.reports_menu(user)
        elif choice == '0':
            print('👋 Logging out...')
            break
        else:
            print('❌ Invalid choice')


def supplier_menu(user):
    """Supplier menu with full implementation"""
    while True:
        print('\n' + '='*60)
        print('SUPPLIER MENU')
        print('='*60)
        print('1) View My Ingredients')
        print('2) Add Ingredient to My Supply List')
        print('3) Remove Ingredient from My Supply List')
        print('4) View My Formulations')
        print('5) Create New Formulation')
        print('6) View Formulation Details')
        print('7) Update Formulation')
        print('8) Delete Formulation')
        print('9) Receive Ingredient Batch (Create Inventory Lot)')
        print('10) View My Ingredient Batches')
        print('11) View Do-Not-Combine Rules')
        print('0) Logout')
        print('='*60)
        choice = input('Choose: ').strip()
        
        if choice == '0':
            print('👋 Logging out...')
            break
        elif choice == '1':
            supplier_actions.view_my_ingredients(user)
        elif choice == '2':
            supplier_actions.add_ingredient_to_supply(user)
        elif choice == '3':
            supplier_actions.remove_ingredient_from_supply(user)
        elif choice == '4':
            supplier_actions.view_my_formulations(user)
        elif choice == '5':
            supplier_actions.create_formulation(user)
        elif choice == '6':
            supplier_actions.view_formulation_details(user)
        elif choice == '7':
            supplier_actions.update_formulation(user)
        elif choice == '8':
            supplier_actions.delete_formulation(user)
        elif choice == '9':
            supplier_actions.receive_ingredient_batch(user)
        elif choice == '10':
            supplier_actions.view_my_batches(user)
        elif choice == '11':
            supplier_actions.view_do_not_combine(user)
        else:
            print('❌ Invalid choice. Please try again.')


def viewer_menu(user):
    """Show menu for VIEWER users - Read-only browsing and analysis"""
    while True:
        print('\n' + '='*80)
        print('👁️  VIEWER MENU (Read-Only)')
        print('='*80)
        print('📦 Browse Products:')
        print('  1. Browse All Products')
        print('  2. Browse by Manufacturer')
        print('  3. Browse by Category')
        print()
        print('🔍 Product Analysis:')
        print('  4. View Product Ingredient List')
        print('  5. Compare Products for Incompatibility')
        print()
        print('📊 System Views:')
        print('  6. View Health Risk Violations')
        print('  7. View All Active Formulations')
        print()
        print('  0. Logout')
        print('='*80)
        
        choice = input('Choose an option: ').strip()
        
        if choice == '1':
            viewer_actions.browse_all_products()
        elif choice == '2':
            viewer_actions.browse_products_by_manufacturer()
        elif choice == '3':
            viewer_actions.browse_products_by_category()
        elif choice == '4':
            viewer_actions.view_product_ingredients()
        elif choice == '5':
            viewer_actions.compare_products_for_incompatibility()
        elif choice == '6':
            viewer_actions.view_health_risk_violations()
        elif choice == '7':
            viewer_actions.view_all_formulations()
        elif choice == '0':
            print('👋 Logging out...')
            break
        else:
            print('❌ Invalid choice')
