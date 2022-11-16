import json
import threading
import time
import tkinter
from functools import partial
from typing import List, Dict, Tuple

playback_speed = 1


def set_speed(speed: float):
    """Sets the speed of the playback. Speed is the coefficient of time, with 1 being normal speed,
    2 being double speed, 0.5 being half speed and so on. Speed must be > 0."""
    global playback_speed
    playback_speed = speed


def next_text_event(events: List[Dict], start_index: int):
    """Starts searching the events array at start index and returns the index of the next text event
    (including the start index if it is a text event). Returns an index out of bounds of the array
    if there is no text event left in the array."""
    curr_index = start_index
    while curr_index < len(events) and "textChange" not in events[curr_index]:
        curr_index += 1

    return curr_index


def apply_text_event(event: dict, displayed_text: tkinter.Text):
    """Interprets the text event and applies it to the location stored in the event onto displayed_text."""
    location = str(event["startLine"] + 1) + "." + str(event["startChar"])
    if event["textChange"] == "":
        displayed_text.delete(location)
    else:
        displayed_text.insert(location, event["textChange"])


def replay(
    file_name: str,
    displayed_text: tkinter.Text,
    time_label: tkinter.Label,
    is_playing: threading.Event,
):
    """Attempts to open the file file_name (JSON data captured by the plugin) and then replays the captured data onto displayed_text.
    time_label is used to display the current time, in seconds of the playback from the start. The playback will play while is_playing is set
    and will stop playing when it is cleared."""
    FRAME_TIME = 0.01
    SECONDS_TO_MILLISECONDS = 1000
    PAUSE_TIMEOUT = 10

    with open(file_name) as file:
        data = json.loads(file.read())
        curr_time = data["start"]
        events = data["events"]
        curr_event = 0

        while curr_event < len(events):
            if is_playing.wait(PAUSE_TIMEOUT):
                time.sleep(FRAME_TIME)
                curr_time += FRAME_TIME * SECONDS_TO_MILLISECONDS * playback_speed
                time_label.config(text=(curr_time - data["start"]) / 1000)

                curr_event = next_text_event(events, curr_event)

                while (
                    curr_event < len(events) and events[curr_event]["time"] <= curr_time
                ):
                    apply_text_event(events[curr_event], displayed_text)
                    curr_event = next_text_event(events, curr_event + 1)
    print("Finished Playback")


def replay_from_file(file: str = "example.json"):
    """Creates the tkinter window and interface for the replay function."""
    is_playing = threading.Event()

    window = tkinter.Tk()
    play_button = tkinter.Button(text="play", command=is_playing.set)
    pause_button = tkinter.Button(text="pause", command=is_playing.clear)
    half_speed = tkinter.Button(text="0.5x Speed", command=partial(set_speed, 0.5))
    normal_speed = tkinter.Button(text="Normal Speed", command=partial(set_speed, 1))
    double_speed = tkinter.Button(text="2x Speed", command=partial(set_speed, 2))
    quad_speed = tkinter.Button(text="4x Speed", command=partial(set_speed, 4))
    time_label = tkinter.Label(text="Not Yet Playing")
    text_box = tkinter.Text()

    time_label.pack()
    play_button.pack()
    half_speed.pack()
    normal_speed.pack()
    double_speed.pack()
    quad_speed.pack()
    pause_button.pack()
    text_box.pack()

    thread = threading.Thread(
        target=replay,
        args=(
            file,
            text_box,
            time_label,
            is_playing,
        ),
    )
    thread.start()
    window.mainloop()


if __name__ == "__main__":
    replay_from_file()
