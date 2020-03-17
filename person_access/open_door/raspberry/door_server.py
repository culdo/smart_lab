#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from time import sleep
from multiprocessing import Process, Value


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/open_door":
            self.send_response(200)
            self.end_headers()

            self.server.is_open.value = 1
            while self.server.is_open.value != 0:
                sleep(0.001)

            self.wfile.write(b'Hello, world!')


class DoorServer(ThreadingMixIn, HTTPServer):
    pass


def switch_door(is_open):
    from lab_door import open_door
    while True:
        if is_open.value == 1:
            open_door()
            is_open.value = 0
        else:
            sleep(0.001)


if __name__ == "__main__":
    httpd = DoorServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)
    httpd.is_open = Value('i', 0)
    p1 = Process(target=switch_door, args=(httpd.is_open,))
    p1.start()
    httpd.serve_forever()
