from pathlib import Path
import wget
import os
from pyunpack import Archive


BASE_DIR = Path(__file__).absolute().parent.parent
DATA_DIR = BASE_DIR / 'data'
MODEL_DIR = BASE_DIR / 'models'
DICT_DIR = DATA_DIR / 'dictionaries'
OUTPUT_DIR = DATA_DIR / 'output'
FINAL_DIR = OUTPUT_DIR / 'full_wav'
MARKUP = DATA_DIR / 'markup'
MARKUP_TXT = MARKUP / 'txt'
PEOPLE_DIR = OUTPUT_DIR / 'people'
SLEPOK_DIR = DATA_DIR / 'slepok'

DATA_RAW_DIR = DICT_DIR / 'data_raw'
DATA_CLIENT_DIR = DATA_RAW_DIR / 'key_words_client'
DATA_SELLER_DIR = DATA_RAW_DIR / 'key_words_seller'
DATA_NORMALIZED_DIR = DICT_DIR / 'data_normalized'
DATA_NORMALIZED_CLIENT_DIR = DATA_NORMALIZED_DIR / 'key_words_client'
DATA_NORMALIZED_SELLER_DIR = DATA_NORMALIZED_DIR / 'key_words_seller'
STAGES_FILE = DICT_DIR / 'stages.txt'


DATA_DIR.mkdir(parents=True, exist_ok=True)
MODEL_DIR.mkdir(parents=True, exist_ok=True)
DICT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)
FINAL_DIR.mkdir(parents=True, exist_ok=True)
MARKUP.mkdir(parents=True, exist_ok=True)
MARKUP_TXT.mkdir(parents=True, exist_ok=True)
PEOPLE_DIR.mkdir(parents=True, exist_ok=True)
SLEPOK_DIR.mkdir(parents=True, exist_ok=True)
DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)
DATA_CLIENT_DIR.mkdir(parents=True, exist_ok=True)
DATA_SELLER_DIR.mkdir(parents=True, exist_ok=True)
DATA_NORMALIZED_CLIENT_DIR.mkdir(parents=True, exist_ok=True)
DATA_NORMALIZED_SELLER_DIR.mkdir(parents=True, exist_ok=True)
DATA_NORMALIZED_SELLER_DIR.mkdir(parents=True, exist_ok=True)


url_vosk = 'https://storage.yandexcloud.net/speechkittest/kaldi_vosk.7z'
url_emotion = 'https://storage.yandexcloud.net/speechkittest/voice_sent.pth'

if not os.path.exists(MODEL_DIR / 'kaldi_vosk'):
    wget.download(url_vosk, out=f'{MODEL_DIR}/')
    Archive(MODEL_DIR / 'kaldi_vosk.7z').extractall(MODEL_DIR)
    os.remove(MODEL_DIR / 'kaldi_vosk.7z')

if not os.path.exists(MODEL_DIR / 'voice_sent.pth'): wget.download(url_emotion, out=f'{MODEL_DIR}/')