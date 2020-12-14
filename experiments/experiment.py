import cv2
import numpy as np
import random
from copy import deepcopy

fps = 30
pause_between_experiments = 3  # secs
background = (255, 255, 255)  # white
calibration_marker_color = (0, 0, 0)  # black
outer_circle_radius = 20
outer_circle_thickness = 7
speeds = [7, 13]
calibration_markers_scale = 2
frame_size = (1280, 720)  # width, height
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

px = frame_size[0] // 2
py = frame_size[1] // 2

out = cv2.VideoWriter(
    "calibration_markers.avi", cv2.VideoWriter_fourcc(*"DIVX"), fps, frame_size
)


def get_initial_image():
    a = np.ones((frame_size[1], frame_size[0])) * background[0]
    b = np.ones((frame_size[1], frame_size[0])) * background[1]
    c = np.ones((frame_size[1], frame_size[0])) * background[2]
    background_color = np.dstack((a, b, c)).astype(np.uint8)
    foo = np.ones((frame_size[1], frame_size[0], 3), dtype=np.uint8)
    foo = foo * background_color
    return foo


def get_image_with_markers(img, center):
    img = cv2.circle(
        img, center, 10 * calibration_markers_scale, calibration_marker_color, -1
    )
    img = cv2.drawMarker(
        img, center, (0, 0, 255), cv2.MARKER_CROSS, 2 * calibration_markers_scale, 2, 1
    )
    img = cv2.circle(
        img,
        center,
        outer_circle_radius * calibration_markers_scale,
        calibration_marker_color,
        outer_circle_thickness * calibration_markers_scale,
    )
    return img


def get_image_with_stop_markers(img, center, calibration_markers_scale):
    img = cv2.drawMarker(
        img, center, (0, 0, 255), cv2.MARKER_CROSS, 2 * calibration_markers_scale, 2, 1
    )
    img = cv2.circle(
        img,
        center,
        8 * calibration_markers_scale,
        calibration_marker_color,
        5 * calibration_markers_scale,
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
    center_markers = getEquidistantPoints(start, end, min(frame_size))
    for center_marker in center_markers[::speed]:
        img = deepcopy(image)
        img = get_image_with_markers(
            img, (int(center_marker[0]), int(center_marker[1]))
        )
        out.write(img)


def draw_switch(frame_size, start, end, speed):
    draw(
        frame_size, start, start, speed
    )  # moves from center to center, basically not moving at all
    draw(
        frame_size, end, end, speed
    )  # moves from center to center, basically not moving at all


def pursuit():
    # Pursuit (Slow movements)
    print("Pursuit...")
    for i in speeds:
        draw(
            frame_size, (frame_size[0] // 2, 0), (frame_size[0] // 2, frame_size[1]), i
        )  # From up to down

    # for i in speeds:
    #     draw(
    #         frame_size, (frame_size[0] // 2, frame_size[1]), (frame_size[0] // 2, 0), i
    #     )  # From down to up

    for i in speeds:
        draw(
            frame_size, (0, frame_size[1] // 2), (frame_size[0], frame_size[1] // 2), i
        )  # From left to right

    # for i in speeds:
    #     draw(
    #         frame_size, (frame_size[0], frame_size[1] // 2), (0, frame_size[1] // 2), i
    #     )  # From right to left

    for i in speeds:
        draw(
            frame_size, (0, 0), (frame_size[0], frame_size[1]), i
        )  # From left top to right down

    # for i in speeds:
    #     draw(
    #         frame_size, (frame_size[0], frame_size[1]), (0, 0), i
    #     )  # From right down to left top

    for i in speeds:
        draw(
            frame_size, (frame_size[0], 0), (0, frame_size[1]), i
        )  # From right top to left down

    # for i in speeds:
    #    draw(
    #        frame_size, (0, frame_size[1]), (frame_size[0], 0), i
    #    )  # From left down to right top
    draw_stop_markers(pause_between_experiments)


def fixation():
    print("Fixation...")
    # Fixation
    for i in range(10):
        random.seed(i)
        center = (random.randint(0, frame_size[0]), random.randint(0, frame_size[1]))
        draw(
            frame_size, center, center, speeds[-1]
        )  # moves from center to center, basically not moving at all
    draw_stop_markers(pause_between_experiments)


def saccade():
    print("Saccade...")
    # Saccade
    repeat = 1
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
        draw_switch(
            frame_size, (px0, py0), (px3, py3), speeds[-1]
        )  # top left to down left

    for i in range(repeat):
        draw_switch(
            frame_size, (px1, py1), (px2, py2), speeds[-1]
        )  # top right to down right

    for i in range(repeat):
        draw_switch(
            frame_size, (px0, py0), (px1, py1), speeds[-1]
        )  # top left to top right

    for i in range(repeat):
        draw_switch(
            frame_size, (px3, py3), (px2, py2), speeds[-1]
        )  # down left to down right
    draw_stop_markers(pause_between_experiments)


def jump():
    print("Sudden Jump...")
    # From bottom to middle
    for i in speeds:
        i = i * 2
        draw(
            frame_size, (px3, py3), (px2 // 2, py2), i
        )  # From left down to center of image
        draw(
            frame_size, (px, py), (px2, frame_size[1] // 2), i
        )  # From left down to center of image

    # From middle to top
    for i in speeds:
        draw(
            frame_size, (px2, py2 // 2), (px, py), i
        )  # From middle left to center of image
        draw(
            frame_size, (px1 // 2, 0 + offset), (px0, py0), i
        )  # From top middle to top left
    draw_stop_markers(pause_between_experiments)


def sin_wave():
    print("Sin Wave...")
    number_of_wave = 2
    max_amplitude = frame_size[1] // 3
    x = np.linspace(0, number_of_wave * np.pi, num=frame_size[0])  # start,stop,step
    amplitude = np.sin(x)
    amplitude = amplitude * max_amplitude
    amplitude = amplitude + frame_size[1] // 2
    for i in range(0, len(amplitude), 8):
        amp = int(amplitude[i])
        if i < offset:
            continue
        if i > frame_size[0] - offset:
            break
        center = (i, amp)
        draw(frame_size, center, center, min(frame_size))
    draw_stop_markers(pause_between_experiments)


def triangle_wave():
    print("Triangle Wave...")
    number_of_wave = 4
    max_amplitude = frame_size[1] // 3
    x = np.linspace(0, number_of_wave * np.pi, num=frame_size[0])  # start,stop,step
    amplitude = np.sin(x)
    amplitude = amplitude * max_amplitude
    amplitude = amplitude + frame_size[1] // 2
    draw_now = False
    for i in range(0, len(amplitude), 50):
        amp = int(amplitude[i])
        if i < offset:
            continue
        if i > frame_size[0] - offset:
            break
        if draw_now == False:
            start = (i, amp)
            draw_now = True
            continue
        stop = (i, amp)
        draw(frame_size, start, stop, 100)
        start = stop
    draw_stop_markers(pause_between_experiments)


def draw_stop_markers(sec):
    image = get_initial_image()
    for _ in range(sec * fps):
        img = deepcopy(image)
        img = get_image_with_stop_markers(img, (px, py), 5)
        out.write(img)


pursuit()
fixation()
saccade()
jump()
sin_wave()
triangle_wave()

out.release()
