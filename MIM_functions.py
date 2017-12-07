import midi
from random import random
from random import sample
import glob, os # os.chdir(), glob.glob()


def listen(allNotes, allTicks):
    # Variables
    numOfNotes = 0  # total number of notes in all learned songs
    numOfSongs = 0  # count number of songs learned
    knownSongs = []

    if os.path.isfile("learned_songs.txt"):
        with open("learned_songs.txt", "r") as rFile:
            knownSongs = rFile.read().splitlines()
            rFile.close()
        numOfNotes = int(knownSongs[0])
        numOfSongs = int(knownSongs[1])

        # remove the first three lines
        for _ in range(3):
            del knownSongs[0]

    # Grab all the MIDI files
    os.chdir("music")   # change directory
    for file in glob.glob("*.mid"):
        # skip if the program has already learned the song
        if file in knownSongs:
            continue

        knownSongs.append(file)
        print "Learning a new song..."
        pattern = midi.read_midifile(file)      # Import MIDI files
        track = pattern[0]                      # target the first track
        numOfNotes = numOfNotes + len(track)    # add the number of notes in this song
        numOfSongs += 1

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
                        allNotes[prevP] = {-1: 1, currP: 1}

                    # track ticks
                    if tick not in allTicks:
                        allTicks.append(tick)

                    # set previous pitch to current pitch
                    prevP = currP
                else:
                    prevP = event.data[0]
        # end of track loop
        
        # keep track of number of notes in each song
    # end of files loop

    allTicks = sorted(allTicks)

    # remember the songs
    wFile = open("learned_songs.txt", "w")

    print "Write notes", numOfNotes
    wFile.write(str(numOfNotes))
    wFile.write("\n")
    print "Write numOfSongs", numOfSongs
    wFile.write(str(numOfSongs))
    wFile.write("\n")

    for tick in allTicks:
        wFile.write(str(tick))
        wFile.write(" ")

    wFile.write("\n")
    for song in knownSongs:
        wFile.write(song)
        wFile.write("\n")

    wFile.close()

    print "Number of songs learned so far: ", numOfSongs
    avgNotes = 0
    if numOfSongs != 0:
        avgNotes = numOfNotes / numOfSongs # CHANGE TO: avgLength = totalLength / len(files)
        print "Average number of notes: ", avgNotes #test - to be deleted
    print ""

    os.chdir("..")  # move back to previous directory

    return avgNotes

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
def recall(allNotes, allTicks):
    if os.path.isfile("brain.txt"):
        print "I know a few songs! Let me recall...\n"
        rFile = open("brain.txt", "r")
        lines = rFile.readlines()
        for l in lines:
            currLine = l.split(" ")
            currNote = int(currLine[0])
            allNotes[currNote] = {}
            for neighbor in range(1, len(currLine) - 1, 2):
                allNotes[currNote][int(currLine[neighbor])] = int(currLine[neighbor + 1])

        rFile.close()

    if os.path.isfile("learned_songs.txt"):
        rFile = open("learned_songs.txt", "r")
        lines = rFile.readlines()
        line = lines[2].strip()     # get rid of \n
        ticks = line.split(" ")  # target the 3rd line
        for tick in ticks:
            allTicks.append(int(tick))

        rFile.close()
    return

