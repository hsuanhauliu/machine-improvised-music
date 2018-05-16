# Machine-Improvised Music Program
This is our AI final project. We designed an AI program that can learn from various single-melody music and come up with its own version of music.

## Pre-requisite
This program uses [python-midi](https://github.com/vishnubob/python-midi) library and must be installed in order to run this program.

## Installation
`git clone https://github.com/hsuanhauliu/COMP5600-AI-Final-Project-Machine-Improvised-Music.git`

### Note
Both MIM_functions.py and MIM_uniqueApproach.py files contain functions that you can use to train an AI and generate music.

#### MIM_functions.py:
- A module that contains functions that are used to import old data (recall),
  learn from inputs (learn), print out notes and their neighbors (printNotes),
  store data (memorize), get information from a single song (singleSong),
  and generate music (three algorithms: createOccurrenceBasedMusic,
  createMeasureBasedMusic, createHillClimbingMusic).

  Note: for the algorithms in this file, make sure to place input music files in
    a directory called "musicInput".

#### MIM_functions_demo.py:
- A main module demonstrating how to use the algorithms in MIM_functions.py

#### MIM_uniqueApproach.py:
- The other module that contains the functions. The listen function is identical
  to the learn function in MIM_functions.py, and the printInfo function is
  identical to the printNotes function in MIM_functions.py. getMusic function is
  used to get the path of the input music directory. The four functions left are
  algorithms used to generate the music.

#### MIM_uniqueApproach_demo.py:
- A main module demonstrating how to use the algorithms in MIM_uniqueApproach.py
