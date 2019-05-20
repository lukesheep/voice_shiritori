# variables and initial setup
import speech_recognition as sr
import sqlite3
import pygame
from tempfile import TemporaryFile
from gtts import gTTS
from pykakasi import kakasi


def speak(c_voice):
    mp3_fp = TemporaryFile()
    tts = gTTS(c_voice, "ja")
    tts.write_to_fp(mp3_fp)
    pygame.mixer.init()
    mp3_fp.seek(0)
    pygame.mixer.music.load(mp3_fp)
    pygame.mixer.music.play()
    print("press enter")
    input()


def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        print("Say something!")
        audio = r.listen(source)
    try:
        print(r.recognize_google(audio, language="ja-JP"))
        user_text = r.recognize_google(audio, language="ja-JP")
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google SR service; {0}".format(e))
    return user_text


# setting up the kakasi lybrary to convert every word to hiragana
kakasi = kakasi()
kakasi.setMode("H", None)
kakasi.setMode("K", "H")
kakasi.setMode("J", "H")
kakasi.setMode("s", False)
kakasi.setMode("C", True)
kakasi.setMode("E", None)
kakasi.setMode("a", None)
converter = kakasi.getConverter()


conn = sqlite3.connect("wnjpn.db")
cursor = conn.cursor()
word = get_audio()
used_word = []
used = True
first = True
letter = "a"
# main game loop
while True:

    # checking if the word is valid
    word = converter.do(word)
    cursor.execute("SELECT * from shiritori_dict where reading=?", [word])
    wordrow = cursor.fetchone()
    if wordrow is None or wordrow[4] == "ん":
        print("word does not exist or finish in ん")
        break
    used_word.append(word)

    if (not first) and (wordrow[3] != letter):
        print("not match the letter")
        break
    first = False
    # computer word selector
    while used is True:
        cursor.execute("SELECT * from shiritori_dict where first=? and last!='ん' ORDER BY RANDOM()", [wordrow[4]])
        wordrow = cursor.fetchone()
        if wordrow is None:
            print("You won")
            break
        if not wordrow[1] in used_word:
            used = False
    print(wordrow[1]+"("+wordrow[2]+")")
    speak(wordrow[1])
    used_word.append(wordrow[1])
    used = True
    word = get_audio()
    letter = wordrow[4]
