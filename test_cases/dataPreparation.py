import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import pickle

file_path = 'xpathsData.csv'
data = pd.read_csv(file_path)

# Function to clean XPath
def clean_xpath(xpath):
    return xpath.strip().strip('"')

data['XPath'] = data['XPath'].apply(clean_xpath)

def extract_features(xpath):
    features = {
        'has_id': int('id=' in xpath),
        'has_class': int('contains(@class' in xpath),
        'has_name': int('name=' in xpath),
        'has_type': int('type=' in xpath),
        'has_label': int('contains(text()' in xpath),
        'has_combination': int('and' in xpath),
        'has_text': int('contains(text()' in xpath and not xpath.startswith('//label')),
        'is_positional': int(xpath.endswith(']') and xpath[-2].isdigit()),
        'is_hierarchical': int('//' in xpath and '/' in xpath.split('//')[-1]),
    }
    return features

data_features = data['XPath'].apply(extract_features).apply(pd.Series)

# Normalize the features using StandardScaler
scaler = StandardScaler()
data_normalized = scaler.fit_transform(data_features)

# data_normalized.to_csv('updatedDataPreparation.csv', index=False)
# Clustering algorithm - KMeans
n_clusters = 9
kmeans = KMeans(n_clusters=n_clusters, random_state=42)
data['Cluster'] = kmeans.fit_predict(data_normalized)

# Save the clustered data
data.to_csv('new_xpaths_clustered.csv', index=False)

# Save scaler and KMeans model as .pkl files
with open('scaler1.pkl', 'wb') as scaler_file:
    pickle.dump(scaler, scaler_file)

with open('kmeans_model1.pkl', 'wb') as kmeans_file:
    pickle.dump(kmeans, kmeans_file)

# Print cluster counts
print("Cluster counts:")
print(data['Cluster'].value_counts())

# Confirm saved files
print("Scaler and KMeans model saved as scaler.pkl and kmeans_model.pkl respectively.")
