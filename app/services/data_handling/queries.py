"""
===========================================================================================================
Program Title: Database Operations - Data Handling
Programmers: Angelica D. Ambrocio and Tashiana Mae C. Bandong
Date Written: October 01, 2024
Date Revised: November 16, 2024

Where the program fits in the general system design:
    This script is part of the backend data handling module in the Theft Prediction application.
    It manages database operations, including selecting, inserting, and clearing data across various tables.
    This ensures that data is correctly inserted and retrieved for model training, evaluation, and forecasting.

Purpose:
    The purpose of this script is to:
    - Fetch all rows from specified database tables.
    - Insert multiple rows of data into the database from various sources (e.g., CSV files, model outputs).
    - Clear all data from specified tables and reset auto-increment sequences to prepare for fresh data.

Data Structures:
    - Lists and Tuples: Used to organize rows of data and parameters passed for database operations.
    - SQLite Database: Used to store and manage the application's data, including model outputs, performance metrics, and feature contributions.
    - Database Cursor: Facilitates the execution of SQL queries to interact with the SQLite database.

Algorithms:
    - Select All from Table: Executes a SQL query to fetch all rows from a specified table.
    - Insert Values into Table: Inserts multiple rows of data into a specified table using parameterized queries to prevent SQL injection.
    - Clear Table Values: Deletes all records from specified tables and resets the auto-increment counter to maintain clean data tables.

Control:
    The script handles the following cases:
    1. Selecting All Data:
        - Fetches all rows from a specified table using a SELECT SQL query.
        
    2. Inserting Data:
        - Inserts data into the specified table using a parameterized SQL INSERT query to prevent SQL injection.
        - The data is inserted in bulk using the `executemany` function for efficiency.
        
    3. Clearing Data:
        - Deletes all records from the specified tables and resets the auto-increment counters to ensure that new data is inserted cleanly.
    
    Error Handling:
    - If an error occurs during database operations, an exception is caught and handled by the `handle_exception` function, which logs the error and returns relevant details.

===========================================================================================================
"""

from app.models.database import get_db_cursor
from app.services.data_handling.error import handle_exception
from app.services.constants import ErrorConst as msg

def select_all_from(table):
    """
    Description:
    Fetches values of selected columns from the specified table.

    Parameters:
    table_name (str): Name of the database table.

    Returns:
    list: List of rows fetched from the table, or error details if an exception occurs.
    """
    _, cursor = get_db_cursor()
    
    try:
        # Execute query to fetch all rows from the table
        cursor.execute(f'SELECT * FROM {table}')
        return cursor.fetchall()
        
    except Exception as e:
        # Handle exceptions and return error details
        return handle_exception(e, context = msg.ERROR_SELECT + table)


def insert_values_into(data, table, columns):
    """
    Description:
    Inserts multiple rows into the specified table.

    Parameters:
    data (list of tuples): Data to be inserted into the table.
    table_name (str): Name of the target database table.
    columns (list of str): List of column names corresponding to the data.

    Returns:
    bool: True if data is inserted successfully, or error details if an exception occurs.
    """
    db, cursor = get_db_cursor()
    
    # Prepare column names and placeholders for the SQL query
    columns_str = ", ".join(columns)
    placeholders = ", ".join(["?" for _ in columns])
    
    try:
        # Check if data is not empty
        if data:
            # Execute the bulk insert operation and commitanscation
            cursor.executemany(f'INSERT INTO {table} ({columns_str}) VALUES ({placeholders})', data)
            db.commit()
        
    except Exception as e:
        # Handle exceptions and return error details
        return handle_exception(e, context = msg.ERROR_INSERT + table)

def clear_table_values(tables):
    """
    Description:
    Clears all data from specified tables and resets auto-increment sequences.

    Parameters:
    tables (list): List of table names to clear.
    """   
    db, cursor = get_db_cursor()
    
    try:
        # Iterate over each table and delete all records, then reset auto-increment sequence
        for table in tables:
            cursor.execute(f'DELETE FROM {table}')
            cursor.execute(f'DELETE FROM sqlite_sequence WHERE name="{table}"')
        db.commit()
        
    except Exception as e:
        # Handle exceptions and return error details
        return handle_exception(e, context = msg.ERROR_DELETE + table)

