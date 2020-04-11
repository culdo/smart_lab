import cv2


def capture_stream(url=None, save_video=False, video_size=(1920, 1080)):
    if url is None:
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, video_size[0])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, video_size[1])
    else:
        cap = cv2.VideoCapture(url)

    if save_video:
        out = cv2.VideoWriter(
            "output.avi", cv2.VideoWriter_fourcc(*"MJPG"), 10.0, video_size)
    print("Starting the YOLO loop...")

    while cap.isOpened():
        ret, raw = cap.read()
        cv2.imshow("raw", raw)
        cv2.waitKey(1)

    cap.release()
    if save_video:
        out.release()


if __name__ == '__main__':
    capture_stream("rtsp://192.168.0.60:554/user=admin&password=&channel=1&stream=0.sdp?real_stream--rtp-caching=1",
                   save_video=True)
