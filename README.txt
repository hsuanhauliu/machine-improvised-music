#AI-Project

The reason that there are two separate files for functions is that both files
are written by different teammates.

MIM_functions.py:
- A module that contains functions that are used to import old data (recall),
  learn from inputs (learn), print out notes and their neighbors (printNotes),
  store data (memorize), get information from a single song (singleSong),
  and generate music (three algorithms: createOccurrenceBasedMusic,
  createMeasureBasedMusic, createHillClimbingMusic).

  Note: for the algorithms in this file, make sure to place input music files in
    a directory called "music".

MIM_functions_demo.py:
- A main module demonstrating how to use the algorithms in MIM_functions.py

MIM_uniqueApproach.py:
- The other module that contains the functions. The listen function is identical
  to the learn function in MIM_functions.py, and the printInfo function is
  identical to the printNotes function in MIM_functions.py. getMusic function is
  used to get the path of the input music directory. The four functions left are
  algorithms used to generate the music.

  Note: for the algorithms in this file, make sure to change the name of the
    directory for input music to "musicInput", or simply change the path string
    in getMusic function to "music".

MIM_uniqueApproach_demo.py:
- A main module demonstrating how to use the algorithms in MIM_uniqueApproach.py

These files can also be found on Github in the link below:
https://github.com/hsuanhauliu/COMP5600-AI-Final-Project-Machine-Improvised-Music

Input data link:
https://github.com/hsuanhauliu/COMP5600-AI-Final-Project-Machine-Improvised-Music/tree/master/musicInput
