import midi
import random
import glob, os # os.chdir(), glob.glob()


def listen():
    # Variables
    totalLength = 0 # Sum of all track lengths
    numOfSongs = 0  # Calculate how many songs that
    allNotes = {}
    knownSongs = []

    if os.path.isfile("learned_songs.txt"):
        with open("learned_songs.txt", "r") as rFile:
            knownSongs = rFile.read().splitlines()
            rFile.close()

    wFile = open("learned_songs.txt", "w")

    # Grab all the MIDI files
    os.chdir("music")   # change directory
    for file in glob.glob("*.mid"):
        wFile.write(file)
        wFile.write("\n")

        if file in knownSongs:
            continue

        print "Learning a new song..."
        pattern = midi.read_midifile(file)  # Import MIDI files
        numOfSongs += 1
        track = pattern[0]

        # Grab information for each note
        prevP = -1

        for event in track:
            if event.name == 'Note On' and event.data[1] == 0:
                if prevP != -1:
                    # get data of current note
                    tick = event.tick
                    currP = event.data[0]

                    if prevP in allNotes:
                        # if the neighbor exists
                        if currP in allNotes[prevP]:
                            allNotes[prevP][currP] += 1
                        # if not
                        else:
                            allNotes[prevP][currP] = 1
                        allNotes[prevP][-1] += 1
                    # if not
                    else:
                        print "what..."
                        allNotes[prevP] = {-1: 1, currP: 1}

                    # set previous pitch to current pitch
                    prevP = currP
                    #print "Tick={}, Note={}".format(tick, currP)
                else:
                    prevP = event.data[0]
        # end of track loop
        totalLength = totalLength + len(track) # Will make more sense when there's more than one file
    # end of files loop

    print "Number of songs learned: ", numOfSongs
    if numOfSongs != 0:
        avgLength = totalLength / numOfSongs # CHANGE TO: avgLength = totalLength / len(files)
        print "Average length: ", avgLength #test - to be deleted
    print ""

    os.chdir("..")  # move back to previous directory
    wFile.close()

    return allNotes

# Do statistical analysis on a single song
def singleSong(fileName):
    allNotes = {}
    pattern = midi.read_midifile(fileName)  # Import MIDI file
    print fileName, "statistics"
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
                if prevP in allNotes:
                    # if the neighbor exists
                    if currP in allNotes[prevP]:
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
    printNotes(allNotes)
    return

# Print out all the notes and their neighbors
def printNotes(allNotes):
    for note in allNotes:
        print "Note", note, " |",
        for neighbor in allNotes[note]:
            print neighbor, ":", allNotes[note][neighbor], "|",
        print ""
    print ""
    return

# Save the statistic data
def memorize(allNotes):
    print "Memorizing what I've learned so far...\n"
    wFile = open("brain.txt", "w")

    for note in allNotes:
        wFile.write(str(note))
        wFile.write(" ")
        for neighbor in allNotes[note]:
            wFile.write(str(neighbor))
            wFile.write(" ")
            wFile.write(str(allNotes[note][neighbor]))
            wFile.write(" ")
        wFile.write("\n")

    wFile.close()
    return

# Input the statistic data
def recall():
    allNotes = {}
    if os.path.isfile("brain.txt"):
        print "I know a few songs! Let me recall...\n"
        rFile = open("brain.txt", "r")
        lines = rFile.readlines()
        for l in lines:
            currLine = l.split(" ")
            currNote = currLine[0]
            allNotes[currNote] = {}
            for neighbor in range(1, len(currLine) - 1, 2):
                allNotes[currNote][currLine[neighbor]] = currLine[neighbor + 1]

        rFile.close()
    return allNotes

# TO BE COMPLETED
def merge_dicts(oldDict, newDict):
    combinedDict = oldDict.copy()
    for note in newDict:
        if note in combinedDict:
            for neighbor in newDict:
                if neighbor in conbinedDict:
                    combinedDict[note][neighbor] += newDict[note][neighbor]
                else:
                    
                    combinedDict[note][neighbor] = newDict[note][neighbor]

    return

def main() :
    # Variables
    allLengths = {} # TO DO
    allNotes = {}
    newNotes = {}

    allNotes = recall() # input statistical data from previous runs, if exists
    if os.path.isfile("brain.txt"):
        newNotes = listen()     # read input songs

        
    printNotes(allNotes)    # show all notes and their neighbors
    memorize(allNotes)      # remember what it has learned so far
    #singleSong("music/melody1.mid")

    # Process





    return

if __name__ == '__main__':
    import sys
    main()
