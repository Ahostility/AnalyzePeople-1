import numpy as np

min_time = 3
d = 0.06
duration = 1.6
max_time = 5


def get_another_fragments(voice_fragments, operator_similarity, wav_splits):
    new_fragments = []
    new_similarity = []
    for voice_fragment in voice_fragments:
        cur_diff = voice_fragment[1] - voice_fragment[0]
        if cur_diff >= min_time:
            ind1 = max(0, int((voice_fragment[0] - duration) / d))
            ind2 = int((voice_fragment[1] - duration) / d)
            if cur_diff <= max_time:
                new_similarity.append(operator_similarity[ind1:ind2].mean())
                new_fragments.append(voice_fragment)
            else:
                cur_similarity_arr, cur_fragments_arr = segment_fragment(operator_similarity[ind1:ind2],
                                                                         wav_splits[ind1:ind2])
                new_similarity += cur_similarity_arr
                new_fragments += cur_fragments_arr

    if len(new_similarity) == 0:
        res = []
    sorted_ids = np.argsort(new_similarity)

    min_id = int(len(sorted_ids) / 8)
    res = new_fragments[sorted_ids[min_id]]
    # print(res)
    # res = [18, 21]
    return res


def segment_fragment(a, wav_splits):
    window = int((min_time - 1.6)/0.06)
    new_similarity = [a[i:i+window].mean() for i in range(len(a) - window + 1)]
    new_fragments = [[wav_splits[i][0], wav_splits[i + window - 1][1]] for i in range(len(new_similarity))]
    return new_similarity, new_fragments


def unite_segments(fragments, min_time):
    res = []
    cut_part = 0.1
    sum_time = 0.0
    for fragment in fragments:
        is_changed = False
        fragment[0] += cut_part
        fragment[1] -= cut_part
        for i in range(len(res)):
            if fragment[0] < res[i][1] and fragment[0] > res[i][0]:
                sum_time += fragment[1] - res[i][1]
                res[i][1] = fragment[1]
                is_changed = True
                break
            elif fragment[1] < res[i][1] and fragment[1] > res[i][0]:
                sum_time += res[i][0] - fragment[0]
                res[i][0] = fragment[0]
                is_changed = True
                break

        if not is_changed:
            sum_time += fragment[1] - fragment[0]
            res.append([fragment[0], fragment[1]])

        if sum_time >= min_time:
            return res
    return res
