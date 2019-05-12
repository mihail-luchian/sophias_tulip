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
    config.get('string_colors',c.DEFAULT_COLOR_STR + ('|'+c.DEFAULT_COLOR_STR)*2))


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


    bins = np.arange(9)/9
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

def generate_patch(height, width, list_color_dicts):

    d = r.choice(len(list_color_dicts))
    patch = np.zeros((height,width,3),dtype='float64')

    color_start_lengths = np.array([
        int(l)
        for _,(_,l) in list_color_dicts[d].items()
    ])

    num_color_samples = width//np.min(color_start_lengths) + 20

    pattern = m.FuzzyProgression(
        values=[0,1,2,3,4],
        positive_shifts=3,
        negative_shifts=3,
        repeat_factor=1,
        self_length=num_color_samples)
    # +1 because we want gradients
    raw_sample = m.sample_markov_hierarchy(pattern,num_color_samples+1)
    sample = color.replace_indices_with_colors(raw_sample,list_color_dicts[d])


    start_lengths = color_start_lengths[raw_sample[:-1].astype('int32')]
    start_lengths = np.cumsum(start_lengths)

    num_vertical_reps = 3
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
        repeats=r.choice([num_vertical_reps+i for i in range(6)],size=(num_vertical_samples,))
        ,axis=0)
    offsets = np.cumsum(offsets,axis=0) + start_lengths
    offsets = np.hstack( [np.zeros((offsets.shape[0],1)),offsets])

    i = 0
    while i < height:

        current_lengths = offsets[i]
        acum_max = np.maximum.accumulate(current_lengths)
        mask = acum_max == current_lengths

        diff = np.diff(current_lengths[mask])
        samples_masked = sample[mask]
        multiples = r.choice([2,3,5,10,25])


        gradient = generate_gradient(samples_masked,diff)[:width]
        patch[i:i+multiples] = gradient[None,:]
        i += multiples

    patch[patch<0]=0
    patch[patch>255]=255
    return patch



def generate_image(gridx, gridy, list_color_dict):

    color_keys = [
        list(i.keys())
        for i in list_color_dict
    ]
    img = np.zeros((HEIGHT,WIDTH,3),dtype='float64')

    startx = 0
    starty = 0

    y_iteration = 0
    gridyextended = np.append(gridy, HEIGHT)
    gridxextended = np.append(gridx, HEIGHT)
    occupied = np.zeros((gridyextended.size,gridxextended.size),dtype='bool')
    for i,y in enumerate(gridyextended):
        endy = y
        num_dicts = r.choice([3])
        list_dicts = [
                list_color_dict[k]
                for k in r.choice([0,1,2],size=num_dicts,replace=False)
        ]
        y_iteration += 1
        for j,x in enumerate(gridxextended):
            endx = x

            if occupied[i,j] > 0:
                startx = endx
                continue

            p = 0.3
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

            patch = generate_patch(height,width,list_dicts)
            img[startyactual:endyactual,startxactual:endxactual] = patch

            startx = endx

        startx = 0

        # if y_iteration % 2 == 0 and num_dicts > 1:
        #     img[starty:endy] = np.roll(img[starty:endy],shift=(r.choice(5)*2+1)*25,axis=1)


        starty = endy


    final = data.upscale_nearest(img,ny = UPSCALE_FACTOR, nx = UPSCALE_FACTOR)

    return final.astype('uint8')


### GENERATE SECTION
print('GENERATE SECTION')

for current_iteration in range(N):
    print('CURRENT_ITERATION:',current_iteration)
    r.init_def_generator(SEED+current_iteration)

    gridpatternx = m.RMM(values=[50,100,100]*2+[150],self_length=10)
    parentx = m.SProg(values=gridpatternx)

    gridpatterny = m.RMM(values=[100,150,300,350]*2+[400,450],self_length=20)
    parenty = m.SProg(values=gridpatterny)

    gridx = m.generate_grid_lines(parentx,WIDTH)
    gridy = m.generate_grid_lines(parenty,HEIGHT)

    print(gridx)
    print(gridy)

    final_img = generate_image(
        gridx, gridy,LIST_COLOR_DICTS)
    # final_img = generate_patch(
    #     HEIGHT, WIDTH,LIST_COLOR_DICTS)


    file.export_image(
        '%d_%d' % (current_iteration,int(round(time.time() * 1000))),
        final_img.astype('uint8'),format='png')
