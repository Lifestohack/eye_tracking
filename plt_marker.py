import os
import cv2
import numpy as np
from external.circle_detector import find_pupil_circle_marker
from external.circle_detector1 import (
    find_pupil_circle_marker as find_pupil_circle_marker1,
)
from helper import (
    get_frames,
    get_calibration_markers_list,
    find_circle_marker,
    get_relevant_markers,
)

sample_path = "data/sample1"
video_sample = os.path.join(sample_path, "world.mp4")
marker_sample = os.path.join(sample_path, "calibration_markers.csv")

markers = get_calibration_markers_list(marker_sample)
cap = cv2.VideoCapture(video_sample)
length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))


def draw(img):
    cv2.imshow("frame", img)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        return


def draw_position_circle(img, frame_index):
    find_markers = None
    # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # find_markers = find_pupil_circle_marker(gray, scale=1)
    # find_markers = find_pupil_circle_marker1(img)
    # find_markers = find_circle_marker(img)
    if find_markers is None:
        find_markers = get_relevant_markers(markers, frame_index)
    no_draw = False
    for ellipses_ in find_markers:
        ellipses = ellipses_["ellipse"]
        if ellipses_["marker_type"] == "Stop":
            circle_color = (0, 0, 255)
        else:
            circle_color = (0, 255, 0)
        center = []
        if isinstance(ellipses, str):
            center = ellipses.strip("()").split(", ")
            center = ((float(center[0])), float(center[1]))
        else:
            center = ellipses[0][0]
        center = np.uint16(np.around(center))
        img = cv2.circle(img, tuple(center), 10, circle_color, 2)
        draw(img)
        no_draw = True
    if no_draw == False:
        draw(img)


while cap.isOpened():
    err, frame = cap.read()
    if not err:
        break
    frame_number = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
    draw_position_circle(frame, frame_number - 1)
