from pathlib import Path
from glob import glob
from miditok import REMI
from miditoolkit import MidiFile
from tqdm import tqdm

# Initialize tokenizer
tokenizer = REMI()

def pick_main_melody_track(midi: MidiFile):
    """Heuristic to pick the main melody/accompaniment track based on average pitch and note density"""
    # As many songs have chords within the melodies, the accompaniment may share the same track
    def track_score(track):
        if not track.notes: # Ensure there are notes in the track
            return 0
        if track.is_drum: # Ignore drum tracks
            return 0
        avg_pitch = sum(n.pitch for n in track.notes) / len(track.notes)
        note_count = len(track.notes)
        return avg_pitch * 0.65 + note_count * 0.35  # The likelihood of a track being the accompaniment, taking into account both average pitch and note density (for accompaniment, note count is more significant due to the presence of chords)

    return max(midi.instruments, key=track_score)

def remove_leading_silence(midi: MidiFile):
    """Shift all notes so the first note starts at tick 0"""
    for track in midi.instruments:
        first_note_start = min(
            (note.start for note in track.notes if note.start is not None),
            default=0
        )
        # Shift notes
        track.notes = [n for n in track.notes]
        for note in track.notes: # Shift each note to maintain relative timing
            note.start -= first_note_start
            note.end -= first_note_start
        min_start_ticks = 10 # Small buffer to remove any early, short notes
        track.notes = [n for n in track.notes if n.start >= min_start_ticks]
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

            # Keep only main melody/accompaniment track
            midi.instruments = [melody_track]

            #Remove leading silence
            midi = remove_leading_silence(midi)

            # Save accompaniment-only MIDI as its own dataset
            if save_melody_dir:
                original_path = Path(path)
                # Add "_acc" before the file extension so that it is easier to differentiate between original and accompaniment-only files
                save_path = Path(save_melody_dir) / f"{original_path.stem}_acc{original_path.suffix}"
                save_path.parent.mkdir(parents=True, exist_ok=True) # Create directories if they don't exist
                midi.dump(save_path) # Save the accompaniment-only MIDI file
            total_files_tokenized += 1 # Keep track of how many files are processed successfully for debugging

        except Exception as e:
            print(f"Skipping {Path(path).name} due to error: {e}")
    return total_files_tokenized

# Extract melodies from MIDI dataset
dataset_folder = r"C:\Users\rober\OneDrive\Documents\0.School\WILLIAM PERKIN\Comp\1. NEA project prototype\MIDI_DATASET"
save_folder = r"C:\Users\rober\OneDrive\Documents\0.School\WILLIAM PERKIN\Comp\1. NEA project prototype\MIDI_DATASET_ACCOMPANIMENT"

tokens_dataset = preprocess_midi_dataset(dataset_folder, save_melody_dir=save_folder)

print(f"Processed {tokens_dataset} accompaniment tracks.")