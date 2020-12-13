import os
import numpy as np
import cv2
from external.circle_detector import find_pupil_circle_marker
import csv


def get_samples(path):
    samples = os.listdir(path)
    samples = [os.path.join(path, sample) for sample in samples if "sample" in sample]
    return samples


def get_raw_data(sample):
    world_index = 0
    cap = cv2.VideoCapture(sample)
    total_frame = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    while cap.isOpened():
        ret, frame = cap.read()
        if ret is False:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        ellipses_list = find_pupil_circle_marker(gray, scale=1)
        world_index += 1
        print((world_index / total_frame) * 100)
        marker_list = []
        del frame, gray
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
        # cv2.imshow('frame',gray)
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #    break
    cap.release()


def export_csv(sample):
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
    samples_path = "data"
    samples = get_samples(samples_path)
    export_csv(samples[-1])
