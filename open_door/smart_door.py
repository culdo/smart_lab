from urllib.request import urlopen
from time import sleep


def open_door(is_open):
    while True:
        if is_open.value == 1:
            with urlopen('http://192.168.0.117:8000/open_door') as response:
                print(response.read())
            # wait people come in
            sleep(5)
        else:
            sleep(0.001)
