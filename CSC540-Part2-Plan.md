# CSC540 Part 2 — Implementation Plan (MySQL + Python)

This file is a **ready-to-use plan** for Deliverable 2. It tells you exactly **what goes in MySQL** (schema, triggers, procedures, views, seed data) and **what goes in Python** (thin CLI), plus the **build order** so you can get to a working demo quickly.

---

## ✅ Submission Checklist

- **Updated ER diagram** + short “what changed” note  
- **Two SQL files**
  - `sql/01_schema_and_logic.sql` — tables, constraints, triggers, procedures, views
  - `sql/02_seed_data.sql` — sample data (as provided by the professor)
- **Menu-driven CLI** (Python) that runs the role flows and the 10–15 preset queries
- **README.txt** (how to run)
- **~4-page report** (FDs, normalization, constraints & where enforced)

---

## 📁 Recommended Repo Layout

```
/project
  /sql
    01_schema_and_logic.sql
    02_seed_data.sql
  /app
    main.py
    db.py
    auth.py
    menus.py
    queries.py
  /docs
    ER_Revised.pdf
    Part2_Report.pdf
  README.txt
```

---

## 🗄️ What to do in **MySQL**

Put **all data rules and core logic** in the database so grading is easy and your app stays thin.

### 1) DDL (schema) – in `01_schema_and_logic.sql`

**Tables (typical names):**
- `manufacturer`, `supplier`, `category`
- `user_account` (role = `MANUFACTURER` | `SUPPLIER` | `VIEWER`; link to exactly **one** manufacturer *or* supplier)
- `ingredient` (atomic/compound flag)
- `supplier_ingredient` (which ingredients a supplier can provide)
- `supplier_formulation`, `supplier_formulation_material` (one-level composition only, versioned ranges)
- `product_type` (manufacturer-scoped id + `standard_batch_units`)
- `recipe_plan`, `recipe_plan_item` (versioned BOM per unit)
- `ingredient_batch` (incoming lots; `on_hand_oz`)
- `product_batch` (finished lots; lot number; `batch_cost` + `unit_cost`)
- `product_batch_consumption` (exact ingredient lots and quantities used)
- `do_not_combine` (global incompatible ingredient pairs)

**Keys, uniqueness, and checks:**
- PK/FKs everywhere; **unique manufacturer-scoped product ids**; **unique lot numbers**
- Positive quantities/costs
- **Non-overlapping** `supplier_formulation` effective dates (enforce with trigger/proc)
- **Composition one-level only** (trigger to forbid materials that themselves appear as parents)

---

### 2) Triggers – also in `01_schema_and_logic.sql`

- **Compute lot number** on `ingredient_batch` insert:  
  `lot_number = CONCAT(ingredient_id,'-',supplier_id,'-',batch_id)` and enforce uniqueness/pattern.
- **Prevent expired consumption** when inserting into `product_batch_consumption`.
- **Maintain on-hand**  
  - After ingredient receipt → **increase** `on_hand_oz`  
  - After consumption → **decrease** `on_hand_oz`  
  - Optional guard so `on_hand_oz` never goes negative

---

### 3) Stored Procedures – also in `01_schema_and_logic.sql`

#### `sp_record_product_batch(...)`
Does the entire posting **transactionally**:

- **Validates:** user owns the product; `produced_units % standard_batch_units = 0`; selected lots belong to valid suppliers/ingredients; lots not expired; and **sufficient on-hand**.
- **Inserts** `product_batch`, **inserts** all `product_batch_consumption` rows, **decrements on-hand**, **computes** `batch_cost` and `unit_cost = batch_cost / produced_units`, **generates** finished-goods lot number `<productTypeId>-<manufacturerId>-<batchId>`.
- **Do-not-combine check**: flatten the one-level ingredients used and **block** if any pair appears in `do_not_combine`.
- All in one `START TRANSACTION … COMMIT/ROLLBACK`.

**Input strategy for multiple lots:**  
Use a tiny **staging table**, e.g.:
```
staging_consumption(
  session_token VARCHAR(64),
  ingredient_batch_id BIGINT,
  qty_oz DECIMAL(12,3)
)
```
App inserts the rows for the current user/session token, then calls:  
`sp_record_product_batch(token, product_type_id, plan_id, produced_units)`  
The proc consumes from the staging rows, posts the batch atomically, and clears the staging rows.

#### Optional/Grad procs
- `sp_trace_recall(ingredient_id_or_lot, start_date, end_date)` — returns affected product batches
- `sp_select_fefo_single_lot(ingredient_id, required_qty)` — returns **one** not-expired lot with earliest expiration that **singly** satisfies the quantity (splitting not allowed)

---

### 4) Views – also in `01_schema_and_logic.sql`

- `v_active_supplier_formulation` (current versions)
- `v_flat_product_bom(plan_id)` (one-level **flattened** ingredient list for labeling)
- `v_report_onhand`, `v_nearly_out_of_stock`, `v_almost_expired` (power the reports directly)

---

### 5) Seed data – in `02_seed_data.sql`

Insert **prof-provided IDs** so preset queries resolve:
- Manufacturers (e.g., `MFG001`, `MFG002`), suppliers (e.g., **Supplier B** with id `21`),
- Categories, ingredients (atomic + compound),
- Supplier formulations (+materials),
- Do-not-combine pairs,
- Recipe plans (+items),
- Ingredient batches (lots),
- At least **one posted product batch** so the cost/trace queries have output.

---

## 🐍 What to do in **Python**

