from .Preprocessing_tools import preprocess_text, stem_text, prepare_file
import itertools
import re


percentage_thresh = 0.1

def build_regex(lst_phrases, interfere_thresh=2):
    res = r''
    for phrase in lst_phrases:
        words = phrase.split(' ')
        if len(words) == 1:
            res += words[0] + ' |'
        else:
            all_combinations = list(itertools.permutations(words))
            for combination in all_combinations:
                res += combination[0] + ' '
                for word in combination[1:]:
                    res += '(?:\w+ ){0,' + str(interfere_thresh) + '}'  + word + ' '
                res += '|'
    return res[:-1]


def search_phrases(text, phrases_search, interfere_thresh=2):
    regex = build_regex(phrases_search)
    text = preprocess_text(text) + ' '
    return [(i.start(), i.end()) for i in re.finditer(regex, text)]


def main_pipeline(text, file_path, isprepare=False):
    indexes, stemmed_text = search_phrases(text, file_path, False)
    for index in indexes:
        pass
