import MIM_functions

def main() :
    # Variables
    allLengths = {} # TO DO
    allNotes = {}

    MIM_functions.recall(allNotes)        # input statistical data from previous runs, if exists
    MIM_functions.listen(allNotes)        # read input songs
    MIM_functions.printNotes(allNotes)    # show all notes and their neighbors
    MIM_functions.memorize(allNotes)      # remember what it has learned so far
    #MIM_functions.singleSong("music/melody1.mid")      # do a statistical analysis on one song

    return

if __name__ == '__main__':
    import sys
    main()
