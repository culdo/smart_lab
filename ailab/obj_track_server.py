#!/usr/bin/env python3
# -*-coding utf-8-*-

"""MJPEG Server for the webcam"""

from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
import time
from multiprocessing import Process, Manager, Queue
from ailab.yolo_tracking.obj_track import handle_yolo_result
from ailab.yolo_tracking import draw_box
from ailab.lab_cast import cast_audio


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):

        # Get the min intra frame delay
        if self.server.maxfps == 0:
            minDelay = 0
        else:
            minDelay = 1.0 / self.server.maxfps

        # Send headers
        self.send_response(200)
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Pragma", "no-cache")
        self.send_header("Connection", "close")
        self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=--myboundary")
        self.end_headers()

        o = self.wfile

        # Send image files in a loop
        lastFrameTime = 0
        while True:

            contents = self.server.ns.img

            # Wait if required so we stay under the max FPS
            if lastFrameTime != 0:
                now = time.time()
                delay = now - lastFrameTime
                if delay < minDelay:
                    time.sleep(minDelay - delay)

            buff = "Content-Length: %s \r\n" % str(len(contents))
            # logging.debug( "Serving frame %s", imageFile )
            o.write(b"--myboundary\r\n")
            o.write(b"Content-Type: image/jpeg\r\n")
            o.write(buff.encode("utf8"))
            o.write(b"\r\n")
            o.write(contents)
            o.write(b"\r\n")

            lastFrameTime = time.time()


class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    pass


def start_track_server():
    port = 8091
    indoor_url = 'http://203.64.134.236:8070'

    server = ThreadingHTTPServer(("0.0.0.0", port), RequestHandler)
    server.maxfps = 0
    print("Listening on Port " + str(port) + "...")

    manager = Manager()
    server.img_ns = manager.Namespace()
    server.img_ns.img = None

    info_ns = manager.Namespace()
    info_ns.curr_frame = None
    state_q = Queue()
    obj_track = Process(target=handle_yolo_result, args=(indoor_url, info_ns, state_q))
    obj_track.start()

    while info_ns.curr_frame is None:
        time.sleep(0.0001)

    track_draw = Process(target=draw_box, args=(server.img_ns, info_ns))
    track_draw.start()

    lab_cast = Process(target=cast_audio, args=(state_q,))
    lab_cast.start()

def start_lab_facility

if __name__ == "__main__":
    start_track_server()
