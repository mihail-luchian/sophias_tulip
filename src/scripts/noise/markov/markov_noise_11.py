print('IMPORTING MODULES')
import time
import constants as c
import script_config as config
import numpy as np
import cv2
import utils.generate_utils as gen
import random_manager as r
import utils.file_utils as file
import utils.data_utils as data
import utils.markov_utils as m
import utils.color_utils as color
import utils.viz_utils as viz

### DATA/INPUT/SHARED by all runs section
print('PREPARING DATA SECTION')
N = 100
SEED = config.get('seed',0)
HEIGHT = 1000
WIDTH  = HEIGHT

UPSCALE_FACTOR = c.INSTA_SIZE // HEIGHT


LIST_COLOR_DICTS = color.build_list_color_dictionaries(
    config.get('string-colors-light-blue', c.DEFAULT_COLOR_STR_2))
COLOR_DICT = color.flatten_color_dicts(LIST_COLOR_DICTS)


### SETUP section
print('SETUP SECTION')
if N>1:
    file.clear_export_dir()


### FUNCTIONS section
print('FUNCTIONS SETUP')


def continous_linspace(values,lengths):

    transitions = np.concatenate(
        [
            np.linspace(0,1,lengths[i])
            for i in range(len(values)-1)
    ])


    bins = np.arange(12)/12
    digitized = np.digitize(transitions,bins)
    transitions = bins[digitized-1]
    transitions = data.ease_inout_sine(transitions)

    values_start = values[:-1]
    values_end = values[1:]

    return (
            np.repeat(values_start,lengths.astype('int32'))*(1-transitions)
            + transitions*np.repeat(values_end,lengths.astype('int32'))
    )

def generate_gradient(colors,lengths):
    # print(colors.shape)
    # print(lengths.shape)

    colors = color.srgb2cam02ucs(colors)

    j = colors[:,0]
    c = colors[:,1]
    h = colors[:,2]

    return color.cam02ucs2srgb(
        np.stack(
            (
                continous_linspace(j,lengths),
                continous_linspace(c,lengths),
                continous_linspace(h,lengths),
            ),
            axis=1,
        )
    )

def generate_patch(height, width, color_dict):

    patch = np.zeros((height,width,3),dtype='float64')

    color_start_lengths = np.array([
        int(l)
        for _,(_,l) in color_dict.items()
    ])

    num_color_samples = width//np.min(color_start_lengths) + 20

    pattern = m.FuzzyProgression(
        values=np.arange(15),
        positive_shifts=3,
        negative_shifts=3,
        self_length=num_color_samples)
    # +1 because we want gradients
    raw_sample = m.sample_markov_hierarchy(pattern,num_color_samples+1)
    sample = color.replace_indices_with_colors(raw_sample,color_dict)


    start_lengths = color_start_lengths[raw_sample[:-1].astype('int32')]
    start_lengths = np.cumsum(start_lengths)

    num_vertical_reps = 4
    num_vertical_samples = height//num_vertical_reps + 3
    model = m.MM(
        values=[-1,0,1],
        preference_matrix=[[0,2,1],[1,2,1],[1,2,0]],
        self_length=num_vertical_samples)
    offsets = np.stack([
        m.sample_markov_hierarchy(model,num_vertical_samples)
        for _ in range(num_color_samples)
    ],axis=1)

    offsets = np.repeat(
        offsets,
        repeats=r.choice([num_vertical_reps+i for i in range(3)],size=(num_vertical_samples,))
        ,axis=0)
    offsets = np.cumsum(offsets,axis=0)
    # offsets[offsets>55] = 55
    # offsets[offsets<-55] = -55
    offsets += start_lengths
    offsets = np.hstack( [np.zeros((offsets.shape[0],1)),offsets])

    i = 0
    while i < height:

        current_lengths = offsets[i]
        acum_max = np.maximum.accumulate(current_lengths)
        mask = acum_max == current_lengths

        diff = np.diff(current_lengths[mask])
        samples_masked = sample[mask]
        multiples = r.choice([2,3,4,5,10]*2+[20,25,50])


        gradient = generate_gradient(samples_masked,diff)[:width]
        patch[i:i+multiples] = gradient[None,:]
        i += multiples

    patch[patch<0]=0
    patch[patch>255]=255
    return patch



### GENERATE SECTION
print('GENERATE SECTION')

for current_iteration in range(N):
    print('CURRENT_ITERATION:',current_iteration)
    r.init_def_generator(SEED+current_iteration)

    final_img = generate_patch(HEIGHT, WIDTH,COLOR_DICT)


    file.export_image(
        '%d_%d' % (current_iteration,int(round(time.time() * 1000))),
        final_img.astype('uint8'),format='png')
