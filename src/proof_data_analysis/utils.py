import datetime
import json
from typing import Dict

import pandas as pd


def load_json(path: str = "example.json") -> Dict:
    """Load the json file containing the keylogged events.

    :param path: path to the json file
    :return: the json object as a dictionary
    """
    with open(path) as f:
        return json.load(f)


def load_df(path_to_json: str = "example.json") -> pd.DataFrame:
    """Load the json file containing the keylogged events and convert
    it to a pandas dataframe.

    :param path_to_json: path to the json file with the keylogged events
    :return: a pandas dataframe with the columns ["Time", "Text_Change", "Start_Line", "End_Line", "Start_Char", "End_Char"]"""
    # load json
    json_object = load_json(path_to_json)
    # get the list of events
    events = json_object["events"]
    # create an empty dataframe
    df = pd.DataFrame(
        columns=[
            "Time",
            "Text_Change",
            "Start_Line",
            "End_Line",
            "Start_Char",
            "End_Char",
        ]
    )

    # iterate through the events
    for event in events:
        # ensure this event has time
        if "time" in event:
            # get the time
            time = datetime.datetime.fromtimestamp(event["time"] / 1000)
            # store the time/text changed in the dataframe
            df.loc[len(df)] = (
                time,
                event["textChange"],
                event["startLine"],
                event["endLine"],
                event["startChar"],
                event["endChar"],
            )

    return df
