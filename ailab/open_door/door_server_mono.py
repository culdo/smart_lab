#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
from lab_door import open_door


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/open_door":
            self.send_response(200)
            self.end_headers()

            open_door()

            self.wfile.write(b'Hello, world!')


if __name__ == "__main__":
    httpd = HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)
    httpd.serve_forever()
