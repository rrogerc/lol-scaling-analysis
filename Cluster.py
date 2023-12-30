import json
import pandas as pd
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt


with open('./diamond_plus.json', 'r') as file:
    all_champions_data = json.load(file)

champions_df = pd.DataFrame(all_champions_data)
champions_df = champions_df.T

kmeans = KMeans(n_clusters=20, random_state=0)
clusters = kmeans.fit_predict(champions_df)

champions_df['Cluster'] = clusters



### Plot each cluster one by one

# for i in range(kmeans.n_clusters):
#     cluster_data = champions_df[champions_df['Cluster'] == i]
#     plt.figure(figsize=(10, 6))
#     for index, row in cluster_data.iterrows():
#         plt.plot(row.drop('Cluster'), label=index)
#     plt.title(f'Cluster {i}')
#     plt.legend()
#     plt.show()
# exit(0)



### Plot all clusters in a single figure

import matplotlib.pyplot as plt

n_clusters = kmeans.n_clusters
n_cols = 5
n_rows = n_clusters // n_cols + (n_clusters % n_cols > 0)

fig, axs = plt.subplots(n_rows, n_cols, figsize=(20, n_rows * 4), sharex=True, sharey=True)

axs = axs.ravel()

for i in range(n_clusters):
    cluster_data = champions_df[champions_df['Cluster'] == i]
    for index, row in cluster_data.iterrows():
        axs[i].plot(row[:-1], label=index)  # Exclude the cluster label from the plot
    axs[i].set_title(f'Cluster {i}')
    axs[i].legend()

fig.suptitle('K-means Clustering of Champion Winrate vs Game Length', fontsize=16)
plt.setp(axs[-n_cols:], xlabel='Game Length')
plt.setp(axs[::n_cols], ylabel='Winrate')

plt.tight_layout()
plt.subplots_adjust(top=0.95)  # Adjust the top value as needed to fit the subtitle

plt.show()


