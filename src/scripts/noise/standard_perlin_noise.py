import numpy as np
from utils.generate_utils import *
from utils.file_utils import *
from utils.data_utils import  *
from properties import *
import matplotlib.pyplot as plt

##########################################################################
### SCRIPT HEADER ########################################################

HEIGHT = 500
WIDTH  = 500

NOISE_NODES_Y = 20
NOISE_NODES_X = 20

IMAGE_DEPTH = CHANNELS_GRAY
# CHANNELS_GRAY
# TODO implement CHANNELS_3 image depth
# CHANNELS_3

RANDOM_SEED = 0

### NON SCRIPT SPECIFIC OPTIONS ##########################################

# concat the input with the output for comparison purposes
BEFORE_AFTER_COMPARISON = YES

# Name of the export file. By specifying an extension you also specify the format of the export
EXPORT_NAME = '10.png'

### END OF SCRIPT HEADER #################################################
##########################################################################

np.random.seed(RANDOM_SEED)

def fade(t):
    return 6 * t**5 - 15 * t**4 + 10 * t**3
    # return 1 / (1 + np.exp(-t*10+5))

RATIO_Y = HEIGHT // NOISE_NODES_Y
RATIO_X = WIDTH // NOISE_NODES_X
coords_y = np.linspace(0,NOISE_NODES_Y,HEIGHT,endpoint=False)
coords_x = np.linspace(0,NOISE_NODES_X,WIDTH,endpoint=False)
noise_index_y = coords_y.astype('int32')
noise_index_x = coords_x.astype('int32')
grid_x,grid_y = np.meshgrid(coords_x,coords_y)
grid_noise_index_x,grid_noise_index_y = np.meshgrid(noise_index_x,noise_index_y)
grid_dif_y = grid_y - grid_noise_index_y
grid_dif_x = grid_x - grid_noise_index_x

DATA_RANDOM_SHAPE = (NOISE_NODES_Y + 1, NOISE_NODES_X + 1)
data_theta_random = np.random.uniform(low=-np.pi, high=np.pi, size=DATA_RANDOM_SHAPE)

data_random = np.stack((np.cos(data_theta_random),np.sin(data_theta_random)),axis=2)

data_switch = np.random.binomial(1,p=0.25,size=DATA_RANDOM_SHAPE)
# data_random[data_switch == 0] *= 0

print(data_random.shape)

fade_y = fade(grid_dif_y)
fade_x = fade(grid_dif_x)


n00 = (data_random[grid_noise_index_y, grid_noise_index_x,0] * (-grid_dif_y) +
       data_random[grid_noise_index_y, grid_noise_index_x,1] * (-grid_dif_x))

n10 = (data_random[grid_noise_index_y, grid_noise_index_x+1,0] * (-grid_dif_y) +
       data_random[grid_noise_index_y, grid_noise_index_x+1,1] * (1-grid_dif_x))

n01 = (data_random[grid_noise_index_y+1, grid_noise_index_x,0] * (1-grid_dif_y) +
       data_random[grid_noise_index_y+1, grid_noise_index_x,1] * (-grid_dif_x))

n11 = (data_random[grid_noise_index_y+1, grid_noise_index_x+1,0] * (1-grid_dif_y) +
       data_random[grid_noise_index_y+1, grid_noise_index_x+1,1] * (1-grid_dif_x))

f = (
    (1-fade_x)*(1-fade_y) * n00 +
    (1-fade_x)*fade_y     * n01 +
    fade_x    *(1-fade_y) * n10 +
    fade_x    *fade_y     * n11 )


f = normalize_tensor(f)
print(f.shape)
export_image(EXPORT_NAME,f)
