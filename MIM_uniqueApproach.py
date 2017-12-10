import midi
import random
import operator
import os

# Obtains input files from "music" directory
# RETURN list containing all input files
def getMusic():
    path = "musicInput" # Specific name of directory containing input .mid files
    fil = os.listdir(path)

    return fil

# Listens to input files and learns note information
# RETURN int representing length of song to be generated
def listen(files, allNotes, allLengths):
    totalLength = 0 # Sum of all track lengths

    for f in files:
        pattern = midi.read_midifile(f) # Import each MIDI file as a Pattern object
        track = pattern[0] # Contains information about musical events

        totalLength = totalLength + len(track) # Add to sum of track lengths

        # Grab information for each note
        prevP = -1 # Placeholder note

        for event in track: # For each "Note" event
            if event.name == 'Note On' and event.data[1] == 0:
                if prevP != -1: # Only focus on successor notes
                    tick = event.tick # Get data of immediate successor note
                    currP = event.data[0] 
                                    
                    if allNotes.has_key(prevP): # If the note exists                        
                        if allNotes[prevP].has_key(currP): # If the neighbor exists
                            allNotes[prevP][currP] += 1 # Increment the occurrance of that neighbor
                        else:
                            allNotes[prevP][currP] = 1 # Add pitch to the neighborhood
                        allNotes[prevP][-1] += 1 # Increment total number of successors for prevP
                    else: # If note does not exist
                        allNotes[prevP] = {-1: 1, currP: 1}

                    # Add each unique note length to the length list
                    if tick not in allLengths:
                    	allLengths.append(tick)
                    
                    # Move from previous pitch to successor pitch
                    prevP = currP

                else: # If prevP is the placeholder value of -1
                    prevP = event.data[0] # Set prevP = first note of input song

    avgLength = totalLength / len(files) # Average of all song lengths determines length of song to be generated
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
#   -Determines PITCH by selecting the most common neighbor note of the current note
#   -Determines note LENGTH by selecting a relatively short fixed length value 
# RETURN Pattern object representing new song
def createGreedyMusic(allNotes, allLengths, avgLength):

    # Initialize Pattern object including track list of note events
    newPattern = midi.Pattern()
    newTrack = midi.Track()
    newPattern.append(newTrack)

    # Generate first note (most common note in dictionary)
    firstNote = list(allNotes.keys())[0] # Pick first note of the whole directory
    commonNote = allNotes[firstNote][-1] # Get its occurrance
    for note in allNotes:
        if allNotes[note][-1] > commonNote: # Find a note with higher occurrance
            commonNote = allNotes[note][-1]
            firstNote = note

    length = allLengths[len(allLengths) / 4] # For sake of testing this approach, note lengths will be fixed at relatively short length

    newTrack.append(midi.NoteOnEvent(tick=0, channel=0, data=[firstNote, 80])) # To start the note
    newTrack.append(midi.NoteOnEvent(tick=length, channel=0, data=[firstNote, 0])) # To end the note

    # Add tracks based on greedy approach
    prevN = firstNote # Point to first note of song
    while len(newTrack) < avgLength: # Until song reaches appropriate length
        nextN = list(allNotes[prevN].keys())[0] # Get note value of first neighbor
        if nextN == -1:
            nextN = list(allNotes[prevN].keys())[1] # Pick next note if first neighbor is -1
        commonNeighbor = allNotes[prevN][nextN] # Get its occurrance within its neighborhood
        for n in allNotes[prevN]:
            if n != -1:
                if allNotes[prevN][n] > commonNeighbor: # Find successor note with higher occurrance
                    commonNeighbor = allNotes[prevN][n]
                    nextN = n

        newTrack.append(midi.NoteOnEvent(tick=0, channel=0, data=[nextN, 80])) # To start the note
        newTrack.append(midi.NoteOnEvent(tick=length, channel=0, data=[nextN, 0])) # To end the note
            
        prevN = nextN # Move from previous note to successor note

    # Signals the end of the song
    newTrack.append(midi.EndOfTrackEvent(tick=1))

    # Export MIDI file.
    midi.write_midifile("ai_greedySong.mid", newPattern)

    return newPattern

