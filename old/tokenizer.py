from miditok import REMI, TokenizerConfig
from miditoolkit import MidiFile
import symusic
from pathlib import Path
import music21 as m21

class MidiTokenizer:
    def __init__(self):
        """Initialize the MidiTokenizer with REMI tokenizer from miditok"""
        # Setting up parameters for REMI tokenizer
        self.config = {
            #"pitch_range": (21, 109),
            "beat_res": {(0, 4): 8, (4, 12): 4},
            "num_velocities": 32,
            "special_tokens": ["PAD", "BOS", "EOS", "MASK"],
            "use_chords": True,
            "use_rests": False,
            "use_tempos": True,
            "use_time_signatures": False,
            "use_programs": False,
            "num_tempos": 32,  # number of tempo bins
            "use_velocities": False,
        }

        self.tokenizer = REMI(TokenizerConfig(self.config))  # Initialize tokenizer
        self.vocab_size = self.tokenizer.vocab_size
        self.tokens = []

    def tokenize_file(self, midi_path: str):
        """Tokenize a single MIDI file and return token IDs"""
        midi_path = Path(midi_path)
        midi = MidiFile(midi_path, clip=True)  # Load MIDI file with clipping
        tokens = self.tokenizer(midi)  # miditok handles parsing and encoding
        self.tokens = tokens[0].ids  # Get token IDs as a list
        return self.tokens

    def get_tokens(self):
        return self.tokens
    
    def tokens_to_string(self, tokens):
        """Convert token IDs back to string representation"""
        return self.tokenizer._ids_to_tokens(tokens)
    
    def string_to_tokens(self, string):
        """Convert string representation back to token IDs"""
        return self.tokenizer._tokens_to_ids(string)
    
    def tokens_to_midi(self, tokens):
        """Convert token IDs back to MIDI file"""
        generated_midi = self.tokenizer(tokens)
        generated_midi.dump_midi("output2.mid")

#previous test        
        
config = {
    "pitch_range": (21, 109),
    "beat_res": {(0, 4): 8, (4, 12): 4},
    "num_velocities": 32,
    "special_tokens": ["PAD", "BOS", "EOS", "MASK"],
    "use_chords": True,
    "use_rests": False,
    "use_tempos": True,
    "use_time_signatures": False,
    "use_programs": False,
    "num_tempos": 32,  # number of tempo bins
    "use_velocities": False,
}
tokenizer = REMI(TokenizerConfig())  # Initialize tokenizer
midi = MidiFile("test_3.mid", clip = True)
for i in range(len(midi.instruments)):
    for msg in midi.instruments[i].notes:
        msg.velocity = 127  # Set a maximum velocity


#print(tokenizer.tokens_to_string([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]))

# Tokenize the MIDI file
tokens = tokenizer(Path("test_2.mid"))  # Tokenize the MIDI file

#Convert tokens back to MIDI
generated_midi = tokenizer(tokens)  # MidiTok can handle PyTorch/Numpy/Tensorflow tensors
generated_midi.dump_midi(Path("output2.mid"))
print("Midi file tokenized and saved as output2.mid")