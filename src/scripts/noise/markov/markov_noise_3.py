import numpy as np
import constants as c
from utils.generate_utils import *
from utils.file_utils import *
import utils.data_utils as data
import utils.markov_utils as markov
import utils.color_utils as color
import utils.viz_utils as viz

### DATA/INPUT/SHARED by all runs section
N = 100

HEIGHT = 200
WIDTH  = HEIGHT
UPSCALE_FACTOR = c.INSTA_SIZE // HEIGHT

NUM_GEN_PATTERNS = 15
PATTERN_LENGTH = 9
MAX_HEIGHT = 3



BASE_DICT = {
    1:color.hex_2_rgb('#d1ffe0'),
    2:color.hex_2_rgb('#d1ffd1'),
    3:color.hex_2_rgb('#e1ffd1'),
    4:color.hex_2_rgb('#f3ffcc'),
    5:color.hex_2_rgb('#fff3cc'),
}

GRAD_DICT = {
    i+10+1:color.hex_2_rgb(h)
    for i,h in enumerate([
        '6b0030',
        '6ddaff',
        'f9502a',
])
}

COLOR_DICT = {
    **BASE_DICT,
    **GRAD_DICT
}

print(COLOR_DICT)

### FUNCTIONS section
def gen_channel(seed):
    img = markov.paint_linearly_markov_hierarchy(
        markov_tree=parent, width=WIDTH, height=HEIGHT, seed=seed)
    img = data.upscale_nearest(img,UPSCALE_FACTOR)
    return img.reshape(HEIGHT*UPSCALE_FACTOR,WIDTH*UPSCALE_FACTOR,1)


### GENERATE SECTION

for current_iteration in range(N):

    np.random.seed(1800+current_iteration)

    heights = np.random.choice(MAX_HEIGHT, size=[10, ]) + 1
    base_values = []
    lengths = [7,6,5]*(PATTERN_LENGTH//3)
    ending = np.random.choice(2,size=NUM_GEN_PATTERNS)
    print(ending)
    for i in range(NUM_GEN_PATTERNS):
        mask = np.random.choice(3, size=PATTERN_LENGTH)
        vs = '012'
        pattern = ''.join([vs[i] for i in mask])
        # if ending[i] == 1:
        #     pattern += '5'
        print(pattern)
        base_values += [
            markov.SimplePattern(pattern, lengths=lengths, candidates=[11,12,13]),
            markov.SimplePattern(pattern, lengths=lengths, candidates=[11,12,13])
        ]

    base = markov.Processor(markov.Processor(
        markov.RandomMarkovModel(
            values=base_values,
            child_lengths=[WIDTH//10],seed=current_iteration*50),
        num_tiles=[7]),num_tiles=[4,5])


    bg = [
        markov.Processor(
            markov.SimpleProgression(values=[i]),
            num_tiles=WIDTH*3)
        for i in [11,13]
    ]

    bg = markov.RandomMarkovModel(values=bg,child_lengths=[1])

    pure = [
        markov.Processor(
            markov.SimpleProgression(values=[i]),
            num_tiles=WIDTH//10)
        for i in [1,2,3,4,5]
    ]

    pure = markov.Processor(markov.SimpleProgression(
        values = [markov.RandomMarkovModel(
            values=pure, child_lengths=[1,2,3], seed=current_iteration)],
            child_lengths=[5]),
        num_tiles=[5])

    pure = markov.SimpleProgression([pure],child_lengths=[1])

    parent = markov.MarkovModel(
        preference_matrix=[[7,2,2],[1,1,0],[3,0,1]],
        values=[base,bg,pure],
        child_lengths=[1])


    s = current_iteration*10
    img = gen_channel(s+1)[:,:,0]
    print(img.shape)
    colored_image = color.replace_indices_with_colors(img, COLOR_DICT)
    print(colored_image.shape)
    if N==1:
        viz.show_image(colored_image)
    else:
        export_image(
        'markov_h_%d' % (current_iteration),colored_image.astype('uint8'),format='png')
