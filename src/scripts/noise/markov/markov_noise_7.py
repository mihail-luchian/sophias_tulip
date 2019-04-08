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
N = 300
SEED = 0
HEIGHT = 400
WIDTH  = HEIGHT

UPSCALE_FACTOR = c.INSTA_SIZE // HEIGHT

NUM_CELLS = 25
START_COLOR = '00357a'
END_COLOR = 'bcffb7'

COLOR_DICT = color.interpolate_hex_colors(START_COLOR,END_COLOR,NUM_CELLS)
COLOR_DICT = {
    **COLOR_DICT,
    NUM_CELLS+1: 'ff7c30',
    NUM_CELLS+2: 'ff5842',
    NUM_CELLS+3: 'cc0489',
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
    print('CURRENT_ITERATION:',current_iteration)
    np.random.seed(SEED+current_iteration)

    pats = [
        gen.gen_random_pattern_with_lengths(
            WIDTH, NUM_CELLS, np.arange(NUM_CELLS), min_length=3, max_length = 230)
        for i in range(5)
    ]


    num_tiles = [1,1,2,2,3,4,10,10,20]
    pattern_models = []


    for pat in pats:
        vls = pat['values']
        zeroes = int(NUM_CELLS/3)
        mask = np.random.choice([2,3,4], size=zeroes)
        mask = np.cumsum(mask)
        mask = mask[mask<NUM_CELLS]
        vls[mask] = np.random.choice([NUM_CELLS+1,NUM_CELLS+2,NUM_CELLS+3])
        lngts = pat['lengths']
        model = m.SimpleProgression(values=m.Processor(
            m.SimpleProgression(
                values=vls,
                lenghts=lngts,
                self_length=NUM_CELLS,
                start_probs=[0,1,2,3]),
            num_tiles=num_tiles),self_length=[5,10,15,20,25])
        pattern_models += [model]

    def update_fun(preference_matrix,start_probs):
        return preference_matrix,np.roll(start_probs,shift=1)
    parent = m.RandomMarkovModel(
        values=pattern_models,
        start_probs=0,
        update_fun=update_fun,update_step=1)

    img = gen_portion(
        parent,
        height=HEIGHT,width=WIDTH,
        tile_height=None,tile_width=None)

    final_img_prototype = data.upscale_nearest(img,UPSCALE_FACTOR)
    final_img = color.replace_indices_with_colors(final_img_prototype,COLOR_DICT).astype('uint8')
    if N==1:
        viz.start_color_editing_tool(
            blueprint=final_img_prototype,
            color_dict=COLOR_DICT,
            downsample=2)
    else:
        file.export_image(
            '%d_%d' % (current_iteration,int(round(time.time() * 1000))),
            final_img,format='png')
