# Database Management System (DBMS) Project
## Food Manufacturing Inventory System

### Project Team
- **Student 1**: Karan Shaunak Patel

### Course Information
- **Instructor**: Prof. Kemafor Ogan
- **Course**: Database Management Systems
- **Semester**: Fall 2025
- **Date**: November 16, 2025

---

## Project Overview

This project implements a comprehensive inventory management system for food manufacturing companies. The system provides:

-  **Ingredient Inventory Tracking** with FEFO (First Expired, First Out)
-  **Product Recipe Management** and versioning
-  **Supplier Relationship Management** with formulations
-  **Product Batch Creation** with automatic ingredient consumption
-  **Regulatory Compliance** (incompatible ingredient tracking)
-  **Product Recall Traceability**
-  **Role-based Access Control** (Manufacturer, Supplier, Viewer)

---

## System Architecture

### Database Schema Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   SUPPLIERS     │    │   INGREDIENTS    │    │ MANUFACTURERS   │
│                 │    │                  │    │                 │
│ • supplier_id   │    │ • ingredient_id  │    │ • manufacturer  │
│ • name          │◄──►│ • name           │◄──►│ • name          │
│ • supplier_code │    │ • is_compound    │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ FORMULATIONS    │    │ INGREDIENT_BATCH │    │ PRODUCT_TYPE    │
│                 │    │                  │    │                 │
│ • pricing       │    │ • lot_number     │    │ • product_name  │
│ • pack_size     │    │ • on_hand_oz     │    │ • batch_size    │
│ • effective_dt  │    │ • expiration     │    │ • category      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │ STAGING_CONSUME  │    │ RECIPE_PLAN     │
                       │                  │    │                 │
                       │ • session_token  │    │ • ingredients   │
                       │ • qty_oz         │    │ • quantities    │
                       └──────────────────┘    └─────────────────┘
                                │                        │
                                └──────┬─────────────────┘
                                       ▼
                              ┌─────────────────┐
                              │ PRODUCT_BATCH   │
                              │                 │
                              │ • lot_number    │
                              │ • produced_units│
                              │ • batch_cost    │
                              └─────────────────┘
```

### Key Technical Features

- **Triggers** for automatic lot number generation and validation
- **Stored Procedures** for complex business logic (sp_record_product_batch)
- **Views** for data aggregation and reporting
- **Foreign Key Constraints** ensuring data integrity
- **Do-not-combine Rules** for regulatory compliance

---

## Installation & Setup

### Prerequisites

1. **MySQL Server 8.0+** (or MariaDB 10.4+)
2. **MySQL Workbench** (for DDL execution)
3. **Python 3.8+**
4. **Python packages**: `mysql-connector-python`, `tabulate`

### Step-by-Step Installation

#### 1. Database Setup

**a) Start MySQL Server**
- Ensure MySQL is running on `localhost:3306`
- Default credentials: `root`/[your-password]

**b) Execute DDL in MySQL Workbench**
- Open MySQL Workbench
- Connect to your MySQL instance
- Open file: `sql/01_schema_and_logic.sql`
- Execute entire script (Ctrl+Shift+Enter)
- Verify database `dbms_project` is created

**c) Load Seed Data**
- Open file: `sql/02_seed_data.sql`
- Execute entire script (Ctrl+Shift+Enter)
- Verify data is loaded: `SELECT COUNT(*) FROM ingredient_batch;`

#### 2. Python Application Setup

**a) Install Dependencies**
```bash
pip install mysql-connector-python tabulate
```

**b) Configure Database Connection**
- Edit file: `app/db.py`
- Update `DB_CONFIG` dictionary:
```python
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '[YOUR_PASSWORD]',
    'database': 'dbms_project'
}
```

**c) Test Database Connection**
```bash
python app/db.py
```
Expected output: "Connection test passed"

#### 3. Application Execution

**a) Start the Application**
```bash
python -m app.main
```

**b) Login with Test Accounts**

| Role | Username | Password | Capabilities |
|------|----------|----------|--------------|
| **Manufacturer** | `jsmith` | `password123` | Product management, batch creation, FEFO |
| **Supplier** | `jdoe` | `password123` | Ingredient supply, formulations, batches |
| **Viewer** | `bjohnson` | `password123` | Read-only browsing, reporting |

---

## Using the System

### Quick Verification Tests

#### 1. Manufacturer Workflow
- Login as `jsmith`/`password123`
- **View My Product Types** → Should see "Steak Dinner"
- **Create Product Batch** → Use Recipe Plan ID: 1, Choose FEFO auto-selection
- **Reports Menu** → View inventory and costs

#### 2. Supplier Workflow  
- Login as `jdoe`/`password123`
- **View My Ingredients** → Should see Salt, Pepper, Beef Steak, etc.
- **Receive Ingredient Batch** → Add new inventory lot
- **View Do-Not-Combine Rules** → See regulatory restrictions

#### 3. Viewer Workflow
- Login as `bjohnson`/`password123`
- **Browse All Products** → See system-wide product catalog
- **Compare Products for Incompatibility** → Test regulatory compliance
- **View Health Risk Violations** → Monitor expired inventory

---

## 📁 File Structure

```
DBMS_final/
├── README.md                           ← This file
├── 01_schema_and_logic_fixed.sql  ← Complete DDL with triggers/procedures
├── 02_seed_data.sql               ← Sample data for testing
└── app/                                ← Python application
    ├── main.py                         ← Application entry point
    ├── requirements.txt                    ← Python dependencies
    ├── auth.py                         ← Authentication logic
    ├── db.py                           ← Database connection utilities
    ├── menus.py                        ← Role-based menu systems
    ├── manufacturer_actions.py         ← Manufacturer functionality
    ├── supplier_actions.py             ← Supplier functionality
    └── viewer_actions.py               ← Viewer functionality
```
---

## Graduate Features Implemented

### 1. FEFO (First Expired, First Out) Inventory Management
- Automatic selection of ingredient lots based on expiration dates
- Session token isolation for staging consumption
- Minimizes food waste through intelligent lot selection

### 2. Product Recall Traceability
- Complete supply chain tracking via `sp_trace_recall` procedure
- Trace any product batch to all ingredient lots used
- Critical for food safety and regulatory compliance

### 3. Advanced Reporting & Analytics
- Real-time inventory monitoring with consumption tracking
- Cost analysis with unit-level breakdown
- Health risk violation detection for expired inventory

### 4. Regulatory Compliance System
- Do-not-combine ingredient rules enforcement
- Automatic validation during product batch creation
- Product incompatibility analysis


---

## Academic Integrity

This project was developed as original work for **Database Management Systems** under the supervision of the course instructor. All code, database design, and documentation represent the collaborative effort of the team members listed above.

---

## The system demonstrates practical application of:

- **Relational Database Design** principles
- **Transaction Management** and ACID properties  
- **Stored Procedures** and trigger programming
- **Multi-user Role-based** access control
- **Business Logic Implementation** in database layer
- **Application Development** with database integration

---