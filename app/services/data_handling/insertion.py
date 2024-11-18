"""
===========================================================================================================
Program Title: Data Insertion
Programmers: Angelica D. Ambrocio and Tashiana Mae C. Bandong
Date Written: October 01, 2024
Date Revised: November 16, 2024

Where the program fits in the general system design:
    This script is part of the backend data processing module in the Theft Prediction application.
    It manages the insertion of data from CSV files, generates and stores performance metrics for NCFS models,
    inserts forecast data based on the best-performing model, and stores feature contributions into the database.

Purpose:
    The purpose of this script is to:
    - Insert data from CSV files into the database to update the necessary tables.
    - Generate and insert performance metrics for different NCFS models, evaluating model accuracy.
    - Identify the best-performing model based on MAPE score, and use it to generate forecasted theft values.
    - Store feature contributions (importance) into the database for analysis.

Data Structures:
    - Lists and Tuples: Used for organizing data rows from CSV files and model outputs.
    - SQLite Database: Used to store processed data, performance metrics, forecasted values, and feature contributions.
    - NCFS Model Outputs: Used for generating and evaluating the predictive models for theft forecasting.

Algorithms:
    - Data Insertion: Handles the insertion of cleaned CSV data into the database tables.
    - NCFS Model Training: Trains NCFS models (with 1 to 4 clusters) and calculates performance metrics such as MAE, RMSE, MAPE, and MAD.
    - Model Evaluation: Identifies the best model based on the lowest MAPE score.
    - Feature Importance Evaluation: Extracts and inserts the contribution of each feature used by the best-performing NCFS model.

Control:
    The script handles the following cases:
    1. **Inserting CSV Data**:
        - Data from a CSV file (e.g., `crime_data.csv`) is inserted into the database after cleaning and preparation.
        
    2. **Inserting Performance Metrics**:
        - For each NCFS model configuration (1 to 4 clusters), performance metrics are calculated and inserted into the `perfmetrics` table.
        
    3. **Inserting NCFS Values**:
        - NCFS model results are inserted into separate tables (e.g., `ncfs1`, `ncfs2`, `ncfs3`, `ncfs4`) based on the number of clusters.
        
    4. **Inserting Forecast Data**:
        - The best model (based on MAPE score) is used to forecast theft data, and the results are inserted into the `bestmodel` table.
        
    5. **Inserting Factor Contributions**:
        - The feature contributions from the best NCFS model are evaluated and inserted into the `factors` table.
        

===========================================================================================================
"""
from .error import handle_exception
from .queries import insert_values_into, select_all_from
from app.services.ncfs_tool import factors_ncfs, train_ncfs_model, train_best_model
from app.services.constants import DatabaseConst as db, ErrorConst as msg

def insert_data_from_csv(data, table):
    """
    Description:
    Inserts data from a CSV file into the specified database table. This function prepares the 
    column names and uses a utility function to perform the insertion.

    Parameters:
    data (list): List of data rows (tuples) to be inserted.
    table (str): Name of the table where the data will be inserted.
    """
    try:
        # Insert data from csv to database
        COLUMNS = ["week_start", "week_end"] + db.THEFT_COLUMNS
        insert_values_into(data, table, COLUMNS)      
              
    except Exception as e:
        return handle_exception(e, context = msg.ERROR_INSERT + table)
    
def insert_perfmetrics(data):
    """
    Description:
    Generates and inserts performance metrics for multiple NCFS models with cluster configurations 
    ranging from 1 to 4. The function uses `train_ncfs_model` to generate metrics, formats them, 
    and inserts them into the `perfmetrics` table.

    Parameters:
    data (str): Data source or table used for training models.
    """    
    try:
        # Generate performance metrics for 1 to 4 clusters and insert to database
        values = [train_ncfs_model(data, clusters) for clusters in range(1, 5)]
        result = [metrics[0] for metrics in values]
        insert_values_into(result, db.PERFMETRICS_TABLE, db.PERFMETRICS_COLUMNS)
        
    except Exception as e:
        return handle_exception(e, context = msg.ERROR_INSERT + db.PERFMETRICS_TABLE)

