import pandas as pd
import numpy as np
import pickle

# Load the clustered data and the saved KMeans model
data = pd.read_csv('new_xpaths_clustered.csv')

with open('kmeans_model.pkl', 'rb') as kmeans_file:
    kmeans = pickle.load(kmeans_file)

# Load the scaler to inverse transform centroids
with open('scaler1.pkl', 'rb') as scaler_file:
    scaler = pickle.load(scaler_file)

# Feature list for reference
feature_columns = [
    'has_id', 'has_class', 'has_name', 'has_type',
    'has_label', 'has_combination', 'has_text',
    'is_positional', 'is_hierarchical'
]

# Get cluster centroids in the original scale
centroids = scaler.inverse_transform(kmeans.cluster_centers_)
centroid_df = pd.DataFrame(centroids, columns=feature_columns)

# Corrected cluster labels based on the provided sequence
cluster_labels = {
    4: "ID-based XPath",
    1: "Class-based XPath",
    3: "Name-based XPath",
    7: "Type-based XPath",
    8: "Label-based XPath",
    6: "Combination of attributes (id + class, name + type)",
    0: "Text-based XPath",
    5: "Positional XPath",
    2: "Parent-child hierarchy XPath"
}

# Map labels to clusters
data['Cluster Label'] = data['Cluster'].map(cluster_labels)
# Save the labeled data
data.to_csv('new_xpaths_clustered_labeled.csv', index=False)

# Print cluster labels for reference
print("Cluster labels applied:")
print(data['Cluster'].value_counts())

for i, label in cluster_labels.items():

    print(f"Cluster {i}: {label}")
