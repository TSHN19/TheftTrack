# =====================================================================================================
# Program Title: Data Extraction and Model Setup for Theft Prediction
# Programmers: Samantha Neil Q. Rico and Tashiana Mae Bandong
# Date Written: October 8, 2024
# Date Revised: October 10, 2024
#
# Where the program fits in the general system design:
# This script is responsible for extracting the socioeconomic data from the SQLite database, mapping the features, and configuring the Gradient Boosting Decision Tree (GBDT) model.
# It provides utility functions to support the overall forecasting system for predicting theft rates using various socioeconomic factors.
#
# Purpose:
# The purpose of this script is to load and preprocess the dataset, provide a mapping for months, and configure the GBDT model to be used in theft rate prediction.
# This script plays a critical role in ensuring that the data is properly structured and that the model parameters are appropriately configured for accurate predictions.
#
# Data structures, algorithms, and control:
# Data Structures:
#    - Pandas DataFrames: Used to hold input data, features, and results.
#    - SQLite Database: Stores the historical socioeconomic and theft data.
#
# Algorithms:
#    - Month Mapping: Used to convert month names into numerical values for easier handling.
#    - GBDT (Gradient Boosting Decision Trees): Configured to predict theft rates based on socioeconomic data.
#
# Control:
#    The script follows a structured workflow to ensure consistency and accuracy.
#    1. Load the data from SQLite database.
#    2. Map month names to numeric values.
#    3. Configure the GBDT model parameters.
# =====================================================================================================

import pandas as pd
import sqlite3
from flask import current_app
from xgboost import XGBRegressor
from app.services.constants import DatabaseConst as db, MONTHS

def load_data_from_db(table):
    """
    Description:
    Load the specified dataset from an SQLite database table.
    
    Parameters:
    table (str): The name of the table in the SQLite database from which to load the data.
    
    Returns:
    DataFrame: The dataset loaded from the specified SQLite table, containing relevant socioeconomic and theft data.
    """
    # Load the specified columns from the SQLite database
    conn = sqlite3.connect(current_app.config['DATABASE'])
    query = f"SELECT {', '.join( db.THEFT_COLUMNS )} FROM {table}"
    data = pd.read_sql(query, conn)
    conn.close()  # Close the database connection
    return data

def month_mapping(data): 
    """
    Description:
    Map month names to their corresponding numerical values and update the 'month' column accordingly.
    
    Parameters:
    data (DataFrame): The input data containing a column with month names.
    
    Returns:
    DataFrame: The input data with the 'month' column mapped to numeric values.
    """
    month_mapping = { name: i for i, name in enumerate ( MONTHS, start = 1 )}
    data['month'] = data['month'].map(month_mapping)  # Map month names to numeric values
    
    return data

def gbdt_model_parameters():
    """
    Description:
    Configure and return the Gradient Boosting Decision Tree (GBDT) model with specific hyperparameters.
    
    Returns:
    XGBRegressor: An XGBoost Regressor model configured for theft rate prediction.
    """
    model = XGBRegressor(
        objective = 'reg:squarederror', 
        random_state = 42,
        n_estimators = 150,
        learning_rate = 0.1,
        max_depth = 3,
        subsample = 0.8,
        colsample_bytree = 1.0,
        alpha = 1,
        reg_lambda = 0
    )
    return model
    