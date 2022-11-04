import json
import threading
import time
import tkinter
from functools import partial

playbackSpeed = 1

def setSpeed(speed):
    global playbackSpeed
    playbackSpeed = speed

def nextTextEvent(events, startIndex):
    '''Starts searching the events array at start index and returns the index of the next text event
    (including the start index if it is a text event). Returns an index out of bounds of the array 
    if there is no text event left in the array'''
    currIndex = startIndex
    while currIndex < len(events) and 'textChange' not in events[currIndex]:
        currIndex += 1
    
    return currIndex
    
def applyTextEvent(event, displayedText):
    location = str(event['startLine'] + 1) + '.' + str(event['startChar'])
    if (event['textChange'] == ''):
        displayedText.delete(location)
    else: 
        displayedText.insert(location, event['textChange'])

def replay(fileName, displayedText, timeLabel, isPlaying):
    FRAME_TIME = 0.01
    SECONDS_TO_MILLISECONDS = 1000
    PAUSE_TIMEOUT = 10
    with open(fileName) as file:
        data = json.loads(file.read())
        currTime = data['start']
        events = data['events']
        currEvent = 0

        while currEvent < len(events):
            if isPlaying.wait(PAUSE_TIMEOUT):
                time.sleep(FRAME_TIME)
                currTime += FRAME_TIME * SECONDS_TO_MILLISECONDS * playbackSpeed
                timeLabel.config(text=(currTime - data['start']) / 1000)

                currEvent = nextTextEvent(events, currEvent)

                while currEvent < len(events) and events[currEvent]['time'] <= currTime:
                    applyTextEvent(events[currEvent], displayedText)
                    currEvent = nextTextEvent(events, currEvent + 1)
    print("Finished Playback")
    
if __name__ == '__main__':
    isPlaying = threading.Event()

    window = tkinter.Tk()
    playButton = tkinter.Button(text='play', command=isPlaying.set)
    pauseButton = tkinter.Button(text='pause', command=isPlaying.clear)
    halfSpeed = tkinter.Button(text='0.5x Speed', command=partial(setSpeed, 0.5))
    normalSpeed = tkinter.Button(text='Normal Speed', command=partial(setSpeed, 1))
    doubleSpeed = tkinter.Button(text='2x Speed', command=partial(setSpeed, 2))
    quadSpeed = tkinter.Button(text='4x Speed', command=partial(setSpeed, 4))
    timeLabel = tkinter.Label(text='Not Yet Playing')
    textBox = tkinter.Text()

    timeLabel.pack()
    playButton.pack()
    halfSpeed.pack()
    normalSpeed.pack()
    doubleSpeed.pack()
    quadSpeed.pack()
    pauseButton.pack()
    textBox.pack()

    thread = threading.Thread(target=replay, args=('example.json', textBox, timeLabel, isPlaying,))
    thread.start()
    window.mainloop()



