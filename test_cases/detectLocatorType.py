import re
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import pickle


# Function to preprocess and extract features from an XPath
def preprocess_and_extract_features(xpath):
    """
    Extracts features from an XPath string to determine its type.
    """
    features = []

    # Feature: Contains 'id'
    features.append(1 if re.search(r"@id=", xpath) else 0)

    # Feature: Contains 'class'
    features.append(1 if re.search(r"contains\(@class", xpath) else 0)

    # Feature: Contains 'name'
    features.append(1 if re.search(r"@name=", xpath) else 0)

    # Feature: Contains 'type'
    features.append(1 if re.search(r"@type=", xpath) else 0)

    # Feature: Contains 'label'
    features.append(1 if re.search(r"contains\(text\(\),", xpath) else 0)

    # Feature: Combination of attributes (id + class, name + type)
    features.append(1 if re.search(r"@id=.*contains\(@class", xpath) or re.search(r"@name=.*@type", xpath) else 0)

    # Feature: Text-based XPath
    features.append(1 if re.search(r"contains\(text\(", xpath) else 0)

    # Feature: Positional XPath (e.g., [n])
    features.append(1 if re.search(r"\[\d+\]", xpath) else 0)

    # Feature: Parent-child hierarchy
    features.append(1 if re.search(r"/", xpath) and not re.search(r"[@\[\]]", xpath.split("/")[-1]) else 0)

    return np.array(features)


# Function to predict the locator type
def predict_locator_type(xpath, model, scaler, cluster_labels):
    """
    Predicts the type of locator (XPath) using a clustering model.
    """
    # Preprocess and extract features
    features = preprocess_and_extract_features(xpath)
    features_scaled = scaler.transform([features])

    # Predict cluster
    cluster = model.predict(features_scaled)[0]

    # Get the label for the cluster
    return cluster_labels.get(cluster, "Unknown Locator Type")


# Load the trained model and scaler
with open("kmeans_model1.pkl", "rb") as model_file:
    kmeans_model = pickle.load(model_file)

with open("scaler1.pkl", "rb") as scaler_file:
    scaler = pickle.load(scaler_file)

# Define cluster labels (determined through analysis of clustering results)
cluster_labels = {
    4: "ID-based XPath",
    0: "Class-based XPath",
    3: "Name-based XPath",
    7: "Type-based XPath",
    8: "Label-based XPath",
    6: "Combination of attributes (id + class, name + type)",
    1: "Text-based XPath",
    5: "Positional XPath",
    2: "Parent-child hierarchy XPath"
}

# Example XPaths to classify
# example_xpaths = [
#     "//*[@id='username']",
#     "//input[contains(@class, 'username')]",
#     "//button[contains(@class, 'btn-primary')]",
#     "//input[@name='email']",
#     "//div[@type='button']",
#     "//label[contains(text(), 'Username')]//input",
#     "//*[@id='search' and contains(@class, 'form-control')]",
#     "//span[contains(text(), 'Submit')]",
#     "//div[3]",
#     "/html/body/div/div[2]/form/input"
# ]
#
# # Classify each XPath
# for xpath in example_xpaths:
#     locator_type = predict_locator_type(xpath, kmeans_model, scaler, cluster_labels)
#     print(f"XPath: {xpath}\nLocator Type: {locator_type}\n")
