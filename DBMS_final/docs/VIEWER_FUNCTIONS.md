# Viewer Functions Documentation

## Overview
This document provides comprehensive documentation for all viewer-specific functionality implemented in `viewer_actions.py`. The Viewer role provides read-only access to the food manufacturing system, enabling external stakeholders, auditors, researchers, and quality inspectors to browse products, analyze ingredients, assess safety compliance, and review supplier information without modification privileges.

---

## Function Categories

| Category | Functions | Purpose |
|----------|-----------|---------|
| **Product Browsing** | 3 functions | Explore product catalog with multiple filtering options |
| **Ingredient Analysis** | 1 function | Examine product compositions and recipe details |
| **Safety & Compliance** | 2 functions | Monitor incompatibility rules and health risk violations |
| **Supplier Intelligence** | 1 function | Review active supplier formulations and pricing |

---

## Core Helper Function

### _print_table(rows, column_keys, display_headers=None)

**Purpose**: Advanced table formatting with flexible column selection and custom headers.

**Parameters**:
- `rows` (list): Database result rows as dictionaries
- `column_keys` (list): Dictionary keys to extract from each row
- `display_headers` (list, optional): Custom column headers for display

**Features**:
- **Flexible Display**: Supports custom column selection from database results
- **Header Customization**: Allows user-friendly column names different from database keys
- **Empty Data Handling**: Gracefully handles missing data with appropriate fallbacks
- **Consistent Formatting**: Uses grid format for professional presentation

**Example Usage**:
```python
_print_table(
    rows=product_data, 
    column_keys=['product_type_id', 'manufacturer_name'], 
    display_headers=['Product ID', 'Manufacturer']
)
```

---

## Product Browsing

### 1. browse_all_products()

**Purpose**: Comprehensive overview of all products in the manufacturing system.

**Database Query**:
```sql
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
```

**Business Intelligence**:
- **Production Metrics**: Shows total batches and units produced per product
- **Portfolio Overview**: Complete product catalog across all manufacturers
- **Category Organization**: Products sorted by category for logical browsing
- **Activity Indicators**: Production activity through batch counts

**Output Example**:
```
┌────────────┬──────────────┬──────────────┬──────────┬───────────┬─────────────┐
│ Product ID │ Manufacturer │ Product Name │ Category │ # Batches │ Total Units │
├────────────┼──────────────┼──────────────┼──────────┼───────────┼─────────────┤
│        100 │ FreshCorp    │ Steak Dinner │ Dinners  │         3 │        900  │
│        101 │ HealthCorp   │ Veggie Bowl  │ Dinners  │         2 │        600  │
└────────────┴──────────────┴──────────────┴──────────┴───────────┴─────────────┘
```

**Business Applications**:
- Market research and competitive analysis
- Production activity monitoring across manufacturers
- Product portfolio assessment for retailers
- Regulatory oversight of food production

---

### 2. browse_products_by_manufacturer()

**Purpose**: Manufacturer-specific product portfolio analysis.

**Interactive Workflow**:
1. **Manufacturer Selection**: Display all available manufacturers
2. **Portfolio Focus**: Show products only from selected manufacturer
3. **Detailed Metrics**: Include manufacturer-specific production statistics

**Database Operations**:
```sql
-- First: Get manufacturer list
SELECT manufacturer_id, name as manufacturer_name 
FROM manufacturer ORDER BY name

-- Then: Get products for selected manufacturer
SELECT 
    pt.product_type_id, pt.name as product_name, c.name as category,
    pt.product_code, COUNT(DISTINCT pb.product_batch_id) as num_batches,
    COALESCE(SUM(pb.produced_units), 0) as total_units
FROM product_type pt
JOIN category c ON pt.category_id = c.category_id
LEFT JOIN product_batch pb ON pt.product_type_id = pb.product_type_id
WHERE pt.manufacturer_id = %s
GROUP BY pt.product_type_id, pt.name, c.name, pt.product_code
ORDER BY c.name, pt.name
```

**Advanced Features**:
- **Product Code Display**: Shows internal manufacturer codes
- **Fallback Option**: Empty input returns to browse_all_products()
- **Manufacturer Validation**: Verifies manufacturer exists before querying
- **Context Preservation**: Maintains manufacturer name throughout display

