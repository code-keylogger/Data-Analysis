import json
import threading
import time
import tkinter


def printText(text):
    for char in text:
        print(char, end="")

def replay(fileName, displayedText, pauseCond):
    with open(fileName) as file:
        data = json.loads(file.read())
        prevTime = data['start']
        delay = 0

        for event in data['events']:
            if 'textChange' in event:
                delay = (event['time'] - prevTime) / 1000.0
                prevTime = event['time']
                time.sleep(delay)
                location = str(event['startLine'] + 1) + '.' + str(event['startChar'])
                displayedText.insert(location, event['textChange'])

    
if __name__ == '__main__':
    pauseCond = threading.Condition()

    window = tkinter.Tk()
    pause = tkinter.Button(text='pause')
    textBox = tkinter.Text()
    pause.pack()
    textBox.pack()

    thread = threading.Thread(target=replay, args=('example.json', textBox, pauseCond,))
    thread.start()
    window.mainloop()



