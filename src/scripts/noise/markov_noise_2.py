import numpy as np
from collections import namedtuple
from utils.generate_utils import *
from utils.file_utils import *
from utils.data_utils import  *
from utils.markov_utils import *
from properties import *

##########################################################################
### SCRIPT HEADER ########################################################

HEIGHT = 100
WIDTH  = 100
UPSCALE_FACTOR = 20
N = 30

IMAGE_DEPTH = CHANNELS_GRAY

### NON SCRIPT SPECIFIC OPTIONS ##########################################

# Name of the export file. By specifying an extension you also specify the format of the export
EXPORT_NAME = '0.png'

### END OF SCRIPT HEADER #################################################
##########################################################################



np.random.seed(100)
first_values = []
for i in range(50):
    cands = np.random.choice(np.arange(3),size=(2,))+1
    mask = np.random.binomial(1,p=0.5,size=WIDTH//10)
    vs = ['0','1']
    pattern = ''.join([ vs[i] for i in mask ])
    print(pattern)
    first_values += [
        SimplePattern(pattern=pattern,candidates=cands) ]

first = FuzzyProgression(
    values=first_values,
    positive_shifts=3, negative_shifts=3, repeat_factor=5,
    child_lengths=[(WIDTH//10)*i for i in range(5,15)])

pure_colors = [
    SimpleProgression(values = [i])
    for i in range(1,5)
]

pure = FuzzyProgression(
    values=pure_colors,
    positive_shifts=2,negative_shifts=2,repeat_factor=1,
    child_lengths=[WIDTH])


accented_values = []
for i in range(10):
    mask = np.random.binomial(2,p=0.5,size=5)
    vs = ['0','1','2']
    pattern = ''.join([ vs[i] for i in mask ])
    print(pattern)
    accented_values += [
        SimplePattern(pattern=pattern,candidates=[4,4,5]) ]

accented = RandomMarkovModel(
    values=accented_values,
    child_lengths=[WIDTH*i for i in range(1,2)])


parent = RandomMarkovModel(
    values=[accented,first,pure],
    child_lengths=[1,2,3,4],
    seed=250)




def gen_channel(seed):
    img = gen_img_markov_hierarchy(
        markov_tree=parent, width=WIDTH, height=HEIGHT, seed=seed)
    img = upscale_nearest(img,UPSCALE_FACTOR)
    return img.reshape(HEIGHT*UPSCALE_FACTOR,WIDTH*UPSCALE_FACTOR,1)


def replace_indices_with_colors(img,dict_colors):
    new_img = np.zeros(list(img.shape)+[3])
    for key,item in dict_colors.items():
        mask = img == key
        new_img[mask] = item

    return new_img


first_color = np.array([255, 208, 0])
second_color = np.array([255, 80, 0])
third_color = np.array([242, 38, 76])
accent_1 = np.array([41, 110, 188])
accent_2 = np.array([ 11, 143, 189])

color_dict = {
    1:first_color,
    2:second_color,
    3:third_color,
    4:accent_1,
    5:accent_2
}

for i in range(N):
    s = i*10
    img = gen_channel(s+1)[:,:,0]
    print(img.shape)
    colored_image = replace_indices_with_colors(img,color_dict)
    print(colored_image.shape)
    export_image(
        'markov_h_%d' % (i),colored_image,format='png')
