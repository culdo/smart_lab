from keras.models import load_model
from keras import backend
import numpy as np
from time import sleep
import cv2
import matplotlib.pyplot as plt
import tensorflow as tf

letters = "0123456789"

model = load_model('nptu_captch.h5')

graph = tf.get_default_graph()


def rgb2gray(rgb):
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
    return gray


def get_ans(captcha_img):

    global graph

    prediction_data = np.stack(np.array(captcha_img) / 255.0)  # predict img local
    prediction_data = rgb2gray(prediction_data)  # 灰階
    prediction_data = prediction_data.reshape(-1, 35, 95, 1)
    with graph.as_default():
        try:
            prediction = model.predict(prediction_data)
        except:
            backend.clear_session()
    # prediction = model.predict(prediction_data)
    # print(captcha_ans)

    captcha_ans = ""

    for digit_onehot in prediction:
        # print(digit_onehot)
        digit_ans = digit_onehot.argmax()
        captcha_ans += str(digit_ans)

    return captcha_ans


def captcha_test():
    from ailab.webap_tools.webap_login import get_captcha
    for i in range(10):  # predict 份數
        img = get_captcha()
        captcha_ans = get_ans(img)
        plt.figure(captcha_ans)
        plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), "gray")
        sleep(3)
    plt.show()


if __name__ == '__main__':
    captcha_test()
