print('IMPORTING MODULES')
### Design principles
### Max number of params ~ 4.5k
### best mean-absolute-error - 0.0057 - 150 epochs
### best tv error -> 0.0094
import time
import constants as C
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
from skimage.transform import resize
from skimage.filters import gaussian
from skimage.restoration import denoise_tv_bregman
### DATA/INPUT/SHARED by all runs section
print('PREPARING DATA SECTION')

DUMP_PREVIOUS_EXPORTS = False
SHOW_DEBUG_DATA = False
START_SERVER = False
SHOW_IMAGES = True
SAVE_IMAGES = False
TRAIN_NNET = True

EXPLORE_LAYER = 'o_0'
NUM_VIZ_ROWS = 1

N = 1
SEED = config.get('seed',325)
HEIGHT = 500
WIDTH  = 500
TRAINING_UPSAMPLE = 2



### NEURAL NET CONSTANTS
LEARNING_RATE = 0.005
NUM_TRAINING_EPOCHS = 110
BATCH_SIZE = 1024
FIRST_DENSE = 5

HIDDEN_STRUCTURE = [
    ('sparse',False,32,2,False),
    ('bottleneck',False,128,16),
    # ('bottleneck',32,16),
    ('sparse',False,46,4,False),
    ('dense',True,8),
]
LOSS_WEIGHTS = [1]

CUSTOM_OBJECTS = {
    'SinLayer':nn.SinLayer,
    'CombinatoryMultiplication':nn.CombinatoryMultiplication,
    'XYCombinations': nn.XYCombinations,
    'SparseConnections': nn.SparseConnections,
    'GraphicTanh': nn.GraphicTanh,
}

COLOR_STRING = config.get(
    'color-string',
    'First:0/fff2c9/2-1/f3ff75/3-2/a7fc4b/3-3/a0ffa8/3-4/d6ffdc/2,Second:0/84ffd4/-1/39f9ed/-2/1ddbf4/-3/1168f4/-4/1da4f2/,Third:0/fff2c9/2-1/f3ff75/3-2/a7fc4b/3-3/a0ffa8/3-4/d6ffdc/2')


### SETUP section
print('SETUP SECTION')
file.check_wip_dirs()
if TRAIN_NNET is True:
    file.clear_logs_folder()

if DUMP_PREVIOUS_EXPORTS:
    print('\tCLEARING EXPORT DIR')
    file.clear_export_folder()
    print('\tDONE CLEARING EXPORT DIR')


### FUNCTIONS section
print('FUNCTIONS SETUP')



def build_nnet(input_size_base, rgen):

    input_base = keras.Input(batch_shape=[None,input_size_base],name='base')

    # gen_init = lambda seed : keras.initializers.RandomUniform(-dev,dev,seed)
    gen_init = lambda rgen : \
        keras.initializers.glorot_normal(r.random_seed_from(rgen))

    dense_layer = lambda output_size,rgen,activation: \
        keras.layers.Dense(
            output_size,
            activation=activation,
            # activation=None,
            kernel_initializer = gen_init(rgen),
            bias_initializer = gen_init(rgen),
        )
    custom_tanh = lambda rgen,name=None: \
        nn.GraphicTanh(r.random_seed_from(rgen),name=name)

    layer_base_1 = dense_layer(FIRST_DENSE,rgen,'tanh')(input_base)
    layer_base_2 = dense_layer(FIRST_DENSE,rgen,'tanh')(input_base)

    sin_layer_low = nn.SinLayer(
        seed=r.random_seed_from(rgen),minf=0.3,maxf=1.5
    )(layer_base_1)

    layer_low = nn.CombinatoryMultiplication(n=FIRST_DENSE)(sin_layer_low)

    sin_layer_high = nn.SinLayer(
        seed=r.random_seed_from(rgen),minf=1.5,maxf=3
    )(layer_base_2)

    layer_high = nn.CombinatoryMultiplication(n=FIRST_DENSE)(sin_layer_high)

    layer_add = nn.XYCombinations(
        seed_bias=r.random_seed_from(rgen),
        seed_scale=r.random_seed_from(rgen)
    )(input_base)
    layer_add = custom_tanh(rgen)(layer_add)

    layer_add = dense_layer(16,rgen,None)(layer_add)
    layer_add = custom_tanh(rgen)(layer_add)

    layer = keras.layers.concatenate(
        [sin_layer_low,sin_layer_high,layer_low,layer_high,layer_add])

    outputs = []
    num_outputs = 0
    for t in HIDDEN_STRUCTURE:
        type = t[0]
        is_output = t[1]
        output_size = t[2]

        if type == 'sparse':
            divisions = t[3]
            shuffle = t[4]
            layer = nn.SparseConnections(
                r.random_seed_from(rgen), output_size,divisions,shuffle
            )(layer)
            layer = custom_tanh(rgen)(layer)
            pass
        elif type == 'bottleneck':
            intermediary = t[3]

            layer = dense_layer(intermediary,rgen,None)(layer)
            layer = custom_tanh(rgen)(layer)
            layer = dense_layer(output_size,rgen,None)(layer)
            layer = custom_tanh(rgen)(layer)

        elif type == 'dense':
            layer = dense_layer(output_size,rgen,None)(layer)
            layer = custom_tanh(rgen)(layer)

        if is_output is True:
            name = 'o_' + str(num_outputs)
            output = dense_layer(1,rgen,None)(layer)
            output = custom_tanh(rgen,name=name)(output)

            outputs += [output]
            num_outputs += 1

    return keras.models.Model(
        inputs=input_base,
        outputs=outputs)

