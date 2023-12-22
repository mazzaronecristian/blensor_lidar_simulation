import matplotlib.pyplot as plt
import pandas as pd


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


# * leggi i dati dal file csv
keyframes = pd.read_csv("keyframes.csv")
labels = keyframes["label"].unique()
# * seleziona i dati relativi alla traiettoria 1
trajectories = {}
for label in labels:
    trajectory = keyframes[keyframes["label"] == label].reset_index(drop=True)
    trajectories[label] = trajectory
print(trajectories)
plot_all_trajectories(trajectories)
