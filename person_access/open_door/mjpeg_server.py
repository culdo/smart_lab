#!/usr/bin/env python3
#-*-coding utf-8-*-

"""MJPEG Server for the webcam"""

import urllib.request
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont, ImageColor
from sys import stdout

from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
import time
import os
from multiprocessing import Process, Queue, Manager


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):

        # Get the min intra frame delay
        maxFPS = maxfps
        if maxFPS == 0:
            minDelay = 0
        else:
            minDelay = 1.0 / maxFPS

        # Send headers
        self.send_response( 200 )
        self.send_header( "Cache-Control", "no-cache" )
        self.send_header( "Pragma", "no-cache" )
        self.send_header( "Connection", "close" )
        self.send_header( "Content-Type", "multipart/x-mixed-replace; boundary=--myboundary" )
        self.end_headers()

        o = self.wfile

        # Send image files in a loop
        lastFrameTime = 0
        while True:

            contents = self.server.ns.img
            # print(img1)
            # img1 = self.server.img_q.get()

            # contents = cv2mat1[1].tostring()

                # Wait if required so we stay under the max FPS
            if lastFrameTime != 0:
                now = time.time()
                delay = now - lastFrameTime
                if delay < minDelay:
                    time.sleep( minDelay - delay )

            buff = "Content-Length: %s \r\n" % str(len(contents))
            # logging.debug( "Serving frame %s", imageFile )
            o.write(b"--myboundary\r\n" )
            o.write(b"Content-Type: image/jpeg\r\n" )
            o.write(buff.encode("utf8"))
            o.write(b"\r\n" )
            o.write( contents )
            o.write(b"\r\n" )

            lastFrameTime = time.time()


class ThreadingHTTPServer( ThreadingMixIn, HTTPServer ):
    pass


def facerec(ns, tolerance=0.45, size_threshold=40000):
    os.environ["CUDA_VISIBLE_DEVICES"] = "0"
    import face_recognition

    known_face_names = ["胡鈞", "莊凱鈞"]
    test_face_encodings = []
    # Load a sample picture and learn how to recognize it.
    for name in known_face_names:
        test_image = face_recognition.load_image_file("face_ID/" + name + ".jpg")
        test_locations = face_recognition.face_locations(test_image, model='cnn')
        test_face_encodings.append(face_recognition.face_encodings(test_image, test_locations, 1000)[0])

    # Create arrays of known face encodings and their names
    known_face_encodings = test_face_encodings

    stream = urllib.request.urlopen(img_url)
    mybytes = bytes()

    while True:
        mybytes += stream.read(1024)
        a = mybytes.find(b'\xff\xd8')
        b = mybytes.find(b'\xff\xd9')
        if a != -1 and b != -1:
            jpg = mybytes[a:b + 2]
            mybytes = mybytes[b + 2:]
            frame = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)

            # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
            rgb_frame = frame[:, :, ::-1]

            # Find all the faces and face encodings in the frame of video
            face_locations = face_recognition.face_locations(rgb_frame, model='cnn')
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations, num_jitters=10)

            # Loop through each face in this frame of video

            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                # See if the face is a match for the known face(s)
                # matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=tolerance)
                similarities = face_recognition.face_distance(known_face_encodings, face_encoding)

                name = "誰喇？"

                face_size = (bottom-top) * (right - left)

                # Find most similar people, different with below method.
                if similarities.min() <= tolerance and face_size > size_threshold:
                    name = known_face_names[similarities.argmin()]

                    # If a match was found in known_face_encodings, just use the first one.
                    # if True in matches:
                    #     first_match_index = matches.index(True)
                    #     name = known_face_names[first_match_index]


                # print name
                stdout.write('\r')
                stdout.write(name + str(face_size))

                # Draw a box around the face
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

                # Draw a label with a name below the face
                cv2.rectangle(frame, (left, bottom), (right, bottom+25), (0, 0, 255), cv2.FILLED)
                # font = cv2.FONT_HERSHEY_DUPLEX
                # cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

                img_PIL = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                font = ImageFont.truetype('NotoSansCJK-Black.ttc', 20)
                # name = name.decode('utf8')
                draw = ImageDraw.Draw(img_PIL)
                draw.text((left, bottom - 6), name + str(face_size), font=font, fill=(255, 255, 255))
                frame = cv2.cvtColor(np.asarray(img_PIL), cv2.COLOR_RGB2BGR)
            # Display the resulting image
            frame = cv2.imencode(".jpeg", frame, (cv2.IMWRITE_JPEG_QUALITY, cameraQuality))[1]
            ns.img = frame
            # print(ns.img)
            # img_q.put(frame)


if __name__ == "__main__":
    cameraQuality = 90
    maxfps = 0
    port = 8091
    img_url = "http://203.64.134.168:9091/"

    server = ThreadingHTTPServer( ("0.0.0.0",port), RequestHandler )
    manager = Manager()
    server.ns = manager.Namespace()
    server.ns.img = np.zeros(1)

    face_rec = Process(target=facerec, args=(server.ns,))
    face_rec.start()

    print("Listening on Port "+str(port)+"...")
    server.serve_forever()