def generate_nnet_input(xx, yy, rgen):
    return np.c_[
        yy.flatten(),
        xx.flatten()
    ]


def load_image_data(heigth,width):

    base_image = file.import_image('tulip_high')
    base_image = resize(base_image, (heigth,width,), order=1)
    base_image_blurred = gaussian(base_image,sigma=4)
    # base_image_blurred = gaussian(base_image,sigma=15)
    base_image_tv = denoise_tv_bregman(base_image,weight=10)
    # base_image = gaussian(base_image,sigma=10)

    labels_blurred = base_image_blurred[:,:,0]
    labels_blurred = data.normalize_01(labels_blurred)
    # labels -= 0.5
    m = np.mean(labels_blurred)
    labels_blurred -= np.mean(labels_blurred)

    labels_tv = base_image_tv[:,:,0]
    labels_tv = data.normalize_01(labels_tv)
    labels_tv -= m

    # return labels_blurred.reshape(-1,1),labels_tv.reshape(-1,1)
    # return [labels_tv.reshape(-1,1)]
    return [labels_blurred.reshape(-1,1)]


def train_network(seed):

    r.init_def_generator(seed)
    rgen = r.bind_generator()

    training_width = WIDTH*TRAINING_UPSAMPLE
    training_height = HEIGHT*TRAINING_UPSAMPLE

    labels = load_image_data(training_height,training_width)

    ly1 = np.linspace(-1,1,num=training_height)
    lx1 = np.linspace(-1,1,num=training_width)
    yy1,xx1 = np.meshgrid(ly1,lx1)

    f = generate_nnet_input(xx1, yy1,r.bind_generator_from(rgen))

    input_size_base = f.shape[1]
    model = build_nnet(
        input_size_base=input_size_base,
        rgen=r.bind_generator_from(rgen))

    def scheduler(epoch):
        current_learning_rate = LEARNING_RATE*(0.996**epoch)
        return current_learning_rate

    lr_callback = keras.callbacks.LearningRateScheduler(scheduler)
    tb_callback = keras.callbacks.TensorBoard(
        log_dir=C.PATH_FOLDER_LOGS, histogram_freq=1,
        write_grads=True, write_images=True
    )
    intermediary_progress_callback = nn.SaveIntermediaryResult(
        f = f, image_width=training_width, image_height=training_height)

    log_gradients_callback = nn.LogGradients(C.PATH_FOLDER_LOGS,f,labels)



    def mean_abs_metric(y_true,y_pred):
        return keras.backend.mean(
            keras.backend.abs(2*(y_true-0.25) - 2*(y_pred-0.25)))


    def compile_fit(model):
        optimizer = keras.optimizers.Adam(lr=LEARNING_RATE)
        # optimizer = keras.optimizers.Adamax(lr=LEARNING_RATE)
        model.compile(
            optimizer=optimizer,
            # loss=keras.losses.mean_squared_error,
            loss=keras.losses.mean_absolute_error,
            # metrics = [mean_abs_metric],
            loss_weights = LOSS_WEIGHTS
        )

        print(model.summary())
        model.fit(
            x = f,
            y=labels,
            batch_size=BATCH_SIZE,epochs=NUM_TRAINING_EPOCHS,
            # callbacks=[lr_callback,tb_callback,intermediary_progress_callback],
            callbacks=[lr_callback,tb_callback,log_gradients_callback],
            use_multiprocessing=True)

    compile_fit(model)

    # for l in model.layers:
    #     l.trainable = True
    #
    # compile_fit(model)

    file.save_nnet(model, rgen, prefix=seed)


