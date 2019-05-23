import sys
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import utils.data_utils as data

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

def start_image_server(color_string,generate_image_function):
    import utils.ui_utils.image_server as image_server
    image_server.start_server(color_string,generate_image_function)