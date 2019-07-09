import MIM_uniqueApproach

# Initializing data structures
allNotes = {} # Dictionary for pitches
allLengths = [] # List for note lengths

files = MIM_uniqueApproach.getMusic() # Grab input files
avgLength = MIM_uniqueApproach.listen(files, allNotes, allLengths) # Learn statistical data from input songs
allLengths = sorted(allLengths) # Sort length list from shortest to longest note lengths
MIM_uniqueApproach.printInfo(allNotes, allLengths) # Print statistical information about notes and lengths
greedySong = MIM_uniqueApproach.createGreedyMusic(allNotes, allLengths, avgLength) # Generate song using greedy approach
fixedProbSong = MIM_uniqueApproach.createFixedProbabilityMusic(allNotes, allLengths, avgLength) # Generate song using fixed probability approach
dynamicProbSong = MIM_uniqueApproach.createDynamicProbabilityMusic(allNotes, allLengths, avgLength) # Generate song using calculated probability approach
optimalSong = MIM_uniqueApproach.createMusic(allNotes, allLengths, avgLength) # Generate song using calculated probability and varied note lengths (with printed display of output)
