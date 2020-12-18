from scipy import spatial
import os
from helper import (
    get_sample_paths,
    get_frames,
    get_calibration_markers_list,
    get_relevant_markers,
)
import cv2
import csv
import numpy as np
from collections import namedtuple
import math

sample_paths = get_sample_paths()
save_path = "results/accuracy.csv"

def get_accuracies(sample):
    gaze_marker_sample_path = os.path.join(sample, "gaze_markers.csv")
    gaze_marker_sample = get_calibration_markers_list(gaze_marker_sample_path)

    gazes = []
    markers = []
    for gaze_marker in gaze_marker_sample:
        gaze_center = (
            float(gaze_marker["gaze"].strip("()").split(", ")[0]),
            float(gaze_marker["gaze"].strip("()").split(", ")[1]),
        )
        gaze_center = np.uint16(np.around(gaze_center))
        gazes.append(gaze_center)
        marker_center = (
            float(gaze_marker["marker"].strip("()").split(", ")[0]),
            float(gaze_marker["marker"].strip("()").split(", ")[1]),
        )
        marker_center = np.uint16(np.around(marker_center))
        markers.append(marker_center)


    def unit_vector(vector):
        """ Returns the unit vector of the vector.  """
        return vector / np.linalg.norm(vector)


    def angle_between(v1, v2):
        """ Returns the angle in radians between vectors 'v1' and 'v2'. """
        v1_u = unit_vector(v1)
        v2_u = unit_vector(v2)
        return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))


    radians = []
    radians_higher_tolerance_ignored = []
    for i, j in zip(gazes, markers):
        a = angle_between(i, j)
        if a < 0.09:    # ignore error higher than 0.09 radian ~ 5 degrees
            radians_higher_tolerance_ignored.append(a)
        radians.append(a)

    return radians, radians_higher_tolerance_ignored

def save_results(results):
    with open(save_path, "a", newline="") as csvfile:
        fieldnames = ["sample", "accuracy", "accuracy_higher_tolerance_ignored", "precision", "precision_higher_tolerance_ignored"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow(result)


for sample in sample_paths:
    results = []
    accuracy = get_accuracies(sample)
    result_dict = {}
    result_dict['sample'] = sample
    avg_rad = sum(accuracy[0]) / len(accuracy[0])
    avg_deg = np.rad2deg(avg_rad)
    avg_rad_higher_tolerance_ignored = sum(accuracy[1]) / len(accuracy[1])
    avg_deg_higher_tolerance_ignored = np.rad2deg(avg_rad_higher_tolerance_ignored)
    result_dict['accuracy'] = avg_deg
    result_dict['accuracy_higher_tolerance_ignored'] = avg_deg_higher_tolerance_ignored
    result_dict['precision'] = avg_deg
    result_dict['precision_higher_tolerance_ignored'] = avg_deg
    results.append(result_dict)
    save_results(results)