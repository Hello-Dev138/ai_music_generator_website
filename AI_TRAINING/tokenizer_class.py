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

    def tokenize_midi_file(self, input_path: str):
        """Tokenize a MIDI file into tokens."""
        return self.tokenizer(Path(input_path))

    def token_ID_2_Midi(self, token_ids: list[int | list[int]], output_path="decoded_midi.mid"):
        """Convert token IDs to a MIDI file and save it."""
        token_str = self.tokenizer._ids_to_tokens(token_ids)

        token_seq = TokSequence(
            ids=token_ids,
            tokens=cast(list[str | list[str]], token_str)
        )
        score = self.tokenizer.decode(token_seq)

        score.dump_midi(Path(output_path))
        print(f"MIDI saved as {output_path}")
        return token_seq

    def merge_midi_paths(self, midi_paths: list[str], output_path=r"C:\Users\rober\OneDrive\Documents\0.School\WILLIAM PERKIN\Comp\1. NEA project prototype\decoded_midi_full.mid"):
        """Merge multiple MIDI files into one."""
        merged_score = stream.Score()
        for path in midi_paths:
            current_stream = converter.parse(path)
            merged_score.insert(0.0, current_stream)
            os.remove(path)

        output_dir = os.path.dirname(output_path)
        try:
            os.makedirs(output_dir, exist_ok=True)
            merged_score.write('midi', fp=output_path)
            merged_score.show('midi')
            return output_path
        except Exception as e:
            print("Error writing MIDI:", e)
            return None


"""
if __name__ == "__main__":
    tokenizer = MidiTokenizer()

    tokens = tokenizer.tokenize_midi_file("jazz_improv.mid")
    midi_paths = []

    sequences = tokens if isinstance(tokens, list) else [tokens]

    for i, token_seq in enumerate(sequences):
        token_ids = token_seq.ids
        tokenizer.token_ID_2_Midi(token_ids, f"decoded_midi{i}.mid")
        midi_paths.append(f"decoded_midi{i}.mid")

    tokenizer.merge_midi_paths(midi_paths)
"""
