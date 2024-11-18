"""
===========================================================================================================
Program Title: Database Operations Module
Programmers: Angelica D. Ambrocio
Date Written: October 01, 2024
Date Revised: November 16, 2024

Where the program fits in the general system design:
    This module provides essential database operations for the application, including establishing 
    connections, managing schema creation, and handling data persistence. It ensures the required tables 
    are created and facilitates database interactions throughout the application.

Functions:
    - `get_db_cursor`: Establishes and retrieves a database connection and cursor for executing queries.
    - `close_db`: Closes the database connection at the end of each request.
    - `create_tables`: Sets up the necessary database schema, creating tables if they do not exist.

Purpose:
    Provides a reliable mechanism for connecting to the SQLite database and creating required tables for 
    storing application data such as theft factors, model outputs, performance metrics, and other related 
    data.

Data Structures:
    - SQLite database with the following tables:
        - `theft_factors`: Stores theft factors data.
        - `bestmodel`: Stores the best model's forecasted values.
        - `ncfs1`, `ncfs2`, `ncfs3`, `ncfs4`: Store NCFS model results.
        - `perfmetrics`: Stores performance metrics for various models.
        - `factors`: Stores factors and their contributions for the best model.
        - `input_theft_factors`: Stores user-uploaded theft factors data.

Algorithms:
    - SQL schema creation commands executed via a cursor to define database tables.
    - Database connections managed using Flask's application context `g`.

Control:
    - Database initialization and teardown handled through Flask application lifecycle hooks.
    - Explicit schema creation to ensure consistent database structure.

===========================================================================================================
"""

import sqlite3
from flask import g, current_app

def get_db_cursor():
    """Get a database connection and cursor."""
    if 'db' not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])  # Connect to the database
        g.db.row_factory = sqlite3.Row                          # Configure rows to behave like dictionaries            
    return g.db, g.db.cursor()

def close_db(error):
    """Close the database connection at the end of the request."""
    db = g.pop('db', None)  # Remove the database connection from `g`
    if db is not None:      # Close the connection if it exists
        db.close()

def create_tables():
    """
    Create necessary tables for the application.
    This function sets up the database schema, ensuring tables exist before use.
    """
    db, cursor = get_db_cursor()
    
    # Drop the table if it exists
    cursor.execute('DROP TABLE IF EXISTS theft_factors')

    # Create the table for theft factors data
    cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS theft_factors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        week_start TEXT,
        week_end TEXT,
        week INTEGER,
        month TEXT,
        year INTEGER,
        theft INTEGER,
        population_rate REAL,
        education_rate REAL,
        poverty_rate REAL,
        inflation_rate REAL,
        unemployment_rate REAL,
        gdp REAL,
        cpi REAL
    )
    ''')

    # Create the table for the best model result
    cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS bestmodel (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        week_start TEXT,
        week_end TEXT,
        forecasted_value REAL
    )
    ''')
    
    # Create the table for NCFS 1 values
    cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS ncfs1 (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        actual_value REAL,
        forecasted_value REAL
    )
    ''')
    
    # Create the table for NCFS 2 values
    cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS ncfs2 (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        actual_value REAL,
        forecasted_value REAL
    )
    ''')
    
    # Create the table for NCFS 3 values
    cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS ncfs3 (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        actual_value REAL,
        forecasted_value REAL
    )
    ''')
    
    # Create the table for NCFS 4 values
    cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS ncfs4 (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        actual_value REAL,
        forecasted_value REAL
    )
    ''')

    # Create the table for Performance Metrics of each NCFS tool    
    cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS perfmetrics (
        model TEXT PRIMARY KEY,
        MAE REAL,
        MAPE REAL,
        RMSE REAL,
        MAD REAL,
        actual_value REAL,
        forecasted_value REAL,
        selected_factors TEXT
    )
    ''')

    # Create the table for Factors of the best model  
    cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS factors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        feature REAL,
        contribution REAL
    )
    ''')

    # Create the table for theft factors data
    cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS input_theft_factors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        week_start TEXT,
        week_end TEXT,
        week INTEGER,
        month TEXT,
        year INTEGER,
        theft INTEGER,
        population_rate REAL,
        education_rate REAL,
        poverty_rate REAL,
        inflation_rate REAL,
        unemployment_rate REAL,
        gdp REAL,
        cpi REAL
    )
    ''')

    db.commit()

