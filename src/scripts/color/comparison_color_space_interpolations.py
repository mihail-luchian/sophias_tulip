print('IMPORTING MODULES')
import time
import constants as c
import script_config as config
import numpy as np
import cv2
import utils.generate_utils as gen
import utils.file_utils as file
import utils.data_utils as data
import utils.markov_utils as m
import utils.color_utils as color
import utils.viz_utils as viz

### DATA/INPUT/SHARED by all runs section
print('PREPARING DATA SECTION')
N = 4
SEED = config.get('seed',0)
HEIGHT = 100
WIDTH  = HEIGHT

UPSCALE_FACTOR = c.INSTA_SIZE // HEIGHT


START_COLOR = 'ff0000'
END_COLOR = '0000ff'


### SETUP section
print('SETUP SECTION')
if N>1:
    file.clear_export_dir()


### FUNCTIONS section
print('FUNCTIONS SETUP')


def lab(c):
    return color.srgb2lab(c)
def lab_back(c):
    return color.lab2srgb(c)

def srgb(c): return c
def srgb_back(c): return c


def cam(c):
    return color.srgb2cam02(c)
def cam_back(c):
    return color.cam022srgb(c)


def camucs(c):
    return color.srgb2cam02ucs(c)
def camucs_back(c):
    return color.cam02ucs2srgb(c)


### GENERATE SECTION
print('GENERATE SECTION')

to_space = [lab,srgb,cam,camucs]
space_back = [lab_back,srgb_back,cam_back,camucs_back]
name = ['lab','srgb','cam', 'camucs']

for current_iteration in range(N):
    print('CURRENT_ITERATION:',current_iteration)
    np.random.seed(SEED+current_iteration)

    start_rgb = color.hex2rgb(START_COLOR)
    end_rgb = color.hex2rgb(END_COLOR)

    start_conv = to_space[current_iteration](start_rgb)
    end_conv = to_space[current_iteration](end_rgb)

    num_steps = 50
    interp_j = np.linspace(start_conv[0], end_conv[0], num_steps)
    interp_c = np.linspace(start_conv[1], end_conv[1], num_steps)
    interp_h = np.linspace(start_conv[2], end_conv[2], num_steps)

    gradient = np.stack(
        (interp_j,interp_c,interp_h),axis=1).reshape(1,num_steps,3)
    gradient = space_back[current_iteration](gradient)
    gradient = np.clip(gradient,0,255)
    img = data.upscale_nearest(gradient, ny=1000, nx=20).astype('uint8')
    print(img.shape)

    file.export_image(
        name[current_iteration] + '%d_%d' % (current_iteration,int(round(time.time() * 1000))),
        img,format='png')
