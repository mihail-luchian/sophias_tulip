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
N = 200
SEED = config.get('seed',0)
HEIGHT = 1000
WIDTH  = HEIGHT

UPSCALE_FACTOR = c.INSTA_SIZE // HEIGHT


COLOR_STRING = config.get('color-string', c.DEFAULT_COLOR_STR_2)


### SETUP section
print('SETUP SECTION')
if N>1:
    file.clear_export_dir()


### FUNCTIONS section
print('FUNCTIONS SETUP')


def continous_linspace(values_start,values_end,lengths,num_bins=50):

    transitions = np.concatenate(
        [
            np.linspace(0,1,lengths[i])
            for i in range(len(values_start))
        ])


    if num_bins < 30:
        bins = np.linspace(0,1,num_bins)
        digitized = np.digitize(transitions,bins)
        transitions = bins[digitized-1]
    transitions = data.ease_inout_sine(transitions)

    return (
            np.repeat(values_start,lengths.astype('int32'))*(1-transitions)
            + transitions*np.repeat(values_end,lengths.astype('int32'))
    )


def generate_gradient(colors_start,colors_end,lengths,num_bins):
    # print(colors.shape)
    # print(lengths.shape)

    colors_start = color.srgb2cam02(colors_start)
    colors_end = color.srgb2cam02(colors_end)

    j_start = colors_start[:,0]
    c_start = colors_start[:,1]
    h_start = colors_start[:,2]

    j_end = colors_end[:,0]
    c_end = colors_end[:,1]
    h_end = colors_end[:,2]

    return color.cam022srgb(
        np.stack(
            (
                continous_linspace(j_start,j_end,lengths, num_bins),
                continous_linspace(c_start,c_end,lengths, num_bins),
                continous_linspace(h_start,h_end,lengths, num_bins),
            ),
            axis=1,
        )
    )
def generate_patch(height, width, color_dict):

    patch = np.zeros((height,width,3),dtype='float64')

    color_start_lengths = np.array([
        int(i)
        for i in color.get_meta_from_dict(color_dict)
    ])

    num_color_samples = width//np.min(color_start_lengths) + 20

    color_codes = color.get_keys_from_dict(color_dict)
    pattern = m.FuzzyProgression(
        values=color_codes,
        positive_shifts=3,
        negative_shifts=3,
        self_length=num_color_samples)

    sample_raw_start = m.sample_markov_hierarchy(pattern,num_color_samples)
    sample_raw_end = m.sample_markov_hierarchy(pattern,num_color_samples)
    sample_raw_backup = m.sample_markov_hierarchy(pattern,num_color_samples)

    # making the probability of same color used smaller
    replace_mask = sample_raw_start == sample_raw_end
    sample_raw_end[replace_mask] = sample_raw_backup[replace_mask]

    sample_start = color.replace_indices_with_colors(sample_raw_start,color_dict)
    sample_end = color.replace_indices_with_colors(sample_raw_end,color_dict)

    switch = np.array([
        r.choice([0, 1], replace=False, size=(2,))
        for i in range(sample_start.shape[0])
    ])

    sample_start_t = np.where(switch[:, 0][:, None], sample_start, sample_end)
    sample_end_t = np.where(switch[:, 1][:, None], sample_start, sample_end)

    sample_start = sample_start_t
    sample_end = sample_end_t


    start_lengths = color.get_meta_for_each_sample(sample_raw_start,color_dict)
    start_lengths = np.array([int(i) for i in start_lengths])
    start_lengths = np.cumsum(start_lengths)

    num_vertical_reps = 2
    num_vertical_samples = height//num_vertical_reps + 3
    model = m.MarkovModel(
        values=np.arange(0,21,5)-10,
        preference_matrix=data.str2mat(
            '0 1 2 1 0, 1 2 3 1 0, 0 1 8 1 0, 0 1 3 2 1, 0 1 2 1 0'),
        self_length=num_vertical_samples)
    offsets = np.stack([
        m.sample_markov_hierarchy(model,num_vertical_samples)
        for _ in range(num_color_samples)
    ],axis=1)

    offsets = np.repeat(
        offsets,
        repeats=r.choice([num_vertical_reps+i for i in range(1)],size=(num_vertical_samples,)),
        axis=0)

    offsets = np.cumsum(offsets,axis=0)
    offsets += start_lengths
    offsets = np.hstack([np.zeros((offsets.shape[0], 1)), offsets])

    i = 0
    offset_index = 0

    multiples_choices = r.choice(
        config.get('multiples-choices',[20,30,40,50]), size=(6,))
    # print('multiples-choices',multiples_choices)

    while i < height:

        current_lengths = offsets[offset_index]
        acum_max = np.maximum.accumulate(current_lengths)
        mask = acum_max == current_lengths

        diff = np.diff(current_lengths[mask])

        samples_start_masked = sample_start[mask[1:]]
        samples_end_masked = sample_end[mask[1:]]

        p_switch = config.get('gradient-switch-p',0.5)

        switch = r.choice([0,1],size=samples_start_masked.shape[0],p=[p_switch,1-p_switch])
        switch = np.stack((switch,1-switch),axis=1)

        sample_start_switched = np.where( switch[:,0][:,None], samples_start_masked, samples_end_masked )
        sample_end_switched = np.where( switch[:,1][:,None], samples_start_masked, samples_end_masked )

        multiples = r.choice(multiples_choices)

        gradient = generate_gradient(
            sample_start_switched,sample_end_switched,diff,r.choice([4,10,100,400]))[:width]
        patch[i:i+multiples] = gradient[None,:]
        i += multiples
        offset_index += 1

    patch[patch<0]=0
    patch[patch>255]=255
    return patch



