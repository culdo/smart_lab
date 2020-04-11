import time

import pychromecast
from pychromecast import APP_MEDIA_RECEIVER


class LabCast:

    def __init__(self, cast_name="Den TV", default_volume=1):
        casts = pychromecast.get_chromecasts()
        if len(casts) == 0:
            print("No Devices Found")
            exit()
        self.cast = next(cc for cc in casts if cc.device.friendly_name == cast_name)
        self.cast.start()
        self.mc = self.cast.media_controller
        self.play_media = self.mc.play_media

        print(self.mc.status)
        time.sleep(1)
        self.cast.set_volume(default_volume)

        print(self.cast.app_display_name)
        self._check_app()

    def _check_app(self):
        if self.cast.app_display_name != "Default Media Receiver":
            print("Killing current running app")
            self.cast.quit_app()
            self._wait_app("Backdrop")
            self.cast.start_app(APP_MEDIA_RECEIVER)
            self._wait_app("Default Media Receiver")

    def _wait_app(self, app_name):
        while self.cast.app_display_name != app_name:
            time.sleep(0.001)

    def say_tts(self, text, lang="zh"):
        tts_api = "https://translate.google.com/translate_tts?ie=UTF-8&q=%s&tl=%s&client=tw-ob"
        self.play_media(tts_api % (text, lang), content_type="audio/mp3")
        time.sleep(1)


if __name__ == '__main__':
    cast = LabCast()
    cast.say_tts("測試測試哦")
