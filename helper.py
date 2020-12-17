import os
import cv2
import csv
import numpy as np

samples_path = "data"
gaze = "gaze_positions.csv"
marker_filename = "calibration_markers.csv"


def get_sample_paths(path=None):
    if path is None:
        path = samples_path
    samples = os.listdir(path)
    samples = [os.path.join(path, sample) for sample in samples]
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
        print(world_index if total_frame == -1 else (world_index / total_frame) * 100)
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


def find_circle_marker(img):
    img = cv2.medianBlur(img, 5)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    circles = cv2.HoughCircles(
        gray,
        cv2.HOUGH_GRADIENT,
        1,
        700,
        param1=300,
        param2=30,
        minRadius=15,
        maxRadius=100,
    )

    marker_list = []
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            marker_dict = {}
            midpoint = img[i[1]][i[0]]
            bgr_sum = sum(midpoint)
            if bgr_sum > 400:
                marker_dict["marker_type"] = "Stop"
            else:
                marker_dict["marker_type"] = "Ref"
            marker_dict["ellipses"] = [((i[0], i[1]),)]
            marker_list.append(marker_dict)
            print(marker_dict["marker_type"])
    return marker_list


def get_relevant_markers(markers, world_index):
    return [x for x in markers if int(x["world_index"]) == world_index]


def get_gaze_data(path=None):
    if path is None:
        path = samples_path


def get_relevant_samples_path(filename, overwrite=False):
    all_samples = get_sample_paths()
    if overwrite:
        return all_samples
    samples_to_detect_markers = []
    for sample in all_samples:
        filenames = os.listdir(sample)
        if not marker_filename in filenames:
            samples_to_detect_markers.append(sample)
    return samples_to_detect_markers
