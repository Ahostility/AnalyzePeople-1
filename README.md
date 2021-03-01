## Install
Для запуска проекта необходимо поставить следующие зависимости:
* Установить [CUDA Toolkit](https://developer.nvidia.com/cuda-downloads) 
* Собрать [kaldi](https://github.com/kaldi-asr/kaldi) 
* Собрать [vosk-api](https://github.com/alphacep/vosk-api), если планируется работа на gpu то необходимо собирать одноименную ветку
* Установить библеотеку для работы с 7z
```bash
sudo apt install p7zip-full p7zip-rar
```
* Установить все зависимости через [pip](https://pip.pypa.io/en/stable/)
```bash
python3.8 -m pip intall -r requirements.txt
```
* Скачать модель
```bash
python3.8 -m dostoevsky download fasttext-social-network-model
```


## USING
### Запуск
Запуск для cpu
```bash
./pipeline.sh PATH
```
Запуск для gpu
```bash
./pipeline_gpu.sh PATH
```
Для анализа текстового  файла на этапы требуется запустить команду, указав путь до файла. По выполнению в тойже папке будет создан файл с раширением json, также вывод будет продублирован в консоли
```bash
python3.8 -m src.StageDetection.detect_stages PATH
```
Для анализа текстового  файла на этапы требуется запустить команду, указав путь до файла. По выполнению в тойже папке будет создан файл с раширением json, также вывод будет продублирован в консоли
```bash
python3.8 -m src.StageDetection.detect_stages PATH
```  
Для аудио и текстовых данных на эмоции выполнить следующие, предварительно поместив данные в data/output/people/, передать просто имя папки лежащей там
```bash
python3.8 -m src.EmotionsRecognizer.predict_mixed test
```  
Результаты храниться в дериктории data/output/people/, они разбиты по клиентам
* result - текстовые файлы с эмоциональным окрасом
* wav - аудио фрагменты
* txt - текстовые файлы с диалогом оператор клиент

###### Для отладки 
```bash
python3.8 -m src.audio.preprocessing ./path/test/
python3.8 -m src.SpeechToText.creat_text data/output/full_wav/test.wav
python3.8 -m src.SpeechToText.grouping_dialogue test
python3.8 -m src.diarization.diarization test
python3.8 -m src.EmotionsRecognizer.predict_mixed test
```