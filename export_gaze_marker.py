import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
import csv

from external.circle_detector import find_pupil_circle_marker
from external.circle_detector1 import (
    find_pupil_circle_marker as find_pupil_circle_marker1,
)
from helper import (
    get_sample_paths,
    get_frames,
    get_calibration_markers_list,
    find_circle_marker,
    get_relevant_markers,
)


def save_gaze_markers_frame(sample, results):
    save_path = os.path.join(sample, "gaze_markers.csv")
    with open(save_path, "w", newline="") as csvfile:
        fieldnames = ["world_index", "gaze_timestamp", "gaze", "marker", "marker_type"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            gazes = result["gaze"]
            marker = result["marker"]
            for gaze in gazes:
                result_dict = {}
                result_dict["world_index"] = marker[0]["world_index"]
                result_dict["gaze_timestamp"] = gaze["gaze_timestamp"]
                result_dict["gaze"] = (
                    float(gaze["norm_pos_x"]) * width,
                    (1 - float(gaze["norm_pos_y"])) * height,
                )
                result_dict["marker"] = marker[0]["ellipse"]
                result_dict["marker_type"] = marker[0]["marker_type"]
                # result['world_index'] = gaz['gaze_timestamp']
                writer.writerow(result_dict)


def save_plt_availability(sample, num_frames):
    result = []
    # sample = "data/diwas"
    plt_img_save = os.path.join(sample, "plt.png")

    marker_sample = os.path.join(sample, "calibration_markers.csv")
    markers = get_calibration_markers_list(marker_sample)

    gaze_sample_path = os.path.join(sample, "exports/000/gaze_positions.csv")
    gaze_samples = get_calibration_markers_list(gaze_sample_path)

    world_time_path = os.path.join(sample, "world.csv")
    world_time = get_calibration_markers_list(world_time_path)

    starting_gaze_time_monotonic = float(gaze_samples[0]["gaze_timestamp"])
    # end_gaze_time_monotonic = float(gaze_samples[-1]['gaze_timestamp'])
    start_world_monotonic = world_time[0]["start"].split(":")
    end_world_monotonic = world_time[0]["end"].split(":")
    start_world_time = int(start_world_monotonic[1])
    end_world_time = int(end_world_monotonic[1])
    if int(start_world_monotonic[0]) != 0:
        start_world_time = int(start_world_monotonic[0]) * 60 + start_world_time
    if int(end_world_monotonic[0]) != 0:
        end_world_time = int(end_world_monotonic[0]) * 60 + end_world_time

    x = np.linspace(0, num_frames, num_frames, endpoint=False)

    y = []
    for i in x:
        print(sample + " -> " + str((i / num_frames) * 100))
        relevant_gaze = get_relevant_markers(gaze_samples, i)
        relevant_marker = get_relevant_markers(markers, i)
        if len(relevant_gaze) > 0 and len(relevant_marker) > 0:
            if (
                float(relevant_gaze[0]["gaze_timestamp"]) - start_world_time
                > starting_gaze_time_monotonic
            ) and (
                starting_gaze_time_monotonic + end_world_time
                > float(relevant_gaze[-1]["gaze_timestamp"])
            ):
                y.append(1)
                a = {}
                a["gaze"] = relevant_gaze
                a["marker"] = relevant_marker
                result.append(a)
            else:
                y.append(0)
        else:
            y.append(0)
    _, ax = plt.subplots(1, 1, sharex=True)
    ax.plot(x, y)
    ax.fill_between(x, y)
    plt.savefig(plt_img_save)
    save_gaze_markers_frame(sample, result)


sample_paths = get_sample_paths()
# sample = "data/alex"
# video_sample = os.path.join(sample, "world.mp4")
# cap = cv2.VideoCapture(video_sample)
# height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
# width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
# fps = cap.get(cv2.CAP_PROP_FPS)      # OpenCV2 version 2 used "CV_CAP_PROP_FPS"
# num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
# cap.release()
# save_plt_availability(sample, num_frames)
for sample in sample_paths:
    video_sample = os.path.join(sample, "world.mp4")
    cap = cv2.VideoCapture(video_sample)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()
    save_plt_availability(sample, num_frames)
