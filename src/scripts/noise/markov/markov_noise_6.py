print('IMPORTING MODULES')
import time
import constants as c
import numpy as np
import utils.generate_utils as gen
import utils.file_utils as file
import utils.data_utils as data
import utils.markov_utils as m
import utils.color_utils as color
import utils.viz_utils as viz

### DATA/INPUT/SHARED by all runs section
print('PREPARING DATA SECTION')
N = 1
SEED = 156894
HEIGHT = 100
WIDTH  = HEIGHT

TILE_WIDTH = 20
TILE_HEIGHT = TILE_WIDTH

UPSCALE_FACTOR = c.INSTA_SIZE // HEIGHT

TILING_OPTIONS = [1,2,3,4,5]


COLOR_DICT = {
    0: '000b14',

    1: 'ffbfc4',
    2: 'ffcfbf',
    3: 'ffe6c4',
    4: 'fff9bf',
    5: 'eeffbf',

}

print(COLOR_DICT)

### SETUP section
print('SETUP SECTION')
file.clear_export_dir()


### FUNCTIONS section
print('FUNCTIONS SETUP')


def gen_channel(parent):
    img = m.paint_linearly_markov_hierarchy(
        markov_tree=parent,
        width=WIDTH, height=HEIGHT)
    img = data.upscale_nearest(img,UPSCALE_FACTOR)
    return img.reshape(img.shape[0],img.shape[1],1)

def gen_patterns(length,num_cells,choices,min_length=1):

    ls = np.ones(num_cells)*min_length
    length_left = length-num_cells*min_length

    for i in range(ls.size-1):
        current_length = np.random.choice(length_left)
        ls[i] += current_length
        length_left = length_left - current_length
    ls[-1] += length_left

    return {
        'values':  np.random.choice(choices,size=(num_cells,)),
        'lengths': np.random.permutation(ls)
    }


def clean_pattern(s):
    return s.replace('-','')


### GENERATE SECTION
print('GENERATE SECTION')

for current_iteration in range(N):

    np.random.seed(SEED+current_iteration)

    p = [
        gen_patterns(TILE_WIDTH,5,[1,2,3,4,5])
        for i in range(5)
    ]
    print(p)

    p = [
        m.SimpleProgression(
            values=i['values'],
            lenghts=i['lengths'],
            self_length = [5,10,15] )
        for i in p
    ]

    parent = m.RandomMarkovModel(
        values = p,
        child_lengths=5
    )

    img = gen_channel(parent)[:,:,0]
    print(img)
    print(img.shape)
    print(np.min(img))
    print(np.max(img))
    colored_image = color.replace_indices_with_colors(img, COLOR_DICT)
    colored_image = colored_image.astype('uint8')

    if N==1:
        viz.start_color_editing_tool(img,COLOR_DICT)
    else:

        file.export_image(
            '%d_%d' % (current_iteration,int(round(time.time() * 1000))),
            colored_image.astype('uint8'),format='png')
