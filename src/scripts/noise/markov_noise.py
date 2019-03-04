import numpy as np
from collections import namedtuple
from utils.generate_utils import *
from utils.file_utils import *
from utils.data_utils import  *
from properties import *

##########################################################################
### SCRIPT HEADER ########################################################

HEIGHT = 500
WIDTH  = 1000

IMAGE_DEPTH = CHANNELS_GRAY
# CHANNELS_GRAY
# TODO implement CHANNELS_3 image depth
# CHANNELS_3

### NON SCRIPT SPECIFIC OPTIONS ##########################################

# concat the input with the output for comparison purposes
BEFORE_AFTER_COMPARISON = YES

# Name of the export file. By specifying an extension you also specify the format of the export
EXPORT_NAME = '0.png'

### END OF SCRIPT HEADER #################################################
##########################################################################


OFFSET = 0.01


### There differen markov chains working in tandem,
### one if for deciding the length, the other one is for deciding the type


def simulate_markov_chain(transition_matrix, start_probs, length):

    num_elems = len(transition_matrix)
    r = np.arange(num_elems)
    pseudo_simulations = np.zeros((num_elems,length)).astype('int32')

    for i in range(num_elems):
        pseudo_simulations[i] = np.random.choice(r,size=length,p=transition_matrix[i])

    start_elem = np.random.choice(r,p=start_probs)

    simulation = np.zeros(length)
    simulation[0] = start_elem
    current_elem = start_elem

    for i in range(1,length):
        new_elem = pseudo_simulations[current_elem,i]
        simulation[i] = new_elem
        current_elem = new_elem

    return simulation.astype('int32')

def simulate_markov_hierarchy(node):
    simulation = simulate_markov_chain(
        transition_matrix=node.transition_matrix,
        start_probs=node.start_probs,
        length=node.length)
    vals = [node.values[i] for i in simulation]

    if node.leaf == False:
        for n in vals:
            m = simulate_markov_hierarchy(n)
            for i in m:
                yield i
    else:
        yield vals


MarkovModel = namedtuple(
    'MarkovModel',
    ['transition_matrix', 'start_probs','values','length','leaf'])


px_1 = MarkovModel(
    transition_matrix=[[0,1],[1,0]],
    start_probs=[0.5,0.5],
    values=['a','b'],
    leaf=True,
    length=10)

px_2 = MarkovModel(
    transition_matrix=[[0.1,0.9],[0.2,0.8]],
    start_probs=[0.5,0.5],
    values=['c','d'],
    leaf=True,
    length=10)

px_3 = MarkovModel(
    transition_matrix=[[0.1,0.9],[0.2,0.8]],
    start_probs=[0.5,0.5],
    values=['e','f'],
    leaf=True,
    length=10)

px_4 = MarkovModel(
    transition_matrix=[[0.1,0.9],[0.2,0.8]],
    start_probs=[0.5,0.5],
    values=['g','h'],
    leaf=True,
    length=10)

node_1 = MarkovModel(
    transition_matrix=[[0.1,0.9],[0.2,0.8]],
    start_probs=[0.5,0.5],
    values=[px_1,px_2],
    leaf=False,
    length=10)

node_2 = MarkovModel(
    transition_matrix=[[0.1,0.9],[0.2,0.8]],
    start_probs=[0.5,0.5],
    values=[px_3,px_4],
    leaf=False,
    length=10)

parent = MarkovModel(
    transition_matrix=[[0.1,0.9],[0.2,0.8]],
    start_probs=[0.5,0.5],
    values=[node_1,node_2],
    leaf=False,
    length=10)

full_simulation = simulate_markov_hierarchy(parent)
for i in full_simulation:
    print(i)