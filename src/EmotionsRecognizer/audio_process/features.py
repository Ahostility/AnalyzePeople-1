import numpy as np
import librosa
from sklearn.preprocessing import StandardScaler

CONST_LEN = 2.5  # const of training
CONST_SR = 16000


def mfcc_extract(data, sampling_rate, n_params):
    """
    MFCC extraction.
    """
    MFCC = librosa.feature.mfcc(data, sr=sampling_rate, n_mfcc=n_params)
    MFCC = np.expand_dims(MFCC, axis=0)
    return MFCC


def process_len(data, sampling_rate):
    """
    if data contains less seconds than CONST_LEN, increase with random
    """
    input_length = sampling_rate * CONST_LEN
    if len(data) < input_length:
        max_offset = input_length - len(data)
        offset = np.random.randint(max_offset)
    else:
        offset = 0
    return np.pad(data, (offset, int(input_length) - len(data) - offset), "constant")


def extract_features(data, sampling_rate):
    data = process_len(data, sampling_rate)
    return mfcc_extract(data, sampling_rate, 30)


def fit_X_scaler(X_train):
    """
    fit StandardScaler，and return StandardScaler object
    """
    sc = StandardScaler()
    for _, clips in enumerate(X_train):
        data_i_truncated = np.squeeze(clips)
        sc.partial_fit(data_i_truncated)
    return sc


def get_X_scaled(X_train):
    """
    apply normlization
    """
    scaler = fit_X_scaler(X_train)
    X_train_new = np.zeros(X_train.shape)
    for indx, clips in enumerate(X_train):
        data_i_truncated = np.squeeze(clips)
        if scaler is not None:  # normlize
            data_i_truncated = scaler.transform(data_i_truncated)
        X_train_new[indx, 0, :, :] = data_i_truncated
    return X_train_new
