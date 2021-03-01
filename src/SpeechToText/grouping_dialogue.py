from ..dirs import MARKUP_TXT, FINAL_DIR, PEOPLE_DIR
from .BadWordsDetection import delete_bad_words
from .GreetingsDetection import find_farewell
from ..audio.audio import read_file, write_file
import sys
import os


def grouping_dialog(name):
    OCCURRENCE_GREETINGS = 10

    with open(f'{MARKUP_TXT}/{name}.txt', 'r', encoding='utf-8') as f:
        data_words = [[float(word.split(', ')[0]), float(word.split(', ')[1]), word.split(', ')[2][1:-1]] for word in
                      f.read().split('\n')[:-1]]
    detection_farewell = 0
    detection_farewell_idx = []
    for idx, (end, start, word) in enumerate(data_words):
        detection_farewell -= 1
        if find_farewell(word) and detection_farewell <= 0:
            detection_farewell = OCCURRENCE_GREETINGS
            detection_farewell_idx.append(idx)
    else:
        if detection_farewell <= 0:
            detection_farewell_idx.append(idx)

    data, samplerate = read_file(f'{FINAL_DIR}/{name}.wav')

    start_sample = 0
    start_dialog = 0
    end_new_file = 0
    for idx, split_point in enumerate(detection_farewell_idx):
        if start_sample:
            end_new_file = end
        start = int(start_sample * samplerate)
        end = int(data_words[split_point][0] * samplerate)

        if not os.path.exists(f'{PEOPLE_DIR}/{name}'): os.mkdir(f'{PEOPLE_DIR}/{name}')
        if not os.path.exists(f'{PEOPLE_DIR}/{name}/wav'): os.mkdir(f'{PEOPLE_DIR}/{name}/wav')
        if not os.path.exists(f'{PEOPLE_DIR}/{name}/txt'): os.mkdir(f'{PEOPLE_DIR}/{name}/txt')
        write_file(f'{PEOPLE_DIR}/{name}/wav/sample-{idx}.wav', data[start: end])

        with open(f'{PEOPLE_DIR}/{name}/txt/sample-{idx}.txt', 'w', encoding='utf-8') as f:
            for start, end, word in data_words[start_dialog:split_point]:
                word = str(word if delete_bad_words(word) else '')
                f.write(f"{round(start-end_new_file, 2)},{round(end-end_new_file, 2)}," + f"'{word}'" + '\n')

        start_sample = data_words[split_point][1]
        start_dialog = split_point


if __name__ == "__main__":
    print(grouping_dialog(sys.argv[1]))
