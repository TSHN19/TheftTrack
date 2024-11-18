"""
===========================================================================================================
This file defines constants used throughout the application for maintaining
consistent values and reducing redundancy. These constants include:

- Month names for display purposes.
- Feature names and related constants for processing and analysis.
- Database table names and column definitions for easy reference.
- Error messages for consistent error handling throughout the application.

Last Modified: November 16, 2024
===========================================================================================================
"""
# Month names for display and formatting purposes
MONTHS = [
    "January", "February", "March", "April", "May", "June", 
    "July", "August", "September", "October", "November", "December"
]

# Feature names used for data analysis and reporting
ALL_FEATURES = [
    "population_rate", "education_rate", "poverty_rate", "inflation_rate", 
    "unemployment_rate", "gdp", "cpi"
]

# Feature names for user-friendly display
FEATURE_NAMES = [
    "Population Rate", "Education Rate", "Poverty Rate", 
    "Inflation Rate", "Unemployment Rate", "GDP", "CPI"
]

# List of database table names used in the application
DB_TABLES = [
    "theft_factors", "bestmodel", "ncfs1", "ncfs2", "ncfs3", "ncfs4", 
    "perfmetrics", "factors", "input_theft_factors"
]

# Database and Table Constants
class DatabaseConst:
    THEFT_FACTORS_TABLE = "theft_factors"
    BESTMODEL_TABLE = "bestmodel"
    NCFS_TABLE = "ncfs"
    FACTORS_TABLE = "factors"
    FORECAST_TABLE = "forecast"
    PERFMETRICS_TABLE = "perfmetrics"
    INPUT_DATA_TABLE = "input_theft_factors"
    
    # List of all database tables
    DB_TABLES = [ 
        "theft_factors", "bestmodel", "ncfs1", "ncfs2", "ncfs3", "ncfs4", "perfmetrics", 
        "factors", "input_theft_factors" 
    ]
    
    # Column names for different tables
    THEFT_COLUMNS = [ 
        "week", "month", "year", "theft", "population_rate", "education_rate", "poverty_rate", 
        "inflation_rate", "unemployment_rate", "gdp", "cpi" 
    ]
    PERFMETRICS_COLUMNS = [ 
        "model", "MAE", "MAPE", "RMSE", "MAD", "actual_value", "forecasted_value", "selected_factors" 
    ]
    NCFS_COLUMNS = [ "id", "date", "actual_value", "forecasted_value" ]
    FORECAST_COLUMNS = [ "week_start", "week_end", "forecasted_value" ]
    FACTOR_COLUMNS = [ "feature", "contribution" ]

# Error Messages Constants for consistent error handling across the application
class ErrorConst:
    ERROR_INSERT    = "Error inserting values at table "
    ERROR_FNF       = "File not found: "
    ERROR_VALUE     = "Data insertion or table clearing issue."
    ERROR_CSV       = "Unexpected error during CSV import process."
    ERROR_ROWS      = "Unexpected error processing row: "
    ERROR_SELECT    = "Error selecting all table values from "
    ERROR_DELETE    = "Error clearing tables: "
    ERROR_GET       = "Error retrieving values from: "