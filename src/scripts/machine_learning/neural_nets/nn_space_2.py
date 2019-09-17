print('IMPORTING MODULES')
import time
import constants as c
import script_config as config
import numpy as np
import utils.generate_utils as gen
import random_manager as r
import utils.file_utils as file
import utils.data_utils as data
import utils.nn_utils as nn
import utils.color_utils as color
import utils.viz_utils as viz
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
# from tensorflow.keras.layers import Input,Dense
# from keras.models import Model
from skimage.transform import resize

### DATA/INPUT/SHARED by all runs section
print('PREPARING DATA SECTION')

DUMP_PREVIOUS_EXPORTS = False
SHOW_DEBUG_DATA = False
START_SERVER = False
SHOW_IMAGES = True
SAVE_IMAGES = False

N = 1
SEED = config.get('seed',325)
HEIGHT = 250
WIDTH  = 250


### NEURAL NET CONSTANTS
INPUT_SIZE = 2
LEARNING_RATE = 0.00005
NUM_TRAINING_EPOCHS = 1000
BATCH_SIZE = 512

NUM_HIDDEN_LAYERS = 3

COLOR_STRING = config.get(
    'color-string',
    'First:0/fff2c9/2-1/f3ff75/3-2/a7fc4b/3-3/a0ffa8/3-4/d6ffdc/2,Second:0/84ffd4/-1/39f9ed/-2/1ddbf4/-3/1168f4/-4/1da4f2/,Third:0/fff2c9/2-1/f3ff75/3-2/a7fc4b/3-3/a0ffa8/3-4/d6ffdc/2')


### SETUP section
print('SETUP SECTION')
file.check_wip_dirs()
file.clear_logs_folder()

if DUMP_PREVIOUS_EXPORTS:
    print('\tCLEARING EXPORT DIR')
    file.clear_export_folder()
    print('\tDONE CLEARING EXPORT DIR')


### FUNCTIONS section
print('FUNCTIONS SETUP')


def build_network(input,rgen):

    dev = 0.15

    # gen_init = lambda seed : keras.initializers.RandomUniform(-dev,dev,seed)
    gen_init = lambda seed : keras.initializers.glorot_uniform(seed)

    layer = input
    for i in range(NUM_HIDDEN_LAYERS):

        layer = keras.layers.Dense(
            32, activation=keras.activations.tanh,
            kernel_initializer = gen_init(r.random_seed_from(rgen)),
            bias_initializer = gen_init(r.random_seed_from(rgen)),
        )(layer)

    layer = keras.layers.Dense(
        4,activation=keras.activations.tanh,
        kernel_initializer = gen_init(r.random_seed_from(rgen)),
        bias_initializer = gen_init(r.random_seed_from(rgen)),
    )(layer)

    output = keras.layers.Dense(
        1,activation=keras.activations.tanh,
        kernel_initializer = gen_init(r.random_seed_from(rgen)),
        bias_initializer = gen_init(r.random_seed_from(rgen)),
    )(layer)
    model = keras.models.Model(inputs=input,outputs=output)

    adam = keras.optimizers.Adam(lr=LEARNING_RATE,beta_1=0.8)
    model.compile(
        optimizer=adam,
        # loss=keras.losses.mean_squared_error,
        loss=keras.losses.mean_absolute_error,
    )

    return model


def generate_full_image(color_string,seed):

    r.init_def_generator(seed)
    rgen = r.bind_generator()

    base_image = resize(file.import_image('tulip'),(HEIGHT,WIDTH))

    input = keras.Input(batch_shape=[None,INPUT_SIZE])
    model = build_network(input=input,rgen=r.bind_generator_from(rgen))
    print(model.summary())

    ly1 = np.linspace(-1,1,num=HEIGHT)
    lx1 = np.linspace(-1,1,num=WIDTH)
    yy1,xx1 = np.meshgrid(ly1,lx1)

    f = np.c_[
            yy1.flatten(),
            xx1.flatten(),
    ]

    labels = base_image[:HEIGHT,:WIDTH,0].reshape(-1,1)
    labels = data.normalize_01(labels)
    labels -= 0.5

    def scheduler(epoch):
        current_learning_rate = LEARNING_RATE*(0.995**epoch)
        return current_learning_rate

    lr_callback = keras.callbacks.LearningRateScheduler(scheduler)
    tb_callback = keras.callbacks.TensorBoard(
        log_dir=c.PATH_FOLDER_LOGS, histogram_freq=1,
        write_grads=True, write_images=True
    )

    model.fit(
        x=f,y=labels,
        batch_size=BATCH_SIZE,epochs=NUM_TRAINING_EPOCHS,
        callbacks=[lr_callback,tb_callback])

    image = model.predict(f)
    image = image.reshape([HEIGHT,WIDTH])
    print(np.max(image),np.min(image))
    image = np.clip(image+0.5,0,1)
    return base_image[:HEIGHT,:WIDTH,0],image


### GENERATE SECTION
print('GENERATE SECTION')

for current_iteration in range(N):
    print('CURRENT_ITERATION:',current_iteration)

    if START_SERVER is True:
        viz.start_image_server(
            generate_full_image,
            COLOR_STRING,
            SEED+current_iteration)
        break
    else:
        images = generate_full_image(COLOR_STRING, SEED + current_iteration)
        if SAVE_IMAGES is True:
            print('\tSAVING IMAGE')
            file.export_image(
                '%d_%d_%d' % (current_iteration,SEED+current_iteration,int(round(time.time() * 1000))),
                images.astype('uint8'),format='png')
        elif SHOW_IMAGES is True:
            viz.show_images(images)


