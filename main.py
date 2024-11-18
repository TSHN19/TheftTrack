"""
This script is used to run the Flask application by creating an instance of the app using the create_app() factory function.
The app is run in debug mode to facilitate easier development and debugging.
"""

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
