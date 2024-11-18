"""
===========================================================================================================
Program Title: Data Retrieval
Programmers: Tashiana Mae C. Bandong
Date Written: October 11, 2024
Date Revised: November 16, 2024

Where the program fits in the general system design:
    This script is part of the backend data retrieval module in the Theft Prediction application.
    It manages the retrieval of theft values based on the selected date and forecast period (e.g., Week, Month, Year).
    The script interacts with the database to query and return necessary information for display or further processing.

Purpose:
    The purpose of this script is to:
    - Retrieve theft values based on the selected date and forecast period.
    - Handle weekly, monthly, and yearly forecasts for the Theft Prediction application.
    - Facilitate database interactions for querying historical theft data.

Data Structures:
    - SQLite Database: Used to store and query historical theft data.
    - Forecast Period Options: Week, Month, and Year as inputs to determine the forecast scope.

Algorithms:
    - Data Retrieval: Retrieves data from the database using SQL queries, based on user-selected date and forecast period.
    - Forecast Handling: Processes the data retrieval for weekly, monthly, and yearly forecasts to cater to different user needs.

Control:
    The script handles the following cases:
    Retrieving Theft Data:
        - Based on user input (`selected_date` and `selected_period`), retrieves the appropriate theft values.
        - Supports weekly, monthly, and yearly data retrieval for different forecasting needs.
===========================================================================================================
"""

from app.models.database import get_db_cursor
from app.services.data_handling.error import handle_exception
from app.services.data_handling.queries import select_all_from
from app.services.constants import ErrorConst as msg, DatabaseConst as db, MONTHS

def get_theft_values(selected_date, selected_period):
    """
    Retrieves theft values based on the selected date and forecast period (Week, Month, Year).
    Handles weekly, monthly, and yearly forecasts.

    Parameters:
    selected_date (str): The selected date in 'YYYY-MM' format.
    selected_period (str): The forecast period (Week, Month, or Year).

    Returns:
    dict: A dictionary containing theft values, week starts, and week ends.
    """
    _, cursor = get_db_cursor()
     
    # For weekly and monthly rendering, process selected date
    if selected_date:
        year, month_number = selected_date.split("-")
        month = MONTHS[int(month_number) - 1]

    # Weekly forecast selected
    if selected_period == "Week":
        data = weekly_forecast(cursor, year, month, month_number, selected_date)
    elif selected_period == "Month":
        data = monthly_forecast(cursor, year)
    else:
        data = yearly_forecast(cursor)
        
    return data

def get_factor_contributions():
    """
    Description:
    Retrieves factor contributions from the database.

    Returns:
    dict: A dictionary with factors and their contributions.
    """
    try:
        # Query factors data and return separate factors and contribution list
        results = select_all_from(db.FACTORS_TABLE)
        return {
            "factors": [row['feature'] for row in results],
            "contributions": [row['contribution'] for row in results]
        }

    except Exception as e:
        # Handle exceptions and return error details
        return handle_exception(e, context = msg.ERROR_GET + db.FACTORS_TABLE)
    
    
def get_tool_evaluation():
    """
    Description:
    Retrieves performance metrics for tool evaluation.

    Returns:
    list: A list of dictionaries containing performance metrics.
    """
    try:
        # Query evaluation data and return resulting list
        results = select_all_from(db.PERFMETRICS_TABLE)
        return [{"mad": row['MAD'], "mae": row['MAE'], "rmse": row['RMSE'], "mape": row['MAPE']} for row in results]
    
    except Exception as e:
        # Handle exceptions and return error details
        return handle_exception(e, context = msg.ERROR_GET + db.PERFMETRICS_TABLE)


