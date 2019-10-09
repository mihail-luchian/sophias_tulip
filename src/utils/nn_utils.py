import tensorflow as tf
from tensorflow import keras
import random_manager as r
import numpy as np
import utils.data_utils as data
import utils.file_utils as file
import constants as C


def create_variable(shape,name='var',dev=0.01,rgen=None):

    seed = None
    if rgen is not None:
        seed = r.random_seed_from(rgen)
    return tf.Variable(
        tf.random_normal(shape, stddev=dev, seed = seed),
        name=name,dtype=tf.float32)

def create_variable_with_value(value,name='var'):
    return tf.Variable(
        value, name=name,dtype=tf.float32)

def dense_layer(input,size,rgen,activation=None,wdev=0.01,bdev=0.01):

    w = create_variable(
        [input.shape.as_list()[1],size],name='w',dev=wdev,
        rgen=r.bind_generator_from(rgen))
    b = create_variable(
        [size],name='b',dev=bdev,
        rgen=r.bind_generator_from(rgen))

    layer = tf.add(tf.matmul(input, w), b)

    if activation is not None:
        layer = activation(layer)

    return layer


def make_batch_generator(input,labels=None,batch_size=32, rgen=None):
    data_len = input.shape[0]
    indices = np.arange(data_len)
    if rgen is not None:
        r.shuffle_from(rgen,indices)

    num_batches = data_len // batch_size

    def batch_generator():
        for i in range(num_batches):
            samples = indices[i*batch_size:(i+1)*batch_size]
            if labels is None:
                yield input[samples]
            else:
                yield input[samples],labels[samples]

    return batch_generator(),num_batches


#############################################################
# Custom layers
#############################################################

class SinLayer(keras.layers.Layer):

    def __init__(self,seed,minf,maxf, **kwargs):
        self.seed = seed
        self.minf = minf
        self.maxf = maxf
        self.rgen = r.make_generator(seed)
        super(SinLayer, self).__init__(**kwargs)

    def build(self, input_shape):

        rseed = lambda : r.random_seed_from(self.rgen)

        bias_initializer = keras.initializers.RandomUniform(
            minval=-np.pi, maxval=np.pi, seed=rseed())
        scale_initializer = keras.initializers.RandomUniform(
            minval=self.minf, maxval=self.maxf, seed=rseed())

        # Create a trainable weight variable for this layer.
        self.bias = self.add_weight(
            name='bias',
            shape=(input_shape[1],),
            initializer=bias_initializer,
            trainable=True)
        self.scale = self.add_weight(
            name='scale',
            shape=(input_shape[1],),
            initializer=scale_initializer,
            trainable=True)
        super(SinLayer, self).build(input_shape)

    def call(self, x):
        return keras.backend.sin( self.scale * np.pi * x - self.bias)

    def compute_output_shape(self, input_shape):
        return input_shape

    def get_config(self):

        my_config = {
            'seed' : self.seed,
            'minf'  : self.minf,
            'maxf'  : self.maxf
        }
        base_config = super(SinLayer, self).get_config()
        my_config.update(base_config)
        return my_config


class XYCombinations(keras.layers.Layer):

    def __init__(self,seed_bias,seed_scale, **kwargs):
        self.seed_bias = seed_bias
        self.seed_scale = seed_scale
        super(XYCombinations, self).__init__(**kwargs)

    def build(self, input_shape):
        bias_initializer = keras.initializers.RandomUniform(
            minval=-1, maxval=1, seed=self.seed_bias)
        scale_initializer = keras.initializers.RandomUniform(
            minval=-1, maxval=1, seed=self.seed_scale)

        # Create a trainable weight variable for this layer.
        self.bias = self.add_weight(
            name='bias',
            shape=(4,),
            initializer=bias_initializer,
            trainable=True)
        self.scale = self.add_weight(
            name='scale',
            shape=(4,),
            initializer=scale_initializer,
            trainable=True)
        super(XYCombinations, self).build(input_shape)

    def call(self, x):
        xx = tf.gather(x,[0],axis=1)
        yy = tf.gather(x,[1],axis=1)
        combinations = tf.concat([
            xx*yy,
            xx**2,
            yy**2,
            yy**2 * xx**2,
        ], axis = 1)
        return self.scale*combinations - self.bias

    def compute_output_shape(self, input_shape):
        return (input_shape[0],4)

    def get_config(self):

        my_config = {
            'seed_scale' : self.seed_scale,
            'seed_bias'  : self.seed_bias
        }
        base_config = super(XYCombinations, self).get_config()
        my_config.update(base_config)
        return my_config



