import os
import cv2
import numpy as np
from helper import get_sample_paths, get_frames, get_calibration_markers_list

sample_paths = get_sample_paths()
video_sample = os.path.join(sample_paths[-1], "world.mp4")
marker_sample = os.path.join(sample_paths[-1], "calibration_markers.csv")

markers_pos = get_calibration_markers_list(marker_sample)
frames = get_frames(video_sample)


def get_markers(world_index):
    markers = []
    first_added = False
    for index, marker in enumerate(markers_pos):
        marker_world_index = int(marker["world_index"])
        if first_added == False and world_index < marker_world_index:
            break
        elif world_index == marker_world_index:
            markers.append(marker)
            markers_pos.pop(index)
            first_added = True
        elif world_index > marker_world_index:
            markers_pos.pop(index)
            break
        else:
            break
    return markers


def draw(img):
    cv2.imshow("frame", img)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        return


for world_index, frame in enumerate(frames):
    # marker_index = int(markers_pos[world_index]['world_index'])
    markers = get_markers(world_index)
    no_draw = False
    for marker in markers:
        center = marker["ellipses_center"].strip("()").split(", ")
        center = (round(int(float(center[0]))), round(int(float(center[1]))))
        frame = cv2.circle(frame, center, 10, (0, 0, 255), 2)
        draw(frame)
        no_draw = True
    if no_draw == False:
        draw(frame)
    pass
