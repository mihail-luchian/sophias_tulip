import tensorflow as tf
import numpy as np
from utils.data_utils import *
from utils.file_utils import *


SIZE = 10
N = 25
UPSCALE = 100
NUM_DRIVERS = 2
np.random.seed(1234)
driver = tf.placeholder(dtype=tf.float32,shape=(NUM_DRIVERS,1))

weights = tf.constant(
    np.random.uniform(-1,1,size = (SIZE*SIZE,NUM_DRIVERS)),
    dtype=np.float32,name='weights')
print(weights)
bias = tf.constant(np.random.uniform(-1,1,size=(SIZE*SIZE,1)),dtype=np.float32)

output = tf.sigmoid( weights @ driver + bias)

with tf.Session() as sess:
    animation = np.zeros((N, SIZE*UPSCALE, SIZE*UPSCALE))
    xs = np.linspace(0,1,num = N)

    for i,x in enumerate(xs):
        d = x*2*np.pi

        d = np.cos(d)
        print(d)

        nn_output = sess.run(
            fetches=[output],
            feed_dict={
                # driver: [[np.cos(d)],[np.sin(d)]]
                driver: [[d],[-1*d]]
            }
        )
        nn_output = normalize_01(nn_output[0]).reshape(SIZE, SIZE)
        nn_output = upscale_nearest(nn_output,UPSCALE)
        animation[i] = np.clip(nn_output,0,1)

export_animation('test.gif',animation,loop=10)