#!/usr/bin/env python3
import serial
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn


ser = serial.Serial('/dev/ttyUSB0', baudrate=115200)
print(ser.name)         # check which port was really used


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/open_door":
            self.send_response(200)
            self.end_headers()
            ser.write(b'o')

            self.wfile.write(b'Hello, world!')


class DoorServer(ThreadingMixIn, HTTPServer):
    pass


if __name__ == "__main__":
    httpd = DoorServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)
    httpd.serve_forever()
