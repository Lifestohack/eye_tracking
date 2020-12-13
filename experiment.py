import cv2
import numpy as np
import random
from copy import deepcopy

background = (255, 255, 255)  # white
calibration_marker_color = (0, 0, 0)  # black
outer_circle_radius = 20
outer_circle_thickness = 7
speeds = [1, 3, 5, 7, 11]
calibration_markers_scale = 2
frame_size = (500, 500)
offset = (outer_circle_radius * calibration_markers_scale) + (
    outer_circle_thickness * calibration_markers_scale
)

px0 = 0 + offset
py0 = 0 + offset

px1 = frame_size[0] - offset
py1 = 0 + offset

px2 = frame_size[0] - offset
py2 = frame_size[1] - offset

px3 = 0 + offset
py3 = frame_size[1] - offset


out = cv2.VideoWriter(
    "calibration_markers.avi", cv2.VideoWriter_fourcc(*"DIVX"), 30, frame_size
)


def get_initial_image():
    a = np.ones((frame_size[0], frame_size[1])) * background[0]
    b = np.ones((frame_size[0], frame_size[1])) * background[1]
    c = np.ones((frame_size[0], frame_size[1])) * background[2]
    background_color = np.dstack((a, b, c)).astype(np.uint8)
    foo = np.ones((frame_size[0], frame_size[1], 3), dtype=np.uint8)
    foo = foo * background_color
    return foo


def get_image_with_markers(img, center):
    img = cv2.circle(
        img, center, 10 * calibration_markers_scale, calibration_marker_color, -1
    )
    img = cv2.circle(
        img,
        center,
        outer_circle_radius * calibration_markers_scale,
        calibration_marker_color,
        outer_circle_thickness * calibration_markers_scale,
    )
    return img


def getEquidistantPoints(p1, p2, n):
    def lerp(v0, v1, i):
        return v0 + i * (v1 - v0)

    return [
        (lerp(p1[0], p2[0], 1.0 / n * i), lerp(p1[1], p2[1], 1.0 / n * i))
        for i in range(n + 1)
    ]


def draw(frame_size, start, end, speed):
    image = get_initial_image()
    center_markers = getEquidistantPoints(start, end, max(frame_size))
    for center_marker in center_markers[::speed]:
        img = deepcopy(image)
        img = get_image_with_markers(
            img, (int(center_marker[0]), int(center_marker[1]))
        )
        out.write(img)


def draw_switch(frame_size, start, end, speed):
    draw(
        frame_size, start, start, speeds[-1]
    )  # moves from center to center, basically not moving at all
    draw(
        frame_size, end, end, speeds[-1]
    )  # moves from center to center, basically not moving at all


# Pursuit (Slow movements)
for i in speeds:
    draw(
        frame_size, (frame_size[0] // 2, 0), (frame_size[0] // 2, frame_size[1]), i
    )  # From up to down

for i in speeds:
    draw(
        frame_size, (frame_size[0] // 2, frame_size[1]), (frame_size[0] // 2, 0), i
    )  # From down to up

for i in speeds:
    draw(
        frame_size, (0, frame_size[1] // 2), (frame_size[0], frame_size[1] // 2), i
    )  # From left to right

for i in speeds:
    draw(
        frame_size, (frame_size[0], frame_size[1] // 2), (0, frame_size[1] // 2), i
    )  # From right to left

for i in speeds:
    draw(
        frame_size, (0, 0), (frame_size[0], frame_size[1]), i
    )  # From left top to right down

for i in speeds:
    draw(
        frame_size, (frame_size[0], frame_size[1]), (0, 0), i
    )  # From right down to left top

for i in speeds:
    draw(
        frame_size, (frame_size[0], 0), (0, frame_size[1]), i
    )  # From right top to left down

for i in speeds:
    draw(
        frame_size, (0, frame_size[1]), (frame_size[0], 0), i
    )  # From left down to right top

# Fixation
for i in range(10):
    random.seed(i)
    center = (random.randint(0, frame_size[0]), random.randint(0, frame_size[1]))
    draw(
        frame_size, center, center, speeds[-3]
    )  # moves from center to center, basically not moving at all

# Saccade
repeat = 2
for i in range(repeat):
    start = (0 + offset, frame_size[1] // 2)  # left middle
    end = (frame_size[0] - offset, frame_size[1] // 2)  # right middle
    draw_switch(frame_size, start, end, speeds[-1])

for i in range(repeat):
    start = (frame_size[0] // 2, 0 + offset)  # top middle
    end = (frame_size[0] // 2, frame_size[1] - offset)  # down middle
    draw_switch(frame_size, start, end, speeds[-1])

for i in range(repeat):
    start = (0 + offset, 0 + offset)  # top left
    end = (frame_size[0] - offset, frame_size[1] - offset)  # down right
    draw_switch(frame_size, start, end, speeds[-1])

for i in range(repeat):
    start = (frame_size[0] - offset, 0 + offset)  # top right
    end = (0 + offset, frame_size[1] - offset)  # down left
    draw_switch(frame_size, start, end, speeds[-1])

for i in range(repeat):
    draw_switch(frame_size, (px0, py0), (px3, py3), speeds[-1])  # top left to down left
for i in range(repeat):
    draw_switch(
        frame_size, (px1, py1), (px2, py2), speeds[-1]
    )  # top right to down right
for i in range(repeat):
    draw_switch(frame_size, (px0, py0), (px1, py1), speeds[-1])  # top left to top right
for i in range(repeat):
    draw_switch(
        frame_size, (px3, py3), (px2, py2), speeds[-1]
    )  # down left to down right

out.release()
