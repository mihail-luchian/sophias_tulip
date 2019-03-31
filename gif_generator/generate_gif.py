import utils.file_utils as file
import constants as c
import os
from os.path import isfile, join
import numpy as np

current_dir = os.path.dirname(os.path.realpath(__file__))
imgs_dir = os.path.join(current_dir,'imgs')

image_names = [f for f in os.listdir(imgs_dir) if isfile(join(imgs_dir, f))]
indices = np.array([int(i[:-4]) for i in image_names])
sorted_args = np.argsort(indices)

sorted_image_names = [ image_names[i] for i in sorted_args ]
list_images = np.array(
    [ file.load_image(os.path.join(imgs_dir,i))[::2,::2,:] for i in sorted_image_names])

print(list_images.shape)

gif_path = os.path.join(current_dir,'movie.gif')
file.export_animation(gif_path,list_images,loop=1,fps=0.75)