# Generates a new melody based on statistics collected from input melodies
#   -Determines PITCH by selecting the most common neighbor note of the current note
#    75% of the time, and selecting a random note otherwise
#   -Determines note LENGTH by selecting a relatively short fixed length value
# RETURN Pattern object representing new song
def createFixedProbabilityMusic(allNotes, allLengths, avgLength):
    
    # Initialize Pattern object including track list of note events
    newPattern = midi.Pattern()
    newTrack = midi.Track()
    newPattern.append(newTrack)

    # Generate first note (most common note in dictionary)
    firstNote = list(allNotes.keys())[0] # Pick first note of the whole directory
    commonNote = allNotes[firstNote][-1] # Get its occurrance
    for note in allNotes:
        if allNotes[note][-1] > commonNote: # Find a note with higher occurrance
            commonNote = allNotes[note][-1]
            firstNote = note

    length = allLengths[len(allLengths) / 4] # For sake of testing this approach, note lengths will be fixed at relatively short length
            
    newTrack.append(midi.NoteOnEvent(tick=0, channel=0, data=[firstNote, 80])) # To start the note
    newTrack.append(midi.NoteOnEvent(tick=length, channel=0, data=[firstNote, 0])) # To end the note

    # Add tracks based on fixed probability
    prevN = firstNote # Point to first note of song
    while len(newTrack) < avgLength: # Until song reaches appropriate length
        nextN = list(allNotes[prevN].keys())[0] # Get note value of first neighbor
        if nextN == -1:
            nextN = list(allNotes[prevN].keys())[1] # Pick next note if first neighbor is -1
        commonNeighbor = allNotes[prevN][nextN] # Get its occurrance within its neighborhood
        for n in allNotes[prevN]:
            if n != -1:
                if allNotes[prevN][n] > commonNeighbor: # Find successor note with higher occurrance
                    commonNeighbor = allNotes[prevN][n]
                    nextN = n

        # Determining probability value
        randProb = random.randint(1, 100)

        # Pick most common successor note 75% of the time, otherwise pick a random note
        if randProb > 75: # If integer is NOT within percentage
            r = random.randint(0, len(allNotes[prevN]) - 1)
            randNote = list(allNotes[prevN].keys())[r]
            while randNote == -1: # Choose a different random value if current value is -1
                r = random.randint(0, len(allNotes[prevN]) - 1)
                randNote = list(allNotes[prevN].keys())[r]
            nextN = randNote # Reassign next note

        newTrack.append(midi.NoteOnEvent(tick=0, channel=0, data=[nextN, 80])) # To start the note
        newTrack.append(midi.NoteOnEvent(tick=length, channel=0, data=[nextN, 0])) # To end the note    
        
        prevN = nextN # Move from previous note to successor note

    # Signals the end of the song
    newTrack.append(midi.EndOfTrackEvent(tick=1))

    # Export MIDI file.
    midi.write_midifile("ai_fixedProbSong.mid", newPattern)

    return newPattern

# Generates a new melody based on statistics collected from input melodies
#   -Determines PITCH by selecting the most common neighbor based on a calculated probability,
#    and selcting a random note otherwise
#   -Determines note LENGTH by selecting a relatively short fixed length value
def createDynamicProbabilityMusic(allNotes, allLengths, avgLength):

    # Initialize Pattern object including track list of note events
    newPattern = midi.Pattern()
    newTrack = midi.Track()
    newPattern.append(newTrack)

    # Generate first note (most common note in dictionary)
    firstNote = list(allNotes.keys())[0] # Pick first note in the whole dictionary
    commonNote = allNotes[firstNote][-1] # Get its occurrance
    for note in allNotes:
        if allNotes[note][-1] > commonNote: # Find a note with higher occurrance
            commonNote = allNotes[note][-1]
            firstNote = note

    length = allLengths[len(allLengths) / 4] # For sake of testing this approach, note lengths will be fixed at relatively short length

    newTrack.append(midi.NoteOnEvent(tick=0, channel=0, data=[firstNote, 80])) # To start the note
    newTrack.append(midi.NoteOnEvent(tick=length, channel=0, data=[firstNote, 0])) # To end the note

    # Add notes based on probability of most common successor note
    prevN = firstNote # Point to first note of the song
    while len(newTrack) < avgLength: # Until song reaches appropriate length
        nextN = list(allNotes[prevN].keys())[0] # Get note value of first neighbor
        if nextN == -1:
            nextN = list(allNotes[prevN].keys())[1] # Pick next note if first neighbor is -1
        commonNeighbor = allNotes[prevN][nextN] # Get its occurrance within its neighborhood
        for n in allNotes[prevN]:
            if n != -1:
                if allNotes[prevN][n] > commonNeighbor: # Find successor note with higher occurrance
                    commonNeighbor = allNotes[prevN][n]
                    nextN = n

        # Determining probability value
        prob = float("{0:.2f}".format((float(commonNeighbor) / float(allNotes[prevN][-1])) * 100)) # Percent frequency of most common neighbor
        randProb = random.randint(1, 100)

        # Choose most common neighbor that percent of the time, or choose a random note
        if randProb > prob: # If integer is NOT within percentage
            r = random.randint(0, len(allNotes[prevN]) - 1)
            randNote = list(allNotes[prevN].keys())[r]
            while randNote == -1: # Choose a different random value if current value is -1
                r = random.randint(0, len(allNotes[prevN]) - 1)
                randNote = list(allNotes[prevN].keys())[r]
            nextN = randNote # Reassign next note

        newTrack.append(midi.NoteOnEvent(tick=0, channel=0, data=[nextN, 80])) # To start the note
        newTrack.append(midi.NoteOnEvent(tick=length, channel=0, data=[nextN, 0])) # To end the note    
       
        prevN = nextN # Move from previous note to successor note

    # Signals the end of the song
    newTrack.append(midi.EndOfTrackEvent(tick=1))

    # Export MIDI file.
    midi.write_midifile("ai_dynamicProbSong.mid", newPattern)

    return newPattern

