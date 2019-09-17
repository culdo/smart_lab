import time, threading

WAIT_SECONDS = 5


def foo():
    print("I'm working!!! %s " % time.ctime())


job1 = threading.Timer(WAIT_SECONDS, foo).start()
time.sleep(1)
job2 = threading.Timer(WAIT_SECONDS, foo).start()

while True:
    print(time.ctime())
    time.sleep(1)