**Business Applications**:
- Supplier evaluation and due diligence
- Manufacturer performance assessment
- Contract negotiation support
- Quality audit preparation

---

### 3. browse_products_by_category()

**Purpose**: Category-based product exploration for market segment analysis.

**Interactive Features**:
- **Category Discovery**: Shows all active categories in the system
- **Flexible Input**: Category name-based selection
- **Market Segmentation**: Groups products by food category types

**Database Query**:
```sql
SELECT 
    pt.product_type_id, m.name as manufacturer_name,
    pt.name as product_name, pt.product_code,
    COUNT(DISTINCT pb.product_batch_id) as num_batches,
    COALESCE(SUM(pb.produced_units), 0) as total_units
FROM product_type pt
JOIN manufacturer m ON pt.manufacturer_id = m.manufacturer_id
JOIN category c ON pt.category_id = c.category_id
LEFT JOIN product_batch pb ON pt.product_type_id = pb.product_type_id
WHERE c.name = %s
GROUP BY pt.product_type_id, m.name, pt.name, pt.product_code
ORDER BY m.name, pt.name
```

**Category Examples**:
- Dinners
- Snacks
- Beverages
- Desserts
- Breakfast Items

**Business Intelligence**:
- **Market Analysis**: Understand product distribution across food categories
- **Competitive Landscape**: See all manufacturers in specific categories
- **Trend Analysis**: Identify popular categories by production volume
- **Gap Analysis**: Discover underrepresented categories

---

## Ingredient Analysis

### 4. view_product_ingredients()

**Purpose**: Detailed ingredient composition analysis for products using active recipe plans.

**Interactive Workflow**:
1. **Product Selection**: Browse and select from all available products
2. **Product Context**: Display product details (name, manufacturer, category)
3. **Ingredient Breakdown**: Show complete ingredient list with quantities
4. **Batch Calculation**: Include standard batch size for scaling calculations

**Database Queries**:
```sql
-- Product context information
SELECT pt.name as product_name, m.name as manufacturer_name, c.name as category
FROM product_type pt
JOIN manufacturer m ON pt.manufacturer_id = m.manufacturer_id
JOIN category c ON pt.category_id = c.category_id
WHERE pt.product_type_id = %s

-- Active recipe plan ingredients
SELECT 
    i.ingredient_id, i.name as ingredient_name,
    rpi.qty_oz_per_unit, pt.standard_batch_units
FROM recipe_plan rp
JOIN recipe_plan_item rpi ON rp.recipe_plan_id = rpi.recipe_plan_id
JOIN ingredient i ON rpi.ingredient_id = i.ingredient_id
JOIN product_type pt ON rp.product_type_id = pt.product_type_id
WHERE rp.product_type_id = %s
ORDER BY rpi.qty_oz_per_unit DESC
```

**Output Features**:
```
================================================================
Product: Premium Beef Stew
Manufacturer: FreshCorp
Category: Dinners
================================================================

Standard Batch Size: 300 units

┌──────────────┬─────────────────┬──────────────────────┐
│ Ingredient   │ Ingredient Name │ Qty per Unit (oz)    │
│ ID           │                 │                      │
├──────────────┼─────────────────┼──────────────────────┤
│           15 │ Beef Chunks     │                 4.5  │
│           20 │ Mixed Veggies   │                 2.0  │
│           25 │ Beef Broth      │                 1.5  │
└──────────────┴─────────────────┴──────────────────────┘
```

**Business Applications**:
- **Nutritional Analysis**: Foundation for nutrition label calculation
- **Cost Estimation**: Ingredient cost analysis for pricing decisions
- **Allergen Assessment**: Identify potential allergens in products
- **Procurement Planning**: Understand ingredient requirements for production
- **Recipe Verification**: Confirm recipe accuracy for quality control

**Advanced Calculations**:
- Per-unit ingredient requirements
- Total batch ingredient needs
- Ingredient intensity analysis (highest quantity ingredients first)

---

## Safety & Compliance

