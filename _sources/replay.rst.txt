Replay
==============

Running the replay tool
*********************************

To start a replay, simply execute the script with the data file as the command line argument.
The file specified must be a properly formatted JSON data file as retrieved from the server. 
The file argument can be the relative or absolute path for the file.

For example, to open a file called "sessions.json" that is located in the same directory as the script:

.. code-block:: bash

    python replay.py sessions.json

After running the script, the tool will open in a new window. In order to start playback, select a session from the dropdown menu
and then press "Play"