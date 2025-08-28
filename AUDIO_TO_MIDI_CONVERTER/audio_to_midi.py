import os
import tensorflow as tf
from basic_pitch.inference import predict_and_save, Model, predict
from basic_pitch import ICASSP_2022_MODEL_PATH

from pathlib import Path

from POSTPROCESSING import MidiPostProcessor

output_dir = r"C:\Users\rober\OneDrive\Documents\0.School\WILLIAM PERKIN\Comp\1. NEA project prototype\AUDIO_TO_MIDI_CONVERTER\output"

input_dir = r"C:\Users\rober\OneDrive\Documents\0.School\WILLIAM PERKIN\Comp\1. NEA project prototype\AUDIO_TO_MIDI_CONVERTER\input"
input_path = os.path.join(input_dir, "sing_test_1.wav")

basic_pitch_model = Model(ICASSP_2022_MODEL_PATH)

# Actually run the prediction model and postprocess the output
# Finally render the generated midi to wav using a soundfont

def generate_clean_midi(input_path, output_dir):
    midi_post_processor = MidiPostProcessor(genre = "pop", force_to_scale = False)
    try:
        predict_and_save(audio_path_list=[input_path],
                        output_directory=output_dir,
                        save_midi=True,
                        sonify_midi=False,
                        save_model_outputs=False,
                        save_notes=False,
                        model_or_model_path=basic_pitch_model)
        input_path = Path(input_path)
        output_path = os.path.join(output_dir, f"{input_path.stem}_basic_pitch.mid")
        pp_midi_path = midi_post_processor.postprocess_midi(midi_file_path=output_path)
        return pp_midi_path

    except Exception as e:
        print("Error occurred while converting wav to midi:", e)

#WORKING TERMINAL COMMAND
#basic-pitch "C:/Users/rober/OneDrive/Documents/0.School/WILLIAM PERKIN/Comp/TESTING/output" "C:/Users/rober/OneDrive/Documents/0.School/WILLIAM PERKIN/Comp/TESTING/input/midiTest.wav"
#basic-pitch "C:/Users/rober/OneDrive/Documents/0.School/WILLIAM PERKIN/Comp/TESTING/output" "C:/Users/rober/OneDrive/Documents/0.School/WILLIAM PERKIN/Comp/TESTING/input/piano_test_1.mp3"