from dostoevsky.tokenization import RegexTokenizer
from dostoevsky.models import FastTextSocialNetworkModel
from .parse_kaldi import open_text

tokenizer = RegexTokenizer()  # токенизатор текста
text_model = FastTextSocialNetworkModel(tokenizer=tokenizer)  # модель анализа тональности

to_numbers = {
    'negative': 0,
    'neutral': 1,
    'positive': 2,
    'skip': 1,
    'speech': 1,
}


def choose_sentiment(pred):
    return sorted(pred, key=lambda x: pred[x])[-1]


def predict_sentiment(texts):
    preds = text_model.predict(texts)
    return list(map(lambda pred: choose_sentiment(pred), preds))


def predict_by_text_file(text_path):
    text = open_text(text_path).strip()
    if text == '':
        return 1
    return predict_by_texts([text])[0]


def predict_by_parsed_kaldi(person_texts):
    res = dict()
    for person in person_texts.keys():
        res[person] = predict_by_texts(person_texts[person])
    return res


def predict_by_texts(texts):
    return list(map(lambda x: to_numbers[x], predict_sentiment(texts)))