def get_tool_comparison():
    """
    Description:
    Retrieves data for tool comparison among NCFS models.

    Returns:
    dict: A dictionary containing actual, forecasted values, and selected factors for each NCFS model.
    """
    try:
        # Query comparison data and return resulting list
        results = select_all_from(db.PERFMETRICS_TABLE)
        
        # Group data for up to four models and return comparison data
        ncfs_metrics = [[] for _ in range(4)]
        for index, row in enumerate(results):
            if index < 4:
                ncfs_metrics[index].extend([row['actual_value'], row['forecasted_value'], row['selected_factors']])
        return { "ncfs1": ncfs_metrics[0], "ncfs2": ncfs_metrics[1], "ncfs3": ncfs_metrics[2], "ncfs4": ncfs_metrics[3] }
    
    except Exception as e:
        # Handle exceptions and return error details
        return handle_exception(e, context = msg.ERROR_GET + db.PERFMETRICS_TABLE)
    
def weekly_forecast(cursor, year, month, month_number, selected_date):
    """
    Description:
    Internal function to retrieve weekly forecast data.

    Parameters:
    cursor: Database cursor object.
    year, month, month_number: Date components for filtering.
    selected_date (str): The selected date in 'YYYY-MM-DD' format.

    Returns:
    dict: A dictionary containing weekly theft values and week ranges.
    """
    # Query for forecasted values
    if year == "2024" and int(month_number) > 9:
        cursor.execute("""
            SELECT forecasted_value, week_start, week_end 
            FROM bestmodel 
            WHERE week_start LIKE ? OR week_end LIKE ?
        """, (f'{selected_date}%', f'{selected_date}%'))
    
    # Query for actual theft data
    else:
        cursor.execute("""
            SELECT theft, week_start, week_end
            FROM theft_factors
            WHERE month LIKE ? AND year LIKE ?
        """, (month, year))

    # Fetch results and separate into lists
    query = cursor.fetchall()
    values = [row[0] for row in query]
    week_starts = [row[1] for row in query]
    week_ends = [row[2] for row in query]

    return { "theft_values": values, "week_starts": week_starts, "week_ends": week_ends }

def monthly_forecast(cursor, year):
    """
    Description:
    Internal function to retrieve monthly forecast data.

    Parameters:
    cursor: Database cursor object.
    year (str): The selected year for filtering.

    Returns:
    dict: A dictionary containing monthly theft values and week ranges.
    """
    # Get actual values based on selected year
    cursor.execute("""
            SELECT theft, week_start, week_end, week
            FROM theft_factors
            WHERE year LIKE ?
        """, (year,))
    query = cursor.fetchall()
    actual_values = [row[0] for row in query]
    actual_starts = [row[1] for row in query]
    actual_ends = [row[2] for row in query]
    week = [row[3] for row in query]

    # Get forecasted values based on selected year
    cursor.execute("""
            SELECT forecasted_value, week_start, week_end
            FROM bestmodel
            WHERE week_end LIKE ?
        """, (f'{year}%',))
    query = cursor.fetchall()
    forecasted_values = [row[0] for row in query]
    forecasted_starts = [row[1] for row in query]
    forecasted_ends = [row[2] for row in query]

    # Combine the result from both queries
    values = actual_values + forecasted_values
    week_starts = actual_starts + forecasted_starts
    week_ends = actual_ends + forecasted_ends

    return { "theft_values": values, "week_starts": week_starts, "week_ends": week_ends, "week": week }

def yearly_forecast(cursor):
    """
    Description:
    Internal function to retrieve yearly forecast data.

    Parameters:
    cursor: Database cursor object.

    Returns:
    dict: A dictionary containing yearly theft values and week ranges.
    """
    # Get actual values
    cursor.execute("SELECT theft, week_start, week_end FROM theft_factors")
    query = cursor.fetchall()
    actual_values = [row[0] for row in query]
    actual_starts = [row[1] for row in query]
    actual_ends = [row[2] for row in query]

    # Get forecasted values
    cursor.execute("SELECT forecasted_value, week_start, week_end FROM bestmodel")
    query = cursor.fetchall()
    forecasted_values = [row[0] for row in query]
    forecasted_starts = [row[1] for row in query]
    forecasted_ends = [row[2] for row in query]

    # Combine the result from both queries
    values = actual_values + forecasted_values
    week_starts = actual_starts + forecasted_starts
    week_ends = actual_ends + forecasted_ends

    return { "theft_values": values[1:], "week_starts": week_starts[1:], "week_ends": week_ends[1:] }
