# =====================================================================================================
# Program Title: Model Training
# Programmers: Samantha Neil Q. Rico and Tashiana Mae Bandong
# Date Written: September 22, 2024
# Date Revised: September 25, 2024
#
# Where the program fits in the general system design:
# This program is part of a predictive analytics system aimed at forecasting theft rates in Chicago City using socioeconomic data.
# It involves preprocessing data, generating temporal features, training a model, and predicting future theft rates.
#
# Purpose:
# The purpose of this program is to predict theft rates using various socioeconomic factors by utilizing advanced machine learning techniques, specifically Gradient Boosting Decision Trees (GBDT).
# It helps in identifying trends, generating features, and making accurate predictions to assist law enforcement and policymakers.
#
# Data structures, algorithms, and control:
# Data Structures:
#    - Pandas DataFrames: Used to hold input data, features, and results.
#    - NumPy Arrays: Used for numerical operations and calculations.
#
# Algorithms:
#    - GBDT (Gradient Boosting Decision Trees): Used for prediction of theft rates.
#    - Rolling Averages and Lag Features: Used to capture trends and past dependencies.
#
# Control:
#    The program follows a structured and sequential workflow.
#    1. Load the data.
#    2. Prepare and preprocess the data.
#    3. Generate temporal features, including lag variables and rolling averages.
#    4. Train the GBDT model using training data.
#    5. Make predictions and update lag features iteratively.
#    6. Calculate and display evaluation metrics.
# =====================================================================================================

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error
from .functions import month_mapping, gbdt_model_parameters

def data_preprocessing(raw_data, selected_factors):
    """
    Description:
    Preprocess the raw data for theft prediction by generating date features and splitting the data into training and testing sets.
    
    Parameters:
    raw_data (DataFrame): The raw input data containing socioeconomic factors and theft data.
    selected_factors (list): List of selected socioeconomic factors to include in the model.
    
    Returns:
    tuple: Training features (X_train), training target (y_train), testing features (X_test), testing target (y_test), and processed test data.
    """
    data = month_mapping(raw_data)      # Map month names to numeric values (e.g., 'January' to 1)
    data['day'] = 1                     # Set day to 1 for consistent month start date
    
    # Create a 'date' column from 'year', 'month', 'day' and adjust by 'week' in days.
    data['date'] = pd.to_datetime(data[['year', 'month', 'day']]) + pd.to_timedelta((data['week'] - 1) * 7, unit='d')

    data.set_index('date', inplace=True)            # Set 'date' as the index for time-based operations
    data['week'] = data.index.to_period('W-SUN')    # Extract weekly periods ending on Sundays
    
    # Generate additional temporal features (lagged variables and rolling averages)
    data = generate_temporal_features(data, selected_factors)   

    # Define features and target variable for theft prediction
    feature_columns = [col for col in data.columns if col not in ['week', 'month', 'year', 'theft']]
   
    # Split the data into training and testing sets (2015-2021 for training, 2022-2023 for testing)
    train_data = data[data['year'].isin(range(2015, 2022))]
    train_data = train_data.groupby(['year', 'month', 'week']).agg('mean').reset_index()
    test_data = data[data['year'] == 2023]
    test_data = test_data.groupby(['year', 'month', 'week']).agg('mean').reset_index()

    # Define training and testing features and targets
    X_train = train_data[feature_columns]
    y_train = train_data['theft']
    X_test = test_data[feature_columns]
    y_test = test_data['theft']

    return X_train, y_train, X_test, y_test, test_data