def makeMusic1(allNotes, allTicks, avgLength):
    # generate new song
    newPattern = midi.Pattern()
    newTrack = midi.Track()
    newPattern.append(newTrack)

    # pick the note with most occurances as the first note
    startNote = allNotes.keys()[0]  # use the very first note and compare
    startTick = allTicks[0]         # use the shortest tick

    # go through all notes
    for note in allNotes:
        # if the note has higher occurances than the current startNote, replace it
        if allNotes[note][-1] > allNotes[startNote][-1]:
            startNote = note

    # add the first note and tick to the track
    newTrack.append(midi.NoteOnEvent(tick = 0, channel = 0, data = [startNote, 80]))
    newTrack.append(midi.NoteOnEvent(tick = startTick, channel = 0, data = [startNote, 0]))

    # add the next note
    prevNote = startNote
    currNote = 0

    while len(newTrack) < avgLength or currNote != startNote:
        randomNum = random()    # generate a random number between 0 and 1
        sumOfProb = 0           # keep track of total probability

        while True:
            randNeighbor = sample(allNotes[prevNote].keys(), 1)[0]
            while randNeighbor == -1:
                randNeighbor = sample(allNotes[prevNote].keys(), 1)[0]

            # calculate the probability of choosing this note
            prob = allNotes[prevNote][randNeighbor] / float(allNotes[prevNote][-1]) + sumOfProb

            if randomNum > prob:
                sumOfProb += prob    # increase the probability of choosing the next note
            else:
                currNote = randNeighbor         # choose this neighbor
                break
        
        # randomly pick a tick from allTricks list
        currTick = sample(allTicks, 1)[0]

        # add next note and tick to the track
        newTrack.append(midi.NoteOnEvent(tick = 0, channel = 0, data = [currNote, 80]))
        newTrack.append(midi.NoteOnEvent(tick = currTick / 2, channel = 0, data = [currNote, 0]))

        prevNote = currNote
    # end of while loop
    
    newTrack.append(midi.EndOfTrackEvent(tick = 1)) # end the track
    midi.write_midifile("ai_song1.mid", newPattern)  # export midi file

    return

def makeMusic2(allNotes, allTicks, avgLength):
    # generate new song
    newPattern = midi.Pattern()
    newTrack = midi.Track()
    newPattern.append(newTrack)

    # pick the note with most occurances as the first note
    startNote = allNotes.keys()[0]  # use the very first note and compare
    startTick = allTicks[0]         # use the shortest tick

    # go through all notes
    for note in allNotes:
        # if the note has higher occurances than the current startNote, replace it
        if allNotes[note][-1] > allNotes[startNote][-1]:
            startNote = note

    # add the first note and tick to the track
    newTrack.append(midi.NoteOnEvent(tick = 0, channel = 0, data = [startNote, 80]))
    newTrack.append(midi.NoteOnEvent(tick = startTick, channel = 0, data = [startNote, 0]))

    # add the next note
    prevNote = startNote
    setsOfNotes = []   # sets of notes

    # make four sets
    for _ in range(4):
        notes = []

        # each set has four notes
        for _ in range(4):
            randomNum = random()    # generate a random number between 0 and 1
            sumOfProb = 0           # keep track of total probability

            while True:
                # pick a random neighbor that is not -1
                randNeighbor = sample(allNotes[prevNote].keys(), 1)[0]
                while randNeighbor == -1:
                    randNeighbor = sample(allNotes[prevNote].keys(), 1)[0]

                # calculate the probability of choosing this note
                prob = allNotes[prevNote][randNeighbor] / float(allNotes[prevNote][-1]) + sumOfProb

                if randomNum > prob:
                    sumOfProb += prob       # increase the probability of choosing the next note
                else:
                    notes.append(randNeighbor)
                    prevNote = randNeighbor
                    break
        # end of inner for loop
        setsOfNotes.append(notes)
    # end of outer for loop
        
    while len(newTrack) < avgLength:
        # randomly pick a tick from allTricks list
        currTick = sample(allTicks, 1)[0]
        # choose a random set of notes
        singleSet = sample(setsOfNotes, 1)[0]

        for s in singleSet:
            newTrack.append(midi.NoteOnEvent(tick = 0, channel = 0, data = [s, 80]))
            newTrack.append(midi.NoteOnEvent(tick = currTick / 2, channel = 0, data = [s, 0]))
    # end of while loop
    
    newTrack.append(midi.EndOfTrackEvent(tick = 1)) # end the track
    midi.write_midifile("ai_song2.mid", newPattern)  # export midi file

    return
