import sys
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import utils.data_utils as data
from utils.ui_utils.color_editing_tool import ColorEditingTool
from PyQt5.QtWidgets import QApplication

def show_animation(data):
    fig = plt.figure()
    ims = []
    for d in data:
        im = plt.imshow(d, animated=True)
        ims.append([im])
    ani = animation.ArtistAnimation(
        fig, ims, interval=35, blit=True)

    plt.show()

def show_image(img):
    if np.max(img) > 1:
        img = data.normalize_tensor(img)
    plt.imshow(img)
    plt.show()

def start_color_editing_tool(img):
    app = QApplication(sys.argv)
    ex = ColorEditingTool(img)
    ex.show()
    sys.exit(app.exec_())