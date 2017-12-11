import midi
import operator
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
    os.chdir("musicInput")   # change directory
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
    # end of files loop

    allTicks = sorted(allTicks)

    print "Number of songs learned so far: ", numOfSongs
    avgNotes = 0
    if numOfSongs != 0:
        avgNotes = numOfNotes / numOfSongs # CHANGE TO: avgLength = totalLength / len(files)
        print "Average number of notes: ", avgNotes #test - to be deleted
    print ""

    os.chdir("..")  # move back to previous directory

    # remember the songs
    wFile = open("learned_songs.txt", "w")

    wFile.write(str(numOfNotes))
    wFile.write("\n")
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

# First method: single note approach
#   Neighbor: choosing based on probability (occurances / total).
#   Tick: randomly choosing among the set.
#   First Note: most common note.
#   First Tick: shortest tick in the set.
#   End Note:   starting note.
#   Results:
#       1. First thing we notice is that some ticks are way too long.
#           - Solution: choose a certain range of ticks in the set.
#       2. Fixed the problem where some notes are much longer than others.
#          However, since the tick of each note is randomly selected, the song
#          doesn't have any rhythm.
#       3. The notes sound okay, but not great. I wonder if we could do better.
def createOccurrenceBasedMusic(allNotes, allTicks, avgLength):
    # generate new song
    newPattern = midi.Pattern()
    newTrack = midi.Track()
    newPattern.append(newTrack)

    # pick the note with most occurances as the first note
    startNote = allNotes.keys()[0]  # use the very first note and compare
    startTick = sorted(allTicks)[0] # use the shortest tick

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
    midi.write_midifile("ai_occurrenceBased.mid", newPattern)  # export midi file

    return

# Second method: measure approach
#   Neighbor: choose neighbor based on probability.
#   Tick: use the median of the tick set to create a set that contains a quarter
#         note, half note, and eighth note. Randomly pick a note that does not 
#         exceed the measure length.
#   First Note: most common note.
#   First Tick: shortest tick in the set.
#   End Note:   starting note.
#   Description:
#       Create sets of notes to simulate each measure, and randomly pick
#       among the set. Number of notes in each measure is set to be eight,
#       since each measure can have at most eight notes (8 eighth notes).
#       For the length limit that we set, 12 sets of measure seen to work
#       okay. Ticks are calculated using the median of tick set mentioned
#       above.
#   Results:
#       1. Certain ticks sound better than random ticks. Big improvement.
#       2. The notes sound better as well.
def createMeasureBasedMusic(allNotes, allTicks, avgLength):
    # generate new song
    newPattern = midi.Pattern()
    newTrack = midi.Track()
    newPattern.append(newTrack)

    # pick the note with most occurances as the first note
    startNote = allNotes.keys()[0]  # use the very first note and compare
    startTick = sorted(allTicks)[0]         # use the shortest tick

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

    # make __ sets
    for _ in range(12):
        notes = []

        # each set has __ notes
        for _ in range(8):
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

    # randomly pick a tick from allTricks list
    medianTick = float(allTicks[len(allTicks)/2])  # define as the quarter note
    setOfTicks = [medianTick, medianTick / 2, medianTick * 2]
    measureLength = medianTick * 4

    # add measures until it reaches minimum length
    while len(newTrack) < avgLength:
       # choose a random set of notes
        singleSet = sample(setsOfNotes, 1)[0]
        sumOfMeasureLength = 0

        for i in singleSet:
            if sumOfMeasureLength == measureLength:
                break

            # choose a random tick from the set
            singleTick = sample(setOfTicks, 1)[0]

            # add the next note
            newTrack.append(midi.NoteOnEvent(tick = 0, channel = 0, data = [i, 80]))

            # choose another tick if the sum is too long

            while measureLength < sumOfMeasureLength + singleTick:
                singleTick = sample(setOfTicks, 1)[0]
            newTrack.append(midi.NoteOnEvent(tick = int(singleTick) / 2, channel = 0, data = [i, 0]))
            sumOfMeasureLength += singleTick
        # end of for loop
    # end of while loop

    # set starting note as end note
    newTrack.append(midi.NoteOnEvent(tick = 0, channel = 0, data = [startNote, 80]))
    newTrack.append(midi.NoteOnEvent(tick = int(measureLength) / 2, channel = 0, data = [startNote, 0]))
    
    newTrack.append(midi.EndOfTrackEvent(tick = 1))     # end the track
    midi.write_midifile("ai_measureBased.mid", newPattern)     # export midi file

    return


