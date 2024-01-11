import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd
import numpy as np


def plot_all_trajectories(trajectories):
    # * plot all trajectories
    for label in trajectories:
        trajectory = trajectories[label]
        plt.plot(trajectory["x"], trajectory["y"], label=label)
    plt.xlabel("x")
    plt.ylabel("y")
    plt.legend()
    plt.show()


def plot_trajectory(trajectory, name):
    # * plot trajectory
    plt.plot(trajectory["x"], trajectory["y"], label=name)
    plt.xlabel("x")
    plt.ylabel("y")
    plt.legend()
    plt.show()


def plot_3d_points(clouds, colors, labels, file_name=None):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")
    for i, cloud in enumerate(clouds):
        x, y, z = cloud
        ax.scatter(x, y, z, c=colors[i], marker=".", label=labels[i])
    ax.set_box_aspect([1, 1, 1])
    # * rotazione di default: ax.view_init(elev=30, azim=-60)
    ax.view_init(elev=30, azim=-30)
    ax.legend()
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    if file_name is not None:
        plt.savefig(file_name)
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


def build_sphere(radius=5, initial_pos=(0, 0, 0), traslation=(0, 0, 0)):
    phi = np.linspace(0, np.pi, 100)
    theta = np.linspace(0, 2 * np.pi, 100)
    phi, theta = np.meshgrid(phi, theta)

    x = radius * np.sin(phi) * np.cos(theta) + initial_pos[0] + traslation[0]
    y = radius * np.sin(phi) * np.sin(theta) + initial_pos[1] + traslation[1]
    z = radius * np.cos(phi) + initial_pos[2] + traslation[2]

    return x, y, z


# * leggi i dati dal file csv e salva tutte le labels di riconoscimenti delle traiettorie in un array
# vehicle_loc_rot = pd.read_csv("vehicle_keyframes.csv")
# labels = vehicle_loc_rot["label"].unique()

# * test plot_all_trajectories per plottare tutte le traiettorie
# trajectories = {}
# for label in labels:
#     trajectory = vehicle_loc_rot[vehicle_loc_rot["label"] == label].reset_index(
#         drop=True
#     )
#     trajectories[label] = trajectory
# print(trajectories)
# plot_all_trajectories(trajectories)


scan = pd.read_csv("scan_sphere.csv")
x1 = scan["x"]
y1 = scan["y"]
z1 = scan["z"]

scan_trasl = pd.read_csv("scan_sphere_trasl.csv")
x2 = scan_trasl["x"]
y2 = scan_trasl["y"]
z2 = scan_trasl["z"]

plot_3d_points(
    [(x1, y1, z1), (x2, y2, z2)],
    colors=["blue", "red"],
    labels=["prima della traslazione", "dopo la traslazione"],
    file_name="scan_sphere.png",
)


x1, y1, z1 = build_sphere(radius=2, initial_pos=(0, 6, -7), traslation=(0, 0, 0))
x2, y2, z2 = build_sphere(radius=2, initial_pos=(0, 6, -7), traslation=(0, -2, 1))
plot_3d_points(
    [(x1, y1, z1), (x2, y2, z2)],
    colors=["blue", "red"],
    labels=["prima della traslazione", "dopo la traslazione"],
    file_name="sphere.png",
)
