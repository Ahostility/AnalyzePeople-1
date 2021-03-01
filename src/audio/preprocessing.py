from ..dirs import FINAL_DIR
from .audio import gluing, read_file, write_file
import numpy as np
import os
import sys


def preprocessing_folder(path_folder_wav):
    wav_name = f"{FINAL_DIR}/{path_folder_wav.split('/')[-2]}.wav"
    data = gluing([read_file(f'{path_folder_wav}/{file_name}')[0] for file_name in os.listdir(path_folder_wav)])
    write_file(wav_name, data)
    if len(data.shape) == 2:
        data = np.mean([data[:, 0], data[:, 1]], axis=0)
    write_file(wav_name.replace('.wav', '_mono.wav'), data)



if __name__ == '__main__':
    preprocessing_folder(sys.argv[1])