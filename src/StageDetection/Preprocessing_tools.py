from ..dirs import DATA_CLIENT_DIR, DATA_SELLER_DIR, DATA_NORMALIZED_CLIENT_DIR, DATA_NORMALIZED_SELLER_DIR
import re
import os
from nltk.stem.snowball import RussianStemmer
import pandas as pd
from .constnats import key_category
import warnings

warnings.simplefilter("ignore")
stemmer = RussianStemmer()

"""def get_stop_words(filepath):
    f = open(filepath, 'r', encoding='utf8')
    stop_words = f.read().split('\n')
    f.close()
    return [stop_word.strip() for stop_word in stop_words]


stop_words = set(get_stop_words(DATA_DIR / 'stop_words.txt'))"""


def preprocess_text(text):
    """
    preprocess text
    """
    text = text.lower()
    text = re.sub('\W+', ' ', text)
    text = re.sub('\d+', ' ', text)
    text = re.sub(' +', ' ', text)
    text = text.replace('ё', 'е')
    return text.strip()


def stem_text(text):
    words = text.split(' ')
    stemmed = []
    for word in words:
        stemmed.append(stemmer.stem(word))
    return stemmed


def full_preprocess_text(text):
    text = preprocess_text(text)
    return ' '.join(stem_text(text))


def create_dir(dir):
    if not os.path.exists(dir):
        os.mkdir(dir)


def open_text(file_path):
    f = open(file_path, 'r', encoding='utf8')
    text = f.read()
    f.close()
    return text


def prepare_files():
    folders = [(DATA_CLIENT_DIR, DATA_NORMALIZED_CLIENT_DIR), (DATA_SELLER_DIR, DATA_NORMALIZED_SELLER_DIR)]
    for folder in folders:
        create_dir(folder[1])

    for folder in folders:
        for file_name in os.listdir(folder[0]):
            read_path_file = os.path.join(folder[0], file_name)
            save_path_file = os.path.join(folder[1], file_name)
            prepare_file(read_path_file, save_path_file)


def prepare_file(read_path_file, save_path_file):
    df = pd.read_excel(read_path_file, engine='openpyxl')
    res_dict = dict()
    for column in df.columns:
        if column == key_category:
            res_dict[column] = list(df[column].dropna().values)
        phrases = list(df[column].values)
        cur_res_phrases = []
        for phrase in phrases:
            if not isinstance(phrase, str) or phrase is None :
                cur_res_phrases.append('')
                continue
            phrase = preprocess_text(phrase)
            cur_res_phrases.append(' '.join(stem_text(phrase)))
        res_dict[column] = cur_res_phrases
    pd.DataFrame.from_dict(res_dict).to_excel(save_path_file, index=False, encoding='utf8')
