# =====================================================================================================
# Program Title: Best Model for Theft Prediction
# Programmers: Samantha Neil Q. Rico and Tashiana Mae Bandong
# Date Written: October 2, 2024
# Date Revised: October 6, 2024
#
# Where the program fits in the general system design: 
# This program is a core component of a predictive analytics system for forecasting theft rates using socioeconomic data. 
# It preprocesses raw data, trains predictive models, and generates future forecasts based on given features.
#
# Purpose: 
# The purpose of this program is to predict theft rates using various socioeconomic factors. 
# It leverages temporal features, rolling averages, and a hybrid of decision tree-based models for accurate predictions.
#
# Data structures, algorithms, and control:
# Data Structures:
#    - Pandas DataFrames: Used to hold input data, features, results, and forecasts.
#    - SQLite Database: Used to store raw data and manage data retrieval.
#    - Python Dictionaries: Used to store models for different socioeconomic factors.
#
# Algorithms:
#    - XGBoost: Used for socioeconomic factor and theft prediction.
#    - StandardScaler: Used for feature normalization.
#    - Temporal Feature Generation: Lag variables and rolling averages used to capture temporal dependencies.
#
# Control:
#    The program follows a structured and sequential workflow.
#    1. Load the data.
#    2. Prepare and preprocess the data.
#    3. Train the models, both for socioeconomic factors and theft prediction.
#    4. Set up the test data.
#    5. Generate forecasts week-by-week using the trained models.
#    6. Update lag variables to improve predictions for future weeks.
# =====================================================================================================

import pandas as pd
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor
from .functions import load_data_from_db, month_mapping, gbdt_model_parameters
from .functions_training import generate_temporal_features

def data_preprocessing(raw_data, selected_factors):
    """
    Description:
    Preprocess the raw data to prepare it for model training. Steps include mapping months, generating 
    temporal features (lag variables, rolling averages), and normalizing selected features.
    
    Parameters:
    raw_data (DataFrame): The raw input data containing socioeconomic factors and theft data.
    selected_factors (list): The selected features to be included in the model.
    
    Returns:
    tuple: Processed DataFrame, feature columns, input features (X), and target variable (y).
    """
    data = month_mapping(raw_data)  # Map month values to correct labels

    # Create a datetime column combining year, month, and week (used as day)
    data['date'] = pd.to_datetime(data[['year', 'month', 'week']].rename(columns={'week': 'day'}))
    data.set_index('date', inplace=True)  # Set the date column as the index

    # Generate additional temporal features (lagged variables and rolling averages)
    data = generate_temporal_features(data, selected_factors)   

    # Normalize selected features to prepare them for training
    scaler = StandardScaler()
    for col in selected_factors:
        data[col] = scaler.fit_transform(data[[col]])

    # Define features and target variable for theft prediction
    feature_columns = [col for col in data.columns if col not in ['week', 'month', 'year', 'theft']]
    X = data[feature_columns]   # Input features
    y = data['theft']           # Target variable (theft)

    return data, feature_columns, X, y

def train_models(data, feature_columns, X, selected_factors):
    """
    Description:
    Train individual models for each selected socioeconomic factor and the main theft prediction model.
    
    Parameters:
    data (DataFrame): The processed data containing socioeconomic factors and theft data.
    feature_columns (list): The list of feature columns to be used for training.
    X (DataFrame): Input features for training.
    selected_factors (list): List of socioeconomic factors to be individually modeled.
    
    Returns:
    tuple: Dictionary of trained models for socioeconomic factors and the trained theft prediction model.
    """
    # Train separate models for each socioeconomic factor in selected_factors
    factor_models = {}
    for factor in selected_factors:
        y = data[factor]  # Get the target variable dynamically based on selected factors
        factor_model = XGBRegressor(objective='reg:squarederror', random_state=42)
        factor_model.fit(X, y)  # Train the model
        factor_models[factor] = factor_model  # Store the model
    
    # Initialize the main Gradient Boosting Decision Tree (GBDT) model for theft prediction
    model = gbdt_model_parameters()

    # Train the theft model with training data
    X_train = data[feature_columns]
    y_train = data['theft']
    model.fit(X_train, y_train)

    return factor_models, model

