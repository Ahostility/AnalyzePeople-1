import numpy as np
import librosa
from .features import get_X_scaled, extract_features, CONST_LEN, CONST_SR
from ...audio.audio import read_file


class WavParts:
    """Splitting audio"""
    def __init__(self, audio_path, part_seconds=CONST_LEN):
        self.sample_rate = CONST_SR
        self.data, _ = read_file(audio_path)
        self.full_duration = librosa.get_duration(self.data, self.sample_rate)
        self.s = part_seconds
        self.c = 0
        self.done = False
        self.durations = []

    def __iter__(self):
        self.c = 0
        self.done = False
        return self

    def __next__(self):
        if self.done:
            raise StopIteration

        end = self.c + self.s
        part = self.data[int(self.c * self.sample_rate): int(end * self.sample_rate)]
        self.durations.append((self.c, end))

        self.c += self.s
        if self.c > self.full_duration:
            self.durations[-1] = (self.durations[-1][0], self.full_duration)
            self.done = True

        res = np.array(part).astype(np.float32)
        return res


class AudioLoader:
    """Class for splitted, preprocessed audio"""
    def __init__(self, audio_path):
        parts = WavParts(audio_path, part_seconds=CONST_LEN)
        sr = parts.sample_rate

        f = lambda x: extract_features(x, sr)
        self.features = get_X_scaled(np.stack(list(map(f, parts))))
        self.durations = parts.durations
        self.full_duration = parts.full_duration
