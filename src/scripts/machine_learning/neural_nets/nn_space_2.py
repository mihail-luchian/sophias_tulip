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
from skimage.filters import gaussian

### DATA/INPUT/SHARED by all runs section
print('PREPARING DATA SECTION')

DUMP_PREVIOUS_EXPORTS = False
SHOW_DEBUG_DATA = False
START_SERVER = False
SHOW_IMAGES = True
SAVE_IMAGES = False

N = 1
SEED = config.get('seed',325)
HEIGHT = 500
WIDTH  = 500
TRAINING_UPSAMPLE = 2


### NEURAL NET CONSTANTS
LEARNING_RATE = 0.01
NUM_TRAINING_EPOCHS = 100
BATCH_SIZE = 2048

HIDDEN_LAYER_SIZE = [32,32,64,64]

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

    # gen_init = lambda seed : keras.initializers.RandomUniform(-dev,dev,seed)
    gen_init = lambda seed : keras.initializers.glorot_uniform(seed)

    layer = input
    list_layers = []
    for i in range(len(HIDDEN_LAYER_SIZE)):
        layer = keras.layers.Dense(
            HIDDEN_LAYER_SIZE[i],
            # activation=None,
            activation=keras.activations.tanh,
            kernel_initializer = gen_init(r.random_seed_from(rgen)),
            bias_initializer = gen_init(r.random_seed_from(rgen)),
        )(layer)
        list_layers += [layer]
        # layer = keras.layers.ReLU()(layer)
        # layer = keras.layers.PReLU()(layer)

    # layer = keras.layers.concatenate(list_layers)

    # layer = keras.layers.Dense(
    #     8,activation=keras.activations.tanh,
    #     kernel_initializer = gen_init(r.random_seed_from(rgen)),
    #     bias_initializer = gen_init(r.random_seed_from(rgen)),
    # )(layer)

    layer = keras.layers.Dense(
        8,activation=keras.activations.tanh,
        kernel_initializer = gen_init(r.random_seed_from(rgen)),
        bias_initializer = gen_init(r.random_seed_from(rgen)),
    )(layer)

    output = keras.layers.Dense(
        1,activation=keras.activations.tanh,
        kernel_initializer = gen_init(r.random_seed_from(rgen)),
        bias_initializer = gen_init(r.random_seed_from(rgen)),
    )(layer)
    model = keras.models.Model(inputs=input,outputs=output)

    adam = keras.optimizers.Adam(lr=LEARNING_RATE)
    model.compile(
        optimizer=adam,
        # loss=keras.losses.mean_squared_error,
        loss=keras.losses.mean_absolute_error,
    )

    return model


def generate_full_image(color_string,seed):

    r.init_def_generator(seed)
    rgen = r.bind_generator()

    training_width = WIDTH*TRAINING_UPSAMPLE
    training_height = HEIGHT*TRAINING_UPSAMPLE

    base_image = file.import_image('tulip_high')
    base_image = resize(
        base_image,
        (training_height,training_width,),
        order=3)
    base_image = gaussian(base_image,sigma=4)


    ly1 = np.linspace(-1,1,num=training_height)
    lx1 = np.linspace(-1,1,num=training_width)
    yy1,xx1 = np.meshgrid(ly1,lx1)

    ly2 = np.linspace(-1,1,num=HEIGHT)
    lx2 = np.linspace(-1,1,num=WIDTH)
    yy2,xx2 = np.meshgrid(ly2,lx2)

    def make_fs(xx,yy):
        return np.c_[
            yy.flatten(),
            xx.flatten(),
            (xx*yy).flatten(),
            (xx**2 - 0.5).flatten(),
            (yy**2 - 0.5).flatten(),
            (yy**2 * xx**2 - 0.5).flatten(),
            (np.sin(2*np.pi*xx)).flatten(),
            (np.sin(2*np.pi*yy)).flatten(),
            (np.sin(2*np.pi*yy)*np.sin(2*np.pi*xx)).flatten(),
        ]

    f1 = make_fs(xx1,yy1)
    f2 = make_fs(xx2,yy2)

    training_image = base_image[:,:,0]
    labels = training_image.reshape(-1,1)
    labels = data.normalize_01(labels)
    labels -= 0.5

    input_size = f1.shape[1]
    input = keras.Input(batch_shape=[None,input_size])
    model = build_network(input=input,rgen=r.bind_generator_from(rgen))
    print(model.summary())

    def scheduler(epoch):
        current_learning_rate = LEARNING_RATE*(0.995**epoch)
        return current_learning_rate

    lr_callback = keras.callbacks.LearningRateScheduler(scheduler)
    tb_callback = keras.callbacks.TensorBoard(
        log_dir=c.PATH_FOLDER_LOGS, histogram_freq=1,
        write_grads=True, write_images=True
    )

    model.fit(
        x=f1,y=labels,
        batch_size=BATCH_SIZE,epochs=NUM_TRAINING_EPOCHS,
        callbacks=[lr_callback,tb_callback])

    image = model.predict(f2)
    image = image.reshape([HEIGHT,WIDTH])
    print(np.max(image),np.min(image))
    image = np.clip(image+0.5,0,1)
    return training_image,image,image-training_image[::TRAINING_UPSAMPLE,::TRAINING_UPSAMPLE]


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
            viz.show_images_together(images)


