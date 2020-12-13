import os
import cv2
import csv

samples_path = "data"
gaze = "gaze_positions.csv"
marker_filename = "calibration_markers.csv"


def get_sample_paths(path=None):
    if path is None:
        path = samples_path
    samples = os.listdir(path)
    samples = [os.path.join(path, sample) for sample in samples if "sample" in sample]
    return samples


def get_frames(path):
    world_index = 0
    cap = cv2.VideoCapture(path)
    total_frame = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    while cap.isOpened():
        ret, frame = cap.read()
        if ret is False:
            break
        yield frame
        print((world_index / total_frame) * 100)
        world_index += 1
    cap.release()


def get_calibration_markers(path=None):
    if path is None:
        path = marker_filename
    with open(path, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            yield row


def get_calibration_markers_list(path=None):
    if path is None:
        path = marker_filename
    markers = []
    with open(path, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            markers.append(row)
    return markers
