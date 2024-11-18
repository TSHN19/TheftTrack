# =====================================================================================================
# Program Title: NCFS-Based Theft Prediction Model Training
# Programmers: Samantha Neil Q. Rico and Tashiana Mae Bandong
# Date Written: September 21, 2024
# Date Revised: September 25, 2024
#
# Where the program fits in the general system design:
# This script is responsible for training Gradient Boosting Decision Tree (GBDT) models using selected socioeconomic features based on Neighborhood Component Feature Selection (NCFS).
# It selects the most impactful features, trains the model, and evaluates its performance for predicting theft rates.
#
# Purpose:
# The purpose of this script is to train GBDT models using selected socioeconomic factors that are identified through NCFS-based feature selection. The trained models are then used to predict theft rates and evaluate the model's performance.
#
# Data structures, algorithms, and control:
# Data Structures:
#    - Pandas DataFrames: Used to hold input data, features, results, and predictions.
#    - NumPy Arrays: Used for handling numerical data and evaluations.
#
# Algorithms:
#    - GBDT (Gradient Boosting Decision Trees): Used for prediction of theft rates based on selected features.
#    - NCFS (Neighborhood Component Feature Selection): Used to identify and select the most important features.
#
# Control:
#    The script follows a structured workflow to select the best features, train a model, and evaluate its performance.
#    1. Load the data from SQLite database.
#    2. Use NCFS to select the most important factors.
#    3. Preprocess the data using selected factors.
#    4. Train the GBDT model using the selected factors.
#    5. Make predictions and evaluate the model's performance.
# =====================================================================================================

import numpy as np
from .ncfsfactors import factors_ncfs
from .functions import load_data_from_db
from .functions_training import data_preprocessing, gbdt_predict, calculate_results

def train_ncfs(table, factors, model):
    """
    Description:
    Train a GBDT model using selected factors from the given SQLite table, and evaluate the model's performance.
    
    Parameters:
    table (str): The name of the table in the SQLite database to load data from.
    factors (tuple): A tuple containing contribution percentages and selected socioeconomic factors.
    model (str): The name of the model being trained (e.g., NCFS 2 Model).
    
    Returns:
    tuple: Performance metrics, NCFS table, and contribution table.
    """
    raw_data = load_data_from_db(table)

    # Unpack tuple into 'contribution' and 'selected_factors' variables
    contribution, selected_factors = factors

    # Preprocess the data
    data = data_preprocessing(raw_data, selected_factors)

    # Make predictions using GBDT model
    y_test, y_pred = gbdt_predict(data, selected_factors)

    # Retrieve test data for evaluation
    test_data = data[-1]
    evaluation, forecast_results = calculate_results(y_test, y_pred, test_data)
    ncfs_table = np.array(forecast_results[['Week', 'Actual Data', 'Forecasted Data']])

    # Compile performance metrics
    performance_metrics = [model] + evaluation + [', '.join(selected_factors)]
    
    return performance_metrics, ncfs_table, contribution

def train_ncfs_model(table, clusters):
    """
    Description:
    Train a GBDT model using selected factors for a given NCFS model.
    
    Parameters:
    table (str): The name of the table in the SQLite database to load data from.
    clusters (int): The number of feature clusters to consider for NCFS.
    
    Returns:
    tuple: Performance metrics, NCFS table, and contribution table.
    """
    factors = factors_ncfs(clusters, table)

    model_name = "NCFS " + str(clusters) + " Model"
    
    # Train the model on the selected factors
    result = train_ncfs(table, factors, model_name)
    
    return result