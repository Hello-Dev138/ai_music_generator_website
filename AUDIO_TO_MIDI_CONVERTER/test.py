import os
import tensorflow as tf
from basic_pitch.inference import predict_and_save, Model, predict
from basic_pitch import ICASSP_2022_MODEL_PATH

output_dir = "C:/Users/rober/OneDrive/Documents/0.School/WILLIAM PERKIN/Comp/TESTING"
input_dir = "C:/Users/rober/OneDrive/Documents/0.School/WILLIAM PERKIN/Comp/TESTING/midiTest.wav"

print("TensorFlow version:", tf.__version__)
print("Saved_model available?", hasattr(tf, "saved_model"))
#basic_pitch_model = Model(ICASSP_2022_MODEL_PATH)

model_output, midi_data, note_events = predict(input_dir)
print(midi_data)

#WORKING TERMINAL COMMAND
#basic-pitch "C:/Users/rober/OneDrive/Documents/0.School/WILLIAM PERKIN/Comp/TESTING/output" "C:/Users/rober/OneDrive/Documents/0.School/WILLIAM PERKIN/Comp/TESTING/input/midiTest.wav"
#basic-pitch "C:/Users/rober/OneDrive/Documents/0.School/WILLIAM PERKIN/Comp/TESTING/output" "C:/Users/rober/OneDrive/Documents/0.School/WILLIAM PERKIN/Comp/TESTING/input/piano_test_1.mp3"