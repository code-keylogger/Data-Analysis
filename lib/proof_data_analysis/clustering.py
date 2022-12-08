import matplotlib.pyplot as plt
import pandas as pd
from sklearn.cluster import KMeans


def plot_kmeans_cluster(df: pd.DataFrame, k=3):
    """Cluster the by session id using kmeans and plot the result. 
    
    .. image:: ../static/kmeans.png
        :alt: kmeans text
    """
    # keep track of values
    group_values = []
    start_char_means = []
    start_line_means = []
    # iterate through sessions
    for _, group in df.groupby(["Session_ID"]):
        # get start char and start line means
        start_char_mean = group["Start_Char"].mean()
        start_line_mean = group["Start_Line"].mean()
        # add to lists
        start_char_means.append(start_char_mean)
        start_line_means.append(start_line_mean)
        # add to group values
        group_values.append((start_char_mean, start_line_mean))

    # cluster the data
    kmeans = KMeans(n_clusters=k, random_state=0).fit(group_values)

    # get colors
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

    # get colors for kmeans labels
    colors = [get_color(val) for val in kmeans.labels_]

    # plot the data
    fig, ax1 = plt.subplots()
    ax1.scatter(start_char_means, start_line_means, color=colors)

    ax1.set_xlabel("Start Char Mean")
    ax1.set_ylabel("Start Line Mean")

    plt.title("K Means Clustering (k={k})".format(k=k))
