from music21 import instrument, note, chord, stream
import copy
import numpy as np

import gradio as gr

from MIDI_SYNTHESIS import MidiSynthesizer

FOLDER_PATH = "C:/Users/rober/OneDrive/Documents/0.School/WILLIAM PERKIN/Comp/1. NEA project prototype/AlgorithmAi"

chords = {
        'Dm7': chord.Chord(['D4', 'F4', 'A4', 'C5']),
        'G7/D': chord.Chord(['D4', 'F4', 'G4', 'B4']),
        'Cmaj7': chord.Chord(['C4', 'E4', 'G4', 'B4']),
        'Gm7': chord.Chord(['A3', 'Db4', 'E4', 'G4']),
        'Fmaj7': chord.Chord(['F4', 'A4', 'C5', 'E5']),
        'Bm7b5/F': chord.Chord(['F4', 'A4', 'B4', 'D5']),
        'Am7/E': chord.Chord(['A4', 'C4', 'E4', 'G4']),
        'Em7': chord.Chord(['E4', 'G4', 'B4', 'D4']),
    }

scales = {
        'C_major': ['C5', 'D5', 'E5', 'G5', 'A5', 'Rest'],
        #'C_major_blues': ['C5', 'D5', 'Eb5', 'E5', 'G5', 'A5', 'Rest']
    }
weights = {
    #'c_major_blues': [1,1,0.1,1,1,1]
}
chord_progressions = {
    'default': ['Dm7', 'G7/D', 'Cmaj7', 'Cmaj7', 'Dm7', 'G7/D', 'Cmaj7', 'Gm7'],
    'jazz_1': ['Fmaj7', 'Bm7b5/F', 'Em7', 'Dm7', 'G7/D', 'Cmaj7']
}

durations = [0.5, 1.0, 2.0, 4.0, 1.5]  # Possible note durations
duration_weights_melody = {
    'default': [0.2, 0.2, 0.2, 0.2, 0.2],  # Weights for each duration
    'fast': [0.7, 0.3, 0.0, 0.0, 0.0],
    'slow': [0.0, 0.1, 0.4, 0.4, 0.1]
}
duration_weights_chords = {
    'default': [0.0, 0.0, 0.5, 0.3, 0.2],  # Weights for each duration
    'fast': [0.2, 0.6, 0.0, 0.0, 0.2],
    'slow': [0.0, 0.0, 0.0, 1.0, 0.0]
}

def generate_chord_pattern(speed: str = 'default'):
    if speed == 'fast':
        max_length = 4.0
    elif speed == 'default':
        max_length = 8
    else:
        max_length = 8.0
    duration_pattern = []
    total_length = 0.0
    while total_length < max_length:
        duration = np.random.choice(durations, p = duration_weights_chords.get(speed))
        if total_length + duration > max_length:
            duration = max_length - total_length
        duration_pattern.append(duration)
        total_length += duration
    return duration_pattern

def jazz_improv(total_length: int, melody_speed: str = 'default'):
    """Function to generate a jazz improvisation MIDI file."""
    # Create a stream to hold the notes
    jazz_score = stream.Score()
    melody_stream = stream.Stream()
    chord_stream = stream.Stream()

    # Add some notes and chords to the stream
    current_length = 0.0
    duration = 1


    while current_length < total_length:
        # Generate a random melody note
        scale = np.random.choice(list(scales.keys()))
        note_name = np.random.choice(scales[scale], p=weights.get(scale, [1/len(scales[scale])]*len(scales[scale])))
        duration = np.random.choice(durations, p=duration_weights_melody.get(melody_speed))
        if current_length + duration > total_length:
            duration = total_length - current_length
        if note_name == 'Rest':
            new_note = note.Rest()
        else:
            new_note = note.Note(note_name)
        new_note.quarterLength = duration
        melody_stream.append(copy.deepcopy(new_note))
        current_length += duration

    # Add a chord progression
    chord_progression_key = np.random.choice(list(chord_progressions.keys()))
    chord_progression = chord_progressions[chord_progression_key]
    current_length = 0.0
    
    duration_pattern = generate_chord_pattern(melody_speed)

    while current_length < total_length:
        for i in range(len(duration_pattern)):
            for chord_name in chord_progression:
                if current_length + duration_pattern[i] > total_length:
                    break
                new_chord = chords[chord_name]
                new_chord.duration.quarterLength = duration_pattern[i]
                chord_stream.append(copy.deepcopy(new_chord))
                current_length += duration_pattern[i]

    #Merge the chord and melody streams into the main jazz stream
    jazz_score.insert(0.0, chord_stream)
    jazz_score.insert(0.0, melody_stream)

    # Write the stream to a MIDI file
    file_path = f"{FOLDER_PATH}/jazz_improv.mid"
    jazz_score.write('midi', fp=file_path)
    

# Gradio interface to generate jazz improvisation
def generate_and_play_jazz_improv(total_length: int, melody_speed: str = 'default'):
    synth = MidiSynthesizer()
    jazz_improv(total_length, melody_speed)
    file_path1 = f"{FOLDER_PATH}/jazz_improv.mid"
    file_path2 = f"{FOLDER_PATH}/jazz_improv.wav"
    synth.synthesize(file_path1, file_path2)
    synth.play(file_path2)
    return file_path1

def generate_jazz_improv_file(total_length: int, melody_speed: str = 'default'):
    jazz_improv(total_length, melody_speed)
    file_path1 = f"{FOLDER_PATH}/jazz_improv.mid"
    return file_path1

#generate_and_play_jazz_improv(64, 'default')  # Initial call to generate a MIDI file

demo = gr.Interface(
    fn=generate_jazz_improv_file,
    inputs=[
        gr.Slider(minimum=16, maximum=128, step=8, label="Choose the maximum length of the improvisation", value=32),
        gr.Dropdown(choices=["slow", "default", "fast"], label="Choose a speed for the improvisation", value="default")
    ],
    outputs=gr.File(label="Download MIDI File")
)

demo.launch()