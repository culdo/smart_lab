import os
import subprocess
import time
from threading import Thread

import requests
from darknet_video.thread_detector import ThreadingDetector
import notify2
import cv2


class PersonIn:
    def __init__(self, cam_url="http://192.168.0.52:8081/"):
        weights_file = os.environ[
                           "HOME"] + "/nptu/lab/computer_vision/darknets/darknet/bin/csresnext50-panet-spp-original-optimal.weights"
        self.td = ThreadingDetector(cam_url,
                                    weights_path=weights_file,
                                    meta_file="coco_cht.data",
                                    white_list=["人"])
        self.opened_time = 0

    def check_person(self, blocking=True, size_threshold=100000):
        def thread():
            while True:
                is_open = False
                for obj in self.td.stream.detections:
                    coord = obj["relative_coordinates"]
                    if coord["width"] * coord["height"] > size_threshold:
                        print(coord["width"] * coord["height"])
                        # print(self.td.stream.yolo_raw)
                        cv2.imwrite("person_in.jpg", self.td.stream.yolo_raw)
                        is_open = True
                if is_open:
                    self._open_door()
                else:
                    time.sleep(0.001)
        t = Thread(target=thread)
        t.start()
        if blocking:
            t.join()

    def _open_door(self, expired_time=5, door_trigger="http://192.168.0.52:8000/open_door_relay"):
        if time.time() - self.opened_time > expired_time:
            sendmessage("想進實驗室的人", "門已由繼電器開啟", "/home/lab-pc1/nptu/lab/smart_lab/person_access/open_door/person_in.jpg")
            requests.get(door_trigger)
            self.opened_time = time.time()


def sendmessage(title, message, icon, expired_time=3000):
    subprocess.call("notify-send -i %s -t %d %s %s"
                    % (icon, expired_time, title, message), shell=True)


if __name__ == '__main__':
    IP_camera = "rtsp://192.168.0.60:554/user=admin&password=&channel=1&stream=0.sdp?real_stream--rtp-caching=1"
    door_cam = "http://192.168.0.52:8081/"
    person_in = PersonIn(door_cam)
    person_in.check_person()
