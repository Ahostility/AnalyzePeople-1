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


def preprocess_file(file_name='farewell_raw.txt'):
    f = open(file_name, 'r', encoding='utf8')
    farewell_list = f.read().split('\n')
    f.close()
    new_farewell_list = []
    for phrase in farewell_list:
        cur_phrase = []
        for word in phrase.split(' '):
            cur_phrase.append(lemmatizer.parse(word)[0].normal_form)
        new_farewell_list.append(' '.join(cur_phrase))

    farewell_txt = '\n'.join(new_farewell_list)
    f = open('farewell.txt', 'w', encoding='utf8')
    f.write(farewell_txt)
    f.close()


def find_farewell(text):
    f = open(f'{DICT_DIR}/farewell.txt', 'r', encoding='utf8')
    farewell_list = f.read().split('\n')
    f.close()

    text = preprocess_text(text)
    text = ' '.join([lemmatizer.parse(word)[0].normal_form for word in text.split(' ')])
    pattern = '|'.join(farewell_list)
    [i.start() for i in re.finditer(pattern, text)]
    return [(i.start(), i.end()) for i in re.finditer(pattern, text)]



if __name__ == "__main__":
    text = 'Добрый день что желаете заказать Здравствуйте что вам нужно пока'
    print(find_farewell(text))