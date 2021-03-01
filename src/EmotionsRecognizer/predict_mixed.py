from .audio_process.predict_voice import predict_voice_by_fragments
from .text_process.predict_text import predict_by_parsed_kaldi
from .text_process.parse_kaldi import parse_kaldi_file
from ..dirs import PEOPLE_DIR
import sys
import os


sentiments = ['negative', 'neutral', 'positive']


def predict_text_voice(voice_num, text_num):
    if voice_num == 0:
        if text_num == 2:
            res = 2
        else:
            res = 0
    elif voice_num == 1:
        res = 1
    else:
        if text_num == 0:
            res = 0
        else:
            res = 2

    return sentiments[res]


def predict_mixed(person_voice_preds, person_text_preds, person_duraions):
    res = dict()
    for person in person_voice_preds:
        voice_preds = person_voice_preds[person]
        text_preds = person_text_preds[person]
        final_mark = [predict_text_voice(voice_preds[i], text_preds[i]) for i in range(len(voice_preds))]
        res[person] = list(zip(final_mark, person_duraions[person]))
    return res


def predict_mixed_file(audio_path, kaldi_path, duration=5):
    person_texts, person_durations = parse_kaldi_file(kaldi_path, duration)
    person_text_preds = predict_by_parsed_kaldi(person_texts)
    person_voice_preds = predict_voice_by_fragments(audio_path, person_durations)
    return predict_mixed(person_voice_preds, person_text_preds, person_durations)


def prognoze_data(name):
    if not os.path.exists(PEOPLE_DIR / name / 'result'): os.mkdir(PEOPLE_DIR / name / 'result')
    txt_folder = PEOPLE_DIR / name / 'txt'
    wav_folder = PEOPLE_DIR / name / 'wav'
    result_folder = PEOPLE_DIR / name / 'result'

    lst_txt = os.listdir(txt_folder)
    lst_wav = os.listdir(wav_folder)

    all_result = []
    for idx, (txt, wav) in enumerate(zip(lst_txt, lst_wav)):
        result = predict_mixed_file(f'{wav_folder}/{wav}', f'{txt_folder}/{txt}')
        all_result.append(result)
        with open(result_folder / f'{name}-{idx}.txt', 'w') as f:
            f.write(str(result))
    
    return all_result


if __name__ == "__main__":
    prognoze_data(sys.argv[1])