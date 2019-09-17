import requests
from ailab.ft2 import put_chinese_text
import cv2
import numpy as np
import time
from PIL import ImageColor


def draw_box(ns, info_q):
    # "BLACK"
    box_colormap = ["NAVY", "BLUE", "AQUA", "TEAL", "OLIVE", "GREEN", "LIME", "ORANGE", "RED", "MAROON",
                    "FUCHSIA", "PURPLE", "GRAY", "SILVER"]
    color_len = len(box_colormap)
    cameraQuality = 90
    image_width = 1280
    image_height = 720
    ft = put_chinese_text('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')

    r = requests.get('http://192.168.0.131:8080/video', stream=True)
    if r.status_code == 200:
        mybytes = bytes()
        for chunk in r.iter_content(chunk_size=1024):
            mybytes += chunk
            a = mybytes.find(b'\xff\xd8')
            b = mybytes.find(b'\xff\xd9')

            if a != -1 and b != -1:
                if not a < (b + 2):
                    # flush to head flag to find correct range
                    mybytes = mybytes[a:]
                else:
                    jpg = mybytes[a:b + 2]
                    # mybytes = mybytes[b + 2:]
                    # mybytes = bytes()

                    frame = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)

                    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
                    # try:
                    #     obj_info_frame = info_q.get_nowait()
                    # except:
                    #     print("info_q is empty, continued...")
                    #     time.sleep(0.01)
                    #     continue
                    obj_info_frame = info_q.curr_frame

                    for obj in obj_info_frame.objects:
                        left = round(
                            (obj.relative_coordinates.center_x - (obj.relative_coordinates.width / 2.0)) * image_width)
                        top = round((obj.relative_coordinates.center_y - (
                                obj.relative_coordinates.height / 2.0)) * image_height)
                        right = round(
                            (obj.relative_coordinates.center_x + (obj.relative_coordinates.width / 2.0)) * image_width)
                        bottom = round((obj.relative_coordinates.center_y + (
                                obj.relative_coordinates.height / 2.0)) * image_height)

                        color = ImageColor.getrgb(box_colormap[obj.state.uid % color_len])
                        color = [v for v in reversed(color)]
                        # print(box_colormap[obj.uid % color_len])
                        # Draw a box around the face
                        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)

                        # Draw a label with a name below the face
                        cv2.rectangle(frame, (left, top - 20), (right, top), color, cv2.FILLED)
                        # cv2.putText(frame, "%s uid=%d" % ("我", obj.uid), (left + 6, top - 6), font, 1.0, (255, 255, 255), 1)
                        stay_time = time.gmtime(obj.state.stay_time)
                        if stay_time[3] > 0:
                            formatted_time = "%dh%dm" % (stay_time[3], stay_time[4])
                        else:
                            formatted_time = "%dm%ds" % (stay_time[4], stay_time[5])
                        frame = ft.draw_text(frame, (left + 6, top - 25), "實驗室帥哥<%d>  %s" % (obj.state.uid, formatted_time),
                                             20,
                                             (255, 255, 255))

                    # Display the resulting image

                    # cv2.imshow("frame", frame)
                    # if cv2.waitKey(1) == 27:
                    #     exit(0)
                    frame = cv2.imencode(".jpeg", frame, (cv2.IMWRITE_JPEG_QUALITY, cameraQuality))[1]
                    ns.img = frame

                    # Clear mybytes buffer to prevent internal bound shift
                    mybytes = bytes()
