import os
import numpy as np
from glob import glob
from tqdm import tqdm
from tokenizer_class import MidiTokenizer
from pathlib import Path

dataset_dir = r"C:\Users\rober\OneDrive\Documents\0.School\WILLIAM PERKIN\Comp\1. NEA project prototype\MIDI_DATASET_MELODY"
save_dir = r"C:\tempp\MELODY_TOKENS"

os.makedirs(save_dir, exist_ok=True)

tokenizer = MidiTokenizer()

midi_paths = glob(f"{dataset_dir}/**/*.mid", recursive=True)

for index, path in enumerate(tqdm(midi_paths, desc="Tokenizing MIDI files")):
    try:
        tokens = tokenizer.tokenize_midi_file(path)
        token_ids = tokens[0].ids if isinstance(tokens, list) else tokens.ids

        if len(token_ids) == 0:
            continue

        # Save each song’s tokens as .npy
        og_path = Path(path)
        save_path = os.path.join(save_dir, f"{og_path.stem}.npy")
        np.save(save_path, np.array(token_ids, dtype=np.int16))  # Small + efficient

    except Exception as e:
        print(f"Skipping {os.path.basename(path)} due to error: {e}")