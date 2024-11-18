"""
===========================================================================================================
Program Title: Webpage Routes Module
Programmers: Tashiana Mae C. Bandong
Date Written: October 11, 2024 
Date Revised: November 15, 2024

Where the program fits in the general system design:
    This module defines the Flask routes responsible for processing user requests and interacting with the 
    application's services. It manages data retrieval, data processing, and displays performance metrics 
    and comparisons for different NCFS models, as well as uploading and processing CSV input files.

Routes:
    - `/`: Displays the main landing page of the application.
    - `/theft_values`: Retrieves the theft values based on a selected date and period.
    - `/factors`: Retrieves the factors and their contributions.
    - `/perfmetrics`: Retrieves the performance metrics for NCFS 1 to 4.
    - `/comparison`: Retrieves the comparison between the actual and forecasted values for NCFS 1 to 4.
    - `/process_input`: Processes a CSV file uploaded by the user.

Purpose:
    Handles user interactions by providing data retrieval functionalities, displaying performance metrics, 
    and allowing CSV file uploads for further processing.
    
Data Structures:
    - Flask Blueprint for modular routing.
    - Form data received from POST requests.
    - CSV data processed using Python's CSV module and `StringIO` for file handling.
    
Algorithms: 
    - SQL queries or service layer functions (e.g., `get_theft_values`, `get_factor_contributions`) are used to 
      fetch and return relevant data for display and processing.
    - CSV data is parsed and processed for user inputs.
    
Control: 
    - Flask routing mechanism using decorators to map URLs to specific handler functions.
    - POST methods for data submission (e.g., `/theft_values`, `/process_input`).
    - GET methods for data retrieval and display (e.g., `/factors`, `/perfmetrics`).
    
===========================================================================================================
"""

import csv
from io import StringIO
from flask import Blueprint, render_template, request
from app.services.data_handling.processor import process_user_csv
from app.services.data_handling.retrieval import get_theft_values, get_factor_contributions, get_tool_evaluation, get_tool_comparison

# Initialize the blueprint for app routes
app_route = Blueprint('main', __name__)

# Route for the landing page
@app_route.route('/')
def index():
    return render_template('index.html')

# Initialize the blueprint for data retrieval routes
retrieve_data = Blueprint("retrieve_data", __name__)

# Route to get the performance metrics of NCFS 1 to 4
@retrieve_data.route('/theft_values', methods=['POST'])
def retrieve_theft_values():
    selected_date = request.form.get('date')
    selected_period = request.form.get('period')
    return get_theft_values(selected_date, selected_period)

# Route to get the factors and its contributions
@retrieve_data.route('/factors')
def retrieve_factors():
    return get_factor_contributions()

# Route to get the performance metrics of NCFS 1 to 4
@retrieve_data.route('/perfmetrics')
def retrieve_perfmetrics():
    return get_tool_evaluation()

# Route to get the actual and forecasted values of NCFS 1 to 4
@retrieve_data.route('/comparison')
def retrieve_comparison():
    return get_tool_comparison()

# Route to process a CSV file uploaded by the user
@retrieve_data.route('/process_input', methods=['POST'])
def upload_data():
    file = request.files['file']
    content = file.read().decode('utf-8')
    csv_data = csv.DictReader(StringIO(content))
    return process_user_csv(csv_data)