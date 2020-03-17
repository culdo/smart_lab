#!/usr/bin/env python
# -*- coding: utf-8 -*-
import face_recognition
import cv2
import urllib
import numpy as np
# import requests
from subprocess import call
from threading import Thread
from PIL import Image, ImageDraw, ImageFont
from sys import stdout

cam_ip = "192.168.0.52"
open_cmd = ("ssh pi@%s" % cam_ip).split()
open_cmd.append('python ~/lab/open_door/open.py')
ready_open = True


def open_door():
    global ready_open
    call(open_cmd)
    ready_open = True


def face_recognize(tolerance=0.45, size_threshold=40000):
    global ready_open

    known_face_names = ["胡鈞", "莊凱鈞"]
    test_face_encodings = []
    # Load a sample picture and learn how to recognize it.
    for name in known_face_names:
        test_image = face_recognition.load_image_file("face_ID/" + name + ".jpg")
        test_locations = face_recognition.face_locations(test_image, model='cnn')
        test_face_encodings.append(face_recognition.face_encodings(test_image, test_locations, 1000)[0])

    # Create arrays of known face encodings and their names
    known_face_encodings = test_face_encodings

    stream = urllib.urlopen('http://%s:8081/' % cam_ip)
    bytes = ''
    while True:
        bytes += stream.read(1024)
        a = bytes.find('\xff\xd8')
        b = bytes.find('\xff\xd9')
        if a != -1 and b != -1:
            jpg = bytes[a:b + 2]
            bytes = bytes[b + 2:]
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

                name = "路人甲？"

                face_size = (bottom-top) * (right - left)

                # Find most similar people, different with below method.
                if similarities.min() <= tolerance and face_size > size_threshold:
                    name = known_face_names[similarities.argmin()]

                    # If a match was found in known_face_encodings, just use the first one.
                    # if True in matches:
                    #     first_match_index = matches.index(True)
                    #     name = known_face_names[first_match_index]

                    if ready_open:
                        ready_open = False
                        proc = Thread(target=open_door)
                        proc.start()
                # print name
                stdout.write('\r')
                stdout.write(name + str(face_size))

                # Draw a box around the face
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

                # Draw a label with a name below the face
                # cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                # font = cv2.FONT_HERSHEY_DUPLEX
                # cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

                img_PIL = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                font = ImageFont.truetype('NotoSansCJK-Black.ttc', 20)
                name = name.decode('utf8')
                draw = ImageDraw.Draw(img_PIL)
                draw.text((left + 6, bottom - 6), name + str(face_size), font=font, fill=(255, 255, 255))
                frame = cv2.cvtColor(np.asarray(img_PIL), cv2.COLOR_RGB2BGR)
            # Display the resulting image
            frame = cv2.resize(frame, None, fx=2.0, fy=2.0)
            cv2.imshow('Video', frame)

            stdout.flush()

            # Hit 'q' on the keyboard to quit!
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    face_recognize()
