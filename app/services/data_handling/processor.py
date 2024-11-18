"""
===========================================================================================================
Program Title: CSV Data Import and Processing for Theft Forecasting
Programmers: Angelica D. Ambrocio and Tashiana Mae C. Bandong
Date Written: October 01, 2024
Date Revised: November 15, 2024

Where the program fits in the general system design:
    This script is part of the backend data processing pipeline in the Theft Prediction application.
    It handles user-uploaded CSV data and pre-existing data for feature selection, model evaluation, 
    and insertion of forecast data into the database.

Purpose:
    The purpose of this script is to manage the data flow for the Theft Prediction model by:
    - Importing and cleaning user-uploaded CSV data.
    - Updating the database by clearing old data and replacing it with the latest processed data.
    - Applying feature selection and training using NCFS models to determine important predictors for theft rates 
        and returning forecast data and performance metrics to the user when processing their CSV data.

Data Structures:
    - Pandas DataFrames: Used for storing and manipulating user-uploaded data.
    - SQLite Database: Used to store cleaned data, feature selection results, performance metrics, 
        forecast data, and model evaluation results.

Algorithms: 
    - Data Cleaning Techniques: Used to remove invalid or duplicate entries from the dataset.
    - NCFS (Neighborhood Component Feature Selection): Used to evaluate the importance of features 
        for predicting theft rates.
    - Model Training and Evaluation: Involves training the theft prediction model and evaluating 
        its performance with selected features.
        
Control: 
    The script handles two primary cases:
    1. Supplemented CSV Data:
        - The existing data tables are cleared.
        - The data from the CSV (data/crime_data.csv) file is inserted into the database to update the records.
        
    2. User-uploaded CSV Data:
        - The input table is cleared of its previous values.
        - The data is cleaned through the `csv_data_processing()` function.
        - Data is imported into a temporary table in the database.
        - The inserted data are used to train the NCFS-GBDT Models (1 to 4), and return its performance metrics.
        - The selected best model (lowest MAPE score) will be used to train and return forecasted theft values.
        - This process is triggered when the user uploads their own CSV data to be processed via the 
            `process_user_csv` function.

    The `modification.py` script is called during app initialization (via the `create_app()` function in 
    `app/__init__.py`) to ensure that data insertion steps are executed automatically when the Flask app is loaded. 
    It is responsible for the insertion of data into the respective tables such as `crime_data`, `perfmetrics`, 
    `ncfs1`, `ncfs2`, `ncfs3`, `ncfs4`, and `factors`.
       
===========================================================================================================
"""

import os, csv
from flask import current_app
from .error import handle_exception
from .insertion import insert_data_from_csv
from .queries import clear_table_values
from app.services.ncfs_tool import train_ncfs_model, train_best_model
from app.services.constants import DatabaseConst as db, ErrorConst as msg

def import_csv_data():
    """
    Description:
    This function imports and processes the CSV data, clearing old records from the database 
    before inserting new data from a predefined CSV file (crime_data.csv).
    """
    try:
        clear_table_values(db.DB_TABLES)
        
        # Define the path to the CSV file
        csv_file_path = os.path.join(current_app.config["BASEDIR"], 'data', 'crime_data.csv')

        # Open the CSV file for reading
        with open(csv_file_path, newline='') as csvfile:
            # Create a CSV reader object
            reader = csv.DictReader(csvfile)
            
            # Process and insert the data into the database
            data = csv_data_processing(reader)
            insert_data_from_csv(data, db.THEFT_FACTORS_TABLE)
            
    except FileNotFoundError as e:
        # Handle file not found error
        return handle_exception(e, context = msg.ERROR_FNF + e.filename)
    
    except ValueError as e:
        # Handle value errors related to table clearing or data insertion
        return handle_exception(e, context = msg.ERROR_VALUE)
    
    except Exception as e:
        # Catch any other unexpected errors
        return handle_exception(e, context = msg.ERROR_CSV)

def process_user_csv(csv_data):
    """
    Description:
    This function processes user-uploaded CSV data. It clears the existing data from the input table,
    processes and inserts the user data into the database, and then trains the NCFS models for forecasting.
    
    Parameters:
    csv_data (list): The user-uploaded data in CSV format.
    
    Returns:
    dict: A dictionary containing the performance metrics of the models, their contributions, and the forecast results.
    """
    try:
        clear_table_values([db.INPUT_DATA_TABLE])   # Clear old records in the input table
        data = csv_data_processing(csv_data)        # Process and clean the CSV data
        
        # Insert cleaned data into the table
        insert_data_from_csv(data, db.INPUT_DATA_TABLE)
        
        # Train NCFS models and get their performance metrics
        performance_metrics, contribution = train_models_evaluation(db.INPUT_DATA_TABLE)
        
        # Get the forecasted values of the best model
        forecast = best_model_forecast(db.INPUT_DATA_TABLE, performance_metrics)
        
        return {
            "models": performance_metrics,
            "contribution": contribution,
            "forecast_result": forecast
        }
            
    except FileNotFoundError as e:
        # Handle file not found error
        return handle_exception(e, context = msg.ERROR_FNF + e.filename)
    
    except ValueError as e:
        # Handle value errors related to table clearing or data insertion
        return handle_exception(e, context = msg.ERROR_VALUE)
    
    except Exception as e:
        # Catch any other unexpected errors
        return handle_exception(e, context = msg.ERROR_CSV)

