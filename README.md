# Enterprise Employee Analytics & Data Warehouse System

An end-to-end employee analytics platform that combines **Python OOP,
synthetic data generation, MySQL OLTP, ETL, dimensional data
warehousing, advanced SQL, SCD Type 2 history, and Streamlit
analytics**.

The system is designed to support both operational HR workflows and
executive-level analytical reporting while preserving historical
employee changes.

------------------------------------------------------------------------

## Table of Contents

-   [Overview](#overview)
-   [Key Objectives](#key-objectives)
-   [Architecture](#architecture)
-   [Technology Stack](#technology-stack)
-   [Project Structure](#project-structure)
-   [Data Pipeline](#data-pipeline)
-   [Data Synthesis](#data-synthesis)
-   [OLTP Database](#oltp-database)
-   [Data Warehouse](#data-warehouse)
-   [SCD Type 2](#scd-type-2)
-   [ETL](#etl)
-   [Advanced SQL](#advanced-sql)
-   [Python Architecture](#python-architecture)
-   [Streamlit Application](#streamlit-application)
-   [Analytics Dashboard](#analytics-dashboard)
-   [Cloud Deployment](#cloud-deployment)
-   [Installation and Setup](#installation-and-setup)
-   [Running the Project](#running-the-project)
-   [Warehouse Refresh](#warehouse-refresh)
-   [Security](#security)
-   [Validation and Error Handling](#validation-and-error-handling)
-   [Performance and Scalability](#performance-and-scalability)
-   [Future Enhancements](#future-enhancements)
-   [License](#license)

------------------------------------------------------------------------

## Overview

The **Enterprise Employee Analytics & Data Warehouse System** provides a
complete data engineering and analytics workflow for employee
performance, project allocation, workforce management, and historical
employee tracking.

The platform separates **transactional workloads** from **analytical
workloads**:

``` text
Synthetic Data
      │
      ▼
Staging Database
      │
      ▼
Normalized OLTP
      │
      │ ETL
      ▼
Star Schema Data Warehouse
      │
      ▼
Streamlit Analytics Application
      │
      ▼
Executive Insights
```

The application supports operational activities such as employee
onboarding, project management, employee assignments, and performance
reviews while using the data warehouse for analytical reporting.

------------------------------------------------------------------------

## Key Objectives

The project focuses on the following capabilities:

-   Generate and process **100,000+ employee records**.
-   Create realistic related datasets for departments, projects,
    assignments, and reviews.
-   Maintain a normalized **OLTP database** for operational
    transactions.
-   Build a **Star Schema data warehouse** for analytics.
-   Use **surrogate keys** for warehouse dimensions.
-   Implement **SCD Type 2** for historical employee changes.
-   Apply advanced SQL techniques including:
    -   CTEs
    -   Window Functions
    -   Stored Procedures
    -   Joins
    -   Aggregations
    -   Ranking
-   Implement modular **Python OOP architecture**.
-   Provide a Streamlit application for operational workflows and
    analytics.
-   Deploy the application to **Streamlit Community Cloud**.
-   Host MySQL databases on **Aiven** with SSL-secured connectivity.

------------------------------------------------------------------------

## Architecture

``` text
                    ┌─────────────────────────┐
                    │   Python Data Generator │
                    │       + Faker           │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │      CSV Data Files      │
                    │ Employees / Projects /  │
                    │ Reviews / History / ... │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │   MySQL Staging Layer   │
                    │    employee_staging     │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │     MySQL OLTP Layer    │
                    │     employee_oltp       │
                    │                         │
                    │ Employees               │
                    │ Departments             │
                    │ Projects                │
                    │ Assignments             │
                    │ Reviews                 │
                    └────────────┬────────────┘
                                 │
                              ETL / SCD2
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │    MySQL OLAP / DW      │
                    │      employee_dw        │
                    │                         │
                    │ Dim_Employee             │
                    │ Dim_Department           │
                    │ Dim_Project              │
                    │ Dim_Date                 │
                    │ Fact_PerformanceReviews  │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │   Streamlit Application │
                    │                         │
                    │ Employee Management     │
                    │ Projects                │
                    │ Performance Reviews     │
                    │ Executive Dashboard     │
                    │ System Information      │
                    └─────────────────────────┘
```

### Cloud Architecture

``` text
Streamlit Community Cloud
          │
          │ SSL / MySQL
          ▼
      Aiven MySQL
          │
     ┌────┴────┐
     ▼         ▼
   OLTP       OLAP
 employee_oltp employee_dw
```

------------------------------------------------------------------------

## Technology Stack

  Layer               Technology
  ------------------- -------------------------------------------
  Programming         Python 3
  Architecture        Object-Oriented Programming
  Data Generation     Faker, pandas
  Database            MySQL 8.x
  Data Warehouse      MySQL Star Schema
  ETL                 Python + SQL
  SQL                 CTEs, Window Functions, Stored Procedures
  Application         Streamlit
  Visualization       Plotly
  Cloud Database      Aiven MySQL
  Cloud Application   Streamlit Community Cloud
  Configuration       python-dotenv
  Version Control     Git / GitHub

------------------------------------------------------------------------

## Project Structure

``` text
enterprise_employee_analytics/
│
├── app.py
├── config.py
├── requirements.txt
├── .env.example
├── .gitignore
├── Makefile
├── setup_windows.bat
│
├── data/
│   ├── README.md
│   └── generated/
│       ├── employees.csv
│       ├── departments.csv
│       ├── projects.csv
│       ├── assignments.csv
│       ├── reviews.csv
│       └── employee_history.csv
│
├── scripts/
│   ├── generate_data.py
│   ├── load_oltp.py
│   ├── run_etl.py
│   └── demo_setup.py
│
├── src/
│   ├── entities.py
│   ├── db_manager.py
│   ├── etl.py
│   └── managers.py
│
├── sql/
│   ├── 01_create_schemas.sql
│   ├── 02_staging_tables.sql
│   ├── 03_oltp_tables.sql
│   ├── 04_olap_tables.sql
│   ├── 05_stored_procedures.sql
│   └── 06_analytics_queries.sql
│
├── tests/
│   └── test_synthesizer.py
│
├── diagrams/
│
└── docs/
```

------------------------------------------------------------------------

## Data Pipeline

The project follows a staged data engineering workflow:

### 1. Generate

Python creates the required synthetic population and related datasets.

### 2. Stage

Generated CSV files are loaded into the MySQL staging database.

### 3. Load OLTP

Data is transformed into normalized operational tables.

### 4. Transform

The ETL layer prepares dimension and fact data for analytical workloads.

### 5. Apply SCD Type 2

Historical employee versions are preserved with validity dates and
current-row indicators.

### 6. Load Warehouse

Data is loaded into the Star Schema.

### 7. Analyze

The Streamlit application queries the warehouse for executive analytics.

------------------------------------------------------------------------

## Data Synthesis

The project is designed to generate **100,000+ employee records**
together with related operational and historical data.

Generated datasets include:

-   Employees
-   Departments
-   Projects
-   Assignments
-   Performance Reviews
-   Employee History

The generated data maintains relationships between entities so that the
resulting dataset can be loaded into the relational database and used
for meaningful warehouse analytics.

Example command:

``` bash
python scripts/generate_data.py --rows 100000
```

The generated files are written under:

``` text
data/generated/
```

------------------------------------------------------------------------

## OLTP Database

The normalized operational database is stored in:

``` text
employee_oltp
```

Core operational entities include:

-   `Employees`
-   `Departments`
-   `Projects`
-   `Assignments`
-   `Reviews`

The OLTP layer is responsible for transactional operations such as:

-   Employee onboarding
-   Department changes
-   Project creation
-   Project assignments
-   Performance review submission

This separation prevents the operational model from becoming tightly
coupled to analytical reporting.

------------------------------------------------------------------------

## Data Warehouse

The analytical database is stored in:

``` text
employee_dw
```

The warehouse follows a **Star Schema**.

### Dimensions

#### Dim_Employee

Contains employee descriptive attributes and historical versions.

Important fields include:

-   `employee_sk`
-   `employee_id`
-   employee attributes
-   `department_sk`
-   role
-   salary
-   `start_date`
-   `end_date`
-   `is_current`

#### Dim_Department

Contains department-level descriptive information.

#### Dim_Project

Contains project-level descriptive information.

#### Dim_Date

Provides date attributes used for time-based analysis.

### Fact

#### Fact_PerformanceReviews

Stores performance review measurements and foreign keys to the warehouse
dimensions.

Measures include:

-   Rating
-   Review score
-   Review count

------------------------------------------------------------------------

## SCD Type 2

Employee history is implemented using **Slowly Changing Dimension Type
2**.

When a tracked employee attribute changes, the existing warehouse
version is not overwritten.

Instead:

``` text
Old Version
    │
    ├── is_current = FALSE
    └── end_date = change date
              │
              ▼
New Version
    │
    ├── new surrogate key
    ├── start_date = change date
    ├── end_date = 9999-12-31
    └── is_current = TRUE
```

This allows historical questions such as:

-   Which department did an employee belong to at a particular point in
    time?
-   Which employee version was valid when a performance review occurred?
-   What changed between historical and current employee records?

The Streamlit application can trigger department changes, and the
warehouse maintains the historical versions.

------------------------------------------------------------------------

## ETL

The primary ETL implementation is provided by:

``` text
src/etl.py
```

The pipeline loads:

-   Dimensions
-   Date dimension
-   Historical employee versions
-   Current employee versions
-   Performance review facts

The fact-loading logic matches reviews to the appropriate employee SCD
Type 2 version based on the review date.

### Full Warehouse Build

``` bash
python scripts/run_etl.py
```

The full ETL workflow can rebuild the warehouse from the generated
source data.

### Non-Destructive Warehouse Refresh

The application also provides a synchronization path that refreshes the
existing warehouse from OLTP without truncating the entire warehouse.

This supports the workflow:

``` text
Streamlit Operation
        │
        ▼
      OLTP
        │
        ▼
Refresh Warehouse
        │
        ▼
      OLAP
        │
        ▼
Dashboard Analytics
```

------------------------------------------------------------------------

## Advanced SQL

The SQL layer demonstrates multiple advanced SQL techniques.

### Common Table Expressions

CTEs are used to structure multi-step analytical and transformation
logic.

### Window Functions

Window functions are used for analytical ranking and transformation
tasks, including patterns based on functions such as:

``` sql
ROW_NUMBER()
DENSE_RANK()
```

### Stored Procedures

Database procedures are included in:

``` text
sql/05_stored_procedures.sql
```

### Analytics Queries

Analytical queries are maintained in:

``` text
sql/06_analytics_queries.sql
```

The analytical layer supports:

-   Performance trends
-   Department performance
-   Top employee analysis
-   Project workload
-   Workforce risk indicators
-   Aggregated review metrics

------------------------------------------------------------------------

## Python Architecture

The Python application follows a modular OOP structure.

### Entities

`src/entities.py`

Defines the core application entities:

-   Employee
-   Project
-   Review

### Database Layer

`src/db_manager.py`

Provides centralized MySQL connection handling.

### Managers / Data Access Layer

`src/managers.py`

Separates application operations from the Streamlit presentation layer.

The manager layer handles operations such as:

-   Employee operations
-   Department changes
-   Project operations
-   Assignments
-   Reviews
-   Analytics queries

### ETL Layer

`src/etl.py`

Encapsulates the warehouse loading and synchronization workflow.

This separation provides clearer responsibilities and makes the
application easier to maintain and test.

------------------------------------------------------------------------

## Streamlit Application

The application is implemented in:

``` text
app.py
```

The application contains the following major areas.

### Dashboard

Provides executive-level analytics from the warehouse.

### Employee Management

Supports:

-   Employee onboarding
-   Employee listing
-   Employee validation
-   Department changes
-   SCD Type 2-triggering department updates

### Projects

Supports:

-   Project creation
-   Employee project assignment
-   Assignment role management

### Performance Reviews

Supports:

-   Employee review submission
-   Project selection
-   Rating
-   Performance score
-   Review comments

### System Information

Provides application/database-related information.

### Warehouse Refresh

Allows operational changes to be synchronized from OLTP into the
existing warehouse.

------------------------------------------------------------------------

## Analytics Dashboard

The dashboard reads analytical data from the **MySQL Star Schema
warehouse**.

Current analytical views include:

### KPI Metrics

-   Current employees
-   Performance reviews
-   Average performance score
-   Total review score

### Year-over-Year Performance

Shows average performance score by year.

### Department Performance

Compares performance across departments.

### Top Employees

Provides top-performing employee analysis by department.

### Project Workload

Shows review/employee workload by project.

### Attrition Risk Proxy

Provides a transparent analytical risk indicator derived from warehouse
data.

> **Important:** The current attrition feature is a proxy/analytical
> indicator and is **not a trained predictive machine-learning model**.

------------------------------------------------------------------------

## Cloud Deployment

The current deployment architecture uses:

### Application

**Streamlit Community Cloud**

### Database

**Aiven MySQL 8.4**

The cloud database contains the project schemas:

``` text
employee_staging
employee_oltp
employee_dw
```

The application connects to Aiven MySQL using SSL.

Database credentials and sensitive configuration are kept outside the
source code and repository.

------------------------------------------------------------------------

## Installation and Setup

### 1. Clone the Repository

``` bash
git clone <repository-url>
cd enterprise_employee_analytics
```

### 2. Create a Virtual Environment

Windows:

``` bash
python -m venv .venv
.venv\Scripts\activate
```

macOS / Linux:

``` bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

``` bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file from `.env.example`.

Example structure:

``` env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password

STAGING_DB=employee_staging
OLTP_DB=employee_oltp
OLAP_DB=employee_dw

DB_SSL_CA=
DB_SSL_VERIFY_CERT=false
DB_SSL_VERIFY_IDENTITY=false
```

For cloud deployment, use the corresponding Aiven connection values and
configure secrets through the deployment platform.

------------------------------------------------------------------------

## Database Setup

Execute the SQL scripts in the following order:

``` text
01_create_schemas.sql
02_staging_tables.sql
03_oltp_tables.sql
04_olap_tables.sql
05_stored_procedures.sql
06_analytics_queries.sql
```

The schema creation order is important because later tables and
procedures depend on the database structures created earlier.

------------------------------------------------------------------------

## Running the Project

### Generate Data

``` bash
python scripts/generate_data.py --rows 100000
```

### Load OLTP

``` bash
python scripts/load_oltp.py
```

### Run ETL

``` bash
python scripts/run_etl.py
```

### Start Streamlit

``` bash
streamlit run app.py
```

The application will normally be available at:

``` text
http://localhost:8501
```

------------------------------------------------------------------------

## Warehouse Refresh

After performing an operational change through the Streamlit
application, use:

``` text
Dashboard → Refresh Warehouse
```

The application synchronizes operational changes into the warehouse
without requiring a complete warehouse rebuild.

This is useful for workflows such as:

``` text
Onboard Employee
       ↓
OLTP
       ↓
Refresh Warehouse
       ↓
OLAP
       ↓
Dashboard
```

------------------------------------------------------------------------

## Security

Sensitive information must never be committed to GitHub.

The following should remain local or be managed through secure
deployment secrets:

``` text
.env
database passwords
SSL certificates
private credentials
virtual environments
```

The repository should contain configuration templates such as:

``` text
.env.example
```

but not actual credentials.

For Streamlit Cloud deployment, database credentials should be stored
using the application's secrets configuration.

------------------------------------------------------------------------

## Validation and Error Handling

The application includes validation for operational workflows.

Examples include:

-   Employee ID existence checks
-   Age validation
-   Role validation
-   Required-field validation
-   Numeric validation for appropriate fields
-   Transactional error handling
-   User-facing Streamlit error messages

The application also separates business/data-access logic from the
presentation layer, making operational failures easier to handle without
exposing raw database implementation details to users.

------------------------------------------------------------------------

## Performance and Scalability

The project is designed around a separation of workloads:

``` text
OLTP
↓
Transactional operations

OLAP / Data Warehouse
↓
Analytical queries
```

This avoids using the transactional model directly for every analytical
query.

The system also avoids unnecessarily loading the complete 100K+ employee
population into interactive UI controls for operations such as employee
assignments and reviews. Employee IDs can be validated directly against
the database.

For warehouse synchronization, the project includes a non-destructive
refresh path rather than rebuilding the complete warehouse for every
application interaction.

------------------------------------------------------------------------

## Project Workflow

A typical end-to-end workflow is:

``` text
1. Generate synthetic data
          ↓
2. Load staging database
          ↓
3. Load normalized OLTP
          ↓
4. Run ETL
          ↓
5. Build / refresh Star Schema
          ↓
6. Open Streamlit application
          ↓
7. Perform HR operations
          ↓
8. Refresh warehouse
          ↓
9. Analyze updated warehouse data
```

------------------------------------------------------------------------

## Future Enhancements

Potential future improvements include:

-   ML-based employee attrition prediction
-   More advanced workforce forecasting
-   Incremental ETL based on change tracking
-   Additional executive KPIs
-   More interactive dashboard filtering
-   Automated data-quality monitoring
-   Role-based authentication
-   Scheduled warehouse refresh
-   Expanded cloud observability
-   More advanced historical employee analytics

------------------------------------------------------------------------

## License

This project is intended for educational, demonstration, and portfolio
purposes.
