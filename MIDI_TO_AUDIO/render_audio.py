import subprocess
import os
from mido import MidiFile, MidiTrack, Message

edm_channel_map = {
    0: 20,
    1: 21
}

class MidiRenderer:
    def __init__(self, genre = "pop", soundfont=r"C:\Users\rober\OneDrive\Documents\0.School\WILLIAM PERKIN\Comp\1. NEA project prototype\soundfonts\Arachno_SoundFont_Version_1.0.sf2", fluidsynth_path=r"C:\ProgramData\chocolatey\bin\fluidsynth.exe"):
        self.soundfont = soundfont
        self.fluidsynth_path = fluidsynth_path
        self.genre = genre.lower() # Ensure that capitalisation is consistent

    def apply_instrument_changes(self, midi_file_path):
        midi = MidiFile(midi_file_path)

        if self.genre == "edm":
            channel_instruments = edm_channel_map
        else:
            channel_instruments = {}
        
        if channel_instruments:
            for i, track in enumerate(midi.tracks):
                for channel, program in channel_instruments.items():
                    # Insert at the beginning of each track
                    track.insert(0, Message('program_change', program=program, channel=channel, time=0))
            
            for track in midi.tracks:
                for msg in track:
                    if msg.type == 'program_change' and msg.channel in channel_instruments:
                        msg.program = channel_instruments[msg.channel]
                        print(f"Changed channel {msg.channel} to instrument {msg.program}")
            # Save a temporary midi file to keep the original intact
            temp_midi = midi_file_path.replace(".mid", "_temp.mid")
            midi.save(temp_midi)
            midi_to_use = temp_midi
            return midi_to_use, True # Return True to indicate a temp file was created
        else:
            midi_to_use = midi_file_path
        return midi_to_use, False # Return False to indicate no temp file was created

    def midi_to_wav(self, midi_file, output_dir):
        """Convert a MIDI file to WAV using FluidSynth."""
        os.makedirs(output_dir, exist_ok=True) # Make sure output folder exists
        output_path = os.path.join(output_dir, os.path.basename(midi_file).replace(".mid", "_rendered.wav"))

        temp_midi_file, temp_created = self.apply_instrument_changes(midi_file)

        cmd = [
            self.fluidsynth_path,
            "-ni",
            "-F", output_path,
            "-r", "44100",
            self.soundfont,
            temp_midi_file
        ]
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error occurred while rendering MIDI to WAV: {e}")
        finally:
            # Remove temporary MIDI if created
            if temp_created and os.path.exists(temp_midi_file):
                os.remove(temp_midi_file)