class SparseConnections(keras.layers.Layer):

    def __init__(self,seed,output_size,divisions,shuffle, **kwargs):
        self.seed = seed
        self.shuffle = shuffle
        self.rgen = r.make_generator(seed)
        self.output_size = output_size
        self.divisions = divisions

        super(SparseConnections, self).__init__(**kwargs)

    def build(self, input_shape):

        if self.shuffle is True:
            input_ranges = r.permutation_from(self.rgen,input_shape[1])
        else:
            input_ranges = np.arange(input_shape[1])

        self.input_ranges = [
            input_ranges[i::self.divisions]
            for i in range(self.divisions)
        ]

        output_ranges = np.arange(self.output_size)
        self.output_ranges = [
            output_ranges[i::self.divisions]
            for i in range(self.divisions)
        ]

        rseed = lambda : r.random_seed_from(self.rgen)

        self.biases = []
        self.kernels = []

        for i in range(len(self.input_ranges)):

            isize = self.input_ranges[i].size
            osize = self.output_ranges[i].size

            bias_initializer = keras.initializers.glorot_uniform(rseed())
            kernel_initializer = keras.initializers.glorot_uniform(rseed())

            # Create a trainable weight variable for this layer.
            self.biases.append(self.add_weight(
                name='bias_' + str(i),
                shape=(osize,),
                initializer=bias_initializer,
                trainable=True))
            self.kernels.append(self.add_weight(
                name='scale_' + str(i),
                shape=(isize,osize),
                initializer=kernel_initializer,
                trainable=True))

        super(SparseConnections, self).build(input_shape)

    def call(self, x):

        tensors = []

        for i in range(len(self.input_ranges)):
            irange = self.input_ranges[i]
            orange = self.output_ranges[i]
            bias = self.biases[i]
            kernel = self.kernels[i]

            xx = tf.gather(x,irange,axis=1)

            output = keras.backend.dot(xx, kernel)
            output = keras.backend.bias_add(output, bias, data_format='channels_last')

            # output = keras.activations.tanh(output)
            # output = custom_tanh(output)

            tensors.append(output)

        return tf.concat(tensors,axis=1)

    def compute_output_shape(self, input_shape):
        return (input_shape[0],self.output_size)

    def get_config(self):

        my_config = {
            'seed' : self.seed,
            'output_size'  : self.output_size,
            'divisions' : self.divisions,
            'shuffle' : self.shuffle
        }
        base_config = super(SparseConnections, self).get_config()
        my_config.update(base_config)
        return my_config



class CombinatoryMultiplication(keras.layers.Layer):

    def __init__(self,n, **kwargs):

        self.n = n
        yy,xx = np.meshgrid(np.arange(n),np.arange(n))
        tril_indices = np.tril_indices(n=n,k=-1)
        self.yy_indices = yy[tril_indices].flatten()
        self.xx_indices = xx[tril_indices].flatten()

        super(CombinatoryMultiplication, self).__init__(**kwargs)

    def build(self, input_shape):
        super(CombinatoryMultiplication, self).build(input_shape)

    def call(self, x):
        return tf.multiply(
            tf.gather(x,self.xx_indices,axis=1),
            tf.gather(x,self.yy_indices,axis=1),
        )

    def compute_output_shape(self, input_shape):
        return (input_shape[0],self.xx_indices.shape[0])

    def get_config(self):

        my_config = {
            'n' : self.n,
        }
        base_config = super(CombinatoryMultiplication, self).get_config()
        my_config.update(base_config)
        return my_config

