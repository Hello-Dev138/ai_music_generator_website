from midi2audio import FluidSynth
import pygame
import subprocess
import os

class MidiSynthesizer:
    def __init__(self, soundfont_path=r"C:\\soundfonts\\FluidR3_GM.sf2"):
        self.soundfont_path = soundfont_path
        self.fluidsynth_path = r'C:\Program Files\fluidsynth\bin\fluidsynth.exe'  # FULL PATH to executable
        self.sample_rate = 44100

    def synthesize(self, midi_file, output_wav):
        if not os.path.exists(self.soundfont_path):
            raise FileNotFoundError(f"SoundFont not found: {self.soundfont_path}")
        if not os.path.exists(midi_file):
            raise FileNotFoundError(f"MIDI file not found: {midi_file}")
        
        command = [
        self.fluidsynth_path,
        '-ni',
        self.soundfont_path,
        midi_file,
        '-F',
        output_wav,
        '-r',
        str(self.sample_rate)
        ]
    
        print("Running FluidSynth command:\n", command)
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode != 0:
            print("FluidSynth Error Output:\n", result.stderr)
            raise RuntimeError("FluidSynth failed to synthesize audio.")

        print("FluidSynth completed successfully.")

    def play(self, wav_file):
        """
        Play a WAV file using the playsound library.

        wav_file: Path to the WAV file to be played
        """
        
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.load(wav_file)  # or .mp3
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():  # Wait for playback to finish
            continue
        pygame.quit()
        return "Playback finished"      