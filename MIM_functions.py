import midi

import operator
from random import random, sample
import glob, os


def generate_music(input_path, output_path, save_songs=False, verbose=False, load=False):
    """ Generate music """
    all_notes, all_lengths, ave_length = {}, [], 0

    if load:
        load_data(all_notes, all_lengths)

    num_notes, num_songs = train(input_path, all_notes, all_lengths, save_songs=save_songs)
    avg_length = num_notes // num_songs

    if verbose:
        printNotes(all_notes)

    if save_songs:
        memorize(all_notes)

    createOccurrenceBasedMusic(all_notes, all_lengths, avg_length)
    createMeasureBasedMusic(all_notes, all_lengths, avg_length)
    createHillClimbingMusic(all_notes, all_lengths, avg_length)

    if verbose:
        print "Finished generating music"


def load_data(all_notes, all_ticks, brain_file="brain.txt", songs_file="learned_songs.txt"):
    """ Load past training data """
    if os.path.isfile("brain.txt"):
        with open(brain_file, "r") as r_file:
            r_file = open(brain_file, "r")
            for l in r_file.readlines():
                currLine = l.split(" ")
                currNote = int(currLine[0])
                all_notes[currNote] = {}
                for neighbor in range(1, len(currLine) - 1, 2):
                    all_notes[currNote][int(currLine[neighbor])] = int(currLine[neighbor + 1])

    if os.path.isfile(songs_file):
        with open(songs_file, "r") as r_file:
            line = r_file.readlines()[2].straip()
            for tick in line.split(" "):
                all_ticks.append(int(tick))


def train(input_path, all_notes, all_ticks, verbose=False, save_songs=False):
    """ Train using input data """
    num_notes, num_songs, known_songs = load_past_songs()

    # Grab all the MIDI files
    os.chdir(input_path)   # change directory
    for midi_file in glob.glob("*.mid"):
        # skip if the program has already learned the song
        if midi_file not in known_songs:
            if verbose:
                print "Learning a new song..."

            known_songs.add(midi_file)
            pattern = midi.read_midifile(midi_file)
            track = pattern[0]
            num_notes += len(track)
            num_songs += 1

            # Grab information for each note
            prev_p = -1
            for event in track:
                if event.name == "Note On" and not event.data[1]:
                    curr_p = event.data[0]
                    if prev_p != -1:
                        # get data of current note
                        tick = event.tick

                        if prev_p in all_notes:
                            if curr_p not in all_notes[prev_p]:
                                all_notes[prev_p][curr_p] = 0
                            all_notes[prev_p][curr_p] += 1
                            all_notes[prev_p][-1] += 1
                        else:
                            all_notes[prev_p] = {-1: 1, curr_p: 1}

                        if tick not in all_ticks:
                            all_ticks.append(tick)
                    prev_p = curr_p

    all_ticks.sort()
    os.chdir("..")  # move back to previous directory

    if verbose:
        print "Number of songs learned so far: ", num_songs

    if save_songs:
        save_songs(num_notes, num_songs, all_ticks, known_songs)

    return num_notes, num_songs


def save_songs(num_notes, num_songs, all_ticks, known_songs, filename="learned_songs.txt"):
    """ Save the songs that have been learned """
    with open(filename, "w") as w_file:
        w_file.write(str(num_notes))
        w_file.write("\n")
        w_file.write(str(num_songs))
        w_file.write("\n")

        for tick in all_ticks:
            w_file.write(str(tick))
            w_file.write(" ")

        w_file.write("\n")
        for song in known_songs:
            w_file.write(song)
            w_file.write("\n")


def load_past_songs(filename="learned_songs.txt"):
    """ Load all songs that have been previously learned """
    num_notes, num_songs, known_songs = 0, 0, []
    if os.path.isfile(filename):
        with open(filename, "r") as r_file:
            known_songs = r_file.read().splitlines()

        num_notes = int(known_songs[0])
        num_songs = int(known_songs[1])

        # remove the first three lines
        for _ in range(3):
            del known_songs[0]

    return num_notes, num_songs, set(known_songs)


