from collections import Counter
from typing import Tuple

import matplotlib.pyplot as plt
import pandas as pd

from proof_data_analysis.utils import get_num_tests_passed, times_to_seconds

def get_time_events(events, time):
    events = events.cumsum()
    times = []
    true_events = []
    last_in = 0
    for time, num_ins in zip(times_to_seconds(time), events):
        if num_ins > last_in:
            times.append(time)
            true_events.append(num_ins)
            last_in = num_ins

    return true_events, times

def plot_depth(df: pd.DataFrame, four=False) -> None:
    """Plot edit depth over time"""

    fig, ax1 = plt.subplots()

    depth = df["Start_Char"]

    if four:
        depth = depth.apply(lambda x: x // 4)

    ax1.plot(times_to_seconds(df["Time"]), depth, "o-", color="green")

    ax2 = ax1.twinx()
    
    # plotting tests passing
    ax2.plot(
        times_to_seconds(df["Time"]),
        get_num_tests_passed(df["Tests_Passed"]),
        "o-",
        color="red",
    )

    # set graph labels
    ax1.set_xlabel("Time (seconds)")
    ylabel = "Depth of edit"
    if four:
        ylabel += " by indent (4 spaces)"
    ax1.set_ylabel(ylabel)
    ax2.set_ylabel("# of Tests Passing")
    ax1.legend(["Edit"], loc="upper left")
    ax2.legend(["# of Tests Passing"], loc="lower left")

def plot_edits(df: pd.DataFrame, ax1=None, id: str = "") -> Tuple[plt.axes, plt.axes]:
    """Plot the number of edits, as well as tests passing over time"""
    if not ax1:
        fig, ax1 = plt.subplots()

    ax2 = ax1.twinx()
    # plotting the number of insertions

    insertions = df["Event_Type"].apply(lambda x: 1 if x == "insert" or x == "replace" else 0)
    insertions, times = get_time_events(insertions, df["Time"])
    
    ax1.plot(times, insertions, "o-", color="green")

    deletions = df["Event_Type"].apply(lambda x: 1 if x == "delete" or x == "replace" else 0)
    deletions, times = get_time_events(deletions, df["Time"])
    
    ax1.plot(times, deletions, "o-", color="blue")

    # plotting tests passing
    ax2.plot(
        times_to_seconds(df["Time"]),
        get_num_tests_passed(df["Tests_Passed"]),
        "o-",
        color="red",
    )

    # set graph labels
    ax1.set_xlabel("Time (seconds)")
    ax1.set_ylabel("# of Edits")
    ax2.set_ylabel("# of Tests Passing")
    ax1.legend(["Insertions", "Deletions"], loc="upper left")
    ax2.legend(["# of Tests Passing"], loc="lower left")
    title = "Edits Over Time"
    if id:
        title += f" (ID: {id})"
    ax1.set_title(title)

    return ax1, ax2


def plot_problem(df: pd.DataFrame, problem: str = "637690c2e5246059c7ccb834") -> None:
    """Show multiple plots of different completions of the same problem."""
    # group df by problem id
    groupby_problem = df.groupby(["Problem_ID"])
    # get the problem we want
    problem = groupby_problem.get_group(problem)
    # group by user id
    session_groups = problem.groupby(["_id"])
    # plot up to 9 sessions
    fig, axs = plt.subplots(nrows=3, ncols=3, figsize=(20, 20))
    # indices for axs
    locs = [[i, j] for i in range(3) for j in range(3)]
    # iterate through each session
    for i, (title, group) in enumerate(session_groups):
        # get the location in the subplot
        r, c = locs[i]
        # plot the edits
        ax1, ax2 = plot_edits(group, axs[r, c], title)

        # carefully remove some y labels so they don't overlap
        if c != 2:
            ax2.set_ylabel("")

        if c != 0:
            ax1.set_ylabel("")

        # only plot up to 9 sessions
        if i >= 8:
            break


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

    # remove "" which is no text changed
    letter_counter.pop("")

    # deal with special case of space
    empty = letter_counter.pop(" ")
    letter_counter[repr(" ")] = empty

    # plot the bar graph
    # from https://stackoverflow.com/questions/16010869/plot-a-bar-using-matplotlib-using-a-dictionary
    D = letter_counter

    ax, fig = plt.subplots()

    fig.bar(range(len(D)), list(D.values()), align="center")
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
