import os
import numpy as np
import cv2
from external.circle_detector import find_pupil_circle_marker
import csv
from helper import get_sample_paths, get_frames


def get_raw_data(sample):
    for world_index, frame in enumerate(get_frames(sample)):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        ellipses_list = find_pupil_circle_marker(gray, scale=1)
        marker_list = []
        for ellipses_ in ellipses_list:
            ellipses = ellipses_["ellipses"]
            img_pos = ellipses[0][0]
            marker_list.append(
                {
                    "world_index": world_index,
                    "ellipses_center": img_pos,
                    "marker_type": ellipses_["marker_type"],
                }
            )
            yield marker_list


def export_raw_data_to_csv(sample):
    video_sample = os.path.join(sample, "world.mp4")
    save_path = os.path.join(sample, "calibration_markers.csv")
    with open(save_path, "a", newline="") as csvfile:
        fieldnames = [
            "world_index",
            "ellipses_center",
            "marker_type",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for _, markers in enumerate(get_raw_data(video_sample)):
            for marker in markers:
                writer.writerow(marker)


if __name__ == "__main__":
    samples = get_sample_paths()
    export_raw_data_to_csv(samples[-1])