### 5. compare_products_for_incompatibility() ⭐ **CRITICAL SAFETY FUNCTION**

**Purpose**: Identify dangerous ingredient combinations between products using the `sp_compare_products_incompatibility` stored procedure.

**Interactive Workflow**:
1. **Product Selection**: Choose two products for compatibility analysis
2. **Product Validation**: Ensure both products exist and are different
3. **Stored Procedure Call**: Execute incompatibility analysis
4. **Safety Assessment**: Report any dangerous ingredient combinations

**Stored Procedure Integration**:
```python
call_query = "CALL sp_compare_products_incompatibility(%s, %s)"
results = run_query(call_query, (product1_id, product2_id))
```

**Safety Logic**:
- **Cross-Reference**: Compares all ingredients from both products
- **Do-Not-Combine Rules**: Uses global incompatibility database
- **Risk Assessment**: Identifies specific problematic ingredient pairs
- **Safety Recommendation**: Provides clear guidance on product combination safety

**Output Scenarios**:

**Safe Combination**:
```
✅ No incompatibilities found!
   Products 'Beef Stew' and 'Chicken Soup' can be safely combined.
```

**Dangerous Combination**:
```
⚠️  INCOMPATIBILITIES DETECTED!

The following ingredient pairs from these products should NOT be combined:

┌──────────────────┬──────────────────┬──────────────────┬──────────────────┐
│ Ingredient A ID  │ Ingredient A     │ Ingredient B ID  │ Ingredient B     │
│                  │ Name             │                  │ Name             │
├──────────────────┼──────────────────┼──────────────────┼──────────────────┤
│              15  │ Sodium Nitrate   │              42  │ Vitamin C        │
└──────────────────┴──────────────────┴──────────────────┴──────────────────┘

⚠️  Found 1 incompatible ingredient pair(s)
   These products should NOT be processed or stored together!
```

**Critical Business Applications**:
- **Food Safety Compliance**: FDA and HACCP requirement compliance
- **Co-packing Safety**: Ensure safe shared production facilities
- **Storage Planning**: Warehouse segregation requirements
- **Quality Control**: Prevent dangerous product combinations
- **Regulatory Audits**: Demonstrate due diligence in safety protocols
- **Insurance Compliance**: Meet food safety insurance requirements

---

### 6. view_health_risk_violations()

**Purpose**: Monitor existing health risk violations through the `v_health_risk_violations` database view.

**Database View Query**:
```sql
SELECT * FROM v_health_risk_violations ORDER BY created_at DESC
```

**Risk Detection Logic**:
The view identifies product batches created in the last 30 days that contain incompatible ingredient combinations, representing immediate health risks in the supply chain.

**Output Scenarios**:

**Safe System State**:
```
✅ No health risk violations detected!
   All recent product batches comply with do-not-combine rules.
```

**Critical Violations Detected**:
```
⚠️  HEALTH RISK VIOLATIONS DETECTED!

┌──────────┬─────────────┬─────────────┬──────────────┬─────────────┬─────────────┬─────────────┐
│ Batch ID │ Lot Number  │ Product     │ Manufacturer │ Ingredient  │ Ingredient  │ Created     │
│          │             │             │ ID           │ A           │ B           │             │
├──────────┼─────────────┼─────────────┼──────────────┼─────────────┼─────────────┼─────────────┤
│      123 │ 100-MFG-123 │ Mixed Salad │           1  │ Preserv. A  │ Acid X      │ 2025-01-15  │
└──────────┴─────────────┴─────────────┴──────────────┴─────────────┴─────────────┴─────────────┘

⚠️  1 violation(s) detected
   ⚠️  These batches contain incompatible ingredient combinations!
```

**Critical Response Applications**:
- **Immediate Recall**: Trigger product recall procedures
- **Quality Investigation**: Launch root cause analysis
- **Regulatory Notification**: Report to FDA and relevant authorities
- **Customer Safety**: Issue safety alerts and notifications
- **Process Review**: Examine production controls and recipe validation
- **Legal Protection**: Document compliance monitoring efforts

**Regulatory Compliance**:
- HACCP (Hazard Analysis Critical Control Points) monitoring
- FDA Food Safety Modernization Act compliance
- ISO 22000 food safety management system requirements
- Traceability requirements for food safety incidents

