import os
import cv2

samples_path = "data"


def get_sample_paths(path=None):
    if path is None:
        path = samples_path
    samples = os.listdir(path)
    samples = [os.path.join(path, sample) for sample in samples if "sample" in sample]
    return samples


def get_frames(sample):
    world_index = 0
    cap = cv2.VideoCapture(sample)
    total_frame = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    while cap.isOpened():
        ret, frame = cap.read()
        if ret is False:
            break
        yield frame
        print((world_index / total_frame) * 100)
        world_index += 1
    cap.release()
