from io import BytesIO

import cv2
import numpy as np

import matplotlib.pyplot as plt
from PIL import Image
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from ailab.webap_tools.captcha_prediction import get_ans

webap_url = "https://webap.nptu.edu.tw/web/Secure/default.aspx"
browser = Chrome()
browser.get(webap_url)
wait = WebDriverWait(browser, 3)
menu = wait.until(
        EC.presence_of_element_located((By.ID, "LoginDefault_ibtLoginStd")))
menu.click()


def get_captcha():
    # now that we have the preliminary stuff out of the way time to get that image :D
    captcha_element = wait.until(
        EC.presence_of_element_located((By.ID, "imgCaptcha")))
    captcha_element.click()
    captcha_element = wait.until(
        EC.presence_of_element_located((By.ID, "imgCaptcha")))
    img = cv2.imdecode(np.fromstring(captcha_element.screenshot_as_png, np.uint8), 1)
    # plt.figure("captcha")
    # plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), "gray")
    return img


def login(student_id, passward):
    captcha_ans = get_ans(get_captcha())
    element = wait.until(
        EC.presence_of_element_located((By.ID, "LoginStd_txtCheckCode")))
    element.send_keys(captcha_ans)
    element = wait.until(
        EC.presence_of_element_located((By.ID, "LoginStd_txtAccount")))
    element.send_keys(student_id)
    element = wait.until(
        EC.presence_of_element_located((By.ID, "LoginStd_txtPassWord")))
    element.send_keys(passward)
    element = wait.until(
        EC.presence_of_element_located((By.ID, "LoginStd_ibtLogin")))
    element.click()
    return browser


def logout():
    element = wait.until(
        EC.presence_of_element_located((By.ID, "CommonHeader_ibtLogOut")))
    element.click()
    wait.until(
        EC.presence_of_element_located((By.ID, "LoginDefault_ibtLoginStd")))
    print("Logout")


if __name__ == '__main__':
    # get_captcha()
    # plt.show()
    login("cbc106008", "2848444B")
