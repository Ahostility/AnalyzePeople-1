import torch
import torch.nn as nn
from torchvision import models
import numpy as np
from .preprocess_audio import AudioLoader
from .preprocess_audio_by_fragments import AudioLoaderByFragments
from ...dirs import MODEL_DIR

N_CLASS = 6
BATCH_SIZE = 200

#------------------model------------------
voice_model = models.resnet50(
    pretrained=True,
    progress=True
)

first_conv_layer = voice_model.conv1
voice_model.conv1 = nn.Sequential(
    nn.Conv2d(1, 3, kernel_size=3, stride=1, padding=1, dilation=1, groups=1, bias=True),
    first_conv_layer
)

num_ftrs = voice_model.fc.in_features
voice_model.fc = torch.nn.Sequential(
    torch.nn.Dropout(0.2),
    torch.nn.Linear(num_ftrs, N_CLASS)
)

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
chechpoint = torch.load(MODEL_DIR / 'voice_sent.pth', map_location=device)
voice_model.load_state_dict(chechpoint["model_state_dict"])
voice_model = voice_model.to(device)
voice_model.eval()
#-----------------------------------------

voice_to_numbers = {
    0: 0,
    3: 0,
    2: 1,
    5: 1,
    1: 2,
    4: 2,
}


def unite_results_list(preds):
    """unites results in all list"""
    elems = [0, 1, 2]
    res_arr = [len(preds[preds == elem]) / len(preds) for elem in elems]
    res = np.argmax(res_arr)
    if res == 1:
        if res_arr[0] < 0.15 and res_arr[2] > 0.35:
            res = 2
        elif res_arr[2] < 0.15 and res_arr[0] > 0.35:
            res = 0
    if res_arr[0] == res_arr[2]:
        res = 1
    return res


def unite_results(preds, unite_ids):
    """unites results in parts of list"""
    res = []
    for ids in unite_ids:
        res.append(unite_results_list(preds[ids]))
    return res


def predict_voice_features(features):
    preds = []
    features = torch.FloatTensor(features[:])
    max_cnt = features.shape[0]
    for i in range(0, features.shape[0], BATCH_SIZE):
        cur_features = features[i:min(i + BATCH_SIZE, max_cnt)]
        cur_features = cur_features.to(device)
        preds += list(voice_model(cur_features).argmax(dim=1).cpu().numpy())
    return preds


def predict_voice(features, unite_ids=None):
    """Predict sentiment by features"""
    preds = predict_voice_features(features)
    f = lambda x: voice_to_numbers[x]
    if unite_ids is None:
        return list(map(f, preds))
    preds = np.array(list(map(f, preds)))
    return unite_results(preds, unite_ids)


def predict_voice_by_fragments(audio_path, person_durations):
    audio_loader = AudioLoaderByFragments(audio_path, person_durations)
    person_preds = dict()
    for person in audio_loader.audio_ids.keys():
        person_preds[person] = predict_voice(audio_loader.features[person],
                                             audio_loader.audio_ids[person])
    return person_preds


def predict_voice_only(audio_path):
    """predict sentiment only by voice"""
    sentiments = ['negative', 'neutral', 'positive']
    audio_loader = AudioLoader(audio_path)
    preds = predict_voice(audio_loader.features)
    return list(zip(map(lambda x: sentiments[x], preds), audio_loader.durations))
