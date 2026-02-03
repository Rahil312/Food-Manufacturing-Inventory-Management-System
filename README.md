# 🏭 Food Manufacturing Inventory Management System

<div align="center">

![MySQL](https://img.shields.io/badge/mysql-%2300f.svg?style=for-the-badge&logo=mysql&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Git](https://img.shields.io/badge/git-%23F05033.svg?style=for-the-badge&logo=git&logoColor=white)
![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white)
![CLI](https://img.shields.io/badge/CLI-Terminal%20Interface-black?style=for-the-badge&logo=windows-terminal&logoColor=white)

[![GitHub Stars](https://img.shields.io/github/stars/Rahil312/Food-Manufacturing-Inventory-Management-System?style=social)](https://github.com/Rahil312/Food-Manufacturing-Inventory-Management-System)
[![GitHub Forks](https://img.shields.io/github/forks/Rahil312/Food-Manufacturing-Inventory-Management-System?style=social)](https://github.com/Rahil312/Food-Manufacturing-Inventory-Management-System/fork)
[![GitHub Issues](https://img.shields.io/github/issues/Rahil312/Food-Manufacturing-Inventory-Management-System)](https://github.com/Rahil312/Food-Manufacturing-Inventory-Management-System/issues)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Made with ❤️](https://img.shields.io/badge/Made%20with-❤️-red.svg)](https://github.com/Rahil312)

> *Advancing Food Manufacturing Through Advanced Database Management*

**A Production-Ready Database Management System for Food Manufacturing**

*Implementing sophisticated DBMS concepts with real-world business logic and enterprise-grade features*

[🚀 Quick Start](#-quick-start) • [📖 Documentation](#-user-roles) • [🏗️ Architecture](#️-database-schema) • [🤝 Contributing](#-contributing) • [📞 Contact](#-connect--support)

</div>

---

## 📋 Table of Contents
- [🎯 Overview](#-overview)
- [✨ Features](#-features)
- [🚀 Quick Start](#-quick-start)
- [👥 User Roles](#-user-roles)
- [🏗️ Database Schema](#️-database-schema)
- [📁 Project Structure](#-project-structure)
- [🛠️ Technologies Used](#️-technologies-used)
- [📚 Implementation Plan](#-implementation-plan)
- [🤝 Contributing](#-contributing)
- [📞 Contact](#-contact)

## 🎯 Overview

> A comprehensive Database Management System (DBMS) project implementing a real-world inventory management solution for food manufacturing companies with advanced features including FEFO inventory tracking, multi-level ingredient composition, and automated compliance checking.

This project demonstrates sophisticated database design and implementation skills through:

- **🔄 FEFO (First Expired, First Out)** inventory tracking with automated lot selection
- **🧪 Multi-level ingredient composition** supporting compound ingredients  
- **📊 Supplier relationship management** with versioned formulations and pricing
- **⚡ Automated product batch creation** with real-time inventory consumption
- **🛡️ Regulatory compliance** through incompatible ingredient tracking and validation
- **📈 Complete audit trail** enabling rapid product recall traceability
- **👤 Role-based access control** with three distinct user privilege levels

**📚 Academic Information:**
- **Course:** Database Management Systems (CSC540)
- **Instructor:** Prof. Kemafor Ogan  
- **Semester:** Fall 2025
- **Implementation:** MySQL Backend + Python CLI Frontend

## ✨ Features

<div align="center">

| 🏭 **Manufacturing** | 🚚 **Supply Chain** | 👁️ **Analytics** | 🛡️ **Compliance** |
|:---:|:---:|:---:|:---:|
| Product Recipe Management | Supplier Formulations | Real-time Reporting | Incompatible Ingredients |
| Batch Production Control | Versioned Pricing | Cost Analysis | Regulatory Compliance |
| Inventory Consumption | Multi-level BOM | Expiration Monitoring | Audit Trail |
| FEFO Lot Selection | Automated Receiving | System-wide Metrics | Recall Traceability |

</div>

### 🎯 Core Functionality
- ✅ **Advanced Inventory Tracking** with FEFO (First Expired, First Out) policy enforcement
- ✅ **Intelligent Recipe Management** supporting multi-level ingredient compositions  
- ✅ **Dynamic Supplier Formulations** with time-based pricing and effective date ranges
- ✅ **Automated Production Workflows** with real-time inventory updates and consumption tracking
- ✅ **Regulatory Compliance Engine** preventing unsafe ingredient combinations at database level
- ✅ **Comprehensive Cost Analytics** with unit cost calculations and profitability analysis
- ✅ **Enterprise-Grade Access Control** supporting Manufacturer, Supplier, and Viewer roles

### 🚀 Advanced Database Features
- **📊 18 Normalized Tables** with comprehensive foreign key relationships and data integrity
- **⚙️ 3 Stored Procedures** implementing complex transactional business logic
- **📈 5 Optimized Views** providing real-time reporting and analytics capabilities  
- **🔧 5 Database Triggers** enforcing automatic business rules and data validation
- **🛡️ Advanced Constraints** ensuring data quality through check constraints and unique indexes
- **🔄 Compound Ingredients** enabling sophisticated bill-of-materials hierarchies

## 🚀 Quick Start

<div align="center">

### 🔧 Prerequisites

![MySQL](https://img.shields.io/badge/MySQL-8.0+-blue?logo=mysql&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.8+-green?logo=python&logoColor=white)
![Git](https://img.shields.io/badge/Git-Latest-red?logo=git&logoColor=white)

</div>

### ⚡ Installation

```bash
# 📥 1. Clone the repository
git clone https://github.com/Rahil312/Food-Manufacturing-Inventory-Management-System.git
cd Food-Manufacturing-Inventory-Management-System

# 🗄️ 2. Set up the database
mysql -u root -p < 01_schema_and_logic.sql
mysql -u root -p < 02_seed_data.sql

# 🔐 3. Configure database connection
cp app/db_config_template.py app/db_config.py
# Edit app/db_config.py with your MySQL credentials

# 📦 4. Install Python dependencies
pip install -r app/requirements.txt

# 🚀 5. Launch the application
python -m app.main
```

### 🔐 Demo Credentials

<div align="center">

| 👤 **Role** | 🔑 **Username** | 🗝️ **Password** | 📋 **Capabilities** |
|:---:|:---:|:---:|:---|
| **🏭 Manufacturer** | `alice_mfg` | `password123` | Full production & inventory management |
| **🚚 Supplier** | `bob_supplier` | `password123` | Ingredient supply & formulation management |
| **👁️ Viewer** | `viewer_user` | `password123` | Read-only access to browse and analyze |

</div>

## 👥 User Roles

<div align="center">

### 🏭 **Manufacturer Role**
![Manufacturer](https://img.shields.io/badge/ACCESS-FULL%20CONTROL-success?style=for-the-badge)

</div>

**Core Responsibilities:** Product development, recipe management, and production operations

**🎯 Key Features:**
- Create and manage product types with standardized batch specifications
- Design versioned recipe plans with multi-level ingredient compositions  
- Execute production batches with automatic FEFO ingredient consumption
- Monitor real-time inventory levels and expiration date management
- Generate comprehensive cost analysis and profitability reports
- Access enterprise dashboard with key performance metrics

**⚙️ Available Operations:**
- **📋 Product Type & Recipe Management** - Create and version product specifications
- **🏭 Production Batch Creation** - Demonstrates `sp_record_product_batch` stored procedure
- **📊 Advanced Inventory Reports** - On-hand, Nearly Out, Almost Expired via database views
- **💰 Cost Analysis & Profitability** - Unit cost tracking and variance analysis

---

<div align="center">

### 🚚 **Supplier Role**  
![Supplier](https://img.shields.io/badge/ACCESS-SUPPLY%20CHAIN-blue?style=for-the-badge)

</div>

**Core Responsibilities:** Ingredient supply, formulation management, and inventory receiving

**🎯 Key Features:**
- Manage comprehensive ingredient supply catalog with dynamic pricing
- Create versioned formulations with detailed material compositions
- Receive ingredient batches with automated lot number generation via triggers
- Monitor ingredient inventory levels with expiration tracking and alerts
- Maintain regulatory compliance with incompatible ingredient rule management
- Track supplier performance metrics and delivery schedules

**⚙️ Available Operations:**
- **📦 Ingredient Supply Management** - Maintain supply catalog and availability
- **🧪 Formulation Creation & Pricing** - Version-controlled recipes with effective dates
- **📥 Ingredient Batch Receiving** - Demonstrates triggers for automated lot generation  
- **📈 Inventory Tracking & Status** - Real-time monitoring with status indicators

---

<div align="center">

### 👁️ **Viewer Role**
![Viewer](https://img.shields.io/badge/ACCESS-READ%20ONLY-orange?style=for-the-badge)

</div>

**Core Responsibilities:** Analysis, reporting, and regulatory oversight

**🎯 Key Features:**
- Browse comprehensive product catalog across all manufacturers (read-only access)
- Analyze detailed product compositions and ingredient usage patterns
- Compare products for regulatory compliance and safety verification
- Generate analytical reports across entire system ecosystem
- Monitor system-wide inventory metrics and production performance
- Access regulatory compliance dashboards and violation tracking

**⚙️ Available Operations:**
- **🔍 Product Browsing & Analysis** - System-wide product catalog exploration  
- **🧬 Ingredient Composition Analysis** - Detailed bill-of-materials breakdown
- **⚖️ Product Incompatibility Checking** - Demonstrates `sp_compare_products` procedure
- **📊 System-wide Reporting & Analytics** - Cross-manufacturer performance metrics

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

<div align="center">

### 🏆 **System Performance Metrics**

![Database Tables](https://img.shields.io/badge/Tables-18-brightgreen?style=for-the-badge)
![Stored Procedures](https://img.shields.io/badge/Procedures-3-blue?style=for-the-badge)
![Views](https://img.shields.io/badge/Views-5-orange?style=for-the-badge)
![Triggers](https://img.shields.io/badge/Triggers-5-red?style=for-the-badge)
![User Roles](https://img.shields.io/badge/Roles-3-purple?style=for-the-badge)

| 📊 **Component** | 🔢 **Count** | ⚡ **Performance** | 🎯 **Purpose** |
|:---:|:---:|:---:|:---|
| **📋 Database Tables** | 18 | Optimized Schema | Complete data normalization |
| **⚙️ Stored Procedures** | 3 | High Performance | Complex business logic |
| **📈 Database Views** | 5 | Fast Queries | Real-time reporting |
| **🔧 Automated Triggers** | 5 | Instant Response | Business rule enforcement |
| **👤 User Role Types** | 3 | Secure Access | Role-based permissions |

</div>

## 📁 Project Structure

```
├── 📄 README.md                    # Comprehensive project documentation
├── 🗃️  01_schema_and_logic.sql      # Complete database schema (600 lines)
├── 🗃️  02_seed_data.sql             # Sample data population  
├── 📊 Normalization_Table.pdf      # Database normalization analysis
├── 📋 DBMS_Project_Final_Report.pdf # Complete project report
├── 🖼️  Final_ER.png                 # Entity Relationship diagram
├── 📄 Final_ER_Diagram.pdf         # Detailed ER documentation
├── 🗂️  app/                        # Python CLI Application
│   ├── 🐍 main.py                  # Application entry point
│   ├── 🔐 auth.py                  # User authentication system
│   ├── 🗄️  db.py                   # Database connectivity layer
│   ├── 🔧 db_config_template.py    # Database configuration template
│   ├── 📋 menus.py                 # Role-based menu system
│   ├── 🏭 manufacturer_actions.py  # Manufacturer operations
│   ├── 🚚 supplier_actions.py      # Supplier operations  
│   ├── 👁️  viewer_actions.py        # Viewer operations
│   ├── 🔍 queries.py               # Database query utilities
│   ├── 🧪 test_queries.py          # Query testing framework
│   ├── 📊 check_all_tables.py      # Database verification
│   ├── 🗑️  clear_data.py            # Data cleanup utilities
│   └── 📦 requirements.txt         # Python dependencies
└── 📊 Additional Documentation     # ER diagrams and project reports
```

## 🛠️ Technologies Used

<div align="center">

### Backend Database
![MySQL](https://img.shields.io/badge/mysql-%2300f.svg?style=for-the-badge&logo=mysql&logoColor=white)
![SQL](https://img.shields.io/badge/SQL-DDL%2FDML-lightgrey?style=for-the-badge)

### Frontend Application  
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![CLI](https://img.shields.io/badge/CLI-Terminal%20Interface-black?style=for-the-badge&logo=windows-terminal)

### Development Tools
![Git](https://img.shields.io/badge/git-%23F05033.svg?style=for-the-badge&logo=git&logoColor=white)
![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white)
![VSCode](https://img.shields.io/badge/Visual%20Studio%20Code-0078d4.svg?style=for-the-badge&logo=visual-studio-code&logoColor=white)

</div>

**🗄️ Database Layer:**
- **MySQL 8.0+** - Primary relational database engine with advanced features
- **SQL DDL/DML** - Comprehensive schema definition and data manipulation
- **Stored Procedures** - Complex transactional business logic implementation
- **Database Triggers** - Automated business rule enforcement and data validation
- **Optimized Views** - High-performance reporting and data aggregation
- **Advanced Constraints** - Data integrity through foreign keys and check constraints

**🐍 Application Layer:**
- **Python 3.8+** - Core application development language
- **mysql-connector-python** - Robust database connectivity and transaction management
- **tabulate** - Professional formatted data presentation and reporting
- **python-dotenv** - Secure environment configuration management

**🔧 Development & Architecture:**
- **Git Version Control** - Professional development workflow and collaboration
- **GitHub Integration** - Repository hosting with comprehensive documentation
- **Modular Architecture** - Clean separation of concerns and maintainable codebase
- **Security Best Practices** - Credential protection and parameterized queries

## 📚 Implementation Plan

<div align="center">

![Implementation](https://img.shields.io/badge/STATUS-100%25%20COMPLETE-brightgreen?style=for-the-badge)

</div>

This project follows a comprehensive implementation strategy ensuring a robust and scalable database application:

### 🏗️ **Database Layer Implementation**

**📋 DDL Schema (`01_schema_and_logic.sql`)**
- **18 Normalized Tables** with complete referential integrity
- **Unique Constraints** ensuring manufacturer-scoped product IDs and lot numbers  
- **Advanced Check Constraints** for positive quantities, costs, and business rules
- **Non-overlapping Formulations** enforced through triggers and procedures

**⚡ Automated Business Logic**
- **🔧 5 Database Triggers** implementing:
  - Automatic lot number generation with format validation
  - Expiration date enforcement (90-day minimum policy)
  - Real-time inventory maintenance on consumption and receipt
  - Prevention of expired ingredient consumption

**⚙️ Stored Procedures**
- **`sp_record_product_batch(...)`** - Complete transactional batch processing
  - Validates ownership, quantities, expiration dates, and ingredient availability
  - Implements FEFO (First Expired, First Out) consumption strategy
  - Enforces regulatory "do-not-combine" rules at database level
  - Calculates batch costs and unit costs with full traceability

### 🐍 **Application Layer Architecture**

**🎯 Role-Based Menu System**
- **Manufacturer Interface** - Production control and inventory management
- **Supplier Interface** - Ingredient management and batch receiving  
- **Viewer Interface** - Analytics and regulatory compliance monitoring

**🔒 Security & Data Integrity**
- **Parameterized Queries** preventing SQL injection attacks
- **Role-based Access Control** with ownership validation
- **Transactional Processing** ensuring data consistency
- **Input Validation** with friendly error messaging

**📊 Advanced Features**
- **Staging Tables** for complex multi-lot ingredient selection
- **FEFO Optimization** with automated lot selection procedures  
- **Real-time Reporting** through optimized database views
- **Cost Analysis** with dynamic unit cost calculation

### 🎯 **Demonstration Workflows**

**🔄 Complete Business Process Flow:**
1. **Supplier Operations** - Receive ingredient batches (triggers lot number generation)
2. **Recipe Management** - Create versioned product formulations  
3. **Production Execution** - Automated batch creation with FEFO consumption
4. **Compliance Monitoring** - Real-time reporting and regulatory checking
5. **Analytics & Insights** - Cost analysis and performance metrics

## 🤝 Contributing

<div align="center">

![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=for-the-badge)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=for-the-badge)
![Issues](https://img.shields.io/badge/issues-welcome-blue.svg?style=for-the-badge)

</div>

### 🚀 **Getting Started with Development**

```bash
# 🍴 1. Fork the repository on GitHub
# 📥 2. Clone your fork locally
git clone https://github.com/YOUR_USERNAME/Food-Manufacturing-Inventory-Management-System.git

# 🌿 3. Create a feature branch
git checkout -b feature/amazing-new-feature

# 💻 4. Make your changes and test thoroughly
# ✅ 5. Commit with descriptive messages
git commit -m 'feat: Add amazing new feature with comprehensive tests'

# 🚀 6. Push to your branch
git push origin feature/amazing-new-feature

# 🔄 7. Open a Pull Request with detailed description
```

### 📋 **Development Guidelines**

**🎯 Code Standards:**
- Follow existing code style and architectural patterns
- Add comprehensive comments for complex business logic
- Implement thorough testing for all database operations
- Maintain backwards compatibility when possible
- Follow security best practices (no hardcoded credentials)

**🗄️ Database Changes:**
- Test schema modifications with representative sample data
- Document new triggers, procedures, and constraints thoroughly  
- Update seed data files when adding new tables or relationships
- Validate foreign key relationships and constraint enforcement

**📝 Documentation:**
- Update README.md for any new features or configuration changes
- Add inline code comments for complex algorithms
- Document API changes and new stored procedure parameters
- Include example usage for new functionality

### 🎯 **Contribution Opportunities**

- **🔧 Feature Enhancements** - Additional reporting views or analytics capabilities
- **🛡️ Security Improvements** - Enhanced authentication or audit logging  
- **📊 Performance Optimization** - Query optimization or indexing strategies
- **🧪 Testing Framework** - Automated testing suite for database procedures
- **📚 Documentation** - Enhanced user guides or API documentation
- **🐛 Bug Fixes** - Issues with existing functionality or edge cases

---

## 📞 Connect & Support

<div align="center">

[![GitHub Profile](https://img.shields.io/badge/GitHub-Follow-black?style=for-the-badge&logo=github)](https://github.com/Rahil312)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?style=for-the-badge&logo=linkedin)](https://www.linkedin.com/in/rahil-shukla-bb8184204/)
[![Email](https://img.shields.io/badge/Email-Contact-red?style=for-the-badge&logo=gmail)](mailto:rshukla7@ncsu.edu)

### 👨‍💻 **Developer Information**

**Rahil Shukla**  
🎓 *Graduate Student in Computer Science*  
🏫 *North Carolina State University*

</div>

### 💬 **Get Help & Support**

<div align="center">

| 📋 **Type** | 🔗 **Resource** | 📝 **Description** |
|:---:|:---:|:---|
| 🐛 **Bug Reports** | [Create an Issue](https://github.com/Rahil312/Food-Manufacturing-Inventory-Management-System/issues) | Found a bug? Let us know! |
| 💡 **Feature Requests** | [Start a Discussion](https://github.com/Rahil312/Food-Manufacturing-Inventory-Management-System/discussions) | Ideas for improvements |
| 📚 **Documentation** | [Check Wiki](https://github.com/Rahil312/Food-Manufacturing-Inventory-Management-System/wiki) | Comprehensive guides |
| ❓ **Questions** | [Review Documentation](./README.md) | Complete project guide |

</div>

### 📧 **Direct Contact**
- **🏫 Academic Email:** [rshukla7@ncsu.edu](mailto:rshukla7@ncsu.edu)
- **💼 Professional Email:** [rahilshukla3122@gmail.com](mailto:rahilshukla3122@gmail.com)
- **⏰ Response Time:** Within 24-48 hours for technical inquiries
- **🎯 Best for:** Project discussions, collaboration opportunities, technical questions

### 🤝 **Collaboration Opportunities**
- **💼 Industry Professionals** - Real-world database implementation discussions
- **🎓 Academic Researchers** - Advanced DBMS concepts and optimizations  
- **👨‍💻 Fellow Developers** - Code review and architectural improvements
- **🏢 Employers** - Technical skills demonstration and project walkthroughs

---

## 📄 License

<div align="center">

[![MIT License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![Open Source](https://img.shields.io/badge/Open%20Source-💚-brightgreen?style=for-the-badge)](https://github.com/Rahil312/Food-Manufacturing-Inventory-Management-System)

</div>

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

## ⭐ **Show Your Support**

**If this project impressed you or helped with your learning:**

[![GitHub stars](https://img.shields.io/github/stars/Rahil312/Food-Manufacturing-Inventory-Management-System?style=social)](https://github.com/Rahil312/Food-Manufacturing-Inventory-Management-System/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/Rahil312/Food-Manufacturing-Inventory-Management-System?style=social)](https://github.com/Rahil312/Food-Manufacturing-Inventory-Management-System/network/members)
[![GitHub watchers](https://img.shields.io/github/watchers/Rahil312/Food-Manufacturing-Inventory-Management-System?style=social)](https://github.com/Rahil312/Food-Manufacturing-Inventory-Management-System/watchers)

**🌟 Star the repository** • **🍴 Fork for your projects** • **👀 Watch for updates** • **🐛 Report issues** • **💡 Suggest improvements**

*Your support helps demonstrate the real-world impact of database projects!*

---

**🏭 Building the Future of Food Manufacturing Through Database Excellence 🗄️**

*Crafted with ❤️ for advanced DBMS education and real-world applications*

### 🎯 **Technical Achievements Demonstrated:**

**🗄️ Database Design Excellence:**
- **Relational Database Design** principles with proper normalization
- **Transaction Management** and ACID properties implementation  
- **Stored Procedures** and trigger programming for business logic
- **Multi-user Role-based** access control with secure authentication

**⚡ Advanced Implementation:**
- **Business Logic Implementation** at the database layer for performance
- **Application Development** with seamless database integration
- **Real-time Inventory Monitoring** with consumption tracking
- **Regulatory Compliance System** with automated validation

**📊 Production-Ready Features:**
- **Cost Analysis** with unit-level breakdown and profitability tracking
- **Health Risk Detection** for expired inventory and safety compliance
- **Do-not-combine Rules** enforcement during product batch creation
- **Product Incompatibility Analysis** for regulatory adherence

![Visitors](https://api.visitorbadge.io/api/visitors?path=Rahil312%2FFood-Manufacturing-Inventory-Management-System&label=Visitors&countColor=%23263759)

</div>