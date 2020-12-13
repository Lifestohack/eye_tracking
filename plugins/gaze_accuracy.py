import logging
from plugin import Plugin
from pyglui import ui
from circle_detector import find_pupil_circle_marker
import cv2
import methods
import msgpack
import file_methods as fm
import csv
from video_capture import EndofVideoError

logger = logging.getLogger(__name__)


class Gaze_Accuracy(Plugin):
    """
    This file is supposed to be used with Pupil's lab player software.
    Copy this file to player's plugin folder.
    """

    order = 1
    icon_chr = chr(0xEC11)
    icon_font = "pupil_icons"

    def __init__(self, g_pool):
        super().__init__(g_pool)
        self.frames = {}
        # self.export()

    def export(self):
        gaze_data = self.g_pool.gaze_positions.data
        cap = self.g_pool.capture

        with open("export_gazeframe.csv", "a", newline="") as csvfile:
            fieldnames = ["index", "gaze", "timestamp", "confidence"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for i in range(len(gaze_data)):
                frame = {}
                gaze = msgpack.unpackb(gaze_data[i].serialized, encoding="utf-8")
                norm_pos = gaze["norm_pos"]
                gaze_x = int(norm_pos[0] * cap.frame_size[1])
                gaze_y = int((1 - norm_pos[1]) * cap.frame_size[0])
                frame["index"] = i
                frame["gaze"] = (gaze_x, gaze_y)
                frame["timestamp"] = gaze["timestamp"]
                frame["confidence"] = gaze["confidence"]
                writer.writerow(frame)
        # world_frames = cap.get_frame_count()
        # while True:
        #     try:
        #         input_frame = cap.get_frame()
        #         gray = input_frame.gray
        #         frame_timestamp = input_frame.timestamp
        #         frame_index = input_frame.index
        #     except EndofVideoError:
        #         break
        # pass

    def recent_events(self, events):
        frame_index = events["frame"].index
        img = events["frame"].gray
        if not frame_index in self.frames:
            pos = find_pupil_circle_marker(img, scale=1)

            def get_gazes():
                for gaze_data in events["gaze"]:
                    gaze = msgpack.unpackb(gaze_data.serialized, encoding="utf-8")
                    norm_pos = gaze["norm_pos"]
                    gaze_x = int(norm_pos[0] * img.shape[1])
                    gaze_y = int((1 - norm_pos[1]) * img.shape[0])
                    yield [gaze_x, gaze_y, gaze["timestamp"], gaze["confidence"]]

            def get_circle():
                circles = pos[-1]["ellipses"] if len(pos) > 0 else None
                if circles is None:
                    return None
                circle_center = circles[0][0]
                y = int(circle_center[1])
                x = int(circle_center[0])
                radius = circles[-1][1][-1]
                marker_type = pos[-1]["marker_type"]
                return [x, y, radius, marker_type]

            circle = get_circle()
            # marker_type = None
            # if circle is not None:
            #     marker_type = circle[-1]
            #     circle.remove(marker_type)

            with open("export_dataframe.csv", "a", newline="") as csvfile:
                fieldnames = [
                    "index",
                    "gaze",
                    "circle",
                    "timestamp",
                    "confidence",
                    "marker_type",
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                # writer.writeheader()
                i = 0
                for gaze in get_gazes():
                    frame = {}
                    frame["index"] = frame_index + i
                    frame["gaze"] = (gaze[0], gaze[1])
                    frame["circle"] = circle
                    frame["timestamp"] = gaze[2]
                    frame["confidence"] = gaze[3]
                    writer.writerow(frame)
                    self.frames[frame_index] = frame
                    # i += 1

            # img = cv2.circle(img, gaze, int(10), (0, 0, 255), 2)
            # img = cv2.circle(img, circle[0], int(20), (0, 0, 255), 2)
            # cv2.imshow("img", img)
            # cv2.waitKey(1)

    pass

    def init_ui(self):
        self.add_menu()
        self.menu.label = "Gaze Accuracy"
