import json
import pandas as pd
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

# Load the winrate data
with open('/Users/rogerchen/Programming/LOL Data/master_plus.json', 'r') as file:
    all_champions_data = json.load(file)

# Convert the data into a DataFrame for easier manipulation
champions_df = pd.DataFrame(all_champions_data)

# Transpose the DataFrame so that each champion is a row and each column is a time bin
champions_df = champions_df.T

# Perform K-means clustering
kmeans = KMeans(n_clusters=40, random_state=0)  # You can choose the number of clusters
clusters = kmeans.fit_predict(champions_df)

# Add the cluster labels to your DataFrame
champions_df['Cluster'] = clusters




# # Plot each cluster
# for i in range(kmeans.n_clusters):
#     cluster_data = champions_df[champions_df['Cluster'] == i]
#     plt.figure(figsize=(10, 6))
#     for index, row in cluster_data.iterrows():
#         plt.plot(row.drop('Cluster'), label=index)
#     plt.title(f'Cluster {i}')
#     plt.legend()
#     plt.show()

# exit(0)


import matplotlib.pyplot as plt

# Assuming 'kmeans.n_clusters' is the number of clusters you have
n_clusters = kmeans.n_clusters
n_cols = 5  # This can be adjusted as needed
n_rows = n_clusters // n_cols + (n_clusters % n_cols > 0)

# Create a large figure to hold all the subplots
fig, axs = plt.subplots(n_rows, n_cols, figsize=(20, n_rows * 4), sharex=True, sharey=True)

# Flatten the axis array for easy iteration
axs = axs.ravel()

for i in range(n_clusters):
    cluster_data = champions_df[champions_df['Cluster'] == i]
    for index, row in cluster_data.iterrows():
        axs[i].plot(row[:-1], label=index)  # Exclude the cluster label from the plot
    axs[i].set_title(f'Cluster {i}')
    axs[i].legend()

# Set a common title and axis labels
fig.suptitle('K-means Clustering of Champion Winrate vs Game Length (k=20)', fontsize=16)
plt.setp(axs[-n_cols:], xlabel='Game Length Bin')
plt.setp(axs[::n_cols], ylabel='Winrate')

# Adjust layout for title and subplots to not overlap
plt.tight_layout()
plt.subplots_adjust(top=0.95)  # Adjust the top value as needed to fit the suptitle

# Show the plot
plt.show()


