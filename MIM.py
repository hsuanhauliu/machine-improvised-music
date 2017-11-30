import midi


def run() :
    MAXSIZE = 128

    # Initializing dictionaries
    allNotes = {}

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

    # print out all the neighbors
    for note in allNotes:
        print "Note", note, "-> ",
        for neighbor in allNotes[note]:
            print neighbor, ":", allNotes[note][neighbor], ",",
        print ""


    # Process





    # Produce new music





    # Export MIDI file.





    return

run()
