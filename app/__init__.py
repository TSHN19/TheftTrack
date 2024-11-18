"""
===========================================================================================================
Program Title: Application Initialization Module
Programmers: Angelica D. Ambrocio and Tashiana Mae Bandong
Date Written: October 01, 2024
Date Revised: November 15, 2024

Where the program fits in the general system design:
    This module initializes the Flask application, configures the SQLite database, 
    registers application blueprints, and manages database table creation and data insertion. 
    It serves as the entry point for the application setup process.

Purpose:
    The purpose of this module is to set up the Flask application environment, ensuring
    the database and routes are ready for use. Additionally, it initializes the database 
    with necessary data for operations.

Data structures, algorithms, and control:
Data Structures:
   - Flask Application: Represents the web application instance.
   - SQLite Database: Stores application data, including theft factors, performance metrics, and forecasts.

Algorithms:
   - Blueprint Registration: Dynamically registers routes for modular application design.
   - Data Insertion: Automates the import of CSV data and calculated values into the database.

Control:
   1. Configure the application and database.
   2. Register blueprints for route organization.
   3. Set up the database tables if they do not exist.
   4. Insert initial data for application functionality.
   5. Handle errors during data initialization with exception handling.
===========================================================================================================
"""

import os
from flask import Flask
from app.controllers import register_blueprints
from app.models.database import create_tables, close_db
from app.services.data_handling.processor import import_csv_data
from app.services.data_handling.insertion import insert_perfmetrics, insert_ncfs_values, insert_factors, insert_forecast

def create_app():
    app = Flask(__name__)

    # Configure the SQLite database
    app.config["BASEDIR"] = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    app.config["DATABASE"] = os.path.join(app.config["BASEDIR"], 'app.db')

    # Register Blueprints for routes
    register_blueprints(app)

    # Teardown context to close database connection after each request
    app.teardown_appcontext(close_db)

    # Initialize database tables and insert initial data
    with app.app_context():
        table = "theft_factors"

        # Initialize database tables and insert initial data if needed
        create_tables()

        # Insert data from CSV and other sources (error handling recommended)
        try:
            import_csv_data()
            insert_perfmetrics(table)   # Insert performance metrics from training
            insert_ncfs_values(table)   # Insert NCFS values on the table
            insert_factors(table)       # Insert factors and contributions  
            insert_forecast(table)      # Insert Best Model results

        except Exception as e:
            app.logger.error(f"Failed to insert data into the {table} table: {e}")
            raise

    return app