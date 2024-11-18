# =====================================================================================================
# Program Title: Socioeconomic Factors Analysis
# Programmers: Samantha Neil Q. Rico and Tashiana Mae Bandong
# Date Written: September 12, 2024
# Date Revised: September 21, 2024
#
# Where the program fits in the general system design: 
# This program is a core component of the analysis of socioeconomic factors related to theft rates. 
# It preprocesses raw data, generates clusters, creates interaction terms, and ranks the importance of different factors using NCFS.
#
# Purpose: 
# The purpose of this program is to analyze the socioeconomic factors influencing theft rates, find interactions among features,
# and identify the most impactful combinations of features to predict theft rates accurately.

# Data structures, algorithms, and control:
# Data Structures:
#    - Pandas DataFrames: Used to hold input data, features, results, and cluster assignments.
#    - NumPy Arrays: Used to hold numerical data for calculations and model inputs.
#    - Python Lists: Used for storing centroids, clusters, interaction terms, and feature combinations.
#
# Algorithms:
#    - Rolling Averages: Used to smooth out fluctuations in theft data.
#    - KMeans Clustering: Used for grouping features to find meaningful relationships.
#    - Interaction Term Generation: Combinations of features to uncover relationships.
#    - NCFS Scores: Used to evaluate feature importance and select the most significant features.
#
# Control:
#    The program follows a structured and sequential workflow.
#    1. Load the data.
#    2. Prepare and preprocess the data.
#    3. Generate clusters using KMeans.
#    4. Create interaction terms from clustered features.
#    5. Calculate NCFS scores to rank feature importance.
#    6. Select the top-ranked features for further analysis.
# =====================================================================================================

import pandas as pd
import numpy as np
from itertools import combinations
from tabulate import tabulate
from .functions import month_mapping
from app.services.constants import ALL_FEATURES, FEATURE_NAMES

def data_preprocessing(raw_data):
    """
    Description:
    Preprocess the raw data for theft analysis, including generating a date index, creating rolling averages, 
    and splitting the data into training and testing sets.
    
    Parameters:
    raw_data (DataFrame): The raw input data containing socioeconomic factors and theft data.
    
    Returns:
    tuple: Processed training features (X_train) and target values (y_train).
    """
    data = month_mapping(raw_data)

    # Create 'date' column from year, month, and week (renamed to day), and set as index for time-based analysis
    data['date'] = pd.to_datetime(data[['year', 'month', 'week']].rename(columns={'week': 'day'}))

    # Set 'date' as the index for easier time-based operations
    data.set_index('date', inplace=True)

    # Create rolling averages for theft rates to smooth out short-term fluctuations
    data['theft_rolling_avg'] = data['theft'].rolling(window=3).mean()

    # Drop NaN values that resulted from the rolling average and datetime conversions
    data.dropna(inplace=True)
    
    # Split data into training (2015-2021) and testing (2022-2023) datasets based on year
    train_data = data[data['year'].isin(range(2015, 2022))]     # Train on data from 2015 to 2021
    test_data = data[data['year'].isin([2023, 2024])]           # Test on data from 2023 and 2024
    
    # Extract features and target variables from training data for model preparation
    X_train = train_data[ALL_FEATURES].dropna().values  # Features for training
    y_train = train_data['theft'].dropna().values  # Target variable (theft rates)

    # Calculate variance for each feature to identify those with no variance
    variances = np.var(X_train, axis=0)
    zero_variance_indices = np.where(variances == 0)[0]  # Find indices of features with zero variance
    result_features = []
    if len(zero_variance_indices) > 0:
        # Remove features with zero variance from the dataset
        print(f"Removing features with zero variance: {zero_variance_indices}")
        X_train = np.delete(X_train, zero_variance_indices, axis=1)

        # Collect the names of the remaining features after zero variance removal
        result_features = [feature for i, feature in enumerate(ALL_FEATURES) if i not in zero_variance_indices]

    return X_train, y_train

