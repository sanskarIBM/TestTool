import pandas as pd
import numpy as np
import pickle

# Load the clustered data and the saved KMeans model
data = pd.read_csv('xpaths_clustered_labeled.csv')

print(data.head(20))