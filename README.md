# Grocery Sales & Inventory Management System

A comprehensive grocery store management system with integrated login, dashboard, and cashier functionality.

## Features

Login System

-   Secure user authentication with email and password
-   Role-based access (Admin/Cashier)
-   Automatic redirection to appropriate interface

Admin Dashboard

-   Real-time statistics (Employees, Suppliers, Products, Sales)
-   Interactive sales graphs (Daily & Cashier performance)
-   Complete CRUD operations for:
    -   Employee Management
    -   Supplier Management
    -   Product Management
    -   Sales & Receipts Viewer

Cashier Interface

-   Product search and selection
-   Shopping cart management
-   Built-in calculator
-   Bill generation and printing
-   Automatic inventory updates
-   Customer receipt management

Installation

Prerequisites

-   Python 3.7 or higher
-   MySQL Server
-   Required Python packages (see requirements.txt)

Database Setup

1.  Create a MySQL database named `grocery`
2.  Create the necessary tables (refer to the table structure in the code)

Running the Application

Option 1: Run from Source

1.  Install dependencies:
    
    ```bash
    pip install -r requirements.txt
    ```
    
2.  Run the application:
    
    ```bash
    python grocery_management_system.py
    ```
    

Option 2: Build as Executable

1.  Install PyInstaller:
    
    ```bash
    pip install pyinstaller
    ```
    
2.  Build the executable:
    
    ```bash
    python build_exe.py
    ```
    
3.  The executable will be created in the `dist` folder

## System Structure

### Main Components

-   **LoginClass**: Handles user authentication and role-based redirection
-   **DashboardClass**: Admin dashboard with statistics and management tools
-   **CashierClass**: Point-of-sale interface for cashiers
-   **EmployeeForm**: Employee management interface
-   **SupplierForm**: Supplier management interface
-   **ProductForm**: Product management interface
-   **SalesForm**: Sales and receipts viewer

### Database Tables

-   **employees**: Employee information and credentials
-   **suppliers**: Supplier details
-   **products**: Product inventory
-   **bills**: Sales receipts (stored as text files)

Usage

For Admin Users

1.  Login with admin credentials
2.  View dashboard statistics
3.  Manage employees, suppliers, and products
4.  View sales reports
5.  Access cashier functionality if needed

For Cashier Users

1.  Login with cashier credentials
2.  Search and select products
3.  Add items to cart
4.  Generate and print receipts
5.  Process payments

Features Breakdown

Employee Management

-   Add, update, archive, and restore employees
-   Search by ID, name, or email
-   Role assignment (Admin/Cashier)
-   Complete employee profile management

Supplier Management

-   Add, update, archive, and restore suppliers
-   Search by invoice number
-   Contact and description management

Product Management

-   Add, update, archive, and restore products
-   Category-based organization
-   Stock management
-   Supplier association
-   Search and filter capabilities

Sales & Reporting

-   Real-time sales tracking
-   Period-based filtering (Daily, Weekly, Monthly, Yearly)
-   Cashier performance analysis
-   Receipt viewing and management

Cashier Operations

-   Product search functionality
-   Shopping cart management
-   Built-in calculator
-   Receipt generation
-   Automatic stock updates
-   Customer information capture

Security Features

-   Role-based access control
-   Secure password authentication
-   Data validation and error handling
-   Archive/restore functionality (soft deletes)

Technical Specifications

Technologies Used

-   **Frontend**: Tkinter (Python GUI)
-   **Backend**: Python
-   **Database**: MySQL
-   **Additional Libraries**:
    -   mysql-connector-python
    -   tkcalendar
    -   PyInstaller (for executable creation)

System Requirements

-   Windows/Linux/macOS
-   Python 3.7+
-   MySQL Server
-   Minimum 4GB RAM
-   500MB disk space

File Structure

```
grocery_management_system.py  # Main application file
requirements.txt             # Python dependencies
build_exe.py                # PyInstaller build script
README.md                   # This file
dist/                       # Built executables (after building)
bills/                      # Sales receipts (created automatically)
```

Support

For issues or questions, please check:

1.  Database connection settings
2.  MySQL server status
3.  Required dependencies installation
4.  User credentials and roles

License

This project is for educational and demonstration purposes.
