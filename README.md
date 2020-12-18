# Eye Tracker Experiments

Create experiments for finding pursuit, fixation and saccade. Analyse the data between the estimated gaze and acutal fixation.

Export the calibration markers position and compare it to the estimated gaze positions. Stop markers are shown in between the experiments so it is easy to assign the experiment type.

Pupil's lab Capture software is used to record the data.
export_gaze_markers.py only works with their format. Please customize the code if you use some other software to record your data.

1. Use experiments/experiments.py to create a video to perform the gaze estimation experiments
2. After you have the experiment recorded use export_calibrations_circle.py to export the position of calibration markers.
3. plt_marker.py can be used to visualize those markers. It will show green circle around the calibration markers.
4. Create a world.csv file with format as state in the sample folder that states the starting and ending of the experiment.
5. Use export_gaze_markers.py to export the gaze data captured from your gaze estimation software and calibration in a csv file. It also export a plt.png image which visualizes total number of frame that can be used to caluclate the accuracy. On those frame where no calibration markers are detected can not be used.
6. Use calculate_accuracy_precision.py to calculate accuracy and precision of your recording. Accuracy is calculated as cosine angle(s) between two n-dimensional vectors. The outlier threshold of 5 degrees, it discards samples with high angular errors.