def generate_image(color_string,seed):

    r.init_def_generator(seed)
    rgen = r.bind_generator()

    training_width = WIDTH*TRAINING_UPSAMPLE
    training_height = HEIGHT*TRAINING_UPSAMPLE
    labels = load_image_data(training_height,training_width)

    model = file.load_nnet(
        rgen,prefix=seed,
        custom_objects=CUSTOM_OBJECTS)

    ly = np.linspace(-1,1,num=HEIGHT)
    lx = np.linspace(-1,1,num=WIDTH)
    yy,xx = np.meshgrid(ly,lx)

    nnet_input = generate_nnet_input(xx, yy,r.bind_generator_from(rgen))

    images_processed = []

    images = model.predict(nnet_input)
    images = [images]

    for image in images:
        image = image.reshape([HEIGHT,WIDTH])
        images_processed += [image]
    for label in labels:
        label = label.reshape([HEIGHT*TRAINING_UPSAMPLE,WIDTH*TRAINING_UPSAMPLE])
        images_processed += [label]

    images_processed += [
        images_processed[0] - images_processed[-1][::TRAINING_UPSAMPLE,::TRAINING_UPSAMPLE]
    ]
    return images_processed

def generate_neuron_images(color_string,seed):

    r.init_def_generator(seed)
    rgen = r.bind_generator()

    model = file.load_nnet(
        rgen,prefix=seed,
        custom_objects=CUSTOM_OBJECTS)
    print(model.summary())

    ly = np.linspace(-1,1,num=HEIGHT)
    lx = np.linspace(-1,1,num=WIDTH)
    yy,xx = np.meshgrid(ly,lx)

    nnet_input = generate_nnet_input(xx, yy,r.bind_generator_from(rgen))

    # layers_of_interest = model.layers[1:-1]
    # print(layers_of_interest)

    layer = model.get_layer(EXPLORE_LAYER)
    print(layer.weights)
    model_inter = keras.models.Model(
        inputs = model.input,
        outputs = layer.output
    )

    activations = model_inter.predict(nnet_input)

    print(activations.shape)
    num_images = activations.shape[1]
    images = []
    for i in range(num_images):
        image = activations[:,i]
        image = image.reshape([HEIGHT,WIDTH])
        # print(np.max(image),np.min(image))
        # image = np.clip(image+0.5,0,1)
        images += [image]

    return images


### GENERATE SECTION
print('GENERATE SECTION')

for current_iteration in range(N):
    print('CURRENT_ITERATION:',current_iteration)

    if START_SERVER is True:
        viz.start_image_server(
            generate_image,
            COLOR_STRING,
            SEED+current_iteration)
        break
    else:

        if TRAIN_NNET is True:
            print('\tTRAINING NNET')
            training_image = train_network(SEED+current_iteration)

        print('\tGENERATING IMAGE')
        # images = generate_neuron_images(COLOR_STRING, SEED + current_iteration)
        images = generate_image(COLOR_STRING, SEED + current_iteration)

        if SAVE_IMAGES is True:
            print('\tSAVING IMAGE')
            file.export_image(
                '%d_%d_%d' % (current_iteration,SEED+current_iteration,int(round(time.time() * 1000))),
                image.astype('uint8'),format='png')
        elif SHOW_IMAGES is True:
            print('\tSHOWING IMAGES')
            viz.show_images_together(images,num_rows=NUM_VIZ_ROWS)