Keep Python as a thin **menu-driven CLI** that:
- Authenticates a user (simple table lookup) and shows a **menu based on role**
- Collects inputs, calls **stored procedures/SELECTs**, and prints results
- Handles only **light** validation (DB remains the source of truth)

### 1) App skeleton

- `db.py`: connection + helpers (`run_query(sql, params)`, `call_proc(name, params)`)
- `auth.py`: simple login; fetch `role`, `manufacturer_id` or `supplier_id`
- `menus.py` (role-based menus):

**Supplier**
- Manage ingredients supplied (CRUD on `supplier_ingredient`)
- Maintain formulations (+materials)
- Receive ingredient batch (INSERT into `ingredient_batch`)

**Manufacturer**
- Create/Update product types
- Create/Update recipe plans
- **Create product batch**
  1. Insert rows into `staging_consumption` for selected lots  
  2. `CALL sp_record_product_batch(token, product_type_id, plan_id, produced_units)`  
  3. Display returned lot number + unit cost
- Reports: run SELECTs/Views and print tables

**Viewer**
- Browse products by manufacturer/category (SELECT)
- Generate ingredient list (SELECT from `v_flat_product_bom`)

**Queries To Grade (10–15 pre-given)**
- Each item prompts for parameters and runs a prewritten SELECT or calls a stored proc.

---

### 2) Error handling & safety

- **Parameterized queries only**, show friendly messages on SQL errors
- For manufacturer/supplier actions, **always pass the logged-in party’s id** to the proc so the DB enforces ownership
- Print tabular output (e.g., `tabulate` or simple string formatting)

---

### 3) Minimal Python examples

**Call a stored procedure**
```python
def record_batch(conn, token, product_type_id, plan_id, produced_units):
    cur = conn.cursor()
    cur.callproc('sp_record_product_batch', [token, product_type_id, plan_id, produced_units])
    # If your proc SELECTs a result set, fetch via cur.stored_results()
    for result in cur.stored_results():
        rows = result.fetchall()
        print(rows)
    cur.close()
```

**Run a preset query**
```python
SQL = """
SELECT pb.product_lot_number, pbc.ingredient_batch_id, ib.lot_number
FROM product_batch pb
JOIN product_batch_consumption pbc ON pbc.product_batch_id = pb.product_batch_id
JOIN ingredient_batch ib ON ib.ingredient_batch_id = pbc.ingredient_batch_id
WHERE pb.product_type_id = %s AND pb.manufacturer_id = %s
ORDER BY pb.created_at DESC
LIMIT 1
"""
rows = run_query(SQL, (100, 'MFG001'))
```

---

## 🚀 What to build **first** (recommended order)

1) **Schema only** (tables + PK/FK + basic CHECKs)  
   - Load `01_schema_and_logic.sql` (temporarily **without** triggers/procs)  
   - Load `02_seed_data.sql` (minimal rows) → verify FK graph and basic SELECTs

2) **Triggers** (lot number, on-hand, prevent expired consumption)  
   - Re-seed; test each trigger with tiny INSERT/UPDATEs

3) **Core procedure `sp_record_product_batch`** (+ staging table)  
   - Write it **transactionally**  
   - Unit-test:
     - ✅ happy path (valid lots, enough qty)
     - ❌ expired lot (should fail)
     - ❌ insufficient qty (should fail)
     - ❌ do-not-combine conflict (should fail)
     - ✅ `unit_cost` math

4) **Views & Report SELECTs**  
   - Ensure each role’s menu item has a ready query

5) **Seed data (final)**  
   - Populate instructor IDs (e.g., product **100**, `MFG001`, Supplier **B=21**, lot `100-MFG001-B0901`, etc.)  
   - Run all preset queries **directly in MySQL** until results look right

6) **Python CLI skeleton**  
   - Login → role menu → wire **Manufacturer: Create Product Batch** first (touches the most logic)  
   - Add Supplier functions, then Viewer, then Preset Queries screen

7) **Polish**  
   - Clean error messages, parameterize everything  
   - Add a short **demo script** (sequence of menu choices) for the TA

---

## 🧭 Quick responsibility map

| Feature / Rule | MySQL | Python |
|---|---|---|
| Tables, PK/FK, uniques, not nulls | ✅ |  |
| Version ranges & non-overlap checks | ✅ (trigger/proc) |  |
| Lot number format + uniqueness | ✅ (trigger) |  |
| 90-day intake rule on ingredient lots | ✅ (trigger/proc) |  |
| Prevent expired consumption | ✅ (trigger) |  |
| Maintain on-hand | ✅ (triggers) |  |
| Post product batch (all-or-nothing) | ✅ (`sp_record_product_batch`) | calls proc |
| Do-not-combine block on posting | ✅ (inside proc) |  |
| FEFO (if doing grad) | ✅ (helper proc) | optional UI flag |
| Reports & preset queries | ✅ (views/SELECTs) | display results |
| Role enforcement (ownership) | ✅ (procs check ids) | pass current ids |
| CLI menus & input collection |  | ✅ |
| Pretty-print results, friendly errors |  | ✅ |

---

## 💡 Demo flow suggestion (fast path)

1. Login as **Supplier** → receive an ingredient batch (watch lot number trigger)  
2. Login as **Manufacturer** → create/update a recipe plan → create product batch (CALL proc)  
3. Run **Reports** → on-hand, almost-expired, batch-cost summary  
4. Run the **preset queries** screen (10–15 queries) and show correct outputs

---

### That’s it!
Use this plan as the blueprint for your `sql/01_schema_and_logic.sql`, `sql/02_seed_data.sql`, and the Python CLI skeleton. Good luck—this structure will make your demo smooth and grading-friendly.
