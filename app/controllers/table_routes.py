"""
===========================================================================================================
Program Title: Table Routes Module
Programmers: Angelica D. Ambrocio
Date Written: October 01, 2024
Date Revised: November 16, 2024

Where the program fits in the general system design:
    This module defines the Flask routes for viewing different database tables in the application.
    The routes correspond to various sections of the system that interact with data tables,
    displaying them on specific web pages.

Routes:
    - `/theft_factors`: Views the records in the 'theft_factors' table.
    - `/bestmodel`: Views the records in the 'bestmodel' table.
    - `/ncfs1`: Views the records in the 'ncfs1' table.
    - `/ncfs2`: Views the records in the 'ncfs2' table.
    - `/ncfs3`: Views the records in the 'ncfs3' table.
    - `/ncfs4`: Views the records in the 'ncfs4' table.
    - `/factors`: Views the records in the 'factors' table.
    - `/perfmetrics`: Views the records in the 'perfmetrics' table.
    - `/input_data`: Views the records in the 'input_theft_factors' table.

Purpose:
    Provides routes to fetch and display data from database tables in HTML templates.
    
Data Structures:
    - Flask Blueprint for modular routing.
    - Templates for rendering HTML views.
    
Algorithms: 
    - SQL queries using the `select_all_from` function to retrieve data from tables.
    
Control: 
    - Flask routing mechanism using decorators to map URLs to specific handler functions.
    - Each route follows the structure:
        1. Fetches all records from the specified table using the `select_all_from` function.
        2. Renders the appropriate HTML template, passing the fetched data to be displayed.
    
===========================================================================================================
"""

from flask import Blueprint, render_template
from app.services.data_handling.queries import select_all_from
from app.services.constants import DatabaseConst as db

# Initialize the blueprint
table_routes = Blueprint("table_routes", __name__)

# Route to view theft_factors
@table_routes.route('/theft_factors')
def view_theft_factors():
    result = select_all_from(db.THEFT_FACTORS_TABLE)
    return render_template('view_theft_factors.html', title = 'Theft Factors', data = result)

# Route to view bestmodel
@table_routes.route('/bestmodel')
def view_bestmodel():
    result = select_all_from(db.BESTMODEL_TABLE)
    return render_template('view_bestmodel.html', title = 'Best Model', data = result)

# Route to view ncfs1
@table_routes.route('/ncfs1')
def view_ncfs1():
    result = select_all_from(db.NCFS_TABLE + 1)
    return render_template('view_ncfs1.html', title = 'NCFS 1', data = result)

# Route to view ncfs2
@table_routes.route('/ncfs2')
def view_ncfs2():
    result = select_all_from(db.NCFS_TABLE + 2)
    return render_template('view_ncfs2.html', title = 'NCFS 2', data = result)

# Route to view ncfs3
@table_routes.route('/ncfs3')
def view_ncfs3():
    result = select_all_from(db.NCFS_TABLE + 3)
    return render_template('view_ncfs3.html', title = 'NCFS 3', data = result)

# Route to view ncfs4
@table_routes.route('/ncfs4')
def view_ncfs4():
    result = select_all_from(db.NCFS_TABLE + 4)
    return render_template('view_ncfs4.html', title = 'NCFS 4', data = result)

# Route to view factors
@table_routes.route('/factors')
def view_factors():
    result = select_all_from(db.FACTORS_TABLE)
    return render_template('view_factors.html', title = 'Factors', data = result)

# Route to view performance metrics
@table_routes.route('/perfmetrics')
def view_perfmetrics():
    result = select_all_from(db.PERFMETRICS_TABLE)
    return render_template('view_perfmetrics.html', title = 'Performance Metrics', data = result)

# Route to view input theft_factors
@table_routes.route('/input_data')
def view_input_data():
    result = select_all_from(db.INPUT_DATA_TABLE)
    return render_template('view_input_data.html', title = 'Input Theft Factors', data = result)