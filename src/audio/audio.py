import soundfile as sf
import numpy as np
import matplotlib.pyplot as plt
import os


def convert_wav(path: str):
    """
        new_path = convert_wav(path)
        output: новое имя файла
    """
    new_path = path.replace(".wav", "_16.wav")
    os.system(f'ffmpeg -i {path} -loglevel quiet -acodec pcm_s16le -ac 2 -ar 16000 {new_path}')
    os.remove(path)
    return new_path


def read_file(path, one=False):
    """
        data, samplerate = read_file('test.wav')
        output: data - массив значений аудио, samplerate - характеристика аудио
    """
    data, samplerate = sf.read(path, dtype='float32')
    if samplerate != 16000:
        data, _ = read_file(convert_wav(path))
    if len(data.shape) == 2 and one:
        data = np.mean([data[:, 0], data[:, 1]], axis=0)
    return data, samplerate


def plot_schedule(data):
    """
        plot_schedule(data)
    """
    plt.figure()
    plt.plot(data)
    plt.show()


def gluing(audio_data):
    """
        full_data = gluing((data, data1))
        output: объединенный массив
    """
    return np.concatenate(audio_data)


def write_file(file_path, data, samplerate=16000):
    """
        write_file('test.wav', full_data, samplerate)
    """
    sf.write(file_path, data, samplerate)