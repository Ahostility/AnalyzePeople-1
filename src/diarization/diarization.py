from ..dirs import PEOPLE_DIR, SLEPOK_DIR
from .audio import preprocess_wav
from resemblyzer.voice_encoder import VoiceEncoder
from .cut_pauses import wav_by_segments
from .kaldi_tools import parse_kaldi_file, creat_output_file, write_file

import os
import numpy as np
import sys


def get_similarity(encoder, cont_embeds, speaker_wav):
    speaker_embeds = encoder.embed_utterance(speaker_wav)
    return cont_embeds @ speaker_embeds


def get_similarity_several(encoder, cont_embeds, speaker_wavs, speaker_names):
    res = dict()
    for i in range(len(speaker_names)):
        res[speaker_names[i]] = get_similarity(encoder, cont_embeds, speaker_wavs[i])
    return res


def get_operator_wavs(operators_dir):
    operator_names = []
    wavs = []
    for slepok_file in os.listdir(operators_dir):
        file_path = os.path.join(operators_dir, slepok_file)
        operator_names.append('_'.join(slepok_file.split('.')[:-1]))
        wav = preprocess_wav(file_path, noise=False)
        wavs.append(wav)
    return wavs, operator_names


def identify_operator(wav, encoder, cont_embeds):
    operators_wavs, operators_names = get_operator_wavs(str(SLEPOK_DIR))
    operators_similarity = get_similarity_several(encoder, cont_embeds, operators_wavs, operators_names)
    operators_similarity_mean = [op_sim.mean() for op_sim in operators_similarity.values()]
    best_id = np.argmax(operators_similarity_mean)
    best_operator_name = operators_names[best_id]
    return operators_wavs[best_id], operators_similarity[best_operator_name], best_operator_name


def make_points(data, timeline, window):
    points = []
    time_points = []
    start = 0
    end = window
    while True:
        points.append(np.mean(data[start:end]))
        time_points.append(timeline[start])
        start = end
        end += window
        if end > len(data):
            return points, time_points


def sliding_window(data, sr=16000,  window=1600, size=300):
    arr_slid = []
    timeline = []
    start = 0
    end = window
    while True:
        timeline.append(start / sr)
        arr_slid.append(np.mean(np.abs(data[start:end])))
        start = end
        end += size
        if end > len(data):
            return make_points(arr_slid, timeline, 20)


def create_make(points_0, points_1, timeline):
    skp_lst = []
    for p_0, p_1 in zip(points_0, points_1):
        skp_lst.append(np.argmax([p_0, p_1]))

    spk = []
    start = 0
    end = 0
    for i in range(1, len(skp_lst)):
        if skp_lst[i] != skp_lst[i - 1]:
            end = i
            spk.append([timeline[start], timeline[end], skp_lst[i - 1]])
            start = end
    return spk


def identification(cutted_data, device):
    encoder = VoiceEncoder(device, verbose=False)
    _, cont_embeds, _ = encoder.embed_utterance(cutted_data, return_partials=True, rate=16)
    operator_wav, operator_similarity, operator_name = identify_operator(cutted_data, encoder, cont_embeds)
    return operator_name


def diarize(wav_fpath, file_kaldi, device):
    start_end_text = parse_kaldi_file(file_kaldi)
    cutted_data, sr, voice_fragments, data = wav_by_segments(wav_fpath, start_end_text, 0)
    name_operator = identification(cutted_data, device)
    points_0, timeline_0 = sliding_window(data[:, 0], sr)
    points_1, timeline_1 = sliding_window(data[:, 1], sr)
    return create_make(points_0, points_1, timeline_0), name_operator


def diarize_all(name, gpu=False):
    folder_kaldi = f'{PEOPLE_DIR}/{name}/txt/'
    folder_wav = f'{PEOPLE_DIR}/{name}/wav/'
    device = 'cuda' if gpu else 'cpu'
    for idx, file_name in enumerate(sorted(os.listdir(folder_kaldi))):
        kaldi_fpath = folder_kaldi + file_name
        wav_fpath = folder_wav + file_name.replace('.txt', '.wav')
        markup, name_operator = diarize(wav_fpath, kaldi_fpath, device)
        result = creat_output_file(kaldi_fpath, markup)
        write_file(result, name_operator, name, idx)


if __name__ == '__main__':
    diarize_all(sys.argv[1])

''' 
        MAX_SIZE = 3500
        start = 0
        end = MAX_SIZE
        partial_embeds = 0
        if MAX_SIZE > len(mels):
            with torch.no_grad():
                melss = torch.from_numpy(mels[start:]).to(self.device)
                partial_embeds = self(melss).cpu().numpy()
        else:
            while True:
                if end > len(mels):
                    with torch.no_grad():
                        melss = torch.from_numpy(mels[start:]).to(self.device)
                        partial_embeds = np.concatenate((partial_embeds, self(melss).cpu().numpy()), axis=0)
                            break
                    elif start == 0:
                        with torch.no_grad():
                            melss = torch.from_numpy(mels[start:end]).to(self.device)
                            partial_embeds = self(melss).cpu().numpy()
                    else:
                        with torch.no_grad():
                            melss = torch.from_numpy(mels[start:end]).to(self.device)
                            partial_embeds = np.concatenate((partial_embeds, self(melss).cpu().numpy()), axis=0)
                    start = end
                    end += MAX_SIZE
                    torch.cuda.empty_cache()
                '''
