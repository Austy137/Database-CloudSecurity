import pyodbc
import bcrypt

# Database connection details
server = 'DESKTOP-57GUPRV\\SQLEXPRESS'  # Replace with your server name
database = 'myapp_db'  # Replace with your database name
driver = '{ODBC Driver 17 for SQL Server}'

# Establish database connection
conn = pyodbc.connect(
    f'DRIVER={driver};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
)
cursor = conn.cursor()

# Function to create the Users table
def create_users_table():
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Users' AND xtype='U')
        CREATE TABLE Users (
            UserID INT PRIMARY KEY IDENTITY(1,1),
            Username NVARCHAR(50) UNIQUE NOT NULL,
            PasswordHash NVARCHAR(100) NOT NULL
        )
    """)
    conn.commit()

# Function to create the Customers table
def create_customers_table():
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Customers' AND xtype='U')
        CREATE TABLE Customers (
            CustomerID INT PRIMARY KEY IDENTITY(1,1),
            CustomerName NVARCHAR(50) NOT NULL,
            ContactName NVARCHAR(50) NOT NULL,
            Country NVARCHAR(50) NOT NULL
        )
    """)
    conn.commit()

# Function to create the Transactions table
def create_transactions_table():
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Transactions' AND xtype='U')
        CREATE TABLE Transactions (
            TransactionID INT PRIMARY KEY IDENTITY(1,1),
            CustomerID INT,
            TransactionDate DATE,
            Amount DECIMAL(10, 2),
            FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID)
        )
    """)
    conn.commit()

# Function to register a new user
def register_user(username, password):
    # Hash the password
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    try:
        cursor.execute("INSERT INTO Users (Username, PasswordHash) VALUES (?, ?)", (username, password_hash.decode('utf-8')))
        conn.commit()
        print("User registered successfully.")
    except pyodbc.IntegrityError:
        print("Username already exists.")

# Function to login a user
def login_user(username, password):
    cursor.execute("SELECT PasswordHash FROM Users WHERE Username = ?", (username,))
    result = cursor.fetchone()
    if result:
        stored_password_hash = result[0].encode('utf-8')
        if bcrypt.checkpw(password.encode('utf-8'), stored_password_hash):
            print("Login successful.")
            return True
        else:
            print("Incorrect password.")
            return False
    else:
        print("Username not found.")
        return False

# Function to display the post-login menu
def post_login_menu():
    while True:
        print("\nPost-login Menu:")
        print("1. View Customers")
        print("2. Add Customer")
        print("3. Update Customer")
        print("4. Delete Customer")
        print("5. Generate User Report")
        print("6. Generate Transaction Report")
        print("7. Logout")
        choice = input("Choose an option: ").strip()
        
        if choice == '1':
            view_customers()
        elif choice == '2':
            add_customer()
        elif choice == '3':
            update_customer()
        elif choice == '4':
            delete_customer()
        elif choice == '5':
            generate_user_report()
        elif choice == '6':
            generate_transaction_report()
        elif choice == '7':
            print("Logging out...")
            break
        else:
            print("Invalid choice. Please try again.")

# Function to view customers (example functionality)
def view_customers():
    cursor.execute("SELECT * FROM Customers")
    rows = cursor.fetchall()
    print("\nCustomers:")
    for row in rows:
        print(f"ID: {row.CustomerID}, Name: {row.CustomerName}, Contact: {row.ContactName}, Country: {row.Country}")

# Function to add a customer
def add_customer():
    customer_name = input("Enter customer name: ").strip()
    contact_name = input("Enter contact name: ").strip()
    country = input("Enter country: ").strip()
    cursor.execute("INSERT INTO Customers (CustomerName, ContactName, Country) VALUES (?, ?, ?)", 
                   (customer_name, contact_name, country))
    conn.commit()
    print("Customer added successfully.")

# Function to update a customer
def update_customer():
    customer_id = input("Enter customer ID to update: ").strip()
    cursor.execute("SELECT * FROM Customers WHERE CustomerID = ?", (customer_id,))
    row = cursor.fetchone()
    if row:
        print(f"Current Name: {row.CustomerName}, Contact: {row.ContactName}, Country: {row.Country}")
        customer_name = input("Enter new customer name (leave blank to keep current): ").strip() or row.CustomerName
        contact_name = input("Enter new contact name (leave blank to keep current): ").strip() or row.ContactName
        country = input("Enter new country (leave blank to keep current): ").strip() or row.Country
        cursor.execute("UPDATE Customers SET CustomerName = ?, ContactName = ?, Country = ? WHERE CustomerID = ?",
                       (customer_name, contact_name, country, customer_id))
        conn.commit()
        print("Customer updated successfully.")
    else:
        print("Customer not found.")

# Function to delete a customer
def delete_customer():
    customer_id = input("Enter customer ID to delete: ").strip()
    cursor.execute("SELECT * FROM Customers WHERE CustomerID = ?", (customer_id,))
    row = cursor.fetchone()
    if row:
        cursor.execute("DELETE FROM Customers WHERE CustomerID = ?", (customer_id,))
        conn.commit()
        print("Customer deleted successfully.")
    else:
        print("Customer not found.")

# Function to generate a user report
def generate_user_report():
    cursor.execute("SELECT UserID, Username FROM Users")
    rows = cursor.fetchall()
    print("\nUser Report:")
    for row in rows:
        print(f"UserID: {row.UserID}, Username: {row.Username}")

# Function to generate a transaction report
def generate_transaction_report():
    cursor.execute("""
        SELECT t.TransactionID, t.TransactionDate, t.Amount, c.CustomerName 
        FROM Transactions t 
        JOIN Customers c ON t.CustomerID = c.CustomerID
    """)
    rows = cursor.fetchall()
    print("\nTransaction Report:")
    for row in rows:
        print(f"TransactionID: {row.TransactionID}, Date: {row.TransactionDate}, Amount: {row.Amount}, Customer: {row.CustomerName}")

# Create the Users, Customers, and Transactions tables
create_users_table()
create_customers_table()
create_transactions_table()

# Example usage
while True:
    action = input("Do you want to register or login? (register/login/exit): ").strip().lower()
    if action == "register":
        username = input("Enter username: ").strip()
        password = input("Enter password: ").strip()
        register_user(username, password)
    elif action == "login":
        username = input("Enter username: ").strip()
        password = input("Enter password: ").strip()
        if login_user(username, password):
            post_login_menu()
    elif action == "exit":
        break
    else:
        print("Invalid action. Please enter 'register', 'login', or 'exit'.")

# Close the connection
cursor.close()
conn.close()
