import matplotlib.pyplot as plt
import pandas as pd
from sklearn.cluster import KMeans


def plot_kmeans_cluster(df: pd.DataFrame):
    """Cluster the data"""
    group_values = []
    start_char_means = []
    start_line_means = []
    for i, group in df.groupby(["Session_ID", "Problem_ID"]):
        start_char_mean = group["Start_Char"].mean()
        start_line_mean = group["Start_Line"].mean()
        start_char_means.append(start_char_mean)
        start_line_means.append(start_line_mean)

        group_values.append((start_char_mean, start_line_mean))

    kmeans = KMeans(n_clusters=3, random_state=0).fit(group_values)

    def get_color(val: int) -> str:
        if val == 0:
            return "green"
        elif val == 1:
            return "red"
        elif val == 2:
            return "blue"
        elif val == 3:
            return "orange"
        elif val == 4:
            return "purple"
        elif val == 5:
            return "black"
        else:
            raise "Not enough colors"

    colors = [get_color(val) for val in kmeans.labels_]

    plt.scatter(start_char_means, start_line_means, color=colors)
