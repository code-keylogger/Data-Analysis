import json
import threading
import time
import tkinter
import sys
import datetime
from functools import partial


class Replay:
    FRAME_TIME = 0.01
    SECONDS_TO_MILLISECONDS = 1000
    PAUSE_TIMEOUT = 1
    playback_speed = 1
    is_playing = threading.Event()
    window_open = threading.Event()
    start_time = 0
    end_time = 0
    curr_event = 0
    curr_time = 0
    displayed_event = 0
    displayed_time = 0
    displayed_text = {}
    events = []

    def set_speed(self, speed: float):
        """Sets the speed of the playback. Speed is the coefficient of time, with 1 being normal speed,
        2 being double speed, 0.5 being half speed and so on. Speed must be > 0."""
        self.playback_speed = speed


    def next_text_event(self, start_index: int):
        """Starts searching the events array at start index and returns the index of the next text event
        (including the start index if it is a text event). Returns an index out of bounds of the array
        if there is no text event left in the array."""
        curr_index = start_index
        while curr_index < len(self.events) and "textChange" not in self.events[curr_index]:
            curr_index += 1

        return curr_index


    def apply_text_event(self, event: dict):
        """Interprets the text event and applies it to the location stored in the event onto displayed_text."""
        location = str(event["startLine"] + 1) + "." + str(event["startChar"])
        if event["textChange"] == "":
            self.displayed_text.delete(location)
        else:
            self.displayed_text.insert(location, event["textChange"])

    def update_text(self):
        """updates displayed_text with any events that have occured since curr_time was increased"""
        while (
                    self.curr_event < len(self.events) and self.events[self.curr_event]["time"] <= self.curr_time
                ):
                    self.apply_text_event(self.events[self.curr_event])
                    self.curr_event = self.next_text_event(self.curr_event + 1)

    def rewind_to_time(self, time: int):
        """Reverts the state of the playback to the specified time"""
        event = self.next_text_event(0)
        next_event = self.next_text_event(event + 1)
        time_absolute = time + self.start_time
        while(next_event < len(self.events) and self.events[next_event]["time"] <= time_absolute):
            event = next_event
            next_event = self.next_text_event(next_event + 1)

        if self.events[event]["time"] > time_absolute:
            self.displayed_text.delete('1.0', 'end')
        else:
            self.revert_to_event(self.events[event])
        

    def revert_to_event(self, event: dict):
        """Rebuilds the current state up to the specified event"""
        self.curr_event = self.next_text_event(0)
        self.curr_time = int(event["time"])
        self.displayed_text.delete('1.0', 'end')
        self.update_text()

    def scrub_to_event(self, event: str):
        """Updates the playback to the event specified"""
        self.is_playing.clear()
        delta_event = int(event) - self.curr_event
        i = self.curr_event
        self.curr_event += delta_event
        if (delta_event > 0):
            while (i < self.curr_event):
                i = self.next_text_event(i)
                if i < len(self.events):
                    self.apply_text_event(self.events[i])
                i += 1
        elif (delta_event < 0):
            next_index = self.next_text_event(int(event))
            if next_index < len(self.events):
                self.revert_to_event(self.events[next_index])
        self.displayed_time.set(self.curr_time - self.start_time)

    def scrub_to_time(self, time: str):
        """Updates the playback to the time specified"""
        self.is_playing.clear()
        delta_time = int(time) - (self.curr_time - self.start_time)
        self.curr_time += delta_time
        if (delta_time > 0):
            self.update_text()
        elif (delta_time < 0):
            self.rewind_to_time(int(time))
        self.displayed_event.set(self.curr_event)

    def startPlayback(self, data: dict, time_label: tkinter.Label):
        """Replays the captured data (JSON data captured by the plugin) onto displayed_text.
        time_label is used to display the current time, in seconds of the playback from the start. The playback will play while is_playing is set
        and will stop playing when it is cleared."""
        self.curr_time = self.start_time
        events = data["events"]
        while self.window_open.is_set():
            if self.is_playing.wait(Replay.PAUSE_TIMEOUT):
                if self.curr_time < self.end_time:
                    time.sleep(Replay.FRAME_TIME)
                    self.curr_time += Replay.FRAME_TIME * Replay.SECONDS_TO_MILLISECONDS * self.playback_speed
                    time_label.config(text=(self.curr_time - self.start_time) / Replay.SECONDS_TO_MILLISECONDS)
                    self.displayed_time.set(self.curr_time - self.start_time)

                    self.curr_event = self.next_text_event(self.curr_event)
                    self.displayed_event.set(self.curr_event)

                    self.update_text()


    def createWindow(self):
        """Creates the tkinter window and interface for the replay function."""
        window = tkinter.Tk()

        play_button = tkinter.Button(text="play", command=self.is_playing.set)
        pause_button = tkinter.Button(text="pause", command=self.is_playing.clear)
        half_speed = tkinter.Button(text="0.5x Speed", command=partial(self.set_speed, 0.5))
        normal_speed = tkinter.Button(text="Normal Speed", command=partial(self.set_speed, 1))
        double_speed = tkinter.Button(text="2x Speed", command=partial(self.set_speed, 2))
        quad_speed = tkinter.Button(text="4x Speed", command=partial(self.set_speed, 4))

        play_button.pack()
        pause_button.pack()
        # half_speed.pack()
        normal_speed.pack()
        double_speed.pack()
        # quad_speed.pack()

        return window

    def last_text_event(self):
        curr = 0
        next = self.next_text_event(0)
        while(next < len(self.events)):
            curr = next
            next = self.next_text_event(next + 1)
        if curr != 0:
            return curr
        else:
            return -1

    def replay_from_file(self, file_name: str = "../../tests/example.json"):
        with open(file_name) as file:
            file_data = json.loads(file.read())
            session = file_data["sessions"][0]
            self.events = session["events"]
            self.start_time = self.events[self.next_text_event(0)]["time"]
            self.end_time = self.events[self.last_text_event()]["time"]
            end_time = self.end_time - self.start_time

            window = self.createWindow()

            self.displayed_time = tkinter.IntVar()
            self.displayed_event = tkinter.IntVar()

            time_slider = tkinter.Scale(window, from_=0, to=end_time, length=600, variable=self.displayed_time, orient="horizontal", command=self.scrub_to_time);
            event_slider = tkinter.Scale(
                window, from_=0, to=len(self.events), length=600, variable=self.displayed_event, orient="horizontal", command=self.scrub_to_event
                )

            time_label = tkinter.Label(text="Not Yet Playing")
            self.displayed_text = tkinter.Text()
            
            time_slider.pack()
            event_slider.pack()

            time_label.pack()
            self.displayed_text.pack()

            self.window_open.set()

            thread = threading.Thread(
                target=self.startPlayback,
                args=(
                    session,
                    time_label,
                ),
            )
            thread.start()
            window.mainloop()
            self.window_open.clear()


if __name__ == "__main__":
    playback = Replay()
    if len(sys.argv) > 1:
        playback.replay_from_file(sys.argv[1])
    else:
        playback.replay_from_file()
