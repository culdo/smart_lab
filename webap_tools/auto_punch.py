import calendar
import threading

import keras

from ailab.webap_tools.webap_login import WebAp
from time import ctime, sleep

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import schedule
from random import randint
from datetime import datetime, timedelta, time
import sys


class AutoPunching(WebAp):

    def nav_to_checkform(self):
        user_menu = self.login(*self.account)
        self.browser.switch_to_default_content()
        self.browser.switch_to_frame(user_menu)
        labor_section = self.wait.until(
            EC.presence_of_element_located((By.ID, "spnode_[B40]_兼任助理差勤作業")))
        labor_section.click()
        self.browser.switch_to_default_content()
        self.browser.switch_to_frame(self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "frame[name='MAIN']"))))
        labor_section = self.wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "#SubMenu_dgData > tbody > tr.TRAlternatingItemStyle > td:nth-child(1) > a")))
        labor_section.click()

    def check_in(self):
        check_in_bt = self.wait.until(
            EC.presence_of_element_located((By.ID, "B4001A_btnIN")))
        check_in_bt.click()
        self.wait.until(EC.alert_is_present())
        alert = self.browser.switch_to.alert
        if alert.text == "打上班卡完成":
            print("上班打卡成功")
        elif alert.text == "不允許重複打卡!!!":
            print("失敗，重複打卡")
        print("Checking in done at %s", ctime())
        alert.accept()
        self.logout()

    def check_out(self, work_content="寫程式"):
        work_content_area = self.wait.until(
            EC.presence_of_element_located((By.ID, "B4001A_txtJOB_NOTES")))
        work_content_area.send_keys(work_content)
        check_out_bt = self.wait.until(
            EC.presence_of_element_located((By.ID, "B4001A_btnOFF")))
        check_out_bt.click()
        self.wait.until(EC.alert_is_present())
        alert = self.browser.switch_to.alert
        if alert.text == "打下班卡完成":
            print("下班打卡成功")
        elif alert.text == "不允許重複打卡!!!":
            print("失敗，重複打卡")
        print("Checking out done at %s" % ctime())
        alert.accept()
        self.logout()

    def plan_job(self, **kwarg):
        login_delta = timedelta(minutes=5)
        for weekday, (check_in_time, check_out_time) in kwarg.items():
            # Login to webap system and navigate to checking page
            check_in_time = datetime.strptime(check_in_time, "%H:%M")
            login_time = (check_in_time - login_delta).strftime("%H:%M")
            job = schedule.every().weeks
            job.start_day = weekday
            job.at(login_time).do(self.nav_to_checkform, kwarg["id"], kwarg["password"])

            # Check-in
            minute_delta = timedelta(minutes=randint(0, 5))
            check_in_time = (check_in_time - minute_delta).strftime("%H:%M")
            job = schedule.every().weeks
            job.start_day = weekday
            job.at(check_in_time).do(self.check_in)

            # Check-out
            minute_delta = timedelta(minutes=randint(0, 5))
            check_out_time = (check_out_time + minute_delta).strftime("%H:%M")
            job = schedule.every().weeks
            job.start_day = weekday
            job.at(check_out_time).do(self.check_out)
        print("已排程事項：")
        for job in schedule.jobs:
            print(job)

    def fill_break_time(self, start_time="12:15", end_time="12:45"):
        break_time_start = self.wait.until(
            EC.presence_of_element_located((By.ID, "B4001A_txtBREAK_STM")))
        break_time_start.send_keys(start_time)
        break_time_end = self.wait.until(
            EC.presence_of_element_located((By.ID, "B4001A_txtBREAK_ETM")))
        break_time_end.send_keys(end_time)

    def calendar_plan_month_job(self, year, month, start_day, end_day, duty_datetime, holiday_list=(),
                                login_delay=2):
        c = calendar.Calendar(firstweekday=6)
        login_delta = timedelta(minutes=login_delay)
        today = datetime.today().day
        if today > start_day:
            start_day = today
        print("排程開始日為%s月%s號" % (month, start_day))
        print("國定假日為%s" % holiday_list)
        for date in c.itermonthdates(year, month):
            weekday = date.strftime("%A").lower()
            if date.day == 21:
                print(weekday)
            if date.month == month and date.day not in holiday_list \
                    and date.day in range(start_day, end_day + 1) \
                    and weekday in duty_datetime.keys():

                # Calculate check-in time.
                check_in_time = duty_datetime[weekday][0]
                check_in_time = datetime.strptime(check_in_time, "%H:%M").time()
                check_in_time = datetime.combine(date, check_in_time)
                check_in_time = check_in_time - timedelta(minutes=randint(0, 5))

                print(date.ctime(), date.weekday())

                # Login to webap system and navigate to checking page
                login_time = check_in_time - login_delta
                if (login_time - datetime.now()).days >= 0:
                    print("login_time=%s " % login_time.ctime())
                    print("check_in_time=%s " % check_in_time.ctime())
                    print("second to wait: %s" % (
                            login_time - datetime.now()).total_seconds())
                    threading.Timer((login_time - datetime.now()).total_seconds(), self.nav_to_checkform).start()

                    # Check in
                    threading.Timer((check_in_time - datetime.now()).total_seconds(), self.check_in).start()
                    # threading.Timer((check_in_time - datetime.now()).total_seconds(), self.logout).start()

                    print()
                else:
                    print("今天上班卡時間已過，繼續排程下班卡")

                # Check out
                check_out_time = duty_datetime[weekday][1]
                check_out_time = datetime.strptime(check_out_time, "%H:%M").time()
                check_out_time = datetime.combine(date, check_out_time)
                check_out_time = check_out_time + timedelta(minutes=randint(0, 5))

                login_time = check_out_time - login_delta
                if (login_time - datetime.now()).days >= 0:
                    threading.Timer((login_time - datetime.now()).total_seconds(), self.nav_to_checkform).start()
                    print("login_time=%s " % login_time.ctime())

                    if check_out_time - check_in_time > timedelta(hours=4.5):
                        print("break_time= 12:15 ~ 12:45")
                        threading.Timer((check_out_time - datetime.now()).total_seconds(), self.fill_break_time).start()
                    threading.Timer((check_out_time - datetime.now()).total_seconds(), self.check_out).start()

                    # threading.Timer((check_out_time - datetime.now()).total_seconds(), self.logout).start()

                    print("check_out_time=%s " % check_out_time.ctime())
                    print()
                else:
                    print("今天下班卡時間已過，繼續排程下一天")

    def test_job(self, arg="default"):
        print("I'm working. arg=" + arg)
        print(datetime.now())


if __name__ == '__main__':
    test_ap = AutoPunching("cbc106008", "2848444B")
    int_args = list(map(int, sys.argv[1:]))
    test_ap.calendar_plan_month_job(int_args[0], int_args[1], int_args[2], int_args[3],
                                    {"monday": ["13:00", "17:00"],
                                     "wednesday": ["13:00", "17:00"],
                                     "friday": ["13:00", "17:00"]}, int_args[4:])
