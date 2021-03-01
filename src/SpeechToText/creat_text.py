from ..dirs import MARKUP_TXT, MODEL_DIR
from vosk import Model, KaldiRecognizer, SetLogLevel
import sys
import wave
import json

SetLogLevel(-1)
model = Model(f"{MODEL_DIR}/kaldi_vosk")


def write_file(data, name):
    with open(f'{MARKUP_TXT}/{name}.txt', 'w', encoding='utf-8') as f:
        for word in data:
            f.write(str([*word.values()])[1:-1] + '\n')


def write_file_text(data, name):
    with open(f'{MARKUP_TXT}/{name}.txt', 'w', encoding='utf-8') as f:
        for word in data:
            f.write(word['word'] + ' ')


def parse_json(data):
    data = json.loads(data)
    for sample in data['result']:
        del sample['conf']
    return data['result']


def creat_text(path):
    wf = wave.open(path.replace('.wav', '_mono.wav'), "rb")
    rec = KaldiRecognizer(model, wf.getframerate())

    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            pass
        else:
            rec.PartialResult()

    write_file(parse_json(rec.FinalResult()), path.split('/')[-1].replace('.wav', ''))
    # try:
    #    write_file_text(parse_json(rec.FinalResult()), path.split('/')[-1].replace('.wav', ''))
    # except:
    #    print(path.split('/')[-1].replace('.wav', ''))


if __name__ == '__main__':
    creat_text(sys.argv[1])
