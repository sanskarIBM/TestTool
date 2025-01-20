from sklearn.cluster import DBSCAN, SpectralClustering
import pandas as pd
from numpy import unique
from numpy import where
from sklearn.datasets import make_classification
from sklearn.cluster import DBSCAN
from matplotlib import pyplot
from sklearn.preprocessing import StandardScaler

file_path = 'xpathsData.csv'
X = pd.read_csv(file_path)



def clean_xpath(xpath):
    return xpath.strip().strip('"')

X['XPath'] = X['XPath'].apply(clean_xpath)

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

data_features = X['XPath'].apply(extract_features).apply(pd.Series)

# Normalize the features using StandardScaler
scaler = StandardScaler()
data_normalized = scaler.fit_transform(data_features)

model = SpectralClustering(n_clusters=9)
# fit model and predict clusters
yhat = model.fit_predict(data_normalized)
# retrieve unique clusters
clusters = unique(yhat)
# create scatter plot for samples from each cluster
for cluster in clusters:
	# get row indexes for samples with this cluster
	row_ix = where(yhat == cluster)
	# create scatter of these samples
	pyplot.scatter(X[row_ix, 0], X[row_ix, 1])
# show the plot
pyplot.show()
print("Labels:", clusters)