import pychromecast
import time


def cast_audio(state_q):

    ttsapi = "https://translate.google.com/translate_tts?ie=UTF-8&q=%s&tl=zh&client=tw-ob"
    count_speech = "實驗室目前有%d人"
    stay_time_speech = "ID%d 以呆一分鐘"
    hello_speech = "實驗室cast系統"

    # Change to the name of your Chromecast
    CAST_NAME = "Den TV"

    casts = pychromecast.get_chromecasts()
    if len(casts) == 0:
        print("No Devices Found")
        exit()
    cast = next(cc for cc in casts if cc.device.friendly_name == CAST_NAME)
    cast.start()

    print(cast.media_controller.status)
    time.sleep(1)
    cast.set_volume(0.5)

    if not cast.is_idle:
        print("Killing current running app")
        cast.quit_app()
        time.sleep(3)

    cast.play_media(ttsapi % hello_speech, "audio/mp3")

    while True:
        if not cast.media_controller.status.player_is_playing:
            state = state_q.get()
            print(state.notify_time)
            cast.play_media(
                ttsapi % (stay_time_speech % state.uid), "audio/mp3")
            time.sleep(0.8)
        else:
            time.sleep(0.01)


if __name__ == "__main__":
    debug = False
    # q = Queue(1)
    # p2 = Process(target=cast_audio, args=(q,))
    # p1 = Process(target=handle_yolo_result, args=(q,))
    # p1.start()
    # p2.start()
    # p1.join()
    # p2.join()
    cast_audio(None)