# Generates a new melody based on statistics collected from input melodies
#   -Determines PITCH by selecting the most common neighbor based on a calculated probability,
#    and selcting a random note otherwise
#   -Determines note LENGTH by selecting a random shorter note length 90% of the time,
#    and selecting a longer note length otherwise 
# RETURN Pattern object representing new song
def createMusic(allNotes, allLengths, avgLength):
    
    # Initialize Pattern object including track list of note events
    newPattern = midi.Pattern()
    newTrack = midi.Track()
    newPattern.append(newTrack)

    # Generate first note (most common note in the dictionary)
    firstNote = list(allNotes.keys())[0] # Pick first note in the whole dictionary
    commonNote = allNotes[firstNote][-1] # Get its occurrance
    for note in allNotes:
        if allNotes[note][-1] > commonNote: # Find a note with higher occurrance
            commonNote = allNotes[note][-1]
            firstNote = note

    # Generate first length
    firstTick = allLengths[0]

    print "Starts on Note ", firstNote, " at length ", firstTick # Begin displaying musical sequence resulting from this approach
    newTrack.append(midi.NoteOnEvent(tick=0, channel=0, data=[firstNote, 80])) # To start the note
    newTrack.append(midi.NoteOnEvent(tick=firstTick, channel=0, data=[firstNote, 0])) # To end the note

    # Add notes based on probability of most common successor note
    prevN = firstNote # Point to first note of the song
    while len(newTrack) < avgLength: # Until the song reaches appropriate length
        nextN = list(allNotes[prevN].keys())[0] # Get note value of first neighbor
        if nextN == -1:
            nextN = list(allNotes[prevN].keys())[1] # Pick next note if first neighbor is -1
        commonNeighbor = allNotes[prevN][nextN] # Get its occurrance within its neighborhood
        for n in allNotes[prevN]:
            if n != -1:
                if allNotes[prevN][n] > commonNeighbor: # Find successor note with higher occurrance
                    commonNeighbor = allNotes[prevN][n]
                    nextN = n

        # Determining probability value
        prob = float("{0:.2f}".format((float(commonNeighbor) / float(allNotes[prevN][-1])) * 100)) # Percent frequency of most common neighbor
        print "Percent frequency of most common neighbor: ", prob, "%" # Display calculated probability
        randProb = random.randint(1, 100)

        # Choose most common neighbor that percent of the time, or choose a random note
        if randProb > prob: # If integer is NOT within percentage...
            r = random.randint(0, len(allNotes[prevN]) - 1)
            randNote = list(allNotes[prevN].keys())[r]
            while randNote == -1: # Choose a different random value if current value is -1
                r = random.randint(0, len(allNotes[prevN]) - 1)
                randNote = list(allNotes[prevN].keys())[r]
            nextN = randNote # Reassign next note

        # Choose shorter note length 90% of the time; otherwise choose longer note length
        randI = random.randint(1, 100)
        divider = len(allLengths) / 4 # Divides length list into four sections
        l = 0
        if randI < 90:
            l = random.randint(0, divider) # Choose within the first quarter of note lengths
        else:
            l = random.randint(divider+1, len(allLengths)-1) # Choose among the longer note lengths
        nextTick = allLengths[l]

        print "Adding Note ", nextN, " at length ", nextTick # Display progress of musical sequence generated by this approach
        newTrack.append(midi.NoteOnEvent(tick=0, channel=0, data=[nextN, 80])) # To start the note
        newTrack.append(midi.NoteOnEvent(tick=nextTick, channel=0, data=[nextN, 0])) # To end the note   
        
        prevN = nextN # Move from previous note to successor note

    # Add a long final note to close the song
    finalNote = firstNote # Last note is the same as the first note
    finalLength = allLengths[len(allLengths)-1] # Last note has the longest length
    print "Ends on Note ", finalNote, " at length ", finalLength # Shows end of the musical sequence generated by this approach
    newTrack.append(midi.NoteOnEvent(tick=0, channel=0, data=[finalNote, 80])) # To start the note
    newTrack.append(midi.NoteOnEvent(tick=finalLength, channel=0, data=[finalNote, 0])) # To end the note

    # Signals the end of the song
    newTrack.append(midi.EndOfTrackEvent(tick=1))

    # Export MIDI file.
    midi.write_midifile("ai_optimalSong.mid", newPattern)

    return newPattern
