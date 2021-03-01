import numpy as np
from .features import get_X_scaled, extract_features, CONST_LEN, CONST_SR
from ...audio.audio import read_file


class WavPartsByText:
    """Splitting audio"""
    def __init__(self, audio_path, durations, part_seconds=CONST_LEN):
        self.sample_rate = CONST_SR
        self.data, _ = read_file(audio_path, True)
        self.durations = durations
        self.full_len = len(durations)
        self.part_seconds = part_seconds
        self.audio_data = []
        self.audio_ids = [[] for _ in range(len(durations))]

    def split_audio(self):
        start_ind = 0
        for i in range(len(self.durations)):
            start = self.durations[i][0]
            while True:
                finish = min(start + self.part_seconds, self.durations[i][1])
                part = self.data[int(start * self.sample_rate): int(finish * self.sample_rate)]
                self.audio_data.append(np.array(part).astype(np.float32))
                self.durations.append([start, finish])
                self.audio_ids[i].append(start_ind)
                start_ind += 1
                start += self.part_seconds
                if start >= self.durations[i][1]:
                    break


class AudioLoaderByFragments:
    """Class for splitted, preprocessed audio"""
    def __init__(self, audio_path, person_durations):
        sr = CONST_SR
        f = lambda x: extract_features(x, sr)

        self.features = dict()
        self.audio_ids = dict()
        for person in person_durations.keys():
            wav_parts = WavPartsByText(audio_path, person_durations[person], part_seconds=CONST_LEN)
            wav_parts.split_audio()
            self.features[person] = get_X_scaled(np.stack(list(map(f, wav_parts.audio_data))))
            self.audio_ids[person] = wav_parts.audio_ids
