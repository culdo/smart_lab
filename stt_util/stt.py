from http.client import BadStatusLine

import speech_recognition as sr
from gtts import gTTS

from chromecast.cast import LabCast


class STT:
    def __init__(self):
        self.r = sr.Recognizer()

    def run(self, lang="zh-TW"):
        is_first = True
        while True:
            with sr.Microphone() as source:
                if is_first:
                    print("Say something")
                self.r.adjust_for_ambient_noise(source)
                audio = self.r.listen(source)
            try:
                speech_text = self.r.recognize_google(audio, language=lang)
                print('text: %s' % speech_text)
            except (sr.UnknownValueError, sr.RequestError, BadStatusLine) as e:
                is_first = False
                print(type(e).__name__)
                if "Too Many Requests" in str(e):
                    raise ConnectionRefusedError("Too Many Requests")
                continue
            return speech_text


if __name__ == '__main__':
    stt = STT()
    lc = LabCast()
    while True:
        speech_text = stt.run()
        lc.say_tts(speech_text)
