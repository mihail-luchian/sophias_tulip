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
N = 20
SEED = config.get('seed',0)
HEIGHT = 1000
WIDTH  = HEIGHT

UPSCALE_FACTOR = c.INSTA_SIZE // HEIGHT


COLOR_STRING = config.get(
    'color-string-3',
    'Yellows:0/ffdbc9/20-1/ffebc4/20-2/f2ffcc/20-3/def9b8/20-4/ffdcba/20,Violets:10/d62a55/20-11/f97cbd/20-12/f48e7f/20-13/ffa29b/20-14/fc8c58/20,Blue:5/2098f9/20-6/2332ff/20-7/1980e8/20-8/0742f2/20-9/21f3ff/20')


### SETUP section
print('SETUP SECTION')
if N>1:
    file.clear_export_dir()


### FUNCTIONS section
print('FUNCTIONS SETUP')

def posterize_sequence(sequence):
    # num_bins = r.choice([4,10,100,400])
    num_bins = 100
    if num_bins < 30:
        bins = np.linspace(0,1,num_bins,endpoint=False)
        digitized = np.digitize(sequence,bins)
        sequence = bins[digitized-1]
    return data.ease_inout_sin(sequence)
    # return sequence

def continous_linspace(values_start,values_end,lengths):

    transitions = np.concatenate(
        [
            posterize_sequence(np.linspace(0,1,lengths[i]))
            for i in range(len(values_start))
        ])


    return (
            np.repeat(values_start,lengths.astype('int32'))*(1-transitions)
            + transitions*np.repeat(values_end,lengths.astype('int32'))
    )


def generate_gradient(colors_start,colors_end,lengths):
    # print(colors.shape)
    # print(lengths.shape)

    colors_start = color.srgb_2_cam02ucs(colors_start)
    colors_end = color.srgb_2_cam02ucs(colors_end)

    j_start = colors_start[:,0]
    c_start = colors_start[:,1]
    h_start = colors_start[:,2]

    j_end = colors_end[:,0]
    c_end = colors_end[:,1]
    h_end = colors_end[:,2]

    return color.cam02ucs_2_srgb(
        np.stack(
            (
                continous_linspace(j_start,j_end,lengths),
                continous_linspace(c_start,c_end,lengths),
                continous_linspace(h_start,h_end,lengths),
            ),
            axis=1,
        )
    )


