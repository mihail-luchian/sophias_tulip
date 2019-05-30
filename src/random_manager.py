import numpy as np

ui32 = np.iinfo(np.uint32)
num_generators = 0

# the default generator is there to be used by the script itself
# so that is doesn't have to keep it's own special generator
KEY_DEFAULT_GENERATOR = 0
default_generator = None

dict_generators = {}

# this function must be called first, to properly setup the default random number generator
# if you call the function again, all the previous generators are discarded
def init_def_generator(seed):
    global default_generator
    global num_generators
    dict_generators.clear()
    default_generator = np.random.RandomState(seed)
    dict_generators[KEY_DEFAULT_GENERATOR] = default_generator
    num_generators += 1


def choice(*args,**kwargs):
    # this is done to make one sampling operation independent from others
    # and thus allow for more sophisticated effects like animation
    seed = random_seed(default_generator)
    return np.random.RandomState(seed).choice(*args,**kwargs)

def choice_from(key,*args,**kwargs):
    # this is done to make one sampling operation independent from others
    # and thus allow for more sophisticated effects like animation
    seed = random_seed(dict_generators[key])
    return np.random.RandomState(seed).choice(*args,**kwargs)


def random_seed(generator):
    return generator.randint(0,ui32.max//2)

def bind_generator():
    global num_generators


    seed = random_seed(default_generator)
    generator = np.random.RandomState(seed)

    # print('Binding network with seed:',seed)

    key = num_generators
    dict_generators[key] = generator
    num_generators += 1

    return key