def prepare_test_data(date_start, date_end, data, feature_columns):
    """
    Description:
    Prepare the test data for forecasting, including initializing feature columns for the target period.
    
    Parameters:
    date_start (str): Start date for the forecast period.
    date_end (str): End date for the forecast period.
    data (DataFrame): The data used to extract the last available values for feature initialization.
    feature_columns (list): List of feature columns to be included in the test data.
    
    Returns:
    DataFrame: Test data prepared for forecasting.
    """
    # Prepare empty test data for forecasting October 2024 for socioeconomic factors
    test_data = pd.DataFrame(index=pd.date_range(date_start, date_end, freq='W-MON'))  # Weekly data starting each Monday
    test_data['year'] = 2024
    test_data['month'] = test_data.index.month
    test_data['week'] = test_data.index.isocalendar().week  # Week number for each date

    # Initialize feature columns in the test data using the last available values from 2023
    for col in feature_columns:
        if col in data.columns:
            test_data[col] = data[col].iloc[-1]  # Use the last value from 2023 for initialization
        else:
            test_data[col] = 0  # Set to zero if there's no corresponding value

    return test_data

def get_forecast(test_data, feature_columns, selected_factors, factor_models, model):
    """
    Description:
    Generate weekly forecasts for socioeconomic factors and theft predictions.
    
    Parameters:
    test_data (DataFrame): The test data for the forecasting period.
    feature_columns (list): List of feature columns for forecasting.
    selected_factors (list): List of socioeconomic factors to be forecasted.
    factor_models (dict): Dictionary of trained models for each socioeconomic factor.
    model: The trained theft prediction model.
    
    Returns:
    list: Forecasted results for each week in the test data.
    """
    forecast_results = []       # List to store the forecasted results for each week

    # Iteratively forecast for each week in the test data
    for i in range(len(test_data)):
        # Set the week start and end dates for the forecast
        week_start = test_data.index[i].strftime('%Y-%m-%d')
        week_end = (test_data.index[i] + pd.Timedelta(days=6)).strftime('%Y-%m-%d')

        # Extract the current feature set for prediction
        X_test = test_data.iloc[[i]][feature_columns]

        # Forecast each socioeconomic factor (e.g., education_rate, unemployment_rate, etc.)
        for factor in selected_factors:
            y_factor_pred = factor_models[factor].predict(X_test)  # Predict the factor value
            test_data.at[test_data.index[i], factor] = y_factor_pred  # Update the test data

        # Forecast theft rate using the current socioeconomic factors
        y_pred = model.predict(X_test)[0]

        # Store the forecasted result
        forecast_results.append({
            'month': test_data.index[i].month,
            'year': test_data.index[i].year,
            'forecasted_value': float(y_pred),
            'week_start': week_start,
            'week_end': week_end
        })

        # Update lag features for the next prediction
        if i < len(test_data) - 1:
            test_data.at[test_data.index[i + 1], 'theft_lag_1'] = y_pred  # Update theft lag feature
            for lag in range(2, 5):
                if i + 1 - lag >= 0:
                    test_data.at[test_data.index[i + 1], f'theft_lag_{lag}'] = forecast_results[i + 1 - lag]['forecasted_value']

    return forecast_results

def train_best_model(table, date_start, date_end, selected_factors):
    """
    Description:
    Train the best model using the historical data and generate forecasts for the given date range.
    
    Parameters:
    table (str): The name of the database table to load data from.
    date_start (str): Start date for the forecast period.
    date_end (str): End date for the forecast period.
    selected_factors (list): List of selected socioeconomic factors to be included in the model.
    
    Returns:
    list: Forecasted results for the given date range.
    """
    # Load the data from the database
    raw_data = load_data_from_db(table)

    # Preprocess the data to prepare for model training
    data, feature_columns, X, _ = data_preprocessing(raw_data, selected_factors)

    # Train the models for the selected factors and the main theft prediction model
    factor_models, model = train_models(data, feature_columns, X, selected_factors)

    # Prepare the test data for forecasting based on the given date range
    test_data = prepare_test_data(date_start, date_end, data, feature_columns)

    # Get the forecast results for the given test data
    forecast_results = get_forecast(test_data, feature_columns, selected_factors, factor_models, model)

    return forecast_results