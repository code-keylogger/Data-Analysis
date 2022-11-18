import json
import threading
import time
import tkinter
import sys
import datetime
from typing import Dict
from functools import partial


class Replay:
    FRAME_TIME = 0.01
    SECONDS_TO_MILLISECONDS = 1000
    PAUSE_TIMEOUT = 1
    playback_speed = 1
    is_playing = threading.Event()
    start_time = 0
    end_time = 0
    curr_event = 0
    curr_time = 0
    slider_event = 0
    slider_time = 0
    displayed_time: tkinter.StringVar
    displayed_text: tkinter.Text
    events = []

    def set_speed(self, speed: str):
        """Sets the speed of the playback. Speed is the coefficient of time, with 1 being normal speed,
        2 being double speed, 0.5 being half speed and so on. Speed must be > 0."""
        self.playback_speed = float(speed)

    def apply_text_event(self, event: Dict):
        """Interprets the text event and applies it to the location stored in the event onto displayed_text."""
        start_location = str(event["startLine"] + 1) + "." + str(event["startChar"])
        end_location = str(event["endLine"] + 1) + "." + str(event["endChar"])
        self.displayed_text.configure(state="normal")

        if event["textChange"] == "":
            self.displayed_text.delete(start_location, end_location)
        else:
            if start_location != end_location:
                self.displayed_text.delete(start_location, end_location)
            self.displayed_text.insert(start_location, event["textChange"])

        self.displayed_text.configure(state="disabled")

    def update_text(self):
        """updates displayed_text with any events that have occured since curr_time was increased"""
        next_event = self.curr_event + 1
        while (
                    next_event < len(self.events) and self.events[next_event]["time"] <= self.curr_time
                ):
                    self.apply_text_event(self.events[next_event])
                    self.curr_event = next_event
                    next_event += 1;

    def rewind_to_time(self, time: int):
        """Reverts the state of the playback to the specified time"""
        event = 0
        next_event = 1
        time_absolute = time + self.start_time
        while(next_event < len(self.events) and self.events[next_event]["time"] <= time_absolute):
            event = next_event
            next_event += 1

        if self.events[event]["time"] > time_absolute:
            self.clear_text()
        else:
            self.revert_to_event(event)
        

    def clear_text(self):
        """Deletes all text from the displayed_text"""
        self.displayed_text.configure(state="normal")
        self.displayed_text.delete('1.0', 'end')
        self.displayed_text.configure(state="normal")

    def revert_to_event(self, event: int):
        """Rebuilds the current state up to the specified event"""
        self.curr_event = 0
        self.clear_text()
        while self.curr_event < event:
            self.apply_text_event(self.events[self.curr_event])
            self.curr_event += 1
        self.apply_text_event(self.events[self.curr_event])
        

    def scrub_to_event(self, event: str):
        """Updates the playback to the event specified"""
        self.is_playing.clear()
        delta_event = int(event) - self.curr_event
        i = self.curr_event + 1
        self.curr_event += delta_event
        if (delta_event > 0):
            while (i <= self.curr_event):
                self.apply_text_event(self.events[i])
                i += 1
        elif (delta_event < 0):
            next_index = int(event)
            if next_index < len(self.events):
                self.revert_to_event(next_index)
        self.curr_time = self.events[self.curr_event]["time"]
        self.slider_time.set(self.curr_time - self.start_time)
        self.displayed_time.set((self.curr_time - self.start_time) / Replay.SECONDS_TO_MILLISECONDS)

    def scrub_to_time(self, time: str):
        """Updates the playback to the time specified"""
        self.is_playing.clear()
        delta_time = int(time) - (self.curr_time - self.start_time)
        self.curr_time += delta_time
        if (delta_time > 0):
            self.update_text()
        elif (delta_time < 0):
            self.rewind_to_time(int(time))
        self.displayed_time.set((self.curr_time - self.start_time) / Replay.SECONDS_TO_MILLISECONDS)
        self.slider_event.set(self.curr_event)

    def startPlayback(self):
        """Replays the captured data (JSON data captured by the plugin) onto displayed_text.
        time_label is used to display the current time, in seconds of the playback from the start. The playback will play while is_playing is set
        and will stop playing when it is cleared."""
        self.curr_time = self.start_time
        self.apply_text_event(self.events[0])
        while True:
            if self.is_playing.wait(Replay.PAUSE_TIMEOUT):
                if self.curr_time < self.end_time:
                    time.sleep(Replay.FRAME_TIME)
                    self.curr_time += Replay.FRAME_TIME * Replay.SECONDS_TO_MILLISECONDS * self.playback_speed
                    self.displayed_time.set((self.curr_time - self.start_time) / Replay.SECONDS_TO_MILLISECONDS)
                    self.slider_time.set(self.curr_time - self.start_time)
                    self.update_text()
                    self.slider_event.set(self.curr_event)
                    


    def createWindow(self):
        """Creates the tkinter window and interface for the replay function."""
        window = tkinter.Tk()

        speeds = ["0.25", "0.5", "1", "2", "4"]
        speed_label = tkinter.StringVar(window)
        speed_label.set("1")

        buttonsFrame = tkinter.Frame(window)
        buttonsFrame.pack()

        play_button = tkinter.Button(buttonsFrame, text="play", command=self.is_playing.set)
        pause_button = tkinter.Button(buttonsFrame, text="pause", command=self.is_playing.clear)
        speed_dropdown = tkinter.OptionMenu(buttonsFrame, speed_label, *speeds, command=self.set_speed)
        
        play_button.pack(side="left")
        pause_button.pack(side="left")
        speed_dropdown.pack(side="left")
        

        return window

    def extract_text_events(self, events):
        """Returns a new array with all text events from events in order"""
        result = [];
        for event in events:
            if "time" in event:
                result.append(event)
        return result

    def replay_from_file(self, file_name: str = "../../tests/example2.json"):
        """Replays the data stored in the file"""
        with open(file_name) as file:
            file_data = json.loads(file.read())
            session = file_data["sessions"][0]
            self.events = self.extract_text_events(session["events"])
            self.start_time = self.events[0]["time"]
            self.end_time = self.events[len(self.events) - 1]["time"]
            end_time = self.end_time - self.start_time

            window = self.createWindow()

            self.slider_time = tkinter.IntVar()
            self.slider_event = tkinter.IntVar()
            self.displayed_time = tkinter.StringVar()
            self.displayed_time.initialize("Not Yet Playing")

            time_slider = tkinter.Scale(window, from_=0, to=end_time, length=600, label="Time", showvalue=0, variable=self.slider_time, orient="horizontal", command=self.scrub_to_time);
            event_slider = tkinter.Scale(
                window, from_=0, to=len(self.events) - 1, length=600, label="Event", variable=self.slider_event, orient="horizontal", command=self.scrub_to_event
                )

            time_label = tkinter.Label(window, textvariable=self.displayed_time)
            self.displayed_text = tkinter.Text(window)
            self.displayed_text.configure(state="disabled")
            
            time_slider.pack()
            event_slider.pack()

            time_label.pack()
            self.displayed_text.pack()

            thread = threading.Thread(
                target=self.startPlayback,
            )
            thread.daemon = True
            thread.start()

            window.mainloop()


if __name__ == "__main__":
    playback = Replay()
    if len(sys.argv) > 1:
        playback.replay_from_file(sys.argv[1])
    else:
        playback.replay_from_file()