def kmeans_clustering(X_train):
    """
    Description:
    Perform KMeans clustering on the training data to group similar data points, with dynamic cluster size determination.
    
    Parameters:
    X_train (ndarray): Training features to be clustered.
    
    Returns:
    tuple: Cluster labels for each sample and the number of clusters.
    """
    def elbow_method(X, max_clusters=10):
        sse = []
        for k in range(1, max_clusters + 1):
            centroids = X[np.random.choice(X.shape[0], k, replace=False)]
            for _ in range(50):  # Iterate to adjust centroids
                clusters = [[] for _ in range(k)]
                for x in X:
                    distances = [np.linalg.norm(x - centroid) for centroid in centroids]
                    cluster_index = np.argmin(distances)
                    clusters[cluster_index].append(x)
                centroids = np.array([np.mean(cluster, axis=0) if len(cluster) > 0 else centroids[i] for i, cluster in enumerate(clusters)])
            sse.append(sum([np.linalg.norm(x - centroids[np.argmin([np.linalg.norm(x - centroid) for centroid in centroids])]) ** 2 for x in X]))
        optimal_k = sse.index(min(sse)) + 1  # Optimal number of clusters with minimum SSE
        return optimal_k

    # Calculate the optimal number of clusters using the elbow method
    n_clusters = elbow_method(X_train)

    # Initialize centroids randomly and perform iterative clustering until convergence
    centroids = X_train[np.random.choice(X_train.shape[0], n_clusters, replace=False)]
    converged = False
    iteration = 0
    max_iterations = 100    # Set maximum number of iterations for convergence

    while not converged and iteration < max_iterations:
        clusters = [[] for _ in range(n_clusters)]
        
        # Assign points to the nearest centroid
        for x in X_train:
            distances = [np.linalg.norm(x - centroid) for centroid in centroids]
            cluster_index = np.argmin(distances)
            clusters[cluster_index].append(x)
        
        # Update centroids based on cluster mean
        new_centroids = []
        for cluster in clusters:
            # Calculate new centroid as mean of points
            if len(cluster) > 0:
                new_centroids.append(np.mean(cluster, axis=0))  

            # Keep old centroid if cluster is empty
            else:
                new_centroids.append(centroids[len(new_centroids)])  
        
        # Check for convergence
        new_centroids = np.array(new_centroids)
        # If centroids do not change significantly, clustering has converged
        if np.allclose(centroids, new_centroids, atol=1e-6):
            converged = True  
        centroids = new_centroids
        iteration += 1

    # Assign each data point to the nearest centroid
    cluster_labels = []
    for x in X_train:
        distances = [np.linalg.norm(x - centroid) for centroid in centroids]
        cluster_labels.append(np.argmin(distances))

    # Create a DataFrame to represent cluster assignments for each sample
    kmeans_table = pd.DataFrame({
        'Sample Index': range(len(X_train)),
        'Cluster': cluster_labels
    })

    print("\nManual KMeans Cluster Assignments:")
    print(tabulate(kmeans_table, headers='keys', tablefmt='fancy_grid'))

    return cluster_labels, n_clusters

def get_interaction_terms(X_train, y_train, n_clusters, cluster_labels, combination_length):
    """
    Description:
    Generate interaction terms from features within each cluster to identify relationships between features.
    
    Parameters:
    X_train (ndarray): Training features.
    y_train (ndarray): Target values (theft rates).
    n_clusters (int): Number of clusters.
    cluster_labels (list): Labels assigned to each sample indicating its cluster.
    combination_length (int): Length of feature combinations to be considered.
    
    Returns:
    list: Interaction terms derived from features within clusters.
    """
    # Create a list to store valid interaction terms and their corresponding combined values
    interaction_terms = []
    interaction_details = []

    for cluster_id in range(n_clusters):
        # Get indices of samples belonging to the current cluster
        cluster_indices = [i for i, label in enumerate(cluster_labels) if label == cluster_id]
        
        if len(cluster_indices) > 0:
            # Retrieve feature names corresponding to the cluster's indices
            cluster_feature_names = [FEATURE_NAMES[i] for i in cluster_indices if i < len(FEATURE_NAMES)]
            
            # Generate all combinations of feature pairs within the cluster
            feature_combinations = list(combinations(cluster_feature_names, combination_length))
            
            for combo in feature_combinations:
                # Find indices of the features in the feature names list
                indices = [FEATURE_NAMES.index(feature) for feature in combo]
                
                # Calculate interaction term by multiplying feature values
                interaction = np.prod(X_train[:, indices], axis=1)
                interaction_variance = np.var(interaction)

                # Apply significance thresholds
                if interaction_variance > 0.01:
                    interaction_corr = np.corrcoef(interaction, y_train)[0, 1] if combination_length == 4 else None
                    
                    # For 4-feature combinations, check correlation threshold
                    if combination_length == 4:
                        if abs(interaction_corr) > 0.2:
                            interaction_terms.append((combo, interaction))
                            interaction_details.append((combo, interaction))
                    else:
                        interaction_terms.append((combo, interaction))
                        interaction_details.append((combo, interaction))

    return interaction_terms

