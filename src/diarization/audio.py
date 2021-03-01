from resemblyzer.hparams import *
from pathlib import Path
from typing import Optional, Union
import numpy as np
from ..audio.audio import read_file


int16_max = (2 ** 15) - 1


def preprocess_wav(fpath_or_wav: Union[str, Path, np.ndarray], channel=0, noise=True, normal=True):
    """
    Applies preprocessing operations to a waveform either on disk or in memory such that  
    The waveform will be resampled to match the data hyperparameters.

    :param channel:
    :param fpath_or_wav: either a filepath to an audio file (many extensions are supported, not
    just .wav), either the waveform as a numpy array of floats.
    :param source_sr: if passing an audio waveform, the sampling rate of the waveform before 
    preprocessing. After preprocessing, the waveform'speaker sampling rate will match the data 
    hyperparameters. If passing a filepath, the sampling rate will be automatically detected and 
    this argument will be ignored.
    """
    # Load the wav from disk if needed
    if isinstance(fpath_or_wav, str) or isinstance(fpath_or_wav, Path):
        wav, _ = read_file(str(fpath_or_wav), noise)
        # wav = wav[channel]
    else:
        wav = fpath_or_wav

    # Apply the preprocessing: normalize volume and shorten long silences
    if normal:
        if len(wav.shape) == 2:
            wav = normalize_volume(wav[channel], audio_norm_target_dBFS, increase_only=True)
        else:
            wav = normalize_volume(wav, audio_norm_target_dBFS, increase_only=True)
    return wav


def normalize_volume(wav, target_dBFS=-30, increase_only=False, decrease_only=False):
    if increase_only and decrease_only:
        raise ValueError("Both increase only and decrease only are set")
    rms = np.sqrt(np.mean((wav * int16_max) ** 2))
    wave_dBFS = 20 * np.log10(rms / int16_max)
    dBFS_change = target_dBFS - wave_dBFS
    if dBFS_change < 0 and increase_only or dBFS_change > 0 and decrease_only:
        return wav
    return wav * (10 ** (dBFS_change / 20))