def csv_data_processing(csv_data):
    """
    Description:
    This function processes the raw CSV data by cleaning and filling missing values.
    For each row, it ensures that the data is valid and complete, using default values for missing fields.
    
    Parameters:
    csv_data (list): List of rows from the CSV file, each containing a dictionary of values.
    
    Returns:
    list: A list of cleaned data tuples ready to be inserted into the database.
    """
    # Strip whi tespace from headers
    headers = [header.strip() for header in csv_data.fieldnames]
    
    # Initialize an empty list to collect cleaned data
    data = []
    
    # Process CSV data
    for row in csv_data:
        try:
            # Handle missing values: Replace empty strings with default values
            week_start = row[headers[0]].strip() if row[headers[0]] else "2023-01-01"
            week_end = row[headers[1]].strip() if row[headers[1]] else "2023-01-07"
            week = int(row[headers[2]]) if row[headers[2]] else 1
            month = row[headers[3]].strip() if row[headers[3]] else 'January'
            year = int(row[headers[4]]) if row[headers[4]] else 2023
            theft = int(row[headers[5]]) if row[headers[5]] else 0
            population_rate = float(row[headers[6]]) if row[headers[6]] else 0.0
            education_rate = float(row[headers[7]]) if row[headers[7]] else 0.0
            poverty_rate = float(row[headers[8]]) if row[headers[8]] else 0.0
            inflation_rate = float(row[headers[9]]) if row[headers[9]] else 0.0
            unemployment_rate = float(row[headers[10]]) if row[headers[10]] else 0.0
            gdp = float(row[headers[11]]) if row[headers[11]] else 0.0
            cpi = float(row[headers[12]]) if row[headers[12]] else 0.0

            # Append cleaned data to the list
            data.append((week_start, week_end, week, month, year, theft, population_rate, education_rate,
                          poverty_rate, inflation_rate, unemployment_rate, gdp, cpi))


        except Exception as e:
            # Handle any unexpected errors using the same function
            handle_exception(e, context = msg.ERROR_ROWS + row)
            continue

    return data

def train_models_evaluation(table):
    """
    Description:
    This function trains multiple NCFS models with different cluster configurations. It evaluates each model 
    and returns the performance metrics (like MAE, MAPE, RMSE, etc.) and the model's contribution.

    Parameters:
    table (str): The name of the table containing the data to train the models.

    Returns:
    tuple: A tuple containing two elements:
        - performance_metrics (list): A list of dictionaries with performance metrics for each model.
        - contribution (list): A list of contributions for each model.
    """
    # Train each NCFS models and returns evaluation
    values = [train_ncfs_model(table, clusters) for clusters in range(1, 5)]
    model_data = [metrics[0] for metrics in values]
    contribution = [metrics[2] for metrics in values]

    # Convert each model's data array into a dictionary
    performance_metrics = [{
            "tool": model[0],
            "mae": model[1],
            "mape": model[2],   
            "rmse": model[3],
            "mad": model[4],
            "actual_value": model[5],
            "forecasted_value": model[6],
            "selected_factor": model[7]
        }
        for model in model_data
    ]
    
    return performance_metrics, contribution

def best_model_forecast(table, performance_metrics):
    """
    Description:
    This function identifies the best model by selecting the one with the lowest MAPE. It then trains the 
    selected model and generates a forecast based on the model's selected factors.

    Parameters:
    table (str): The name of the table containing the data.
    performance_metrics (list): A list of dictionaries with performance metrics for each trained model.

    Returns:
    list: A list of forecast results generated by the best model.
    """
    # Find the index of the model with the lowest MAPE
    best_model = min(
        range(len(performance_metrics)), 
        key=lambda i: performance_metrics[i]["mape"]
    )

    # Store the selected factor of the model with the lowest MAPE
    bestmodel_factors = performance_metrics[best_model]["selected_factor"]

    # Train the best model and forecast based on the selected factors
    forecast = train_best_model(table, "2024-09-30", "2024-10-27", bestmodel_factors.split(", "))
    
    return forecast
