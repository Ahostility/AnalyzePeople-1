def open_text(file_path):
    f = open(file_path, 'r', encoding='utf8')
    text = f.read()
    f.close()
    return text


def add_to_dict(d, key, elem):
    if key in d:
        d[key].append(elem)
    else:
        d[key] = [elem]


def parse_kaldi_file(file_path, duration, silence_limit_un=2, silence_limit_process=6, max_error=2):
    lines = open_text(file_path).split('\n')[1:]
    res_texts = dict()
    res_durations = dict()
    mixed_mark = 'x'
    max_duration = duration + max_error
    prev_person = -1
    cur_union_text = ''
    cur_union_dur = []
    for line in lines:
        if line == '':
            continue
        time_person_text = line.split(', ')
        start = float(time_person_text[0])
        end = float(time_person_text[1])
        person = float(time_person_text[2])
        text = time_person_text[3].strip(" '")
        if person == prev_person and\
                start - cur_union_dur[1] <= silence_limit_un and\
                end - cur_union_dur[0] <= max_duration:
            cur_union_dur[1] = end
            cur_union_text += ' ' + text

        elif prev_person == -1:
            cur_union_text = text
            cur_union_dur = [start, end]

        else:
            add_to_dict(res_texts, prev_person, cur_union_text)
            add_to_dict(res_durations, prev_person, cur_union_dur)
            if start - cur_union_dur[1] > silence_limit_process:
                add_to_dict(res_texts, mixed_mark, 'он')
                add_to_dict(res_durations, mixed_mark, [cur_union_dur[1], start])
            cur_union_dur = [start, end]
            cur_union_text = text
        prev_person = person

    if prev_person != -1:
        add_to_dict(res_texts, prev_person, cur_union_text)
        add_to_dict(res_durations, prev_person, cur_union_dur)
    return res_texts, res_durations
