import cv2
import numpy as np
import random

background = (0,0,255)
speeds = [1,3,5,7,11]
calibration_markers_scale = 2
frame_size = (500, 500)

out = cv2.VideoWriter('calibration_markers.avi',cv2.VideoWriter_fourcc(*'DIVX'), 30, frame_size)

def get_image_with_markers(img, center):
    img = cv2.circle(img, center, 10*calibration_markers_scale, (0,0,0), -1)
    img = cv2.circle(img, center, 20 * calibration_markers_scale, (0,0,0), 7 * calibration_markers_scale)
    return img

def getEquidistantPoints(p1, p2, n):
    def lerp(v0, v1, i):
        return v0 + i * (v1 - v0)
    return [(lerp(p1[0],p2[0],1./n*i), lerp(p1[1],p2[1],1./n*i)) for i in range(n+1)]

def draw(frame_size, start, end, speed):
    center_markers = getEquidistantPoints(start, end, max(frame_size))
    for center_marker in center_markers[::speed]:
        img = np.ones((frame_size[0], frame_size[1], 3), dtype=np.uint8) * 255 
        #img = np.multiply(img * background)
        img = get_image_with_markers(img, (int(center_marker[0]), int(center_marker[1])))
        out.write(img)

# Pursuit (Slow movements)
# From up to down
for i in speeds:
    draw(frame_size, (frame_size[0]//2, 0), (frame_size[0]//2, frame_size[1]), i)

# From down to up
for i in speeds:
    draw(frame_size, (frame_size[0]//2, frame_size[1]), (frame_size[0]//2, 0), i)

# From left to right
for i in speeds:
    draw(frame_size, (0, frame_size[1]//2), (frame_size[0], frame_size[1]//2), i)

# From right to left
for i in speeds:
    draw(frame_size, (frame_size[0], frame_size[1]//2), (0, frame_size[1]//2), i)


# From left top to right down
for i in speeds:
    draw(frame_size, (0, 0), (frame_size[0], frame_size[1]), i)

# From right down to left top
for i in speeds:
    draw(frame_size, (frame_size[0], frame_size[1]), (0, 0), i)

# From right top to left down
for i in speeds:
    draw(frame_size, (frame_size[0], 0), (0, frame_size[1]), i)

# From left down to right top
for i in speeds:
    draw(frame_size, (0, frame_size[1]), (frame_size[0], 0), i)

# Fixation
for i in range(10):
    random.seed(i)
    center = (random.randint(0, frame_size[0]), random.randint(0, frame_size[1]))
    draw(frame_size, center, center, speeds[-3])

out.release()