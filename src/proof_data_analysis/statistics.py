import pandas as pd

def calc_statistics(df:pd.DataFrame) -> None:
    print("Total number of edits: {}".format(len(df)))