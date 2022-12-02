import pandas as pd


def calc_statistics(df: pd.DataFrame) -> None:
    """Calculate basic statistics for the dataframe"""
    print("Total number of edits: {}".format(len(df)))
    print(
        "Total number of insertion only events: {}".format(
            len(df[df["Event_Type"] == "insert"])
        )
    )
    print(
        "Total number of deletion only events: {}".format(
            len(df[df["Event_Type"] == "delete"])
        )
    )
    print(
        "Total number of replacement events: {}".format(
            len(df[df["Event_Type"] == "replace"])
        )
    )
