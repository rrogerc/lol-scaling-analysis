# Best Scaling Champions in League of Legends

This project analyzes champion performance data to determine which champions scale the best throughout a game in League of Legends. The analysis is based on data gathered from various competitive tiers, including Diamond+, Emerald+, and Master+.

## Project Overview

- **Scrape.py**
A script used to scrape and collect champion data from the web. This data serves as the basis for further analysis.

- **Cluster.py**
Contains the clustering algorithm to group champions according to their scaling metrics, helping to identify which champions perform better as the game progresses.

- **Analysis.ipynb**
A Jupyter Notebook that combines data exploration, visualization, and further statistical analysis to interpret champion scaling trends.

- **Data Files**
  - **diamond_plus.json**: Scaling metrics for champions from the Diamond+ tier.
  - **emerald_plus.json**: Scaling metrics for champions from the Emerald+ tier.
  - **master_plus.json**: Scaling metrics for champions from the Master+ tier.

## Prerequisites

- **Python 3.x**
- Required Python packages:
  - pandas
  - numpy
  - matplotlib
  - scikit-learn

