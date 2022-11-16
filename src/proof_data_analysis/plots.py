from collections import Counter

import matplotlib.pyplot as plt
import pandas as pd


def plot_edits_over_time(df: pd.DataFrame) -> None:
    """Plot the number of edits over time"""
    # just plotting time against the index
    plt.plot(times_to_seconds(df["Time"]), list(df.index), "o-")
    # set graph labels
    plt.xlabel("Time (seconds)")
    plt.ylabel("Total Number of Edits")
    plt.title("Edits Over Time")


def plot_letter_count(df: pd.DataFrame) -> None:
    """Plot a bar graph of the number of times each letter was typed"""

    # from https://stackoverflow.com/questions/26520111/how-can-i-convert-special-characters-in-a-string-back-into-escape-sequences
    def raw(string: str, replace: bool = False) -> str:
        """Returns the raw representation of a string. If replace is true, replace a single backslash's repr \\ with \."""
        r = repr(string)[1:-1]  # Strip the quotes from representation
        if replace:
            r = r.replace("\\\\", "\\")
        return r

    # use Counter to count the number of times each letter is typed
    letter_counter = Counter()
    # iterate through each row in the dataframe to count
    # the number of times each letter is typed
    for _, row in df.iterrows():
        # get raw representation of the text, that \n and \t are not escaped
        letter_counter[raw(row["Text_Change"])] += 1

    # deal with special case of space
    empty = letter_counter.pop(" ")
    letter_counter[repr("")] = empty

    # plot the bar graph
    # from https://stackoverflow.com/questions/16010869/plot-a-bar-using-matplotlib-using-a-dictionary
    D = letter_counter

    plt.bar(range(len(D)), list(D.values()), align="center")
    plt.xticks(range(len(D)), list(D.keys()))

    plt.xlabel("Letter")
    plt.ylabel("Count")
    plt.title("Letter Count")


# TODO: refactor/remove this
def plot_jumps(df: pd.DataFrame) -> None:
    """Plot the number of jumps over time"""
    last_char_pos = -1
    last_line_pos = -1
    jumps = []
    for i, row in df.iterrows():
        jumped = False
        if row["Start_Char"] <= last_char_pos:
            if row["Start_Line"] > last_line_pos and row["Start_Char"] != 0:
                jumped = True
        last_char_pos = row["End_Char"]
        last_line_pos = row["End_Line"]
        jumps.append(jumped)

    y_vals = []
    num_jumps = 0
    for jump in jumps:
        if jump:
            num_jumps += 1
        y_vals.append(num_jumps)

    plt.plot(list(df.index), y_vals)

    plt.xlabel("Total Number of Edits")
    plt.ylabel("Number of Jumps")
    plt.title("Jumps Over Time")
