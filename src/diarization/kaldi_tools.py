from ..dirs import PEOPLE_DIR


def open_text(file_path):
    f = open(file_path, 'r', encoding='utf8')
    text = f.read()
    f.close()
    return text


def parse_kaldi_file(file_path, min_pause = 1):
    lines = open_text(file_path).split('\n')
    res_durations = []
    was = False
    for line in lines:
        if line == '':
            continue
        time_text = line.split(',')
        start = float(time_text[1])
        end = float(time_text[0])
        text = time_text[2].strip("'")
        if not was:
            res_durations = [[start, end, text]]
            was = True
        elif start - res_durations[-1][1] < min_pause:
            res_durations[-1][1] = end
            res_durations[-1][2] += text
        else:
            res_durations.append([start, end, text])
    return res_durations


def read_kaldi_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = []
        for line in f.readlines():
            values = line.split(',')
            data.append([float(values[0]), float(values[1]), values[2][1:-2]])
    return data


def write_file(markup, name_operator, name, idx):
    with open(f'{PEOPLE_DIR}/{name}/txt/sample-{idx}.txt', 'w', encoding='utf-8') as f:
        f.write(name_operator + '\n')
        for sample in markup:
            f.write(str([*sample])[1:-1] + '\n')


def creat_output_file(file_path, markup):
    data = read_kaldi_file(file_path)
    dialog = []
    for start, end, spk in markup:
        phrase = ''
        for end_w, start_w, word in data:
            if start < start_w <= end:
                phrase += word + ' '
        if phrase != '':
            dialog.append([round(start, 2), round(end, 2), spk, phrase[:-1]])
    return dialog
