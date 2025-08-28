from miditok import REMI, TokenizerConfig, TokSequence
from pathlib import Path
from music21 import stream, converter
import os
from typing import cast

class MidiTokenizer:
    def __init__(self, config: dict | None = None):
        """Initialize the tokenizer with default or custom config."""
        default_config = {
            "pitch_range": (21, 109),
            "beat_res": {(0, 4): 8, (4, 12): 4},
            "num_velocities": 32,
            "special_tokens": ["PAD", "BOS", "EOS", "MASK"],
            "use_chords": True,
            "use_rests": True,
            "use_tempos": False,
            "use_time_signatures": False,
            "use_programs": False,
            "use_velocities": True,
            
        }
        cfg = TokenizerConfig(**(config or default_config))
        self.tokenizer = REMI(cfg)
        self.midi_paths = []

    def tokenize_midi_file(self, input_path: str):
        """Tokenize a MIDI file into tokens."""
        return self.tokenizer(Path(input_path))

    def token_ids_to_midi(self, token_ids: list[int | list[int]], output_dir=r"C:\Users\rober\OneDrive\Documents\0.School\WILLIAM PERKIN\Comp\1. NEA project prototype\files\generated_midi_files"):
        """Convert token IDs to a MIDI file and save it."""
        self.midi_paths = []
        #Convert token IDs back into tokens (strings)
        token_str = self.tokenizer._ids_to_tokens(token_ids)

        #Create a Toksequence from the tokens
        token_seq = TokSequence(
            ids=token_ids,
            tokens=cast(list[str | list[str]], token_str)  # Avoid Pylance complaints
        )

        #Decode into Score
        score = self.tokenizer.decode([token_seq])

        #Export the decoded MIDI
        os.makedirs(output_dir, exist_ok=True)
        output_file_path = os.path.join(output_dir, f"decoded_midi_temp.mid")
        score.dump_midi(Path(output_file_path))
        print(f"MIDI saved as {output_file_path}")
        self.midi_paths.append(output_file_path)
        return self.midi_paths

    def merge_midi_paths(self, output_dir=r"C:\Users\rober\OneDrive\Documents\0.School\WILLIAM PERKIN\Comp\1. NEA project prototype\files\generated_midi_files"):
        """Merge multiple MIDI files into one."""
        merged_score = stream.Score()
        for path in self.midi_paths:
            current_stream = converter.parse(path)
            merged_score.insert(0.0, current_stream)
            os.remove(path)

        output_path = os.path.join(output_dir, "merged_generated_midi.mid")
        try:
            os.makedirs(output_dir, exist_ok=True)
            merged_score.write('midi', fp=output_path)
            return output_path
        except Exception as e:
            print("Error writing MIDI:", e)
            return None