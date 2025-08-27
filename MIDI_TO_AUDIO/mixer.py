from pydub import AudioSegment
from pydub.utils import db_to_float
import array

# mixer code heavily inspired by https://gist.github.com/jiaaro/b610728a642bbaa28b3f1e5d3b6f9cf7

class Mixer(object):
    def __init__(self):
        self.parts = []
    
    def overlay(self, sound, position=0):
        self.parts.append((position, sound))
        return self
        
    def _sync(self):
        positions, segs = zip(*self.parts)

        frame_rate = segs[0].frame_rate
        array_type = segs[0].array_type
        
        offsets = [int(frame_rate * pos / 1000.0) for pos in positions]
        segs = AudioSegment.empty()._sync(*segs)
        return list(zip(offsets, segs))
    
    def __len__(self):
        parts = self._sync()
        seg = parts[0][1]
        frame_count = max(
            offset + seg.frame_count()
            for offset, seg in parts
        )
        return 1000.0 * frame_count / seg.frame_rate
        
    def append(self, sound):
        self.overlay(sound, position=len(self))
        
    def to_audio_segment(self, gain=0):
        samp_multiplier = db_to_float(gain)
        parts = self._sync()
        seg = parts[0][1]
        channels = seg.channels
        
        frame_count = max(
            offset + seg.frame_count()
            for offset, seg in parts
        )
        sample_count = int(frame_count * seg.channels)
        
        output = array.array(seg.array_type, [0]*sample_count)
        for offset, seg in parts:
            sample_offset = offset * channels
            samples = seg.get_array_of_samples()
            for i in range(len(samples)):
                output[i+sample_offset] += int(samples[i] * samp_multiplier)
        
        return seg._spawn(output)
        
        
sound1 = AudioSegment.from_file(r"C:\Users\rober\OneDrive\Documents\0.School\WILLIAM PERKIN\Comp\1. NEA project prototype\MIDI_TO_AUDIO\output\rendered_song.wav")
sound2 = AudioSegment.from_file(r"C:\Users\rober\OneDrive\Documents\0.School\WILLIAM PERKIN\Comp\1. NEA project prototype\MIDI_TO_AUDIO\output\rendered_song0.wav")


m = Mixer()
m.overlay(sound1)
m.overlay(sound2, 1000)

m_segment = m.to_audio_segment(gain=-5.0)
m_segment.export(r"C:\Users\rober\OneDrive\Documents\0.School\WILLIAM PERKIN\Comp\1. NEA project prototype\MIDI_TO_AUDIO\output\combined_output_mixer.wav", format="wav")