def generate_patch(height, width, color_dict,rkey):

    patch = np.zeros((height,width,3),dtype='float64')

    color_start_lengths = np.array([
        int(i)
        for i in color.get_meta_from_palette(color_dict)
    ])

    num_color_samples = width//np.min(color_start_lengths) + 20

    color_codes = color.get_keys_from_palette(color_dict)
    pattern = m.FuzzyProgression(
        values=color_codes,
        positive_shifts=3,
        negative_shifts=3,
        self_length=num_color_samples,
        parent_rkey=r.bind_generator_from(rkey))

    sample_raw_start = m.sample_markov_hierarchy(pattern,num_color_samples).astype('int32')
    sample_raw_down_start = m.sample_markov_hierarchy(pattern,num_color_samples).astype('int32')
    # print(sample_raw_start)
    sample_raw_end = m.sample_markov_hierarchy(pattern,num_color_samples).astype('int32')
    sample_raw_down_end = m.sample_markov_hierarchy(pattern,num_color_samples).astype('int32')
    sample_raw_backup = m.sample_markov_hierarchy(pattern,num_color_samples).astype('int32')
    # making the probability of same color used smaller
    replace_mask = sample_raw_start == sample_raw_end
    sample_raw_end[replace_mask] = sample_raw_backup[replace_mask]

    sample_start = color.replace_indices_with_colors(sample_raw_start,color_dict)
    sample_end = color.replace_indices_with_colors(sample_raw_end,color_dict)

    sample_down_start = color.replace_indices_with_colors(sample_raw_down_start,color_dict)
    sample_down_end = color.replace_indices_with_colors(sample_raw_down_end,color_dict)

    switch_key = r.bind_generator_from(rkey)
    switch = np.array([
        r.choice_from(switch_key,[0, 1], replace=False, size=(2,))
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
        values=np.arange(0,41,10)-20,
        preference_matrix=data.str2mat(
            '0 1 5 1 0, 1 2 5 1 0, 0 1 10 1 0, 0 1 5 2 1, 0 1 5 1 0'),
        self_length=num_vertical_samples,
        parent_rkey=r.bind_generator_from(rkey))

    offsets = np.stack([
        m.sample_markov_hierarchy(model,num_vertical_samples)
        for _ in range(num_color_samples)
    ],axis=1)

    offsets = np.repeat(
        offsets,
        repeats=r.choice_from(rkey,[num_vertical_reps+i for i in range(1)],size=(num_vertical_samples,)),
        axis=0)

    offsets = np.cumsum(offsets,axis=0)
    offsets += start_lengths
    offsets = np.hstack([np.zeros((offsets.shape[0], 1)), offsets])

    i = 0
    offset_index = 0

    transition = np.linspace(0,1,num_vertical_samples)
    sample_start_gradient = sample_start[:,:,None]*(1-transition) + sample_down_start[:,:,None]*transition
    sample_end_gradient = sample_end[:,:,None]*(1-transition) + sample_down_end[:,:,None]*transition


    multiples_choices = r.choice_from(
        rkey,config.get('multiples-choices',[20,30,40,50]), size=(6,))
    # print('multiples-choices',multiples_choices)

    while i < height:
        loop_key = r.bind_generator_from(rkey)
        current_lengths = offsets[offset_index]
        acum_max = np.maximum.accumulate(current_lengths)
        mask = acum_max == current_lengths

        diff = np.diff(current_lengths[mask])

        samples_start_masked = sample_start[mask[1:]]
        samples_end_masked = sample_end[mask[1:]]
        #
        # samples_start_masked = sample_start_gradient[:,:,i//num_vertical_reps][mask[1:]]
        # samples_end_masked = sample_end_gradient[:,:,i//num_vertical_reps][mask[1:]]

        p_switch = config.get('gradient-switch-p',0.5)

        switch = r.choice_from(loop_key,[0,1],size=samples_start_masked.shape[0],p=[p_switch,1-p_switch])
        switch = np.stack((switch,1-switch),axis=1)

        sample_start_switched = np.where( switch[:,0][:,None], samples_start_masked, samples_end_masked )
        sample_end_switched = np.where( switch[:,1][:,None], samples_start_masked, samples_end_masked )

        multiples = r.choice_from(loop_key,multiples_choices)

        gradient = generate_gradient(
            sample_start_switched,sample_end_switched,diff)[:width]
        patch[i:i+multiples] = gradient[None,:]
        i += multiples
        offset_index += 1

    patch[patch<0]=0
    patch[patch>255]=255
    return patch



def generate_image(gridx, gridy, color_repository, rkey):
    keys = list(color_repository.keys())
    key_probabilities = [0.4,0.4,0.2]
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
        rxkey = r.bind_generator_from(rkey)
        for j,x in enumerate(gridxextended):

            endx = x

            if occupied[i,j] > 0:
                startx = endx
                continue

            p = 0.5
            elongatey = r.choice_from(rxkey,[True,False],p=[p,1-p])
            elongatex = r.choice_from(rxkey,[True,False],p=[0,1])
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


            key = r.choice_from(rxkey,keys,p=key_probabilities)

            patch = r.call_and_bind_from(
                rxkey,generate_patch,
                height, width, color_repository[key])
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

    def generate_full_image(color_string,seed):
        r.init_def_generator(seed)

        valuesx = [75+current_iteration*3,100+current_iteration*2,150+current_iteration]
        valuesy = [250,300,350]
        gridpatternx = m.FuzzyProgression(
            values=valuesx,
            positive_shifts=1,
            repeat_factor=3,
            self_length=20)
        parentx = m.SProg(values=gridpatternx)

        gridpatterny = m.RMM(values=valuesy,self_length=20)
        parenty = m.SProg(values=gridpatterny)

        gridx = m.generate_grid_lines(parentx,WIDTH)
        # gridy = m.generate_grid_lines(parenty,HEIGHT)
        gridy = [HEIGHT//2]

        # print(gridx)
        # print(gridy)

        color_repository = color.build_color_repository(color_string)
        final_img = r.call_and_bind(
            generate_image,
            gridx, gridy, color_repository)


        return final_img


    # imgs = generate_full_image(COLOR_STRING)
    # file.export_image(
    #     '%d_%d' % (current_iteration,int(round(time.time() * 1000))),
    #     imgs.astype('uint8'),format='png')
    #
    if N==1:
        viz.start_image_server(
            COLOR_STRING,
            generate_full_image,
            SEED+current_iteration)
    else:
        imgs = generate_full_image(COLOR_STRING,SEED)
        file.export_image(
            '%d_%d_%d' % (current_iteration,SEED+current_iteration,int(round(time.time() * 1000))),
            imgs.astype('uint8'),format='png')