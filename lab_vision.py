import requests
import pychromecast
from multiprocessing import Process, Queue
from object_rec import object_recognize
import time


def cast_audio(q):
    CAST_NAME = "Den TV"
    casts = pychromecast.get_chromecasts()
    if len(casts) == 0:
        print("No Devices Found")
        exit()
    cast = next(cc for cc in casts if cc.device.friendly_name == CAST_NAME)
    cast.start()

    if not cast.is_idle:
        print("Killing current running app")
        cast.quit_app()
        time.sleep(3)

    ttsapi = "https://translate.google.com/translate_tts?ie=UTF-8&q=%s&tl=zh&client=tw-ob"
    query = "實驗室目前有%d人"
    while True:
        person_num = q.get()
        if not cast.media_controller.status.player_is_playing:
            cast.play_media(
                (ttsapi % (query % person_num)), "audio/mp3")
            time.sleep(0.8)


def lab_notify(q):
    r = requests.get('http://203.64.134.236:8070', stream=True)
    predict_json = ""
    is_append = False

    for c_bin in r.iter_lines(chunk_size=512):
        if c_bin:
            c = c_bin.decode("ascii")
            if c == "{":
                is_append = True
                predict_json = ""
            if c == "}, ":
                predict_json += "}"
                if debug:
                    print(predict_json)
                else:
                    object_recognize(predict_json, q)
                is_append = False
            if is_append:
                predict_json += c


if __name__ == "__main__":
    debug = False
    q = Queue(1)
    # p2 = Process(target=cast_audio, args=(q,))
    p1 = Process(target=lab_notify, args=(q,))
    p1.start()
    # p2.start()
    p1.join()
    # p2.join()
