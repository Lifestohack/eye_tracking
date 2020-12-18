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
import cv2
import numpy as np
import os

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
        video_path = self.g_pool.capture.source_path
        self.export_calibration_markers(
            video_path, intrinsics=self.g_pool.capture.intrinsics
        )

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
        # asdf(events)
        pass

    def asdf(self, events):
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

    def init_ui(self):
        self.add_menu()
        self.menu.label = "Export Markers"
        self.menu.append(
            ui.Info_Text(
                "Calibration marker will be automatically exported "
                "if this plugin is activated. "
            )
        )

    def deinit_ui(self):
        self.remove_menu()

    def write_to_csv(self, save_path, locations):
        save_path = os.path.join(save_path, "markers_norm_3d.csv")
        with open(save_path, "w", newline="") as csvfile:
            fieldnames = ["world_index", "marker", "marker_norm", "marker_type"]
            writer = csv.DictWriter(
                csvfile,
                fieldnames=fieldnames,
                quoting=csv.QUOTE_NONE,
                delimiter=",",
                quotechar="",
            )
            writer.writeheader()
            writer.writerows(locations)

    def export_calibration_markers(self, video_path, intrinsics):
        markers = self.get_location_from_frame(video_path)
        locations = [sample[0]["marker"] for sample in markers]
        undistorted_3d = intrinsics.unprojectPoints(locations, normalize=True)
        calibration_markers = []
        for dis, loc in zip(undistorted_3d, markers):
            temp = {}
            temp["marker_norm"] = dis
            temp["marker"] = loc[0]["marker"]
            temp["world_index"] = loc[0]["world_index"]
            temp["marker_type"] = loc[0]["marker_type"]
            calibration_markers.append(temp)
        save_path = os.path.dirname(video_path)
        self.write_to_csv(save_path, calibration_markers)

    def find_circle_marker(self, img, frame_num):
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
                marker_dict["marker"] = np.array([i[0], i[1]])
                marker_dict["world_index"] = frame_num
                marker_list.append(marker_dict)
        return marker_list

    def get_location_from_frame(self, video_path):
        locations = []
        cap = cv2.VideoCapture(video_path)
        frame_num = 0
        frames_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        while cap.isOpened():
            err, frame = cap.read()
            if not err:
                break
            print((frame_num / frames_count) * 100)
            marker = self.find_circle_marker(frame, frame_num)
            if len(marker) > 0:
                locations.append(marker)
            # if frame_num>10:
            #     break
            frame_num += 1
        cap.release()
        return locations
