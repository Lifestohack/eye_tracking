import os
from helper import (
    get_sample_paths,
    get_frames,
    get_calibration_markers_list,
    get_relevant_markers,
)
import cv2
import numpy as np

sample_paths = get_sample_paths()
sample = "data/sample1"
video_sample = os.path.join(sample, "world.mp4")


def draw(img):
    cv2.imshow("frame", img)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        return


cap = cv2.VideoCapture(video_sample)

gaze_marker_sample_path = os.path.join(sample, "gaze_markers.csv")
gaze_marker_sample = get_calibration_markers_list(gaze_marker_sample_path)

world_index = 0
while cap.isOpened():
    print(world_index)
    ret, frame = cap.read()
    if ret is False:
        break
    results = get_relevant_markers(gaze_marker_sample, world_index)
    if len(results) > 0:
        no_draw = False
        for gaze_marker in results:
            gaze_center = (
                float(gaze_marker["gaze"].strip("()").split(", ")[0]),
                float(gaze_marker["gaze"].strip("()").split(", ")[1]),
            )
            gaze_center = np.uint16(np.around(gaze_center))
            marker_center = (
                float(gaze_marker["marker"].strip("()").split(", ")[0]),
                float(gaze_marker["marker"].strip("()").split(", ")[1]),
            )
            marker_center = np.uint16(np.around(marker_center))

            frame = cv2.circle(
                frame, (gaze_center[0], gaze_center[1]), 10, (0, 0, 255), 2
            )
            frame = cv2.circle(
                frame, (marker_center[0], marker_center[1]), 10, (0, 255, 0), 2
            )
            draw(frame)
            no_draw = True
        if no_draw == False:
            draw(frame)
    world_index += 1
