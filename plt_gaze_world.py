import os
import cv2
from helper import get_sample_paths, get_frames

sample_paths = get_sample_paths()
video_sample = os.path.join(sample_paths[-1], "world.mp4")

for world_index, frame in enumerate(get_frames(video_sample)):
    cv2.imshow("frame", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
