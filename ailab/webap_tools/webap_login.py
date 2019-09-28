from io import BytesIO

import cv2
import numpy as np

import matplotlib.pyplot as plt
from PIL import Image
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import UnexpectedAlertPresentException

from ailab.webap_tools.captcha_prediction import get_ans
import time


class WebAp:
    def __init__(self, *args):
        self.account = args
        webap_url = "https://webap.nptu.edu.tw/web/Secure/default.aspx"
        self.browser = Chrome()
        self.browser.get(webap_url)
        self.wait = WebDriverWait(self.browser, 3)

    def get_captcha(self):
        # now that we have the preliminary stuff out of the way time to get that image :D
        captcha_element = self.wait.until(
            EC.presence_of_element_located((By.ID, "imgCaptcha")))
        captcha_element.click()
        captcha_element = self.wait.until(
            EC.presence_of_element_located((By.ID, "imgCaptcha")))
        img = cv2.imdecode(np.fromstring(captcha_element.screenshot_as_png, np.uint8), 1)
        # plt.figure("captcha")
        # plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), "gray")
        return img

    def login(self, student_id, passward):
        self.enter_login_page()
        while True:
            try:
                captcha_ans = get_ans(self.get_captcha())
                element = self.wait.until(
                    EC.presence_of_element_located((By.ID, "LoginStd_txtCheckCode")))
                element.send_keys(captcha_ans)
                element = self.wait.until(
                    EC.presence_of_element_located((By.ID, "LoginStd_txtAccount")))
                element.send_keys(student_id)
                element = self.wait.until(
                    EC.presence_of_element_located((By.ID, "LoginStd_txtPassWord")))
                element.send_keys(passward)
                element = self.wait.until(
                    EC.presence_of_element_located((By.ID, "LoginStd_ibtLogin")))
                element.click()

            except UnexpectedAlertPresentException:
                print(UnexpectedAlertPresentException)
                self.browser.refresh()
                time.sleep(5)
                continue
            break

    def logout(self):
        self.browser.switch_to_default_content()
        self.browser.switch_to.frame(self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "frame[name='MAIN']"))))
        element = self.wait.until(
            EC.presence_of_element_located((By.ID, "CommonHeader_ibtLogOut")))
        element.click()
        self.wait.until(EC.alert_is_present())
        alert = self.browser.switch_to.alert
        alert.accept()
        print("Logout at %s" % time.ctime())

    def enter_login_page(self):
        menu = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[id*='ibtLoginStd']")))
        menu.click()

    def test(self):
        while True:
            self.enter_login_page()
            captcha_ans = get_ans(self.get_captcha())
            element = self.wait.until(
                EC.presence_of_element_located((By.ID, "LoginStd_txtCheckCode")))
            element.clear()
            element.send_keys(captcha_ans)
            time.sleep(1)


if __name__ == '__main__':
    test_ap = WebAp()
    test_ap.test()
    # get_captcha()
    # plt.show()
    # menu_frame, main_frame = login("cbc106008", "2848444B")

