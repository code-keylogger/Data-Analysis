import datetime
import json
import sys
import threading
import time
import tkinter
from functools import partial
from typing import Dict, List


class Replay:
    FRAME_TIME = 0.01
    """Time in seconds between each frame"""
    SECONDS_TO_MILLISECONDS = 1000
    PAUSE_TIMEOUT = 1
    """Sets the timeout in seconds for the wait method in start_playback()"""
    SLIDER_LENGTH = 600
    file_data: Dict = {}
    """Entire JSON object loaded in from the argument file"""
    playback_speed = 1
    """Speed is the coefficient of time, with 1 being normal speed,
     Speed must be > 0."""
    is_playing = threading.Event()
    """Stops playback when cleared, resumes when set"""
    start_time = 0
    """Absolute time of the first event in ms"""
    end_time = 0
    """Absolute time of the last event in ms"""
    curr_event = 0
    """Index of the current text event, the range of events 0-curr_event (inclusive)
    should always be the displayed events in displayed_text."""
    curr_time = 0
    """Absolute time of the playback in ms, the range of events with time <= curr_time should
    always be the displayed events in displayed_text"""
    slider_event: tkinter.IntVar
    """Controls the position of the event slider"""
    slider_time: tkinter.IntVar
    """Controls the position of the time slider"""
    displayed_time: tkinter.StringVar
    """The time displayed above the playback window"""
    displayed_text: tkinter.Text
    """The playback window, should always be state="disabled" unless writing to it to prevent the user
    from typing into it"""
    time_slider: tkinter.Scale
    """The slider that allows time scrubbing of the playback"""
    event_slider: tkinter.Scale
    """The slider that allows event scrubbing of the playback"""
    events = []
    """List of all text events in the current session"""

    def set_speed(self, speed: str):
        """Sets the speed of the playback.
        :param speed: Speed is the coefficient of time, with 1 being normal speed, Speed must be > 0."""
        self.playback_speed = float(speed)

    def _apply_text_event(self, event: Dict):
        """Interprets the text event and applies it to the location stored in the event onto displayed_text.
        :param event: Text event to apply"""
        # Tkinter text objects determine location with strings in the form "lineNum.charNum"
        # their lines are 1 indexed, so we must increment our line indices
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

    def _update_text(self):
        """Updates displayed_text with any events that have occured since curr_time was increased"""
        next_event = self.curr_event + 1
        while (
            next_event < len(self.events)
            and self.events[next_event]["time"] <= self.curr_time
        ):
            self._apply_text_event(self.events[next_event])
            self.curr_event = next_event
            next_event += 1

    def _rewind_to_time(self, time: int):
        """Reverts the state of the playback to the specified time
        :param time: the time, in ms, to rewind to. This time is relative
        to the duration of the playback, with 0 being the start of the playback"""
        event = 0
        next_event = 1
        time_absolute = time + self.start_time
        # find the event to revert to based on the time
        while (
            next_event < len(self.events)
            and self.events[next_event]["time"] <= time_absolute
        ):
            event = next_event
            next_event += 1

        if self.events[event]["time"] > time_absolute:
            # if we have scrolled too far back
            self._clear_text()
        else:
            self._revert_to_event(event)

    def _clear_text(self):
        """Deletes all text from displayed_text"""
        self.displayed_text.configure(state="normal")
        self.displayed_text.delete("1.0", "end")
        self.displayed_text.configure(state="normal")

    def _revert_to_event(self, event: int):
        """Rebuilds the current state up to the specified event
        :param event: the index of the event to revert to. This will be the last rendered event"""
        # reset back to start state
        self.curr_event = 0
        self._clear_text()
        # re-apply all events up to the current event
        while self.curr_event < event:
            self._apply_text_event(self.events[self.curr_event])
            self.curr_event += 1
        self._apply_text_event(self.events[self.curr_event])

    def scrub_to_event(self, event: str):
        """Updates the playback to the event specified
        :param event: The index of the event to revert to. Recieved from slider which makes it a string"""
        # pause
        self.is_playing.clear()

        delta_event = int(event) - self.curr_event
        i = self.curr_event + 1
        self.curr_event += delta_event

        if delta_event > 0:
            # scrubbing forwards
            while i <= self.curr_event:
                self._apply_text_event(self.events[i])
                i += 1
        elif delta_event <= 0:
            # scrubbing backwards
            next_index = int(event)
            if next_index < len(self.events):
                self._revert_to_event(next_index)

        # adjust curr_time and displayed times
        self.curr_time = self.events[self.curr_event]["time"]
        self.slider_time.set(self.curr_time - self.start_time)
        self.displayed_time.set(
            (self.curr_time - self.start_time) / Replay.SECONDS_TO_MILLISECONDS
        )

    def scrub_to_time(self, time: str):
        """Updates the playback to the time specified
        :param time: Time, in milliseconds, to set playback to. Recieved from slider which makes it a string."""
        # pause
        self.is_playing.clear()

        delta_time = int(time) - (self.curr_time - self.start_time)
        self.curr_time += delta_time

        if delta_time > 0:
            # scrubbing forwards
            self._update_text()
        elif delta_time < 0:
            # scrubbing backwards
            self._rewind_to_time(int(time))

        # adjust displayed events (curr_event is updated by update_text and rewind_to_time)
        self.displayed_time.set(
            (self.curr_time - self.start_time) / Replay.SECONDS_TO_MILLISECONDS
        )
        self.slider_event.set(self.curr_event)

    def _start_playback(self):
        """Replays the captured data (JSON data captured by the plugin) onto displayed_text.
        time_label is used to display the current time, in seconds of the playback from the start. The playback will play while is_playing is set
        and will stop playing when it is cleared."""
        # time offset
        self.curr_time = self.start_time
        while True:
            if self.is_playing.wait(Replay.PAUSE_TIMEOUT):
                if self.curr_time < self.end_time:
                    # Wait for frame time and increase the current time by frame time (scaled to playback speed)
                    time.sleep(Replay.FRAME_TIME)
                    self.curr_time += (
                        Replay.FRAME_TIME
                        * Replay.SECONDS_TO_MILLISECONDS
                        * self.playback_speed
                    )
                    # update displayed times
                    self.displayed_time.set(
                        (self.curr_time - self.start_time)
                        / Replay.SECONDS_TO_MILLISECONDS
                    )
                    self.slider_time.set(self.curr_time - self.start_time)
                    # update displayed text and slider event
                    self._update_text()
                    self.slider_event.set(self.curr_event)
                else:
                    # pause when we reach the end of playback
                    self.is_playing.clear()

    def _create_window(self, file_name: str):
        """Creates the tkinter window and interface for the replay function.
        :returns: the created window"""
        window = tkinter.Tk()
        window.title("Replay Tool: " + file_name)

        speeds = ["0.25", "0.5", "1", "2", "4"]
        sessions = range(len(self.file_data["sessions"]))

        self.slider_time = tkinter.IntVar()
        self.slider_event = tkinter.IntVar()
        self.displayed_time = tkinter.StringVar()
        self.displayed_time.initialize("Not Yet Playing")

        # create basic structure and labels
        buttonsFrame = tkinter.Frame(window)
        time_label = tkinter.Label(window, textvariable=self.displayed_time)
        self.displayed_text = tkinter.Text(window)
        self.displayed_text.configure(state="disabled")

        speed_label = tkinter.Label(buttonsFrame, text="Playback Speed:")
        speed_text = tkinter.StringVar(window)
        sessions_label = tkinter.Label(buttonsFrame, text="Session Selection:")
        sessions_text = tkinter.IntVar(window)
        speed_text.set("1")
        sessions_text.set("Please Select a Session")

        # create basic conrols
        play_button = tkinter.Button(
            buttonsFrame, text="Play", command=self.is_playing.set
        )
        pause_button = tkinter.Button(
            buttonsFrame, text="Pause", command=self.is_playing.clear
        )
        speed_dropdown = tkinter.OptionMenu(
            buttonsFrame, speed_text, *speeds, command=self.set_speed
        )
        sessions_dropdown = tkinter.OptionMenu(
            buttonsFrame, sessions_text, *sessions, command=self.open_session
        )
        self.time_slider = tkinter.Scale(
            window,
            length=self.SLIDER_LENGTH,
            label="Time",
            showvalue=0,
            variable=self.slider_time,
            orient="horizontal",
            command=self.scrub_to_time,
        )
        self.event_slider = tkinter.Scale(
            window,
            length=self.SLIDER_LENGTH,
            label="Event",
            variable=self.slider_event,
            orient="horizontal",
            command=self.scrub_to_event,
        )

        # pack all GUI elements
        buttonsFrame.pack()
        play_button.pack(side="left")
        pause_button.pack(side="left")
        speed_label.pack(side="left")
        speed_dropdown.pack(side="left")
        sessions_label.pack(side="left")
        sessions_dropdown.pack(side="left")
        self.time_slider.pack()
        self.event_slider.pack()
        time_label.pack()
        self.displayed_text.pack()

        return window

    def _extract_text_events(self, events: List):
        """Returns a new array with all text events from events in order
        :param events: An array of events from a session
        :returns: an array of only the text events from the original array, preserving order."""
        result = []
        for event in events:
            # only text events have a time field
            if "time" in event:
                result.append(event)
        return result

    def open_session(self, session_num: int):
        """Opens the specified session, re-initializing values and updating
        the necessary GUI configs, then resets playback to event 0
        :param session_num: index of the session to open"""
        session = self.file_data["sessions"][session_num]

        self.events = self._extract_text_events(session["events"])
        if len(self.events) == 0:
        # error case when there are no events in the session
           self.time_slider.config(to=0)
           self.event_slider.config(to=0)

           self._clear_text()
           self.displayed_time.set("There are no events in this session!")
        else:
            self.start_time = self.events[0]["time"]
            self.end_time = self.events[len(self.events) - 1]["time"]
            duration = self.end_time - self.start_time

            self.time_slider.config(to=duration)
            self.event_slider.config(to=len(self.events) - 1)

            self.scrub_to_event(0)

    def replay_from_file(self, file_name: str):
        """Replays the data stored in the file
        :param file_name: relative or absolute file path."""
        with open(file_name) as file:
            try:
                self.file_data: Dict = json.loads(file.read())
            except json.JSONDecodeError:
                print("The file: \"" + file_name + "\" was not a vaild JSON file")
                return

            # error cases for malformed data
            if "sessions" not in self.file_data.keys():
                print("The file: \"" + file_name + "\" was not a vaild data file, no sessions field present")
                return
            elif len(self.file_data["sessions"]) == 0:
                print("The file: \"" + file_name + "\" has no sessions")
                return

            window = self._create_window(file_name)

            thread = threading.Thread(
                target=self._start_playback,
            )
            # so the thread will die when the window is closed
            thread.daemon = True
            thread.start()

            window.mainloop()


if __name__ == "__main__":
    playback = Replay()
    if len(sys.argv) > 1:
        playback.replay_from_file(sys.argv[1])
    else:
        print("No data file specified.")
