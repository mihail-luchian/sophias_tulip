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
N = 100
SEED = 0
HEIGHT = 400
WIDTH  = HEIGHT

TILE_WIDTHS  = [10,20,40,50,80]
TILE_HEIGHTS = [10,20,40,50]
PORTIONS_HEIGHTS = [1]

UPSCALE_FACTOR = c.INSTA_SIZE // HEIGHT

TILING_OPTIONS = [1,2,3,4,5]


COLOR_DICT = {0: '00103e', 1: 'f96b88', 2: 'ff9e80', 3: 'ffd88c', 4: 'ffffd7', 5: 'cdff9b'}

print(COLOR_DICT)

### SETUP section
print('SETUP SECTION')
file.clear_export_dir()


### FUNCTIONS section
print('FUNCTIONS SETUP')


def gen_portion(parent,height,width,tile_height,tile_width):
    img = m.paint_linearly_markov_hierarchy(
        markov_tree=parent,
        width=width, height=height,tile_width=tile_width,tile_height=tile_height)
    return img.reshape(img.shape[0],img.shape[1])

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

    portions = []
    current_height = 0
    while current_height < HEIGHT:
        current_tile_height = np.random.choice(TILE_HEIGHTS)
        current_tile_width = np.random.choice(TILE_WIDTHS)
        l = np.random.choice(PORTIONS_HEIGHTS)

        portion_height = current_tile_height*l
        current_height += portion_height
        print(current_height,current_tile_width,current_tile_height,l)

        num_segments = current_tile_width//5
        current_colors = np.random.choice([0,1,2,3,4,5],size=num_segments)
        p = [
            gen_patterns(current_tile_width,num_segments,current_colors,min_length=2)
            for i in range(np.random.choice([2,3]))
        ]
        print(p)
        p = [
            m.Processor(
                m.SimpleProgression(
                    values=i['values'],
                    lenghts=i['lengths'],
                    self_length=num_segments,
                    start_probs=0),
                num_tiles=[2,4,5,6,8])
            for i in p
        ]

        parent = m.RandomMarkovModel(values = p)

        img = gen_portion(
            parent,
            height=portion_height,width=WIDTH,
            tile_height=current_tile_height,tile_width=current_tile_width)

        portions += [img]
        print(img.shape)
        print(np.min(img))
        print(np.max(img))

    final_img_prototype = np.vstack(portions)
    final_img_prototype = final_img_prototype[:HEIGHT,:WIDTH]
    final_img_prototype = data.upscale_nearest(final_img_prototype,UPSCALE_FACTOR)
    print(final_img_prototype.shape)
    colored_img = color.replace_indices_with_colors(
        final_img_prototype,COLOR_DICT).astype('uint8')

    if N==1:
        viz.start_color_editing_tool(final_img_prototype,COLOR_DICT)
    else:
        file.export_image(
            '%d_%d' % (current_iteration,int(round(time.time() * 1000))),
            colored_img.astype('uint8'),format='png')