---

## Supplier Intelligence

### 7. view_all_formulations()

**Purpose**: Comprehensive overview of active supplier formulations through the `v_active_formulations` database view.

**Database View Query**:
```sql
SELECT * FROM v_active_formulations
ORDER BY supplier_name, ingredient_name
```

**Business Intelligence Features**:
- **Current Formulations Only**: Shows only active formulations within effective date ranges
- **Pricing Visibility**: Current unit prices across all suppliers
- **Supplier Comparison**: Side-by-side comparison of formulations for the same ingredients
- **Market Analysis**: Understanding of supplier capabilities and pricing

**Output Format**:
```
┌────────────────┬────────────┬─────────────────┬─────────────────┬─────────────┬───────────────┬─────────────┐
│ Formulation ID │ Supplier   │ Ingredient      │ Pack Size (oz)  │ Unit Price  │ Effective     │ Effective   │
│                │            │                 │                 │             │ From          │ To          │
├────────────────┼────────────┼─────────────────┼─────────────────┼─────────────┼───────────────┼─────────────┤
│             15 │ FreshSupply│ Organic Tomatoes│            50.0 │       12.50 │ 2025-01-01    │ None        │
│             16 │ QualityFarm│ Organic Tomatoes│            45.0 │       11.75 │ 2025-01-01    │ 2025-12-31  │
└────────────────┴────────────┴─────────────────┴─────────────────┴─────────────┴───────────────┴─────────────┘
```

**Strategic Business Applications**:

**Procurement Intelligence**:
- **Price Comparison**: Compare formulation prices across suppliers
- **Supplier Evaluation**: Assess supplier capabilities and specializations
- **Contract Negotiation**: Market pricing information for negotiations
- **Alternative Sourcing**: Identify alternative suppliers for ingredients

**Market Analysis**:
- **Competitive Pricing**: Understand market pricing for ingredients
- **Supplier Capabilities**: See which suppliers offer which ingredients
- **Market Coverage**: Identify ingredient availability gaps
- **Pricing Trends**: Historical pricing through effective date analysis

**Quality Management**:
- **Formulation Standards**: Review supplier formulation specifications
- **Package Sizing**: Understand available packaging options
- **Supplier Diversity**: Monitor supplier base breadth
- **Supply Chain Risk**: Assess dependency on specific suppliers

---

## Integration Features

### Read-Only Security Model
- **No Database Modifications**: All functions use SELECT queries only
- **Cross-Entity Access**: Can view data across all manufacturers and suppliers
- **Audit Trail Safe**: No risk of data modification during reviews
- **Compliance Friendly**: Supports regulatory audits without system risk

### Advanced Reporting Capabilities
- **Cross-Referential Analysis**: Links data across multiple tables
- **Business Intelligence**: Provides actionable insights beyond raw data
- **Formatted Output**: Professional presentation suitable for stakeholder reports
- **Flexible Filtering**: Multiple browse options for different analysis needs

### Safety-First Design
- **Critical Safety Functions**: Incompatibility checking as primary feature
- **Real-Time Monitoring**: Current violations and risk assessment
- **Regulatory Compliance**: Supports FDA and food safety requirements
- **Preventive Analysis**: Product comparison before problems occur

### Stakeholder Value
- **External Auditors**: Complete system visibility without modification risk
- **Regulatory Inspectors**: Safety compliance monitoring and verification
- **Business Analysts**: Market intelligence and competitive analysis
- **Quality Managers**: Safety verification and supplier assessment
- **Procurement Teams**: Supplier intelligence and pricing analysis

### Performance Optimization
- **Efficient Queries**: Optimized JOINs with proper aggregate functions
- **View-Based Access**: Uses database views for complex pre-computed queries
- **Minimal Data Transfer**: Focused queries returning only necessary information
- **User-Friendly Display**: Clear formatting with intuitive column headers

This comprehensive viewer function suite provides essential read-only access to the food manufacturing system, enabling external stakeholders to perform critical safety assessments, business intelligence analysis, and regulatory compliance monitoring without any risk of data modification or system disruption.