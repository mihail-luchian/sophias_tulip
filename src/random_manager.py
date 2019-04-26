import numpy as np

ui32 = np.iinfo(np.uint32)
num_generators = 0

# the default generator is there to be used by the script itself
# so that is doesn't have to keep it's own special generator
KEY_DEFAULT_GENERATOR = 0
default_generator = None

dict_generators = {}

# this function must be called first, to properly setup the default random number generator
def init_def_generator(seed):
    global default_generator
    default_generator = np.random.RandomState(seed)
    dict_generators[KEY_DEFAULT_GENERATOR] = default_generator
    num_generators += 1


def choice(*args,**kwargs):
    return default_generator.choice(*args,**kwargs)

def choice_from(key,*args,**kwargs):
    return dict_generators[key].choice(*args,**kwargs)

def bind_generator():
    global num_generators

    seed = default_generator.randint(0,ui32.max)
    generator = np.random.RandomState(seed)

    key = num_generators
    dict_generators[key] = generator
    num_generators += 1

    return key