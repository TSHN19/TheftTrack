# =====================================================================================================
# Program Title: Feature Selection for Theft Prediction
# Programmers: Samantha Neil Q. Rico and Tashiana Mae Bandong
# Date Written: September 12, 2024
# Date Revised: September 15, 2024
#
# Where the program fits in the general system design:
# This script implements the feature selection process for a predictive model aimed at forecasting theft rates.
# It includes data preprocessing, clustering, interaction term generation, feature ranking, and contribution analysis.
#
# Purpose:
# The purpose of this script is to select the most influential socioeconomic features that affect theft rates by using clustering and ranking techniques like K-means and NCFS.
# The selected features will improve the accuracy of the model in predicting theft rates.
#
# Data structures, algorithms, and control:
# Data Structures:
#    - Pandas DataFrames: Used to manage and manipulate input data and features.
#    - Python Lists: Used to store interaction terms and contribution percentages.
#
# Algorithms:
#    - K-Means Clustering: Used to group features into clusters.
#    - NCFS (Neighborhood Component Feature Selection): Used to evaluate and rank feature importance.
#
# Control:
#    The script follows a structured workflow to select the best features for model training.
#    1. Load the data from the SQLite database.
#    2. Preprocess the data to prepare it for analysis.
#    3. Cluster features and generate interaction terms.
#    4. Rank feature importance using NCFS scores.
#    5. Create and display a contribution table for selected features.
# =====================================================================================================

from tabulate import tabulate
from .functions import load_data_from_db
from .functions_factors import data_preprocessing, kmeans_clustering, get_interaction_terms, calculate_ncfs, get_highest_weighted, get_contribution

def get_factors(combination_length, table):
    """
    Description:
    Implements the feature selection process by analyzing cluster interaction terms and ranking them based on NCFS scores.
    
    Parameters:
    combination_length (int): The number of features to consider in combinations.
    table (str): The name of the table in the SQLite database to load data from.
    
    Returns:
    tuple: Sorted NCFS scores, contribution table, and selected feature columns.
    """
    # Load analysis data from SQLite database into 'data' variable
    raw_data = load_data_from_db(table)

    # Preprocess data with month mapping, rolling averages, feature extraction, and zero-variance filtering
    X_train, y_train = data_preprocessing(raw_data)

    # For Models NCFS 2 to 4, implement interaction terms formed through kmeans clustering
    if combination_length > 1:
        # Perform K-Means clustering on the preprocessed training data
        cluster_labels, n_clusters = kmeans_clustering(X_train)
        
        # Generate interaction terms based on cluster labels and the number of clusters
        interaction_terms = get_interaction_terms(X_train, y_train, n_clusters, cluster_labels, combination_length)
    
        # Compute and rank feature interactions by importance using NCFS scores
        sorted_ncfs_scores = calculate_ncfs(interaction_terms, y_train, X_train)

        # Retrieve the highest weighted feature features and their corresponding selected columns
        highest_weighted_features, selected_columns = get_highest_weighted(combination_length, sorted_ncfs_scores)

        # Create a contribution table that details the contributions of the highest weighted features
        contribution_table = get_contribution(sorted_ncfs_scores, highest_weighted_features)

    # Calculate feature scores directly for NCFS 1
    else:
        # Compute and rank feature interactions by importance using NCFS scores
        contribution_table = ""
        sorted_ncfs_scores = calculate_ncfs(None, y_train, X_train)
    
        # Retrieve the highest weighted feature features and their corresponding selected columns
        highest_weighted_features, selected_columns = get_highest_weighted(combination_length, sorted_ncfs_scores)

    return sorted_ncfs_scores, contribution_table, selected_columns

def factors_ncfs(combination_length, table):
    """
    Description:
    Retrieve and display the top-ranked feature clusters based on the specified combination length.
    
    Parameters:
    combination_length (int): The number of features to consider in combinations.
    table (str): The name of the table in the SQLite database to load data from.
    
    Returns:
    tuple: Contribution table and selected feature columns.
    """
    sorted_ncfs_scores, contribution_table, selected_columns = get_factors(combination_length, table)

    # Display NCFS ranked interaction terms
    print(f"\nRanked Interaction Terms from NCFS {combination_length}:")
    ncfs_table = []
    for item in sorted_ncfs_scores:
        feature = item[0] if combination_length == 1 else ' & '.join(item[0])
        display_item = {'Feature Cluster': feature, 'NCFS Score': item[1]}
        ncfs_table.append(display_item)

    print(tabulate(ncfs_table, headers='keys', tablefmt='fancy_grid'))

    # Display contribution percentages of each selected feature
    print("\nContribution of Selected Features in Theft Prediction:")
    print(tabulate(contribution_table, headers='keys', tablefmt='fancy_grid'))

    return contribution_table, selected_columns