import midi
import random
import operator
import os

# Obtains input files from "music" directory
# RETURN list containing all input files
def getMusic():
    path = "musicInput"
    fil = os.listdir(path)

    return fil

# Listens to input files and learns note information
# RETURN int representing length of song to be generated
def listen(files, allNotes, allLengths):
    totalLength = 0 # Sum of all track lengths

    for f in files:
        # Import MIDI files
        pattern = midi.read_midifile(f)
        track = pattern[0]

        totalLength = totalLength + len(track) # Will make more sense when there's more than one file

        # Grab information for each note
        prevP = -1

        for event in track:
            if event.name == 'Note On' and event.data[1] == 0:
                if prevP != -1:
                    # get data of current note
                    tick = event.tick
                    currP = event.data[0]
                    
                    # if the note exists
                    if allNotes.has_key(prevP):
                        # if the neighbor exists
                        if allNotes[prevP].has_key(currP):
                            allNotes[prevP][currP] += 1
                        # if not
                        else:
                            allNotes[prevP][currP] = 1
                        allNotes[prevP][-1] += 1
                    # if not
                    else:
                        allNotes[prevP] = {-1: 1, currP: 1}

                    # if the length exists
                    if tick not in allLengths:
                    	allLengths.append(tick)
                    
                    # set previous pitch to current pitch
                    prevP = currP

                else:
                    prevP = event.data[0]

    avgLength = totalLength / len(files)
    print "Length of upcoming track: ", avgLength

    return avgLength

# Displays pitch neighborhoods and note lengths
# RETURN NONE
def printInfo(allNotes, allLengths):
    print "Note lengths: ", allLengths

    # print out all the neighbors
    for note in allNotes:
        print "Note", note, "-> ",
        for neighbor in allNotes[note]:
            print neighbor, ":", allNotes[note][neighbor], ",",
        print ""
    print ""

    return

# Generates a new melody based on statistics collected from input melodies
# RETURN Pattern object representing new song
def createMusic(allNotes, allLengths, avgLength):
    newPattern = midi.Pattern()
    newTrack = midi.Track()
    newPattern.append(newTrack)

    # Fixed meter
    #newTrack.append(midi.TimeSignatureEvent(tick=0, data=[4, 2, 24, 8]))

    # Generate first note
    firstNote = list(allNotes.keys())[0]
    commonNote = allNotes[firstNote][-1]
    for note in allNotes:
        if allNotes[note][-1] > commonNote:
            commonNote = allNotes[note][-1]
            firstNote = note
    # To determine first length
    firstTick = allLengths[0]
    print "Starts on Note ", firstNote, " at length ", firstTick
    newTrack.append(midi.NoteOnEvent(tick=0, channel=0, data=[firstNote, 80])), #to start the note
    newTrack.append(midi.NoteOnEvent(tick=firstTick, channel=0, data=[firstNote, 0])), #to end the note

    # Add notes to the melodic sequence
    prevN = firstNote # Parent note = first note of song

    # Until the new song is as long as the average length
    i = 0
    while len(newTrack) < avgLength:
        nextN = list(allNotes[prevN].keys())[i] # Key of first neighbor
        if nextN == -1:
        	i += 1
        	continue

        commonNeighbor = allNotes[prevN][nextN] # Occurrance of first neighbor

        # Finding most occurring neighboring note
        for n in allNotes[prevN]:
            if n != -1:
                if allNotes[prevN][n] > commonNeighbor:
                    commonNeighbor = allNotes[prevN][n]
                    nextN = n

        
        prob = float("{0:.2f}".format((float(commonNeighbor) / float(allNotes[prevN][-1])) * 100)) # Percent frequency of most common neighbor
        print "Percent frequency of most common neighbor: ", prob, "%"
        randProb = random.randint(1, 100)

        # Choose most common neighbor that percent of the time, or choose a random note
        if randProb > prob: # If integer is NOT within percentage...
            r = random.randint(0, len(allNotes[prevN]) - 1)
            randNote = list(allNotes[prevN].keys())[r]
            if randNote != -1:
                nextN = randNote

        # Choose note length based on probability
        randI = random.randint(1, len(allLengths))
        divider = len(allLengths) / 4
        l = 0
        if randI < 80:
        	l = random.randint(0, divider)
        else:
        	l = random.randint(divider+1, len(allLengths)-1)
        nextTick = allLengths[l]

        print "Adding Note ", nextN, " at length ", nextTick
        newTrack.append(midi.NoteOnEvent(tick=0, channel=0, data=[nextN, 80])), # To start the note
        newTrack.append(midi.NoteOnEvent(tick=(nextTick), channel=0, data=[nextN, 0])), # To end the note   
        
        prevN = nextN # Move forward in sequence
        i = 0 # Reset index for next iteration


    # Officially end the song
    finalNote = firstNote
    finalLength = allLengths[len(allLengths)-1]
    print "Ends on Note ", finalNote, " at length ", finalLength
    newTrack.append(midi.NoteOnEvent(tick=0, channel=0, data=[finalNote, 80])), # To start the note
    newTrack.append(midi.NoteOnEvent(tick=finalLength, channel=0, data=[finalNote, 0])), # To end the note
    newTrack.append(midi.EndOfTrackEvent(tick=1))

    return newPattern