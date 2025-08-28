import pretty_midi
from music21 import key, note, pitch, converter
import os
from pathlib import Path

class MidiPostProcessor:
    def __init__(self, genre="jazz", tonic="C", key_type="major", key_detection_flag=True, force_to_scale = True, glue_notes_flag=True, make_monophonic = False ,output_dir=r"C:\Users\rober\OneDrive\Documents\0.School\WILLIAM PERKIN\Comp\1. NEA project prototype\files\generated_midi_files\postprocessed"):
        self.OUTPUT_DIR = output_dir
        
        self.genre = genre.lower() # Make sure that any capital letters won't affect the code working properly
        self.tonic = tonic.lower() # Same here
        self.key_type = key_type.lower() # Same here
        self.key_detection = key_detection_flag
        self.force_to_scale = force_to_scale
        self.glue_notes_flag = glue_notes_flag
        self.make_monophonic = make_monophonic

    # Quantize to nearest grid step
    def _quantize_time(self, time, grid = 0.25):
        """Snap time to nearest grid (e.g., 0.25 = 1/16 note if 1.0=quarter note)."""
        return round(time / grid) * grid

    # Force pitch into scale of choice
    def _force_to_scale(self, midi_note, scale_pitches):
        """Shift a MIDI note to the nearest pitch in the chosen scale."""
        p = pitch.Pitch(midi_note)

        # Find note's octave
        octave = p.octave

        # Transpose scale pitches into the same octave as the note
        same_octave_scale = [sp.transpose((octave - sp.octave) * 12) for sp in scale_pitches]
        
        # Find the closest pitch in this octave
        closest = min(same_octave_scale, key=lambda sp: abs(p.midi - sp.midi))
        
        return closest.midi

    def _swing_quantize_time(self, time, grid = 0.25, swing_amount = 0.1):
        """Add swing quantization to make midi sound more human, for selected genres"""
        quantized_time = self._quantize_time(time, grid)
        if quantized_time % 1 == 0:  # If on beat
            return quantized_time + swing_amount
        return quantized_time

    def _glue_notes(self, midi, threshold = 0.1):
        """Glue notes that are very close together to make the final audio sound more conjoined"""
        for instrument in midi.instruments:
            instrument.notes.sort(key = lambda note: note.start)  # Ensure notes are sorted by start time
            glued_notes = []
            previous_note = None
            for note in instrument.notes:
                if previous_note and (note.start - previous_note.end) <= threshold: # If the second current start within the threshold of the previous note
                    if note.pitch == previous_note.pitch: # Only glue if they are the same pitch
                        previous_note.end = max(previous_note.end, note.end)
                        glued_notes.append(previous_note)
                    else:
                        glued_notes.append(note)
                elif not previous_note:
                    previous_note = instrument.notes[0]
                    glued_notes.append(previous_note)
                else:
                    glued_notes.append(note)
            instrument.notes = glued_notes

    def _remove_leading_silence(self, midi):
        """Shift all notes so the first note starts at tick 0"""
        for track in midi.instruments:
            first_note_start = min((note.start for note in track.notes if note.start is not None),default=0) # Find the start time of the first note (anything before that is silence)

            # Shift all notes by the start time of the first note so that the first note starts at tick zero and all other notes maintain their relative timing
            track.notes = [n for n in track.notes]
            for note in track.notes: # Shift each note to maintain relative timing
                note.start -= first_note_start
                note.end -= first_note_start
        return midi

    def _flatten_melody(self, midi):
        """Make the melody monophonic by removing overlapping notes. Higher pitch notes are prioritised."""
        # This is so that there are no chords, only a melody
        for track in midi.instruments:
            if not track.notes:
                continue
            # Sort notes by start time, and then by pitch (descending so it uses the higher note first) for notes starting at the same time
            notes = sorted(track.notes, key=lambda n: (n.start, -n.pitch))
            flattened_notes = [] # List to hold the flattened notes
            active_note = None

            # Iterate through sorted notes and add to flattened list if they don't overlap
            for note in notes:
                if active_note is None:
                    # Start with the first note
                    active_note = note
                    flattened_notes.append(active_note)
                else:
                    if note.start == active_note.start:
                        # If multiple notes start at the same time, keep the higher pitch note to remove chords
                        continue
                    # If the the new note's velocity is too low, even if it is a higher pitch, skip it
                    if note.velocity < active_note.velocity * 0.8:
                        continue
                    elif note.start < active_note.end:
                        # If new note is higher pitch and overlaps, cut the active note short
                        if note.pitch > active_note.pitch:
                            active_note.end = note.start
                            active_note = note
                            flattened_notes.append(active_note)
                        #Otherwise, skip the overlapping note
                    else:
                        flattened_notes.append(note) # Add note if it doesn't overlap
                        active_note = note
            track.notes = flattened_notes # Replace the track's notes with the flattened melody
        return midi

    def _detect_key(self, midi_file_path):
        score = converter.parse(midi_file_path)
        detected_key = score.analyze("key")  # Use music21 to automatically detect/predict the key of the midi file
        print(f"Detected key: {detected_key.tonic.name} {detected_key.mode}")
        return detected_key.tonic.name, detected_key.mode
    
    def set_key_manually(self, tonic, key_type):
        self.key_detection = False
        self.tonic = tonic
        self.key_type = key_type
    
    def set_key_automatically(self):
        self.key_detection = True
    
    def set_monophonic(self, make_monophonic = True):
        self.make_monophonic = make_monophonic

    def set_glue_notes(self, glue_notes_flag = True):
        self.glue_notes_flag = glue_notes_flag

    def set_genre(self, genre):
        self.genre = genre
    
    def set_force_to_scale(self, force_to_scale = True):
        self.force_to_scale = force_to_scale

    # Use a postprocessing function to make the output more consistent
    def postprocess_midi(self, midi_file_path):
        """Postprocess a MIDI file by applying various transformations e.g. quantization, tuning to the correct key, gluing notes and making midi files monophonic"""
        midi = pretty_midi.PrettyMIDI(midi_file_path)
        if self.key_detection:
            self.tonic, self.key_type = self._detect_key(midi_file_path) # Detect key if chosen, otherwise use given key in parameters
        key_used = key.Key(self.tonic, self.key_type)
        scale_pitches = [p for p in key_used.pitches]  # All the notes used in the scale of choice

        # Process each instrument
        for instrument in midi.instruments:
            for note in instrument.notes:
                # Quantize start & end
                if self.genre in ["jazz"]:
                    note.start = self._swing_quantize_time(note.start, grid=0.25, swing_amount=0.1)
                    note.end = self._swing_quantize_time(note.end, grid=0.25, swing_amount=0.1)
                else:
                    note.start = self._quantize_time(note.start, grid=0.25)  # 1/16 note grid
                    note.end = self._quantize_time(note.end, grid=0.25)
                if note.end <= note.start:  # Avoid zero-length notes
                    note.end = note.start + 0.25

                # Force pitch into scale
                if self.force_to_scale:
                    note.pitch = self._force_to_scale(note.pitch, scale_pitches)
        if self.glue_notes_flag:
            self._glue_notes(midi)
        self._remove_leading_silence(midi)
        if self.make_monophonic:
            self._flatten_melody(midi)

        # Save cleaned MIDI
        midi_output_dir = self.OUTPUT_DIR
        os.makedirs(midi_output_dir, exist_ok=True)
        
        midi_file_path = Path(midi_file_path)
        midi_output_path = os.path.join(midi_output_dir, f"{midi_file_path.stem}_postprocessed.mid")
        midi.write(midi_output_path)
        
        print(f"Postprocessed MIDI saved as {midi_output_path}")
        return midi_output_path
    
    def add_drums(self, midi_file_path, beat_length = 0.25):
        midi = pretty_midi.PrettyMIDI(midi_file_path)
        # Create a new drum instrument
        drum = pretty_midi.Instrument(program=0, is_drum=True)

        # Find the length of the MIDI file
        midi_length = midi.get_end_time()

        # Add kicks at every beat and snares every other beat
        t = 0
        beat_count = 0
        while t < midi_length:
            if beat_count % 1 == 0:
                kick = pretty_midi.Note(velocity=100, pitch=36, start=t, end=t+0.1)  # MIDI pitch 36 is a kick drum
                drum.notes.append(kick)
            if beat_count % 2 == 0:
                snare = pretty_midi.Note(velocity=100, pitch=38, start=t, end=t+0.1)  # MIDI pitch 38 is a snare drum
                drum.notes.append(snare)
            if beat_count % 0.5 == 0:
                hi_hat = pretty_midi.Note(velocity=100, pitch=42, start=t, end=t+0.1)  # MIDI pitch 42 is a closed hi-hat
                drum.notes.append(hi_hat)
            t += beat_length
            beat_count += 0.5
        midi.instruments.append(drum)

        output_file_path = os.path.join(self.OUTPUT_DIR, f"{Path(midi_file_path).stem}_with_drums.mid")
        # Save the modified MIDI file
        midi.write(output_file_path)
        return output_file_path