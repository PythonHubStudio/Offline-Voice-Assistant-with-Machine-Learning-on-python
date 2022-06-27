import pyttsx3		#pip install pyttsx3


#Инициализация голосового "движка" при старте программы
#
#Голос берется из системы, первый попавшийся
#
#Доп материал:
#https://pypi.org/project/pyttsx3/
#https://pyttsx3.readthedocs.io/en/latest/
#https://github.com/nateshmbhat/pyttsx3
#На Linux-ax, скорее всего нужно еще:
#sudo apt update && sudo apt install espeak ffmpeg libespeak1

engine = pyttsx3.init()
engine.setProperty('rate', 180)				#скорость речи


def speaker(text):
	'''Озвучка текста'''
	engine.say(text)
	engine.runAndWait()