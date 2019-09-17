print('IMPORTING MODULES')
import time
import constants as c
import script_config as config
import numpy as np
import utils.generate_utils as gen
import random_manager as r
import utils.file_utils as file
import utils.data_utils as data
import utils.markov_utils as m
import utils.color_utils as color
import utils.viz_utils as viz
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter

### DATA/INPUT/SHARED by all runs section
print('PREPARING DATA SECTION')
DUMP_PREVIOUS_EXPORTS = True
SHOW_DEBUG_DATA = False
START_SERVER = False
SAVE_IMAGES = False

N = 10
SEED = config.get('seed',301)
HEIGHT = 1000
WIDTH  = 1000

TO_GENERATE = int(HEIGHT * 0.8)
LEFT_OVER = HEIGHT - TO_GENERATE
NUM_REPEATS  = 10
LENGTH_REPEATS = LEFT_OVER // NUM_REPEATS

SEGMENT_LENGTH = 40


UPSCALE_FACTOR_Y = c.INSTA_SIZE // HEIGHT
UPSCALE_FACTOR_X = c.INSTA_SIZE // WIDTH


COLOR_STRING = config.get(
    'color-string',
    'First:0/fff2c9/2-1/f3ff75/3-2/a7fc4b/3-3/a0ffa8/3-4/d6ffdc/2,Second:0/84ffd4/-1/39f9ed/-2/1ddbf4/-3/1168f4/-4/1da4f2/,Third:0/fff2c9/2-1/f3ff75/3-2/a7fc4b/3-3/a0ffa8/3-4/d6ffdc/2')


### SETUP section
print('SETUP SECTION')
if DUMP_PREVIOUS_EXPORTS:
    file.clear_export_folder()


### FUNCTIONS section
print('FUNCTIONS SETUP')

def integrate_and_normalize(series,n):
    series_int = data.integrate_series(series, n, mean_influence=1)
    # series_int = gaussian_filter(series_int,sigma=2.5)
    # series_int = data.concat_signals([series_int, series_int], [1, -1])
    # series_int -= np.min(series_int)
    # series_int /= np.max(series_int)
    return series_int


def interpolate_colors(color_1,color_2,interpolation_sequence):
    return color_1[:,None]*(1-interpolation_sequence)[None,:] + color_2[:,None]*(interpolation_sequence)[None,:]

def generate_full_image(color_string,seed):
    r.init_def_generator(seed)

    image = np.zeros((HEIGHT,WIDTH,3))
    plots = []
    loop_key = r.bind_generator()
    setup_key = r.bind_generator()

    post_process = lambda x: data.integrate_series(x,n=2,mean_influences=[0,0])


    pup = m.SimpleProgression(
        values=1,
        self_length=[10,40,50],
        post_process=post_process
    )
    pdown = m.SimpleProgression(
        values=-1,
        self_length=[10,40,50],
        post_process=post_process
    )
    arc = m.RandomMarkovModel(values=[pup,pdown],self_length=[2])


    p = m.RandomMarkovModel(
        # values=[p1, p2, arc],
        values=[arc],
        parent_rkey=r.bind_generator_from(setup_key)
    )


    # for i in range(-30,30):
    for i in range(1):

        sample = m.sample_markov_hierarchy(p, 1000)
        sample = data.integrate_series(sample,1,mean_influences=1)
        # sample = data.integrate_series(sample,1,mean_influences=0)
        # sample -= np.min(sample)
        # sample = data.integrate_series(sample,1)

        # slices = [ np.s_[:50],np.s_[50:100], np.s_[100:] ]
        # for slice in slices:
        #     sample[slice] -= np.mean(sample[slice])
        # sample = data.integrate_series(sample,1)
        # sample[:60+i] -= np.mean(sample[:60+i])
        # sample[60+i:] -= np.mean(sample[60+i:])
        # sample = data.integrate_series(sample,1)
        plots += [sample]

    plt.plot(plots[0])
    mng = plt.get_current_fig_manager()
    mng.full_screen_toggle()
    plt.show()
    # viz.animate_plots_y(plots)

    return image


### GENERATE SECTION
print('GENERATE SECTION')

for current_iteration in range(N):
    print('CURRENT_ITERATION:',current_iteration)

    if START_SERVER is True:
        viz.start_image_server(
            generate_full_image,
            COLOR_STRING,
            SEED+current_iteration)
        break
    else:
        image = generate_full_image(COLOR_STRING,SEED+current_iteration)
        if SAVE_IMAGES is True:
            print('\tSAVING IMAGE')
            file.export_image(
                '%d_%d_%d' % (current_iteration,SEED+current_iteration,int(round(time.time() * 1000))),
                image.astype('uint8'),format='png')


