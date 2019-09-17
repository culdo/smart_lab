import calendar
import threading

from ailab.webap_tools.webap_login import login, logout, wait, browser
from time import asctime, sleep

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import schedule
from random import randint
from datetime import datetime, timedelta, time


def nav_to_checkform(*args):
    login(*args)
    labor_section = wait.until(
        EC.presence_of_element_located((By.ID, "spnode_[B40]_兼任助理差勤作業")))
    labor_section.click()


def check_in():
    check_in_bt = wait.until(
        EC.presence_of_element_located((By.ID, "B4001A_btnIN")))
    check_in_bt.click()
    try:
        wait.until(
            EC.text_to_be_present_in_element((By.ID, "B4001A_lblIN")))
        print("打卡成功")
    except:
        alert = browser.switch_to.alert
        alert.accept()
        print("失敗，重複打卡")
    sleep(3)
    logout()


def check_out(work_content="寫程式"):
    work_content_area = wait.until(
        EC.presence_of_element_located((By.ID, "B4001A_txtJOB_NOTES")))
    work_content_area.send_keys(work_content)
    check_out_bt = wait.until(
        EC.presence_of_element_located((By.ID, "B4001A_btnOFF")))
    check_out_bt.click()
    sleep(3)
    logout()


def plan_job(**kwarg):
    login_delta = timedelta(minutes=5)
    for weekday, (check_in_time, check_out_time) in kwarg.items():
        # Login to webap system and navigate to checking page
        check_in_time = datetime.strptime(check_in_time, "%H:%M")
        login_time = (check_in_time - login_delta).strftime("%H:%M")
        job = schedule.every().weeks
        job.start_day = weekday
        job.at(login_time).do(nav_to_checkform, kwarg["id"], kwarg["password"])

        # Check-in
        minute_delta = timedelta(minutes=randint(0, 5))
        check_in_time = (check_in_time - minute_delta).strftime("%H:%M")
        job = schedule.every().weeks
        job.start_day = weekday
        job.at(check_in_time).do(check_in)

        # Check-out
        minute_delta = timedelta(minutes=randint(0, 5))
        check_out_time = (check_out_time + minute_delta).strftime("%H:%M")
        job = schedule.every().weeks
        job.start_day = weekday
        job.at(check_out_time).do(check_out)
    print("已排程事項：")
    for job in schedule.jobs:
        print(job)


def calendar_plan_job(year, month, start_day, end_day, holiday, duty_datetime):
    c = calendar.Calendar(firstweekday=6)
    login_delta = timedelta(minutes=5)
    for date in c.itermonthdates(year, month):
        if date.month == month and date.day not in holiday \
                and date in range(start_day, end_day + 1):
            weekday = date.strftime("%A").lower()
            if weekday in duty_datetime.keys():
                # Calculate check-in time.
                check_in_time = duty_datetime[weekday][0]
                check_in_time = datetime.strptime(check_in_time, "%H:%M").time()
                check_in_time = datetime.combine(date, check_in_time)

                # Login to webap system and navigate to checking page
                login_time = check_in_time - login_delta
                threading.Timer((datetime.now() - login_time).seconds, nav_to_checkform).start()

                # Check in
                check_in_time = check_in_time - timedelta(minutes=randint(0, 5))
                threading.Timer((datetime.now() - check_in_time).seconds, check_in).start()

                # Check out
                check_out_time = duty_datetime[weekday][1]
                check_out_time = datetime.strptime(check_out_time, "%H:%M").time()
                check_out_time = datetime.combine(date, check_out_time)
                check_out_time = check_out_time + timedelta(minutes=randint(0, 5))
                threading.Timer((datetime.now() - check_out_time).seconds, check_out).start()

                print(date, date.weekday)


def test_job(arg="default"):
    print("I'm working. arg=" + arg)
    print(datetime.now())


if __name__ == '__main__':
    pass
    # browser = login("cbc106008", "2848444B")
    # nav_to_punchform()
    # check_in()

