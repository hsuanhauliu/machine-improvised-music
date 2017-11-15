import midi


def run() :
    MAXSIZE = 128

    # Initializing dictionaries
    counter = -1
    neighborhood = {}
    while counter < MAXSIZE:
        neighborhood.setdefault(counter, 0)

    counter = 0
    allNotes = {}
    while counter < MAXSIZE:
        allNotes.setdefault(counter, neighborhood)

    # Import MIDI files
    pattern = midi.read_midifile("melody1.mid")
    track = pattern[0]

    # Grab information for each note
    for event in track:
        if event.name == 'Note On':
            tick = event.tick
            pitch = event.data[0]
            volume = event.data[1]
            if volume == 0:
                print "Tick={}, Note={}, Volume={}".format(tick, pitch, volume)




    # Process





    # Produce new music





    # Export MIDI file.





    return