def insert_ncfs_values(data):
    """
    Description:
    Inserts NCFS model values into tables for each cluster configuration (1 to 4). This function 
    prepares the data for each cluster and inserts formatted results into their respective tables.

    Parameters:
    data (str): Data source or table used for training models.
    """
    # Iterate over each model and table
    for clusters in range(1, 5):
        table = db.NCFS_TABLE + str(clusters)
        try:
            # Train the NCFS modeland retrieve table data
            ncfs_table = train_ncfs_model(data, clusters)
            values = ncfs_table[1]
            result = []

            # Prepare rows for insertion and insert data
            for incrementing_id, row in enumerate(values, start=1):
                week, actual_data, forecasted_data = row
                week = str(week)
                result.append((incrementing_id, week, round(actual_data, 2), round(forecasted_data, 2)))
            insert_values_into(result, table, db.NCFS_COLUMNS)
            
        except Exception as e:
            return handle_exception(e, context = msg.ERROR_INSERT + table)

def insert_forecast(data):
    """
    Description:
    Inserts forecasted values into the `bestmodel` table. The function identifies the best model 
    based on the lowest MAPE from the `perfmetrics` table, trains the best model, and inserts the 
    formatted forecast data into the database.

    Parameters:
    data (str): Data source or table used for training models.
    """
    try:
        # Retrieve all rows from the 'perfmetrics' table
        models = select_all_from(db.PERFMETRICS_TABLE)
        lowest_mape = float('inf')
        selected_factors = None
        
        # Find the best model based on the lowest MAPE
        for index, row in enumerate(models):
            if row['MAPE'] < lowest_mape:
                lowest_mape = row['MAPE']  
                selected_factors = row['selected_factors']

        # Train the best model and retrieve forecast values
        values = train_best_model(data, "2024-09-30", "2024-10-27", selected_factors.split(", "))

        # Prepare rows with formatted forecasted values
        result = [(row['week_start'], row['week_end'], f"{row['forecasted_value']:.2f}") for row in values]

        # Insert forecast data into the database
        insert_values_into(result, db.BESTMODEL_TABLE, db.FORECAST_COLUMNS)
        
    except Exception as e:
        return handle_exception(e, context = msg.ERROR_INSERT + db.PERFMETRICS_TABLE)

def insert_factors(data):
    """
    Description:
    Inserts the contribution of factors into the `factors` table. The function identifies the best 
    NCFS model based on the lowest MAPE, extracts feature contributions, and inserts the data into 
    the database.

    Parameters:
    data (str): Data source or table used for training models.
    """
    try: 
        # Retrieve all rows from the 'perfmetrics' table
        models = select_all_from(db.PERFMETRICS_TABLE)
        lowest_mape = float('inf')
        bestmodel = None
        
        # Find the best model based on the lowest MAPE
        for index, row in enumerate(models):
            if row['MAPE'] < lowest_mape:
                lowest_mape = row['MAPE']  
                bestmodel = row['model']

        # Extract the model number (e.g., 'NCFS 2' -> '2')
        model = bestmodel.split(" ")[1]
        values = []

        # Train the model based on its configuration
        if model == "2":
            values = factors_ncfs(2, data)[0]
        elif model == "3":
            values = factors_ncfs(3, data)[0]
        elif model == "4":
            values = factors_ncfs(4, data)[0]

        # Prepare rows with formatted contribution values
        result = [(row['Feature'], f"{row['Contribution (%)']:.2f}") for row in values]

        # Insert feature contributions data into the database
        insert_values_into(result, db.FACTORS_TABLE, db.FACTOR_COLUMNS)

    except Exception as e:
        return handle_exception(e, context = msg.ERROR_INSERT + db.FACTORS_TABLE)