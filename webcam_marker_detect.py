import cv2
from helper import (
    get_sample_paths,
    get_frames,
    get_calibration_markers_list,
    find_circle_marker,
)
from external.circle_detector import find_pupil_circle_marker


def get_raw_data(sample):
    for world_index, frame in enumerate(get_frames(sample)):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # ellipses_list = find_circle_marker(gray)
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

        yield marker_list, frame


def draw(img):
    cv2.imshow("frame", img)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        return


if __name__ == "__main__":
    # Point the camera to that marker to see if it detects the marker
    for marker_list, frame in get_raw_data(0):
        no_draw = False
        for marker in marker_list:
            center = (
                round(int(float(marker["ellipses_center"][0]))),
                round(int(float(marker["ellipses_center"][1]))),
            )
            frame = cv2.circle(frame, center, 10, (0, 0, 255), 2)
            draw(frame)
            no_draw = True
        if no_draw == False:
            draw(frame)
