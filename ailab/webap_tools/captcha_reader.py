import cv2
import matplotlib.pyplot as plt
from ailab.webap_tools.webap_login import get_captcha


def preprocessor(bgr_img):
    first_thresh_val = 180
    gray_inv = 255-cv2.cvtColor(bgr_img, cv2.COLOR_BGR2GRAY)
    ret, thresholded = cv2.threshold(gray_inv, first_thresh_val, 255, cv2.THRESH_BINARY)
    plt.figure()
    plt.imshow(thresholded, "gray")


def solve_captcha(bin_img):
    digit_w = 28
    digit_h = 18
    digit_xy = [[8, 5], [9, 26], [9, 47], [9, 68]]
    digit_img = []
    for i, (x, y) in enumerate(digit_xy):
        digit = bin_img[y:y + digit_h, x:x + digit_w]
        digit_img.append(digit)
        plt.figure("digit_%s" % i)
        plt.imshow(digit)


if __name__ == '__main__':
    captcha_img = get_captcha()
    preprocessor(captcha_img)
    plt.show()