# Third method: traditional Hill Climbing approach, with random reset
#   Neighbor: choose the most frequent neighbor.
#   Tick: use the median of the tick set to create a set that contains a quarter
#         note, half note, and eighth note. Randomly pick a note that does not 
#         exceed the measure length.
#   First Note: random note.
#   First Tick: shortest tick in the set.
#   End Note:   best neighbor at the time when it reaches optima.
#   Description:
#       Greedily choose a neighbor based on occurances. Random reset a starting
#       point if the best neighbor cannot improve, as long as it's within the
#       time limit.
#   Results:
#       The notes seem to sound okay. Occasionally the program does choose weird
#       neighbor as the next note. This is probably affect by the input midi
#       files. Performance is not better than the previous method. Also, the
#       ending note sounds random.
def createHillClimbingMusic(allNotes, allTicks, avgLength):
    # generate new song
    newPattern = midi.Pattern()
    newTrack = midi.Track()
    newPattern.append(newTrack)

    # pick the note with most occurances as the first note
    startNote = sample(allNotes.keys(), 1)[0]   # use random note to start
    startTick = sorted(allTicks)[0]             # use the shortest tick
    newTrack.append(midi.NoteOnEvent(tick = 0, channel = 0, data = [startNote, 80]))
    newTrack.append(midi.NoteOnEvent(tick = int(startTick) / 2, channel = 0, data = [startNote, 0]))
    
    # randomly pick a tick from allTicks list
    medianTick = float(allTicks[len(allTicks)/2])  # define as the quarter note
    setOfTicks = [medianTick, medianTick / 2, medianTick * 2]
    measureLength = medianTick * 4
    sumOfMeasureLength = 0
    goalFound = False

    # keep track of previous note and current note
    prevNote = startNote
    currNote = 0

    # hill climbing starts
    while goalFound == False or len(newTrack) < avgLength:
        # find best neighbor
        neighborhood = allNotes[prevNote].items()
        neighborhood.sort(key = operator.itemgetter(1), reverse = True)
        if neighborhood[0][0] == -1:
            currNote = neighborhood[1][0]
        else:
            currNote = neighborhood[0][0]

        # if the neighbor doesn't improves current note, random restart
        if allNotes[currNote][-1] <= allNotes[prevNote][-1]:
            currNote = sample(allNotes.keys(), 1)[0]
            goalFound = True
            if len(newTrack) >= avgLength:
                break
        else:
            goalFound = False
        newTrack.append(midi.NoteOnEvent(tick = 0, channel = 0, data = [currNote, 80]))

        # now choose a tick
        if sumOfMeasureLength == measureLength:
            sumOfMeasureLength = 0  # reset sum

        singleTick = sample(setOfTicks, 1)[0]   # pick a random tick from the set
        while measureLength < sumOfMeasureLength + singleTick:
            singleTick = sample(setOfTicks, 1)[0]
        sumOfMeasureLength += singleTick

        newTrack.append(midi.NoteOnEvent(tick = int(singleTick) / 2, channel = 0, data = [currNote, 0]))
        prevNote = currNote
    
    newTrack.append(midi.EndOfTrackEvent(tick = 1))     # end the track
    midi.write_midifile("ai_hillClimbing.mid", newPattern)     # export midi file

    return
