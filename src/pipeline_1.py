from .diarization.diarization import diarize_all
# from .EmotionsRecognizer.predict_mixed import prognoze_data
import sys


def pipeline(path_folder, gpu=False):
    name_folder = path_folder.split('/')[-2]
    diarize_all(name_folder, gpu)
    # prognoze_data(name_folder)


if __name__ == '__main__':
    pipeline(sys.argv[1], True)