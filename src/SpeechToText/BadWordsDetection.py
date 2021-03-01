from ..dirs import DICT_DIR
import re
from pymorphy2 import MorphAnalyzer

lemmatizer = MorphAnalyzer()

def preprocess_text(text):
    text = text.lower()
    text = re.sub('\W+', ' ', text)
    text = re.sub('\d+', ' ', text)
    text = re.sub(' +', ' ', text)
    text = text.replace('ё', 'е')
    return text.strip()


def delete_bad_words(text):
    f = open(f'{DICT_DIR}/BadWords.txt', 'r', encoding='utf8')
    bad_words_list = set(f.read().split('\n'))
    f.close()

    text = preprocess_text(text)
    res = []
    for word in text.split(' '):
        if lemmatizer.parse(word)[0].normal_form not in bad_words_list:
            res.append(word)
    return ' '.join(res)


# if __name__ == "__main__":
    # print(delete_bad_words('Привет блядь'))