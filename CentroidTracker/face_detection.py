import face_recognition
import cv2
import numpy as np
from pyimagesearch.centroidtrack import CentroidTrack
from pyimagesearch.centroidtracker import CentroidTracker


face_cascade = cv2.CascadeClassifier('xml/haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier('xml/haarcascade_eye.xml')


ip_camera = 'rtsp://admin:Vietnam@3i@117.6.131.222:6969'
video = 'video/walking.mp4'

# Get a reference to webcam #0 (the default one)
video_capture = cv2.VideoCapture(0)

ct = CentroidTrack(10)

while True:
    # Grab a single frame of video
    ret, frame = video_capture.read()

    frame = cv2.resize(frame, (0, 0), fx=1, fy=1)

    H = len(frame)
    W = len(frame[0])
    half_W = W

    detect_frame = np.array(frame[:, :half_W, :])

    gray = cv2.cvtColor(detect_frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(detect_frame, 1.3, 5)

    rects = []

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        rects.append([x, y, x+w, y+h])

    objects = ct.update(rects)

    for (objectID, centroid) in objects.items():
        # draw both the ID of the object and the centroid of the
        # object on the output frame
        text = "ID {}".format(objectID)
        cv2.putText(frame, text, (centroid[0] - 10, centroid[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.circle(frame, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)
        # print(centroid)

    # Display the resulting image
    cv2.imshow('Video', frame)

    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()

cv2.destroyAllWindows()