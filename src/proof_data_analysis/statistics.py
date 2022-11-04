import pandas as pd


# TODO: add more statistics
def calc_statistics(df: pd.DataFrame) -> None:
    """Calculate basic statistics for the dataframe"""
    print("Total number of edits: {}".format(len(df)))
