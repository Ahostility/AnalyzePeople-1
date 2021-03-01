from .audio.preprocessing import preprocessing_folder
from .SpeechToText.grouping_dialogue import grouping_dialog
from .diarization.diarization import diarize_all
# from .EmotionsRecognizer.predict_mixed import prognoze_data
from .dirs import FINAL_DIR
import sys


def pipeline(path_folder, gpu=False):
    name_folder = path_folder.split('/')[-2]
    preprocessing_folder(path_folder)
    if gpu:
        from .SpeechToText.gpu_creat_text import creat_text_gpu
        creat_text_gpu(f'{FINAL_DIR}/{name_folder}.wav')
    else:
        from .SpeechToText.creat_text import creat_text
        creat_text(f'{FINAL_DIR}/{name_folder}.wav')
    grouping_dialog(name_folder)
    diarize_all(name_folder, gpu)
    # prognoze_data(name_folder)


if __name__ == '__main__':
    pipeline(sys.argv[1])