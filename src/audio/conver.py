import os

for name in os.listdir('../../data/output/full_wav'):
    os.system(f'ffmpeg -i full_wav/{name} -acodec pcm_s16le -ar 16000 -ac 1 wav/{name.replace("mp3", "wav")}')