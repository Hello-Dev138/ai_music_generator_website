# Test to encapsulate all modules:
# 1. Convert a wav file into midi using basic pitch
# 2. Postprocess the midi file
# 3. Use the postprocessed midi file as an input to the AI model
# 4. Postprocess the output from the AI model
# 5. Render the generated midi into a wav file

import os
from AUDIO_TO_MIDI_CONVERTER import audio_to_midi
from POSTPROCESSING import MidiPostProcessor
from AI_MODELS import AIGenerator
from AI_TRAINING import MidiTokenizer
from MIDI_TO_AUDIO import MidiRenderer

# Set up constants for file directories
FILES_DIR = r"C:\Users\rober\OneDrive\Documents\0.School\WILLIAM PERKIN\Comp\1. NEA project prototype\files"
USER_WAV_FILES_DIR = os.path.join(FILES_DIR, "user_wav_files")
USER_MIDI_FILES_DIR = os.path.join(FILES_DIR, "user_midi_files")

GENERATED_MIDI_FILES_DIR = os.path.join(FILES_DIR, "generated_midi_files")
GENERATED_WAV_FILES_DIR = os.path.join(FILES_DIR, "generated_wav_files")
POSTPROCESSED_MIDI_FILES_DIR = os.path.join(FILES_DIR, "postprocessed_midi_files")

# Genre of music to make
genre = "classical"
starting_file_type = "wav"

if starting_file_type == "wav":
    # Get a wav file that was inputted from the user
    user_wav_file_path = os.path.join(USER_WAV_FILES_DIR, "sing_test_1.wav")

    # Convert wav file to midi file and save it in the generated midi files directory. This will return the file path of the postprocessed midi file
    generated_midi_path = audio_to_midi.generate_clean_midi(user_wav_file_path, GENERATED_MIDI_FILES_DIR)

    # As the generate_clean_midi function already postprocesses the midi file, we can use the returned path directly
    postprocessed_midi_path = generated_midi_path
else:
    # If starting with MIDI, use the provided postprocessed MIDI path
    user_midi_file_path = os.path.join(USER_MIDI_FILES_DIR, "Bach--Fugue-in-D-Minor.mid")
    initial_midi_post_processor = MidiPostProcessor(genre = genre, glue_notes_flag=False, make_monophonic=False, force_to_scale=False,) # Just to quantize the timing
    postprocessed_midi_path = initial_midi_post_processor.postprocess_midi(user_midi_file_path)

# Tokenize the postprocessed midi file
tokenizer = MidiTokenizer()
tokens = tokenizer.tokenize_midi_file(postprocessed_midi_path)

# Ensure tokens is a list
for i in range(len(tokens)): 
    token_ids = tokens[i].ids if isinstance(tokens, list) else tokens.ids

# Initialize the AI generator
ai_generator = AIGenerator(token_ids=token_ids, tokens_to_gen=1000, use_first_n_tokens=10, type_gen="acc", top_k=10, temperature=1.1)

# Generate tokens using the AI model
ai_generator.generate()

# Get the generated token IDs
generated_token_ids = ai_generator.get_generated_token_ids()

# Generate temp midi file(s) based on the generated tokens
tokenizer.token_ids_to_midi(generated_token_ids)

# Merge the generated midi files into one
merged_midi_path = tokenizer.merge_midi_paths()

# Postprocess the merged midi file
midi_post_processor = MidiPostProcessor(genre = genre, glue_notes_flag=False, make_monophonic=False, force_to_scale=True)
postprocessed_midi_path = midi_post_processor.postprocess_midi(merged_midi_path)

# Add drums to the postprocessed midi file
postprocessed_midi_path = midi_post_processor.add_drums(postprocessed_midi_path)

# Render the postprocessed midi file into a wav file
renderer = MidiRenderer(soundfont = r"C:\Users\rober\OneDrive\Documents\0.School\WILLIAM PERKIN\Comp\1. NEA project prototype\soundfonts\Arachno_SoundFont_Version_1.0.sf2")
renderer.midi_to_wav(postprocessed_midi_path, GENERATED_WAV_FILES_DIR)