def generate_temporal_features(data, selected_factors):
    """
    Description:
    Generate temporal features, such as lagged variables and rolling averages, to capture trends in socioeconomic factors and theft rates.
    
    Parameters:
    data (DataFrame): The input data containing socioeconomic factors and theft data.
    selected_factors (list): List of selected socioeconomic factors to generate temporal features for.
    
    Returns:
    DataFrame: Data with additional temporal features for model training and prediction.
    """
    for col in selected_factors:
        # Add yearly change feature to capture yearly trends
        data[f'{col}_yearly_change'] = data[col] - data[col].shift(52)
        # Create lag features for 1, 2, and 3 months to capture recent past trends
        for lag in range(1, 4):
            data[f'{col}_lag_{lag}'] = data[col].shift(lag)
        # Add longer-term lag variables to capture seasonal/annual changes
        for lag in [12, 52]:
            data[f'{col}_lag_{lag}'] = data[col].shift(lag)

    # Create lag and differencing features for theft rates to capture trends
    data['theft_diff'] = data['theft'] - data['theft'].shift(1)  # Differencing feature to capture short-term changes

    # Create lag features for theft to capture weekly trends
    for lag in range(1, 5):
        data[f'theft_lag_{lag}'] = data['theft'].shift(lag)

    # Create one interaction term for the selected socioeconomic factors
    if len(selected_factors) != 1:
        interaction_name = '_x_'.join(selected_factors)
        data[interaction_name] = 1

        # Compute the interaction term and add it to the dataframe
        for factor in selected_factors:
            data[interaction_name] *= data[factor]

    # Create rolling averages for socioeconomic factors and theft to capture trends
    for col in selected_factors + ['theft']:
        for window in [4, 8, 12, 24]:  # Different rolling window sizes
            data[f'{col}_rolling_avg_{window}'] = data[col].rolling(window=window).mean()

    # Drop rows with NaN values resulting from lagging and rolling features
    data.dropna(inplace=True)

    return data

def gbdt_predict(data, selected_factors):
    """
    Description:
    Train a GBDT model and predict theft rates for the test data.
    
    Parameters:
    data (tuple): A tuple containing training features (X_train), training target (y_train), testing features (X_test), and testing target (y_test).
    selected_factors (list): List of selected socioeconomic factors used in the model.
    
    Returns:
    tuple: Actual target values (y_test) and predicted target values (y_pred).
    """
    X_train, y_train, X_test, y_test, _ = data
    model = gbdt_model_parameters()     # Initialize the GBDT model with specified parameters
    model.fit(X_train, y_train)         # Train the model using the training data
    y_pred = model.predict(X_test)      # Make predictions for 2023

    # Update lag variables for each week during forecasting (used for recursive predictions)
    for i in range(len(y_pred)):
        if i > 0:
            for col in selected_factors:
                for lag in range(1, 4):
                    X_test.iloc[i, X_test.columns.get_loc(f'{col}_lag_{lag}')] = X_test.iloc[i - 1][col]

    return y_test, y_pred

def calculate_results(y_test, y_pred, test_data):
    """
    Description:
    Calculate and display error metrics to evaluate the model's performance, and display the forecast results.
    
    Parameters:
    y_test (Series): Actual target values for the test data.
    y_pred (ndarray): Predicted target values for the test data.
    test_data (DataFrame): Processed test data containing feature and target values.
    
    Returns:
    tuple: A list of rounded error metrics and a DataFrame of forecast results.
    """
    # Calculate error metrics to evaluate model performance
    mae = mean_absolute_error(y_test, y_pred)  # Mean Absolute Error
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))  # Root Mean Squared Error
    mad = np.mean(np.abs(y_test - np.mean(y_test)))  # Mean Absolute Deviation
    mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100  # Mean Absolute Percentage Error (MAPE)

    # Print evaluation results for theft predictions
    print("\nForecasted Theft Rates for January to December 2023:")
    forecast_results = pd.DataFrame({
        'Week': test_data['week'],
        'Month': test_data['month'],
        'Year': test_data['year'],
        'Actual Data': y_test,
        'Forecasted Data': y_pred,
        'Difference': y_test - y_pred
    })
    print(forecast_results)

    # Print the error metrics for evaluation
    print("\nError Metrics:")
    print(f"Mean Absolute Error (MAE): {mae:.2f}")
    print(f"Root Mean Squared Error (RMSE): {rmse:.2f}")
    print(f"Mean Absolute Deviation (MAD): {mad:.2f}")
    print(f"Mean Absolute Percentage Error (MAPE): {mape:.2f}%")

    # Print average actual and forecasted values for the whole of 2023
    actual_value = y_test.mean()
    forecasted_value = y_pred.mean()
    print(f"\nAverage Actual Theft Rate for 2023: {actual_value:.2f}")
    print(f"Average Forecasted Theft Rate for 2023: {forecasted_value:.2f}")

    return [round(mae, 2), round(mape, 2), round(rmse, 2), round(mad, 2), round(actual_value, 2), f"{forecasted_value:.2f}"], forecast_results