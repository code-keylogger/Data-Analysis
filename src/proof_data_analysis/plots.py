from collections import Counter

import matplotlib.pyplot as plt
import pandas as pd


def plot_edits_over_time(df: pd.DataFrame):
    """Plot the number of edits over time"""
    # just plotting time against the index
    plt.plot(df["Time"], list(df.index))
    # set graph labels
    plt.xlabel("Time")
    plt.ylabel("Total Number of Edits")
    plt.title("Edits Over Time")


def plot_letter_count(df: pd.DataFrame) -> None:
    # from https://stackoverflow.com/questions/26520111/how-can-i-convert-special-characters-in-a-string-back-into-escape-sequences
    def raw(string: str, replace: bool = False) -> str:
        """Returns the raw representation of a string. If replace is true, replace a single backslash's repr \\ with \."""
        r = repr(string)[1:-1]  # Strip the quotes from representation
        if replace:
            r = r.replace("\\\\", "\\")
        return r

    letter_counter = Counter()
    for i, row in df.iterrows():
        letter_counter[raw(row["Text_Change"])] += 1

    empty = letter_counter.pop(" ")
    letter_counter[repr("")] = empty

    # from https://stackoverflow.com/questions/16010869/plot-a-bar-using-matplotlib-using-a-dictionary
    D = letter_counter

    p = plt.bar(range(len(D)), list(D.values()), align="center")
    plt.xticks(range(len(D)), list(D.keys()))

    plt.xlabel("Letter")
    plt.ylabel("Count")
    plt.title("Letter Count")