def generate_image(gridx, gridy, color_repository):

    keys = list(color_repository.keys())
    key_probabilities = [0.35,0.35,0.3]
    img = np.zeros((HEIGHT,WIDTH,3),dtype='float64')


    startx = 0
    starty = 0

    y_iteration = 0
    gridyextended = np.append(gridy, HEIGHT)
    gridxextended = np.append(gridx, HEIGHT)
    occupied = np.zeros((gridyextended.size,gridxextended.size),dtype='bool')
    for i,y in enumerate(gridyextended):
        endy = y
        y_iteration += 1
        for j,x in enumerate(gridxextended):
            endx = x

            if occupied[i,j] > 0:
                startx = endx
                continue

            p = 0.5
            elongatey = r.choice([True,False],p=[p,1-p])
            elongatex = r.choice([True,False],p=[p,1-p])
            if i >= gridyextended.size-1: elongatey = False
            if j >= gridxextended.size-1: elongatex = False

            startyactual = starty
            endyactual = endy
            startxactual = startx
            endxactual = endx

            height = endy - starty
            width = endx - startx

            if elongatey:
                add_height = gridyextended[i + 1] - gridyextended[i]
                height = endy + add_height - starty
                endyactual += add_height

            if elongatex:
                add_width = gridxextended[j + 1] - gridxextended[j]
                width = endx + add_width - startx
                endxactual += add_width

            if elongatex and elongatey:
                occupied[i:i+2,j:j+2] = True
            elif elongatex and not elongatey:
                occupied[i,j:j+2] = True
            elif elongatey and not elongatex:
                occupied[i:i+2,j] = True
            else:
                occupied[i,j] = True

            patch = generate_patch(
                height, width,
                color_repository[r.choice(keys,p=key_probabilities)])
            img[startyactual:endyactual,startxactual:endxactual] = patch

            startx = endx

        startx = 0
        starty = endy


    final = data.upscale_nearest(img,ny = UPSCALE_FACTOR, nx = UPSCALE_FACTOR)

    return final.astype('uint8')


### GENERATE SECTION
print('GENERATE SECTION')

for current_iteration in range(N):
    print('CURRENT_ITERATION:',current_iteration)

    def generate_full_image(color_string):
        r.init_def_generator(SEED+current_iteration)

        valuesx = [150,200,250]
        valuesy = [200,250,300]
        gridpatternx = m.RMM(values=valuesx,self_length=20)
        parentx = m.SProg(values=gridpatternx)

        gridpatterny = m.RMM(values=valuesy,self_length=20)
        parenty = m.SProg(values=gridpatterny)

        gridx = m.generate_grid_lines(parentx,WIDTH)
        gridy = m.generate_grid_lines(parenty,HEIGHT)

        # print(gridx)
        # print(gridy)

        color_repository = color.build_color_repository(color_string)
        final_img = generate_image(gridx, gridy, color_repository)


        return final_img


    # imgs = generate_full_image(COLOR_STRING)
    # file.export_image(
    #     '%d_%d' % (current_iteration,int(round(time.time() * 1000))),
    #     imgs.astype('uint8'),format='png')
    #
    if N==1:
        viz.start_image_server(COLOR_STRING,generate_full_image)
    else:
        imgs = generate_full_image(COLOR_STRING)
        file.export_image(
            '%d_%d_%d' % (current_iteration,SEED+current_iteration,int(round(time.time() * 1000))),
            imgs.astype('uint8'),format='png')