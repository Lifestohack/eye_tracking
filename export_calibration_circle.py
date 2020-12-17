import os
import numpy as np
import cv2
from external.circle_detector import find_pupil_circle_marker
import csv
from helper import get_sample_paths, get_frames, find_circle_marker
from external.circle_detector1 import (
    find_pupil_circle_marker as find_pupil_circle_marker1,
)


def get_raw_data(sample):
    for world_index, frame in enumerate(get_frames(sample)):
        # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # ellipses_list = find_pupil_circle_marker(gray, scale=1)
        # ellipses_list = find_circle_marker(frame)
        ellipses_list = find_pupil_circle_marker1(frame)
        marker_list = []
        for ellipses_ in ellipses_list:
            ellipses = ellipses_["ellipse"]
            img_pos = ellipses[0][0]
            marker_list.append(
                {
                    "world_index": world_index,
                    "ellipse": img_pos,
                    "marker_type": ellipses_["marker_type"],
                }
            )
            yield marker_list


def export_raw_data_to_csv(sample, save_file_name):
    video_sample = os.path.join(sample, "world.mp4")
    save_path = os.path.join(sample, save_file_name)
    markers_list = []
    for _, markers in enumerate(get_raw_data(video_sample)):
        for marker in markers:
            markers_list.append(marker)

    with open(save_path, "w", newline="") as csvfile:
        fieldnames = [
            "world_index",
            "ellipse",
            "marker_type",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for marker in markers_list:
            writer.writerow(marker)


def get_samples(marker_filename, overwrite=False):
    all_samples = get_sample_paths()
    if overwrite:
        return all_samples
    samples_to_detect_markers = []
    for sample in all_samples:
        filenames = os.listdir(sample)
        if not marker_filename in filenames:
            samples_to_detect_markers.append(sample)
    return samples_to_detect_markers


if __name__ == "__main__":
    marker_filename = "calibration_markers.csv"
    sampels = get_samples(marker_filename, False)
    for sample in sampels:
        export_raw_data_to_csv(sample, marker_filename)
