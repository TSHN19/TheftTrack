"""
This module is responsible for registering Flask blueprints in the controllers of the application.
===========================================================================================================

Module: __init__.py (Controllers)

Description:
    - Registers the blueprints for handling different routes in the application.
    - Each blueprint represents a modular section of the app (e.g., app routes, table routes, data retrieval routes).
    - Provides a clean and organized routing system for the application.

Functions:
    - register_blueprints(app): Registers all blueprints with the main app instance.

Modules Imported:
    - app_routes: Contains the routes for the core functionality of the application.
    - table_routes: Contains routes related to database operations.
    - retrive_data: Handles routes for retrieving data from the app.
    
===========================================================================================================
"""

from .app_routes import app_route, retrieve_data
from .table_routes import table_routes

def register_blueprints(app):
    """
    Description:
    Registers the application blueprints with the Flask app.
    The blueprints provide modularization of routes, each dedicated to different functions on the app:
    - `app_route`: Handles main app routes (like rendering the homepage).
    - `table_routes`: Handles routes for displaying database tables.
    - `retrieve_data`: Manages routes for data interactions and user requests.
        
    Parameters:
    app (Flask): The Flask application instance to which the blueprints will be registered.
    """
    
    # Register the main app route blueprint
    app.register_blueprint(app_route)
    
    # Register the table-related routes blueprint with a URL prefix
    app.register_blueprint(table_routes, url_prefix='/table')
    
    # Register the data retrieval routes blueprint with a URL prefix
    app.register_blueprint(retrieve_data, url_prefix='/retrieve')
