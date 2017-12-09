import midi
import random
import operator
import os
import MIM_uniqueApproach

# Initializing data structures
allNotes = {} # Dictionary for pitches
allLengths = [] # List for note lengths

files = MIM_uniqueApproach.getMusic()
avgLength = MIM_uniqueApproach.listen(files, allNotes, allLengths)
allLengths = sorted(allLengths)
MIM_uniqueApproach.printInfo(allNotes, allLengths)
newSong = MIM_uniqueApproach.createMusic(allNotes, allLengths, avgLength)

# Export MIDI file.
midi.write_midifile("aiSong.mid", newSong)