def custom_tanh(x):
    # return 0.5 * keras.backend.tanh(2*x)*keras.backend.log(2*keras.backend.abs(x)+4)
    return 0.5*keras.backend.tanh(x)*keras.backend.log(keras.backend.abs(x)+10)


class GraphicTanh(keras.layers.Layer):

    def __init__(self,seed, **kwargs):
        self.rgen = r.make_generator(seed)
        self.seed = seed
        super(GraphicTanh, self).__init__(**kwargs)

    def build(self, input_shape):

        rseed = lambda : r.random_seed_from(self.rgen)

        d_initializer = keras.initializers.RandomUniform(
            minval=0.5, maxval=2, seed=rseed())
        b_initializer = keras.initializers.RandomUniform(
            minval=0.5, maxval=3.5, seed=rseed())

        self.d = self.add_weight(
            name='d',
            shape=(1,),
            initializer=d_initializer,
            trainable=True)
        self.b = self.add_weight(
            name='b',
            shape=(1,),
            initializer=b_initializer,
            trainable=True)

        super(GraphicTanh, self).build(input_shape)

    def call(self, x):
        return self.d*(1 - 2 / (keras.backend.exp(self.b*x) + 1))
        # return keras.backend.tanh(x)*(1+0.01*keras.backend.relu(keras.backend.abs(x))**2)
        # return keras.backend.tanh(x)*keras.backend.log(
        #     keras.backend.abs(x)+10)


    def compute_output_shape(self, input_shape):
        return input_shape

    def get_config(self):

        my_config = {
            'seed' : self.seed,
        }
        base_config = super(GraphicTanh, self).get_config()
        my_config.update(base_config)
        return my_config

#############################################################
# Custom callbacks
#############################################################

class SaveIntermediaryResult(keras.callbacks.Callback):

    def __init__(self, f, image_height, image_width):
        self.f = f
        self.image_height = image_height
        self.image_width = image_width
        super(SaveIntermediaryResult, self).__init__()

    def on_batch_end(self, epoch, logs={}):
        image = self.model.predict(self.f)
        image = 255*data.normalize_01(image.reshape(self.image_height, self.image_width))
        file.export_image(
            '%d' % (epoch), image.astype('uint8'),format='jpg')


class LogGradients(keras.callbacks.Callback):

    def __init__(self,logdir,inputs,outputs):
        self.file_writer = tf.summary.create_file_writer(logdir)
        self.inputs = inputs
        self.outputs = outputs
        super(LogGradients, self).__init__()


    def set_model(self, model):
        self.model = model
        self.grads = self.model.optimizer.get_gradients(
            self.model.total_loss, self.model.trainable_weights)
        self.f = keras.backend.function(
            [self.model._feed_inputs,self.model._feed_targets], self.grads)

    def on_epoch_end(self,epoch,logs={}):


        output_grad = self.f([self.inputs,self.outputs])
        # print(output_grad)

        # for layer in self.model.layers:
        #     for weight in layer.trainable_weights:
        #         mapped_weight_name = weight.name.replace(':', '_')
        #         grads = self.model.optimizer.get_gradients(
        #             self.model.total_loss, weight)
        #
        #         def is_indexed_slices(grad):
        #             return type(grad).__name__ == 'IndexedSlices'
        #
        #         grads = [
        #             grad.values if is_indexed_slices(grad) else grad
        #             for grad in grads]
        #
        #         print(grads)
                # with self.file_writer.as_default():
                #     print(mapped_weight_name)
                #     print(grads)
                #     tf.summary.histogram(
                #         mapped_weight_name, np.arange(10),step=epoch)

                    # grads = [
                    #     grad.values if is_indexed_slices(grad) else grad
                    #     for grad in grads]
        #

        # print()
        # print(self.model.updates)
