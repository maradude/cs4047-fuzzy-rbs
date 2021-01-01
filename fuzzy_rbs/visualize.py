"""
based on example from official documentation:
https://pythonhosted.org/scikit-fuzzy/auto_examples/plot_control_system_advanced.html#view-the-control-space
"""
# Plot the result in pretty 3D with alpha blending
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # Required for 3D plotting
import numpy as np


def plot3dFRB(sim, inputx, inputy, output):
    """
    hard coded to work with example.txt
    """
    upsampled1 = np.arange(0, 100)
    unsampled2 = np.arange(0, 20)
    x, y = np.meshgrid(upsampled1, unsampled2)
    z = np.zeros_like(x)

    # Loop through the system 21*21 times to collect the control surface
    for i in range(20):
        for j in range(100):
            sim.input[inputx] = x[i, j]
            sim.input[inputy] = y[i, j]
            sim.compute()
            z[i, j] = sim.output[output]
    return x, y, z


def make_plot(x, y, z, x_lab, y_lab, z_lab):
    """
    show a 3d plot
    """
    fig = plt.figure(figsize=(12, 12))
    ax = fig.add_subplot(111, projection="3d")

    ax.plot_surface(
        x, y, z, rstride=1, cstride=1, cmap="viridis", linewidth=0.4, antialiased=True
    )
    ax.view_init(30, 200)
