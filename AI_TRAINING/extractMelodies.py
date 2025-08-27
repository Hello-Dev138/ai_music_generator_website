from pathlib import Path
from glob import glob
from miditok import REMI
from miditoolkit import MidiFile
from tqdm import tqdm

# Initialize tokenizer
tokenizer = REMI()

def pick_main_melody_track(midi: MidiFile):
    """Heuristic to pick the main melody track based on average pitch and note density"""
    def track_score(track):
        if not track.notes: # Ensure there are notes in the track
            return 0
        if track.is_drum: # Ignore drum tracks
            return 0
        avg_pitch = sum(n.pitch for n in track.notes) / len(track.notes) # Average pitch of notes
        note_count = len(track.notes) # Number of notes in the track
        return avg_pitch * 0.85 + note_count * 0.15  # The likelihood of a track being the melody, taking into account both average pitch and note density
        
    return max(midi.instruments, key=track_score)

def remove_leading_silence(midi: MidiFile): # This is because a lot of the melodies don't start until a few seconds in, this is critical so that training isnt skewed with silence
    """Shift all notes so the first note starts at tick 0"""
    for track in midi.instruments:
        first_note_start = min((note.start for note in track.notes if note.start is not None),default=0) # Find the start time of the first note (anything before that is silence)

        # Shift all notes by the start time of the first note so that the first note starts at tick zero and all other notes maintain their relative timing
        track.notes = [n for n in track.notes]
        for note in track.notes: # Shift each note to maintain relative timing
            note.start -= first_note_start
            note.end -= first_note_start
        min_start_ticks = 10 # Small buffer to remove any early, short notes
        track.notes = [n for n in track.notes if n.start >= min_start_ticks] # Remove these short notes that could skew training
    return midi

def flatten_melody(midi: MidiFile):
    """Make the melody monophonic by removing overlapping notes. Higher pitch notes are prioritised."""
    # This is so that the ai model will only train on the melody, ensuring that it is possible to learn how to generate melodies that sound good
    for track in midi.instruments:
        if not track.notes:
            continue
        # Sort notes by start time, and then by pitch (descending so it uses the higher note) for notes starting at the same time
        notes = sorted(track.notes, key=lambda n: (n.start, -n.pitch))
        flattened_notes = [] # List to hold the flattened notes
        active_note = None

        # Iterate through sorted notes and add to flattened list if they don't overlap
        for note in notes:
            if active_note is None:
                # Start with the first note
                active_note = note
                flattened_notes.append(active_note)
            else:
                if note.start == active_note.start:
                    # If multiple notes start at the same time, keep the higher pitch note to remove chords
                    continue
                if note.start < active_note.end:
                    # If new note is higher pitch and overlaps, cut the active note short
                    if note.pitch > active_note.pitch:
                        active_note.end = note.start
                        active_note = note
                        flattened_notes.append(active_note)
                    #Otherwise, skip the overlapping note
                else:
                    flattened_notes.append(note) # Add note if it doesn't overlap
                    active_note = note
        track.notes = flattened_notes # Replace the track's notes with the flattened melody
    return midi

def preprocess_midi_dataset(dataset_dir: str,save_melody_dir: str):  
    """Preprocess an entire MIDI dataset by extracting melody tracks"""
    # Find all MIDI files recursively
    midi_paths = glob(f"{dataset_dir}/**/*.mid", recursive=True)

    total_files_tokenized = 0

    for path in tqdm(midi_paths, desc="Processing MIDI files", unit="file"):
        try:
            midi = MidiFile(path, clip=True)
            melody_track = pick_main_melody_track(midi)

            # Keep only melody track
            midi.instruments = [melody_track]

            #Remove leading silence
            midi = remove_leading_silence(midi)

            # Flatten and quantize melody
            midi = flatten_melody(midi)

            # Save melody-only MIDI as its own dataset
            if save_melody_dir:
                original_path = Path(path)
                # Add "_melody" before the file extension so that it is easier to differentiate between original and melody-only files
                save_path = Path(save_melody_dir) / f"{original_path.stem}_melody{original_path.suffix}"
                save_path.parent.mkdir(parents=True, exist_ok=True)
                midi.dump(save_path)
            total_files_tokenized += 1

        except Exception as e:
            print(f"Skipping {Path(path).name} due to error: {e}")
    return total_files_tokenized

# Extract melodies from MIDI dataset
dataset_folder = r"C:\Users\rober\OneDrive\Documents\0.School\WILLIAM PERKIN\Comp\1. NEA project prototype\MIDI_DATASET"
save_folder = r"C:\Users\rober\OneDrive\Documents\0.School\WILLIAM PERKIN\Comp\1. NEA project prototype\MIDI_DATASET_MELODY"

tokens_dataset = preprocess_midi_dataset(dataset_folder, save_melody_dir=save_folder)

print(f"Processed {tokens_dataset} melody tracks.")