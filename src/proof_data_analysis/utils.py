
import datetime
import json

import pandas as pd

def load_json(path:str="example.json"):
    with open(path) as f:
        return json.load(f)

def load_df(path_to_json:str="example.json"):
    json_object = load_json(path_to_json)
    events = json_object["events"]
    df = pd.DataFrame(columns=["Time", "Text_Change"])
    for event in events:
        if 'time' in event:
            time = datetime.datetime.fromtimestamp(event["time"]/1000)
            df.loc[len(df)] = (time, event["textChange"])
    return df