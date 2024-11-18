# Project Title: TheftTrackCHCG

## Description

TheftTrack is a machine learning-based forecasting tool designed to predict weekly rates of theft in Chicago. By leveraging models such as Neighborhood Component Feature Selection (NCFS) and Gradient Boosting Decision Tree (GBDT), TheftTrack aims to assist authorities and stakeholders in making data-driven decisions to reduce theft incidents. The tool integrates interaction terms derived from k-means clustering for better feature selection and model accuracy.

## Folder Structure Overview

The project is organized as follows:

- **app/**  
  - **controllers/**: Holds route handlers that manage application routes.
    - **\_\_init\_\_.py**: Initializes the controllers package.
    - **app_routes.py**: Manages core application routes such as rendering the homepage.
    - **table_routes.py**: Handles routes and operations related to database tables.
  - **models/**: Contains files related to the database.
    - **database.py**: Defines functions for creating and connecting to the database.
  - **services/**:Provides business logic, including data management and model-related functions.
    - **data_handling/**: Handles tasks related to importing, inserting, and modifying data.
      - **error.py**: Standardizes exception handling and provides detailed JSON error responses.
      - **insertion.py**: Contains functions for inserting data into the database.
      - **processor.py**: Manages data processing tasks.
      - **queries.py**: Contains reusable database query functions.
      - **retrieval.py**: Manages data retrieval tasks for the application.
    - **ncfs_tool/**: Implements model functions and processing logic.
      - **bestmodel.py**: Handles training, evaluation, data preprocessing, and forecast generation for the best model.
      - **functions.py**: Common functions used on feature selection and training.
      - **functions_factors.py**: Contains functions used for feature selection process.
      - **functions_training.py**: Contains functions used for the training process.
      - **ncfsfactors.py**: Processes feature selection on NCFS models with different clusters.
      - **ncfstraining.py**: Contains training logic for NCFS models using the GBDT model.
  - **static/**: Static files such as CSS and JavaScript.
  - **templates/**: HTML templates for rendering views.
  - **\_\_init\_\_.py**: Initializes the app with configurations and setup.

- **data/**: Contains the initial data file(s), such as `crime_data.csv`, for loading into the database.

- **main.py**: The entry point of the application.

## Contributors

- **Samantha Neil Q. Rico**  
  - Role: Lead Developer  
  - Email: your.email@example.com  
  - GitHub: [Rieil](https://github.com/Rieil)

- **Angelica D. Ambrocio**  
  - Role: Full-Stack Developer  
  - Email: angelambrocio7112@gmail.com
  - GitHub: [Angel7112](https://github.com/Angel7112)

- **Tashiana Mae C. Bandong**  
  - Role: Full-Stack Developer
  - Email: tashianamae5193@gmail.com 
  - GitHub: [TSHN19](https://github.com/TSHN19)

- **Alyssa Nicole B. Ramos**  
  - Role: Frontend Developer  
  - Email: balilanicole@gmail.com  
  - GitHub: [alyramos](https://github.com/alyramos)
