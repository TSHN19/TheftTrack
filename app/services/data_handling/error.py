"""
===========================================================================================================
Program Title: Exception Handler
Programmers: Tashiana Mae C. Bandong
Date Written: November 05, 2024
Date Revised: November 16, 2024

Where the program fits in the system:
    This function is part of the error handling module in the Theft Prediction application.
    It standardizes exception handling across the application.

Purpose:
    This function handles exceptions by capturing error details and returning a structured JSON response
    with the error message, traceback, and timestamp.

Data Structures:
    - Dictionary: Used to structure the error response with message, traceback, and timestamp.
    - String: Stores the exception message and traceback.
    - Datetime: Captures the timestamp when the error occurred.

Algorithms:
    - Exception Handling: Catches exceptions and generates error details.
    - JSON Response: Constructs a structured response for the error.

Control:
    Handles errors by capturing details and returning them in a JSON response with:
    - A status indicating an error.
    - An optional context message for location details.
    - The error message, traceback, and timestamp for debugging.

===========================================================================================================
"""

import traceback
from datetime import datetime
from flask import jsonify

def handle_exception(exception, context = None):
    """
    Description:
    Handle exceptions in a standardized way across the application.

    Parameters:
    exception (Exception): The exception that was raised.
    context (str): Optional string providing context for where the error occurred.

    Returns:
    dict: A structured error response containing error details.
    """
    
    # Capture the full traceback for debugging purposes
    error_message = str(exception)
    error_traceback = traceback.format_exc()
    error_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Prepare the structured error response for the user
    error_response = {
        "status": "error",
        "message": context,
        "details": {
            "time": error_time,
            "error_message": error_message,
            "traceback": error_traceback
        }
    }

    return jsonify(error_response)

