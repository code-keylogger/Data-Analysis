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
    :return: a pandas dataframe with a row for each keylogged event"""
    # load json
    json_object = load_json(path_to_json)
    # get the list of events
    sessions = json_object["sessions"]
    # create an empty dataframe
    df = pd.DataFrame(
        columns=[
            "_id",
            "User_ID",
            "Problem_ID",
            "Problem_Start_Time",
            "Problem_End_Time",
            "Time",
            "Text_Change",
            "Start_Line",
            "End_Line",
            "Start_Char",
            "End_Char",
            "Tests_Passed",
            "Event_Type",
        ]
    )

    for session in sessions:
        for event in session["events"]:
            if "startLine" in event:
                time = datetime.datetime.fromtimestamp(event["time"] / 1000)
                # store the time/text changed in the dataframe

                df.loc[len(df)] = (
                    session["_id"],
                    session["userID"],
                    session["problemID"],
                    session["start"],
                    session["end"],
                    time,
                    event["textChange"],
                    event["startLine"],
                    event["endLine"],
                    event["startChar"],
                    event["endChar"],
                    event["testsPassed"],
                    # TODO: refactor this; this is a hack
                    "delete" if event["textChange"] == "" else "insert",
                )

    return df


def times_to_seconds(time: pd.Series) -> pd.Series:
    """Convert a series of time stamps to seconds

    Each resulting datapoint is just the amount of seconds from the
    first time stamp
    """
    # get the first time stamp
    first_time = time.iloc[0]
    # convert each time stamp to seconds
    return time.apply(lambda x: (x - first_time).total_seconds())


def get_num_tests_passed(tests_passed: pd.Series) -> pd.Series:
    """Convert a series of tests passed to a series of numbers

    Each resulting datapoint is just the number of tests passed

    e.g. [[1,2], [3,4], [1,2,3]] -> [2, 2, 3]
    """
    return tests_passed.apply(lambda x: len(x))
