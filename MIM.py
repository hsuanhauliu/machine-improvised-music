import midi
import random

def run() :
    MAXSIZE = 128

    # Initializing dictionaries
    allNotes = {}
    allLengths = {} # TO DO

    totalLength = 0 # Sum of all track lengths

    # Import MIDI files
    pattern = midi.read_midifile("melody1.mid")
    track = pattern[0]

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
                
                # set previous pitch to current pitch
                prevP = currP
                #print "Tick={}, Note={}".format(tick, currP)
            else:
                prevP = event.data[0]

    totalLength = totalLength + len(track) # Will make more sense when there's more than one file
    avgLength = totalLength # CHANGE TO: avgLength = totalLength / len(files)
    print "Length of upcoming track: ", avgLength

    # print out all the neighbors
    for note in allNotes:
        print "Note", note, "-> ",
        for neighbor in allNotes[note]:
            print neighbor, ":", allNotes[note][neighbor], ",",
        print ""


    # Process





    # Produce new music
    newPattern = midi.Pattern()
    newTrack = midi.Track()
    newPattern.append(newTrack)

    #Generate first note
    firstNote = list(allNotes.keys())[0]
    commonNote = allNotes[firstNote][-1]
    for note in allNotes:
        if allNotes[note][-1] > commonNote:
            commonNote = allNotes[note][-1]
            firstNote = note
    newTrack.append(midi.NoteOnEvent(tick=0, channel=0, data=[firstNote, 80])), #to start the note
    newTrack.append(midi.NoteOnEvent(tick=239, channel=0, data=[firstNote, 0])), #to end the note

    # Add notes based on probability
    prevN = firstNote # Parent note = first note of song

    # Until the new song is as long as the average length
    while len(newTrack) < avgLength:
        nextN = list(allNotes[prevN].keys())[0] # Key of first neighbor
        commonNeighbor = allNotes[prevN][nextN] # Occurrance of first neighbor

        # Finding most occurring neighboring note
        for n in allNotes[prevN]:
            if n != -1:
                if allNotes[prevN][n] > commonNeighbor:
                    commonNeighbor = allNotes[prevN][n]
                    nextN = n

        prob = (commonNeighbor / allNotes[prevN][-1]) * 100 # Percent frequency of most common neighbor
        randProb = random.randint(1, 100)

        #Choose most common neighbor second that percent of the time, or choose a random note
        if randProb < prob:
            newTrack.append(midi.NoteOnEvent(tick=0, channel=0, data=[nextN, 80])), # To start the note
            newTrack.append(midi.NoteOnEvent(tick=239, channel=0, data=[nextN, 0])), # To end the note
        else:
            r = random.randint(0, len(allNotes[prevN]) - 1)
            randNote = list(allNotes[prevN].keys())[r]
            if randNote != -1:
                nextN = randNote
                newTrack.append(midi.NoteOnEvent(tick=0, channel=0, data=[nextN, 80])), # To start the note
                newTrack.append(midi.NoteOnEvent(tick=239, channel=0, data=[nextN, 0])), # To end the note    
        prevN = nextN #Move forward in sequence

    # Officially end the song
    newTrack.append(midi.EndOfTrackEvent(tick=1))

    # Export MIDI file.
    midi.write_midifile("aiSong.mid", newPattern)

    return

run()
