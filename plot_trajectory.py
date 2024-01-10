import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


# trajectories: dictionary of pandas dataframes
# trajectories = {
#     "label1": pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]}),
#     "label2": pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]}),
#     ...}
# plot all trajectories in the dictionary
def plot_all_trajectories(trajectories):
    # * plot all trajectories
    for label in trajectories:
        trajectory = trajectories[label]
        plt.plot(trajectory["x"], trajectory["y"], label=label)
    plt.xlabel("x")
    plt.ylabel("y")
    plt.legend()
    plt.show()


# trajectory: pandas dataframe like pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
# name: string (name of the trajectory)
# plot trajectory
def plot_trajectory(trajectory, name):
    # * plot trajectory
    plt.plot(trajectory["x"], trajectory["y"], label=name)
    plt.xlabel("x")
    plt.ylabel("y")
    plt.legend()
    plt.show()


def center_trajectory(trajectory):
    plot_trajectory(trajectory, "Trajectory")
    x_coords = trajectory["x"]
    y_coords = trajectory["y"]

    centroid_x = np.mean(x_coords)
    centroid_y = np.mean(y_coords)

    translation_x = -centroid_x
    translation_y = -centroid_y

    x_coords_trasl = x_coords + translation_x
    y_coords_trasl = y_coords + translation_y

    trajectory["x"] = x_coords_trasl
    trajectory["y"] = y_coords_trasl
    plot_trajectory(trajectory, "Trajectory traslata")


# * leggi i dati dal file csv e salva tutte le labels di riconoscimenti delle traiettorie in un array
vehicle_loc_rot = pd.read_csv("vehicle_keyframes.csv")
labels = vehicle_loc_rot["label"].unique()

# * test plot_all_trajectories per plottare tutte le traiettorie
# trajectories = {}
# for label in labels:
#     trajectory = vehicle_loc_rot[vehicle_loc_rot["label"] == label].reset_index(
#         drop=True
#     )
#     trajectories[label] = trajectory
# print(trajectories)
# plot_all_trajectories(trajectories)

# * Test center_trajectory per traslare una traiettoria nel centro del sistema di riferimento
# trajectory_1 = vehicle_loc_rot[vehicle_loc_rot["label"] == labels[0]].reset_index(
#     drop=True
# )

# center_trajectory(trajectory_1)
