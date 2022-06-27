'''
Голосовой ассистент "Крендель".

from YT channel PythonHubStudio

python 3.8 и выше.

Распаковать в проект языковую модель vosk

Требуется:
pip install vosk
pip install sounddevice
pip install scikit-learn
pip install pyttsx3

Не обязательно:
pip install requests

#На Linux-ax, скорее всего нужно еще, если ошибка pyttsx3:
#sudo apt update && sudo apt install espeak ffmpeg libespeak1
#https://github.com/nateshmbhat/pyttsx3

Для получения справки, спроси у него 'Что ты умеешь Крендель?' или 'справка Крендель'

Ссылки на библиотеки и доп материалы:
sounddevice
https://pypi.org/project/sounddevice/
https://python-sounddevice.readthedocs.io/en/0.4.4/
vosk
https://pypi.org/project/vosk/
https://github.com/alphacep/vosk-api
https://alphacephei.com/vosk/
sklearn
https://pypi.org/project/scikit-learn/
https://scikit-learn.org/stable/
pyttsx3
https://pypi.org/project/pyttsx3/
https://pyttsx3.readthedocs.io/en/latest/
requests
https://pypi.org/project/requests/

'''

from sklearn.feature_extraction.text import CountVectorizer     #pip install scikit-learn
from sklearn.linear_model import LogisticRegression
import sounddevice as sd    #pip install sounddevice
import vosk                 #pip install vosk

import json
import queue

import words
from skills import *
import voice


q = queue.Queue()

model = vosk.Model('model_small')       #голосовую модель vosk нужно поместить в папку с файлами проекта
                                        #https://alphacephei.com/vosk/
                                        #https://alphacephei.com/vosk/models

device = sd.default.device     # <--- по умолчанию
                                #или -> sd.default.device = 1, 3, python -m sounddevice просмотр 
samplerate = int(sd.query_devices(device[0], 'input')['default_samplerate'])  #получаем частоту микрофона


def callback(indata, frames, time, status):
    '''
    Добавляет в очередь семплы из потока.
    вызывается каждый раз при наполнении blocksize
    в sd.RawInputStream'''

    q.put(bytes(indata))


def recognize(data, vectorizer, clf):
    '''
    Анализ распознанной речи
    '''

    #проверяем есть ли имя бота в data, если нет, то return
    trg = words.TRIGGERS.intersection(data.split())
    if not trg:
        return

    #удаляем имя бота из текста
    data.replace(list(trg)[0], '')

    #получаем вектор полученного текста
    #сравниваем с вариантами, получая наиболее подходящий ответ
    text_vector = vectorizer.transform([data]).toarray()[0]
    answer = clf.predict([text_vector])[0]

    #получение имени функции из ответа из data_set
    func_name = answer.split()[0]

    #озвучка ответа из модели data_set
    voice.speaker(answer.replace(func_name, ''))

    #запуск функции из skills
    exec(func_name + '()')


def main():
    '''
    Обучаем матрицу ИИ
    и постоянно слушаем микрофон
    '''

    #Обучение матрицы на data_set модели
    vectorizer = CountVectorizer()
    vectors = vectorizer.fit_transform(list(words.data_set.keys()))
    
    clf = LogisticRegression()
    clf.fit(vectors, list(words.data_set.values()))

    del words.data_set

    #постоянная прослушка микрофона
    with sd.RawInputStream(samplerate=samplerate, blocksize = 16000, device=device[0], dtype='int16',
                                channels=1, callback=callback):

        rec = vosk.KaldiRecognizer(model, samplerate)
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                data = json.loads(rec.Result())['text']
                recognize(data, vectorizer, clf)
            # else:
            #     print(rec.PartialResult())


if __name__ == '__main__':
    main()

