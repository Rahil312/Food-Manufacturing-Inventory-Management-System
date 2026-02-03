# 🏭 Food Manufacturing Inventory Management System

> A comprehensive Database Management System (DBMS) project implementing a real-world inventory management solution for food manufacturing companies.

## 📋 Table of Contents
- [Overview](#overview)
- [Features](#features)
- [System Architecture](#system-architecture)  
- [Quick Start](#quick-start)
- [User Roles](#user-roles)
- [Database Schema](#database-schema)
- [Project Structure](#project-structure)
- [Technologies Used](#technologies-used)
- [Contributing](#contributing)

## 🎯 Overview

This project implements a production-ready inventory management system for food manufacturing companies with advanced features including:

- **FEFO (First Expired, First Out)** inventory tracking
- **Multi-level ingredient composition** (compound ingredients)
- **Supplier relationship management** with versioned formulations
- **Automated product batch creation** with ingredient consumption
- **Regulatory compliance** through incompatible ingredient tracking
- **Complete audit trail** for product recall traceability
- **Role-based access control** with three distinct user types

**Course Information:**
- **Instructor:** Prof. Kemafor Ogan
- **Course:** Database Management Systems  
- **Semester:** Fall 2025

## ✨ Features

### Core Functionality
- ✅ **Ingredient Inventory Tracking** with expiration management
- ✅ **Product Recipe Management** with versioning support
- ✅ **Supplier Formulations** with pricing and effective date ranges
- ✅ **Automated Batch Production** with real-time inventory updates
- ✅ **Regulatory Compliance** via incompatible ingredient rules
- ✅ **Cost Analysis & Reporting** across all operations
- ✅ **Multi-role User Management** (Manufacturer/Supplier/Viewer)

### Advanced Database Features
- **18 Tables** with comprehensive foreign key relationships
- **3 Stored Procedures** for complex business logic automation
- **5 Database Views** for optimized reporting and analytics  
- **5 Triggers** implementing automatic business rules
- **Check Constraints** ensuring data integrity at database level
- **Compound Ingredients** supporting multi-level bill of materials

## 🚀 Quick Start

### Prerequisites
- MySQL Server 8.0+ 
- Python 3.8+
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/food-manufacturing-inventory-system.git
   cd food-manufacturing-inventory-system
   ```

2. **Set up the database**
   ```bash
   # Create and populate the database (use the enhanced version)
   mysql -u root -p < DBMS_final/sql/QUICK_START.sql
   ```

3. **Configure database connection**
   ```bash
   # Copy the template and add your credentials
   cp app/db_config_template.py app/db_config.py
   # Edit app/db_config.py with your MySQL credentials
   ```

4. **Install Python dependencies**
   ```bash
   pip install -r app/requirements.txt
   ```

5. **Run the application**
   ```bash
   python -m app.main
   ```

### 🔐 Test Credentials
| Role | Username | Password | Description |
|------|----------|----------|-------------|
| **Manufacturer** | `alice_mfg` | `password123` | Full production & inventory management |
| **Supplier** | `bob_supplier` | `password123` | Ingredient supply & formulation management |
| **Viewer** | `viewer_user` | `password123` | Read-only access to browse and analyze |

## 👥 User Roles

### 🏭 Manufacturer Role
**Core Responsibilities:** Product development, recipe management, and production operations

**Key Features:**
- Create and manage product types and recipes
- Execute production batches with automatic ingredient consumption
- Monitor inventory levels and expiration dates  
- Generate cost analysis and profitability reports
- Access comprehensive dashboard with key metrics

**Available Operations:**
- Product Type & Recipe Management
- Production Batch Creation (demonstrates stored procedure `sp_record_product_batch`)
- Inventory Reports (On-hand, Nearly Out, Almost Expired)
- Cost Analysis & Profitability Tracking

### 🚚 Supplier Role  
**Core Responsibilities:** Ingredient supply, formulation management, and inventory receiving

**Key Features:**
- Manage ingredient supply catalog and pricing
- Create versioned formulations with material compositions
- Receive ingredient batches with automated lot number generation
- Monitor ingredient inventory and expiration tracking
- Maintain compliance with incompatible ingredient rules

**Available Operations:**
- Ingredient Supply Management
- Formulation Creation & Pricing
- Ingredient Batch Receiving (demonstrates triggers for lot generation)
- Inventory Tracking & Status Monitoring

### 👁️ Viewer Role
**Core Responsibilities:** Analysis, reporting, and regulatory oversight

**Key Features:**
- Browse all products and manufacturers (read-only)
- Analyze product compositions and ingredient usage
- Compare products for regulatory compliance 
- Generate analytical reports across the system
- Monitor system-wide inventory and production metrics

**Available Operations:**
- Product Browsing & Analysis  
- Ingredient Composition Analysis
- Product Incompatibility Checking (demonstrates `sp_compare_products`)
- System-wide Reporting & Analytics

## 🏗️ Database Schema

### Core Entity Relationships

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
```

### Key Database Objects

**📊 Tables (18 total)**
- `ingredient` & `ingredient_material` - Multi-level ingredient composition
- `supplier_formulation` - Versioned supplier pricing and recipes
- `ingredient_batch` - FEFO inventory with lot tracking
- `product_batch` - Production records with full traceability
- `do_not_combine` - Regulatory compliance rules

**⚙️ Stored Procedures (3 total)**
- `sp_record_product_batch` - Automated production with inventory updates
- `sp_compare_products` - Regulatory compliance checking
- `sp_get_unit_cost` - Dynamic cost calculation

**📈 Views (5 total)**  
- `v_report_onhand` - Real-time inventory reporting
- `v_nearly_out_of_stock` - Automated reorder alerts
- `v_almost_expired` - Expiration management dashboard

**🔧 Triggers (5 total)**
- Auto-generation of lot numbers for traceability
- Expiration date validation (90-day minimum)
- Inventory level maintenance on consumption

## 📁 Project Structure

```
├── 📄 README.md                    # Project documentation
├── 🗃️  01_schema_and_logic.sql      # Core database schema (600 lines)
├── 🗃️  02_seed_data.sql             # Sample data population  
├── 🗂️  app/                        # Python CLI Application
│   ├── 🐍 main.py                  # Application entry point
│   ├── 🔐 auth.py                  # User authentication
│   ├── 🗄️  db.py                   # Database connectivity
│   ├── 📋 menus.py                 # Role-based menu system
│   ├── 🏭 manufacturer_actions.py  # Manufacturer operations
│   ├── 🚚 supplier_actions.py      # Supplier operations  
│   ├── 👁️  viewer_actions.py        # Viewer operations
│   └── 📦 requirements.txt         # Python dependencies
├── 🗂️  DBMS_final/                 # Enhanced implementation
│   ├── 📚 docs/                    # Comprehensive documentation
│   ├── 🗃️  sql/                    # Enhanced SQL scripts
│   └── 🧪 tests/                   # Testing framework
└── 📊 Documentation & Diagrams     # ER diagrams and reports
```

## 🛠️ Technologies Used

### Backend Database
- **MySQL 8.0+** - Primary database engine
- **SQL DDL/DML** - Schema definition and data manipulation  
- **Stored Procedures** - Complex business logic implementation
- **Triggers** - Automated business rule enforcement
- **Views** - Optimized reporting and data presentation

### Frontend Application  
- **Python 3.8+** - Core application language
- **mysql-connector-python** - Database connectivity
- **tabulate** - Formatted data presentation
- **python-dotenv** - Environment configuration management

### Development & Deployment
- **Git** - Version control
- **GitHub** - Repository hosting and collaboration
- **Modular Architecture** - Separation of concerns and maintainability

## 🤝 Contributing

### Setup for Development

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Create a feature branch**: `git checkout -b feature/amazing-feature`  
4. **Make your changes** and test thoroughly
5. **Commit your changes**: `git commit -m 'Add amazing feature'`
6. **Push to your branch**: `git push origin feature/amazing-feature`
7. **Open a Pull Request** with detailed description

### Development Guidelines

- Follow existing code style and structure
- Add appropriate comments for complex logic
- Test all database operations thoroughly  
- Update documentation for any schema changes
- Ensure security best practices (no hardcoded credentials)

### Database Changes

- Always test schema changes with sample data
- Document any new triggers, procedures, or constraints
- Maintain backwards compatibility when possible
- Update seed data if new tables are added

---

## 📄 License

This project is part of an academic coursework for Database Management Systems. Please respect academic integrity guidelines when referencing or building upon this work.

## 🙋‍♀️ Support

For questions about this project:
- Check the comprehensive documentation in `/DBMS_final/docs/`
- Review the testing guide in `/DBMS_final/TESTING_GUIDE.md`
- Examine the implementation roadmap for feature details

---

**⭐ If you found this project helpful, please consider giving it a star!**

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