def calculate_ncfs(interaction_terms, y_train, X_train):
    """
    Description:
    Calculate NCFS (Neighborhood Component Feature Selection) scores for each interaction term to evaluate its importance.
    
    Parameters:
    interaction_terms (list): List of feature interactions to be evaluated.
    y_train (ndarray): Target values (theft rates).
    X_train (ndarray): Training features.
    
    Returns:
    list: Sorted NCFS scores indicating the importance of each interaction term.
    """
    def knn_classifier(X, y, n_neighbors=4, distance_weighted=False):
        def predict(x):
            # Calculate distances to all points and find nearest neighbors
            distances = np.linalg.norm(X - x, axis=1)
            neighbor_indices = np.argsort(distances)[:n_neighbors]
            neighbor_votes = y[neighbor_indices]
            if distance_weighted:
                # Weighted prediction based on distances
                weights = 1 / (distances[neighbor_indices] + 1e-5)  # Adding small value to avoid division by zero
                predicted_value = np.round(np.average(neighbor_votes, weights=weights))
            else:
                predicted_value = np.round(np.mean(neighbor_votes))
            return predicted_value
        
        # Calculate accuracy using leave-one-out cross-validation
        correct_predictions = 0
        for i in range(len(X)):
            X_train_subset = np.delete(X, i, axis=0)
            y_train_subset = np.delete(y, i, axis=0)
            y_pred = predict(X[i])
            if y_pred == y[i]:
                correct_predictions += 1
        
        accuracy = correct_predictions / len(X)
        return accuracy

    # Perform k-fold cross-validation and return the mean accuracy
    def cross_validate(data, target):
        accuracies = []
        for fold in range(num_folds):
            start = fold * fold_size
            end = start + fold_size if fold != num_folds - 1 else len(data)

            # Split the data into training and validation sets
            X_val = data[start:end]
            y_val = target[start:end]
            X_train_fold = np.delete(data, slice(start, end), axis=0)
            y_train_fold = np.delete(target, slice(start, end), axis=0)

            # Calculate accuracy using KNN classifier
            accuracy = knn_classifier(X_train_fold, y_train_fold, n_neighbors=4, distance_weighted=True)
            accuracies.append(accuracy)

        return np.mean(accuracies)
    
    ncfs_scores = []
    num_folds = 5  # Number of splits for cross-validation
    fold_size = len(X_train) // num_folds  # Size of each fold

    # Calculate NCFS Score for Interaction Terms: NCFS 2, NCFS 3, NCFS 4
    if interaction_terms is None:
        # Calculate NCFS scores for each feature
        for i, feature_name in enumerate(FEATURE_NAMES):
            feature_data = X_train[:, i].reshape(-1, 1)  # Extract the feature data
            mean_accuracy = cross_validate(feature_data, y_train)
            ncfs_scores.append((feature_name, mean_accuracy))

    # Calculate NCFS Score for NCFS 1    
    else:
        # Calculate NCFS scores for each interaction term
        for clusters, interaction in interaction_terms:
            X_combined = np.column_stack([X_train, interaction])
            mean_accuracy = cross_validate(X_combined, y_train)
            ncfs_scores.append((clusters, mean_accuracy))

    # Sort features or interactions by their NCFS scores in descending order
    sorted_ncfs_scores = sorted(ncfs_scores, key=lambda x: x[1], reverse=True)

    return sorted_ncfs_scores

def get_highest_weighted(N, sorted_ncfs_scores):
    """
    Description:
    Retrieve the top N features based on their NCFS scores.
    
    Parameters:
    N (int): Number of top features to retrieve.
    sorted_ncfs_scores (list): Sorted NCFS scores for features or feature interactions.
    
    Returns:
    tuple: Names and columns of selected features for further model training.
    """
    # Check if NCFS scores were calculated
    if N > 1:
        # Extract the top N features from the highest weighted entry
        highest_weighted_features = sorted_ncfs_scores[0][0][:N]
        selected_features_indices = [FEATURE_NAMES.index(feature) for feature in highest_weighted_features]
        
        # Get the equivalent column names
        selected_columns = [ALL_FEATURES[i] for i in selected_features_indices]

        # Print the selected features for GBDT training
        selected_features_str = ', '.join(highest_weighted_features)
        print(f"\nSelected Features for GBDT Training: {selected_features_str}")
        
        return highest_weighted_features, selected_columns
    else:
        highest_weighted_features = sorted_ncfs_scores[0][0]
        selected_feature_index = FEATURE_NAMES.index(highest_weighted_features)
        selected_columns = ALL_FEATURES[selected_feature_index]

        print(f"\nSelected Features for GBDT Training: {highest_weighted_features}")
        
        return highest_weighted_features, [selected_columns]

def get_contribution(sorted_ncfs_scores, highest_weighted_pair):
    """
    Description:
    Calculate the contribution of each feature to the model based on NCFS scores.
    
    Parameters:
    sorted_ncfs_scores (list): Sorted NCFS scores for feature interactions.
    highest_weighted_pair (list): The top-ranked features selected for further analysis.
    
    Returns:
    list: A list of dictionaries containing feature names and their respective contribution percentages.
    """
    feature_contribution = {}

    # Iterate through sorted NCFS scores to build feature contribution mapping
    for item in sorted_ncfs_scores:
        pair = item[0]
        score = item[1]
        for feature in pair:
            if feature not in feature_contribution:
                feature_contribution[feature] = []
            feature_contribution[feature].append(score)

    # Calculate relative contribution of selected features
    if sorted_ncfs_scores:
        selected_features = highest_weighted_pair
        selected_scores = [feature_contribution[feature] for feature in selected_features]
        avg_scores = [np.mean(scores) for scores in selected_scores]
        total_score = sum(avg_scores)
        contribution_percentages = [(feature, (avg_score / total_score) * 100) for feature, avg_score in zip(selected_features, avg_scores)]

        # Get contribution percentages of each selected feature
        contribution_table = []
        for feature, percentage in contribution_percentages:
            contribution_table.append({
                'Feature': feature,
                'Contribution (%)': percentage
            })

    return contribution_table