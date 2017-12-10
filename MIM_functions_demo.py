import MIM_functions

def main() :
    # Variables
    allNotes = {}   # dictionary of notes and their neighborhood
    allLengths = [] # list of lengths
    avgLength = 0

    MIM_functions.recall(allNotes, allLengths)        # input statistical data from previous runs, if exists
    avgLength = MIM_functions.listen(allNotes, allLengths)        # read input songs
    #MIM_functions.printNotes(allNotes)    # show all notes and their neighbors
    #MIM_functions.memorize(allNotes)      # remember what it has learned so far
    #MIM_functions.singleSong("music/melody2.mid")      # do a statistical analysis on one song

    # limit the range of ticks
    #allLengths2 = sorted(i for i in allLengths if i < 500 and i > 200)   
    MIM_functions.createOccurrenceBasedMusic(allNotes, allLengths, avgLength)
    MIM_functions.createMeasureBasedMusic(allNotes, allLengths, avgLength)
    MIM_functions.createHillClimbingMusic(allNotes, allLengths, avgLength)
    print "Music generated. Enjoy!"

    return

if __name__ == '__main__':
    import sys
    main()
