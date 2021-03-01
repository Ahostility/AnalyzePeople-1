import noisereduce as nr
import numpy as np


def search_silence(data, step=8000):
    start = 0
    end = step
    mean = []
    while True:
        mean.append([np.abs(data[start:end]).mean(), start, end])
        if end > len(data):
            kol = len(mean)
            return sorted(mean)[int(kol/8)]
        start = end
        end += step


def cut_noise(data, channels=0):
    # load data
    index = search_silence(data)
    # select section of data that is noise
    # noisy_part = data[99200:115200]
    noisy_part = data[index[1]:index[2]]
    # perform noise reduction
    print(data.shape)
    reduced_noise_0 = nr.reduce_noise(audio_clip=data[:, 0], noise_clip=noisy_part[:, 0])
    reduced_noise_1 = nr.reduce_noise(audio_clip=data[:, 1], noise_clip=noisy_part[:, 1])
    return reduced_noise_0, reduced_noise_1