def analyze_single_song(filename, verbose=False):
    """ Perform statistical analysis on a single song """
    all_notes = {}
    pattern = midi.read_midifile(filename)  # Import MIDI file

    if verbose:
        print filename, "statistics"

    # Grab information for each note
    prev_p = -1
    track = pattern[0]
    for event in track:
        if event.name == 'Note On' and not event.data[1]:
            curr_p = event.data[0]
            if prev_p != -1:
                tick = event.tick
                if prev_p in all_notes:
                    if curr_p not in all_notes[prev_p]:
                        all_notes[prev_p][curr_p] = 0
                    all_notes[prev_p][curr_p] += 1
                    all_notes[prev_p][-1] += 1
                else:
                    all_notes[prev_p] = {-1: 1, curr_p: 1}

            prev_p = curr_p


def printNotes(all_notes):
    """ Print out all the notes and their neighbors """
    for note in all_notes:
        print "Note", note, " |",
        for neighbor in all_notes[note]:
            print neighbor, ":", all_notes[note][neighbor], "|",
        print ""
    print ""


def memorize(all_notes):
    """ Save training data """
    with open("brain.txt", "w") as w_file:
        for note in all_notes:
            w_file.write(str(note))
            w_file.write(" ")
            for neighbor in all_notes[note]:
                w_file.write(str(neighbor))
                w_file.write(" ")
                w_file.write(str(all_notes[note][neighbor]))
                w_file.write(" ")
            w_file.write("\n")


def createOccurrenceBasedMusic(allNotes, allTicks, avgLength):
    """
    First method: single note approach
      Neighbor: choosing based on probability (occurances / total).
      Tick: randomly choosing among the set.
      First Note: most common note.
      First Tick: shortest tick in the set.
      End Note:   starting note.
      Results:
          1. First thing we notice is that some ticks are way too long.
              - Solution: choose a certain range of ticks in the set.
          2. Fixed the problem where some notes are much longer than others.
             However, since the tick of each note is randomly selected, the song
             doesn't have any rhythm.
          3. The notes sound okay, but not great. I wonder if we could do better.
    """

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


def createMeasureBasedMusic(allNotes, allTicks, avgLength):
    """
    Second method: measure approach
      Neighbor: choose neighbor based on probability.
      Tick: use the median of the tick set to create a set that contains a quarter
            note, half note, and eighth note. Randomly pick a note that does not 
            exceed the measure length.
      First Note: most common note.
      First Tick: shortest tick in the set.
      End Note:   starting note.
      Description:
          Create sets of notes to simulate each measure, and randomly pick
          among the set. Number of notes in each measure is set to be eight,
          since each measure can have at most eight notes (8 eighth notes).
          For the length limit that we set, 12 sets of measure seen to work
          okay. Ticks are calculated using the median of tick set mentioned
          above.
      Results:
          1. Certain ticks sound better than random ticks. Big improvement.
          2. The notes sound better as well.
    """
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


def createHillClimbingMusic(allNotes, allTicks, avgLength):
    """
    Third method: traditional Hill Climbing approach, with random reset
      Neighbor: choose the most frequent neighbor.
      Tick: use the median of the tick set to create a set that contains a quarter
            note, half note, and eighth note. Randomly pick a note that does not 
            exceed the measure length.
      First Note: random note.
      First Tick: shortest tick in the set.
      End Note:   best neighbor at the time when it reaches optima.
      Description:
          Greedily choose a neighbor based on occurances. Random reset a starting
          point if the best neighbor cannot improve, as long as it's within the
          time limit.
      Results:
          The notes seem to sound okay. Occasionally the program does choose weird
          neighbor as the next note. This is probably affect by the input midi
          files. Performance is not better than the previous method. Also, the
          ending note sounds random.
    """
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
