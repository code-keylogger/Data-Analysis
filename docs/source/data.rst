Data 
========

Downloading the Data 
*********************************

To download the data, run the following command at the root level of this project

.. code-block:: bash

    mkdir data/
    curl --location --request GET 'http://virulent.cs.umd.edu:3000/sessions' > data/sessions.json


Understanding Stored Data
*********************************
We record VSCode event data into JSON files. The meaning of each field is not
trival to understand, so we describe them below. We record two types of events,
mouse movements/hightlights and keyboard events. The following comments are
extracted from the VSCode API: https://code.visualstudio.com/api/references/vscode-api

Mouse movements and highlights
####################################

.. code-block:: json

    {
        // The position of the cursor.
        "active": {
            "line": 0,
            "character": 1
        },
        // The position at which the selection starts (equal to either start or end position)
        "anchor": {
            "line": 0,
            "character": 1
        },
        // The end position of the selection.
        "end": {
            "line": 0,
            "character": 1
        },
        // A selection is reversed if its anchor is the end position.
        "isReversed": true,
        // The start position of the selection.
        "start": {
            "line": 0,
            "character": 1
        }
    }

Keyboard Events
####################################

.. code-block:: json

    {
        "startLine": 0,
        "startChar": 1,
        "endLine": 0,
        "endChar": 1,
        "textChange": "H",
        "testsPassed": [],
        "time": 1666896719657
    },

.. automodule:: proof_data_analysis.utils
   :members: 
   :undoc-members:
