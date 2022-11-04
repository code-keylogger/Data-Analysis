import json
import threading
import time
import tkinter
from functools import partial

playbackSpeed = 1


def set_speed(speed):
    global playbackSpeed
    playbackSpeed = speed


def next_text_event(events, start_index):
    """Starts searching the events array at start index and returns the index of the next text event
    (including the start index if it is a text event). Returns an index out of bounds of the array
    if there is no text event left in the array"""
    curr_index = start_index
    while curr_index < len(events) and "textChange" not in events[curr_index]:
        curr_index += 1

    return curr_index


def apply_text_event(event, displayed_text):
    location = str(event["startLine"] + 1) + "." + str(event["startChar"])
    if event["textChange"] == "":
        displayed_text.delete(location)
    else:
        displayed_text.insert(location, event["textChange"])


def replay(file_name, displayed_text, time_label, is_playing):
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
                curr_time += FRAME_TIME * SECONDS_TO_MILLISECONDS * playbackSpeed
                time_label.config(text=(curr_time - data["start"]) / 1000)

                curr_event = next_text_event(events, curr_event)

                while (
                    curr_event < len(events) and events[curr_event]["time"] <= curr_time
                ):
                    apply_text_event(events[curr_event], displayed_text)
                    curr_event = next_text_event(events, curr_event + 1)
    print("Finished Playback")


def replay_from_file(file: str = "example.json"):
    is_playing = threading.Event()

    window = tkinter.Tk()
    playButton = tkinter.Button(text="play", command=is_playing.set)
    pauseButton = tkinter.Button(text="pause", command=is_playing.clear)
    halfSpeed = tkinter.Button(text="0.5x Speed", command=partial(set_speed, 0.5))
    normalSpeed = tkinter.Button(text="Normal Speed", command=partial(set_speed, 1))
    doubleSpeed = tkinter.Button(text="2x Speed", command=partial(set_speed, 2))
    quadSpeed = tkinter.Button(text="4x Speed", command=partial(set_speed, 4))
    time_label = tkinter.Label(text="Not Yet Playing")
    textBox = tkinter.Text()

    time_label.pack()
    playButton.pack()
    halfSpeed.pack()
    normalSpeed.pack()
    doubleSpeed.pack()
    quadSpeed.pack()
    pauseButton.pack()
    textBox.pack()

    thread = threading.Thread(
        target=replay,
        args=(
            file,
            textBox,
            time_label,
            is_playing,
        ),
    )
    thread.start()
    window.mainloop()


if __name__ == "__main__":
    replay_from_file()
