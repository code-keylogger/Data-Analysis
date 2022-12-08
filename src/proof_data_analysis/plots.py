import ast
import tkinter
from collections import Counter
from typing import Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import MaxNLocator

from proof_data_analysis.utils import get_num_tests_passed, times_to_seconds

def _set_tests_passing(ax: plt.Axes, df: pd.DataFrame) -> None:
    """Set the tests passing axis."""
    ax2 = ax.twinx()
    ax2.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax2.plot(
        times_to_seconds(df["Time"]),
        get_num_tests_passed(df["Tests_Passed"]),
        "o-",
        color="red",
    )
    ax2.set_ylabel("# of Tests Passing")
    ax2.legend(["# of Tests Passing"], loc="lower left")

def _apply_text_event(text, event):
    """Interprets the text event and applies it to the location stored in the event onto displayed_text.
    :param event: Text event to apply"""
    # Tkinter text objects determine location with strings in the form "lineNum.charNum"
    # their lines are 1 indexed, so we must increment our line indices
    start_location = str(event["Start_Line"] + 1) + "." + str(event["Start_Char"])
    end_location = str(event["End_Line"] + 1) + "." + str(event["End_Char"])
    text.configure(state="normal")

    # check for deletion
    if event["Text_Change"] == "":
        text.delete(start_location, end_location)
    # check for insertion
    else:
        if start_location != end_location:
            text.delete(start_location, end_location)
        text.insert(start_location, event["Text_Change"])

    text.configure(state="disabled")


def _get_time_events(events, time):
    """Get the number of events at each time stamp."""
    events = events.cumsum()
    times = []
    true_events = []
    last_in = 0
    # get the number of events at each time stamp
    for time, num_ins in zip(times_to_seconds(time), events):
        if num_ins > last_in:
            times.append(time)
            true_events.append(num_ins)
            last_in = num_ins

    return true_events, times


def plot_parsable(df: pd.DataFrame) -> None:
    """Plot edit depth over time.
    
    .. image:: ../static/parsable.png
        :alt: parsable text
    """

    fig, ax1 = plt.subplots()
    
    text = tkinter.Text()
    passing = np.zeros(len(df))
    # check if each text is parsable
    for i, row in df.iterrows():
        _apply_text_event(text, row)
        try:
            ast.parse(text.get("1.0", "end"))
        except:
            passing[i] = 1

    # plot
    ax1.plot(times_to_seconds(df["Time"]), passing, "o-", color="green")
    ax1.yaxis.set_major_locator(MaxNLocator(integer=True))

    ax2 = ax1.twinx()
    ax2.yaxis.set_major_locator(MaxNLocator(integer=True))

    # plotting tests passing
    _set_tests_passing(ax2, df)

    # set graph labels
    ax1.set_xlabel("Time (seconds)")
    ylabel = "Parsable"
    ax1.set_ylabel(ylabel)
    ax1.legend(["Parsable"], loc="upper left")




def plot_depth(df: pd.DataFrame, four=False) -> None:
    """Plot edit depth over time.

    :param four: If true, divide depth by 4 to get the number of indents.
    
    .. image:: ../static/depth.png
        :alt: depth text
    """

    fig, ax1 = plt.subplots()

    depth = df["Start_Char"]

    # divide by 4 to get the number of indents
    if four:
        depth = depth.apply(lambda x: x // 4)

    ax1.plot(times_to_seconds(df["Time"]), depth, "o-", color="green")

    ax2 = ax1.twinx()

    ax1.yaxis.set_major_locator(MaxNLocator(integer=True))

    _set_tests_passing(ax2, df)

    # set graph labels
    ax1.set_xlabel("Time (seconds)")
    ylabel = "Depth of edit (characters)"
    if four:
        ylabel += " by indent (4 spaces)"
    ax1.set_ylabel(ylabel)
    ax1.legend(["Edit"], loc="upper left")
      
    plt.title(ylabel)


def plot_edits(df: pd.DataFrame, ax1=None, id: str = "") -> Tuple[plt.axes, plt.axes]:
    """Plot the number of edits, as well as tests passing over time.
    
    .. image:: ../static/edits.png
        :alt: edits text
    """
    if not ax1:
        fig, ax1 = plt.subplots()

    ax2 = ax1.twinx()
    # plotting the number of insertions

    insertions = df["Event_Type"].apply(
        lambda x: 1 if x == "insert" or x == "replace" else 0
    )
    insertions, times = _get_time_events(insertions, df["Time"])

    ax1.plot(times, insertions, "o-", color="green")

    deletions = df["Event_Type"].apply(
        lambda x: 1 if x == "delete" or x == "replace" else 0
    )
    deletions, times = _get_time_events(deletions, df["Time"])

    ax1.plot(times, deletions, "o-", color="blue")

    _set_tests_passing(ax2, df)

    # set graph labels
    ax1.set_xlabel("Time (seconds)")
    ax1.set_ylabel("# of Edits")
    ax1.legend(["Insertions", "Deletions"], loc="upper left")
    title = "Edits Over Time"
    if id:
        title += f" (ID: {id})"
    ax1.set_title(title)

    return ax1, ax2


def plot_problem(df: pd.DataFrame, problem: str) -> None:
    """Show multiple plots of different completions of the same problem.

    :param problem: Problem ID to plot, e.g. 6377c2b06f4750d88ff2a7b4

    .. image:: ../static/multi_problem.png
        :alt: multi_problem text
    """
    # group df by problem id
    groupby_problem = df.groupby(["Problem_ID"])
    # get the problem we want
    problem = groupby_problem.get_group(problem)
    # group by user id
    session_groups = problem.groupby(["Session_ID"])
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
    """Plot a bar graph of the number of times each letter was typed.
    
    .. image:: ../static/letter_count.png
        :alt: letter_count text
    """

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


def plot_line_changes(df: pd.DataFrame) -> None:
    """Plot the number of line changes over time.
    
    .. image:: ../static/line_changes.png
        :alt: line_changes text
    """
    last_line_pos = -1
    jumps = []
    for i, row in df.iterrows():
        jumped = False
        if row["Start_Line"] != last_line_pos:
            jumped = True

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
    plt.ylabel("Number of Line Changes")
    plt.title("Line Changes Over Time")
