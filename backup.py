import pyodbc
import os
from datetime import datetime

# Database connection details
server = 'DESKTOP-57GUPRV\\SQLEXPRESS'  # Replace with your server name
database = 'myapp_db'  # Replace with your database name
driver = '{ODBC Driver 17 for SQL Server}'
backup_directory = 'C:\\backups'  # Directory where backups will be stored

# Establish database connection with autocommit enabled
try:
    conn = pyodbc.connect(
        f'DRIVER={driver};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
    )
    conn.autocommit = True
    cursor = conn.cursor()
    print("Connection successful")
except Exception as e:
    print(f"Connection failed: {e}")
    exit()

def backup_database():
    # Ensure the backup directory exists
    if not os.path.exists(backup_directory):
        os.makedirs(backup_directory)
    
    # Generate the backup file name
    backup_file = os.path.join(backup_directory, f'{database}_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.bak')
    
    # Backup SQL command
    backup_command = f"BACKUP DATABASE [{database}] TO DISK = '{backup_file}'"
    
    try:
        cursor.execute(backup_command)
        print(f"Database backup successful: {backup_file}")
    except Exception as e:
        print(f"Error during backup: {e}")

# Run the backup manually for testing
backup_database()

# Close the connection
cursor.close()
conn.close()
