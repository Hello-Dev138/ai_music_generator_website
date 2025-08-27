import subprocess
import os
from mido import MidiFile, MidiTrack, Message

edm_channel_map = {
    0: 20,
    1: 21
}

def apply_instrument_changes(midi_file_path, genre = "edm"):
    midi = MidiFile(midi_file_path)
    
    if genre == "edm":
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

def midi_to_wav(midi_file, output_file, soundfont=r"C:\Users\rober\OneDrive\Documents\0.School\WILLIAM PERKIN\Comp\1. NEA project prototype\soundfonts\Arachno_SoundFont_Version_1.0.sf2", genre="edm"):
    """Convert a MIDI file to WAV using FluidSynth."""
    # Command to render MIDI to WAV
    genre = genre.lower()
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True) # Make sure output folder exists

    temp_midi_file, temp_created = apply_instrument_changes(midi_file, genre)

    cmd = [
        r"C:\ProgramData\chocolatey\bin\fluidsynth.exe",
        "-ni",
        "-F", output_file,
        "-r", "44100",
        soundfont,
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

# Example usage
input_folder_dir = r"C:\Users\rober\OneDrive\Documents\0.School\WILLIAM PERKIN\Comp\1. NEA project prototype\MIDI_TO_AUDIO\input"
output_folder_dir = r"C:\Users\rober\OneDrive\Documents\0.School\WILLIAM PERKIN\Comp\1. NEA project prototype\MIDI_TO_AUDIO\output"

midi_file = os.path.join(input_folder_dir, "jazz_improv.mid")
output_file = os.path.join(output_folder_dir, "rendered_song.wav")
output_file2 = os.path.join(output_folder_dir, "rendered_song0.wav")

soundfont1=r"C:\Users\rober\OneDrive\Documents\0.School\WILLIAM PERKIN\Comp\1. NEA project prototype\soundfonts\Arachno_SoundFont_Version_1.0.sf2"
soundfont2 = r"C:\Users\rober\OneDrive\Documents\0.School\WILLIAM PERKIN\Comp\1. NEA project prototype\soundfonts\Nokia_S30.sf2"

midi_to_wav(midi_file, output_file, soundfont1, genre = 'edm')
print(f"Rendered {os.path.basename(midi_file)} → {os.path.basename(output_file)} using {os.path.basename(soundfont1)}")

midi_to_wav(midi_file, output_file2, soundfont2)
print(f"Rendered {os.path.basename(midi_file)} → {os.path.basename(output_file2)} using {os.path.basename(soundfont2)}")