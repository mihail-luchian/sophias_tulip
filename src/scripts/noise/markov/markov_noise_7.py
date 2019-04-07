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
SEED = 587458
HEIGHT = 400
WIDTH  = HEIGHT

UPSCALE_FACTOR = c.INSTA_SIZE // HEIGHT

NUM_CELLS = 20
START_COLOR = '000000'
END_COLOR = 'ffffff'

COLOR_DICT = color.interpolate_hex_colors(START_COLOR,END_COLOR,NUM_CELLS)
COLOR_DICT = {
    **COLOR_DICT,
    NUM_CELLS+1: '5d4e60'
}
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



### GENERATE SECTION
print('GENERATE SECTION')

for current_iteration in range(N):

    np.random.seed(SEED+current_iteration)

    pat = gen.gen_random_pattern_with_lengths(
        WIDTH, NUM_CELLS, np.arange(NUM_CELLS), min_length=5)


    num_tiles = np.random.poisson(3,size=5)+1
    vls = pat['values']
    zeroes = NUM_CELLS - NUM_CELLS//5
    vls[ np.random.choice(NUM_CELLS,size=zeroes,replace=False) ] = NUM_CELLS+1
    lngts = pat['lengths']
    model = m.Processor(
        m.SimpleProgression(
            values=vls,
            lenghts=lngts,
            self_length=NUM_CELLS,
            start_probs=[0,2,4,8,10]),
        num_tiles=num_tiles
    )

    parent = m.SimpleProgression(values=model)

    img = gen_portion(
        parent,
        height=HEIGHT,width=WIDTH,
        tile_height=None,tile_width=None)

    final_img_prototype = data.upscale_nearest(img,UPSCALE_FACTOR)
    final_img = color.replace_indices_with_colors(final_img_prototype,COLOR_DICT).astype('uint8')
    if N==1:
        viz.start_color_editing_tool(final_img_prototype,COLOR_DICT)
    else:
        file.export_image(
            '%d_%d' % (current_iteration,int(round(time.time() * 1000))),
            final_img,format='png')
