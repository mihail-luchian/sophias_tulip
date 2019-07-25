import numpy as np
import constants as c
import random_manager as r
from utils.data_type_utils import *

def markov_model_is_leaf(values):
    # we examine two cases:
    # the values might be just a list, then we look only at the first element
    # the values is a list of list and then we have to look at the first element of the first list

    if is_listy(values[0]) and hasattr(values[0][0],'type'):
        return False
    elif hasattr(values[0],'type'):
        return False
    else:
        return True


def simulate_markov_chain(node,length,rkey):
    if node.update_step is None or node.update_fun is None:
        sample = simulate_markov_chain_without_update(
            transition_matrix=node.transition_matrix,
            start_probs=node.start_probs,
            length=length,
            rkey=rkey)
    else:
        sample = simulate_markov_chain_with_update(node,length)

    return sample

def simulate_markov_chain_without_update(
        transition_matrix, start_probs, length, rkey):

    num_elems = len(transition_matrix)
    element_range = np.arange(num_elems)
    pseudo_simulations = np.zeros((num_elems,length)).astype('int32')

    for i in range(num_elems):
        s = r.choice_from(rkey, element_range, size=length, p=transition_matrix[i])
        pseudo_simulations[i] = s

    start_elem = r.choice_from(rkey, element_range, p=start_probs)

    simulation = np.zeros(length)
    simulation[0] = start_elem
    current_elem = start_elem

    for i in range(1,length):
        new_elem = pseudo_simulations[current_elem,i]
        simulation[i] = new_elem
        current_elem = new_elem

    return simulation.astype('int32')



def simulate_markov_chain_with_update(node, length):

    ## THIS FUNCTION NEEDS TO BE REWRITTEN


    current_length = 0
    first_step = node.update_step - node.simulated_length % node.update_step
    simulations = []
    while current_length < length:
        sim_length = node.update_step if current_length > 0 else first_step
        current_length += sim_length

        simulations += [ simulate_markov_chain_without_update(
            node.transition_matrix,node.start_probs,sim_length,node.random_key) ]

        update_node(node)

    simulation = np.concatenate(simulations)[:length]
    node.simulated_length += length
    return simulation


def update_node(node):
    new_preference_matrix, new_start_probs = node.update_fun(
        node.preference_matrix, node.start_probs)

    node.preference_matrix = new_preference_matrix
    node.transition_matrix = compute_transition_matrix(node.preference_matrix)
    node.start_probs = new_start_probs / np.sum(new_start_probs)


def simulate_markov_generator(node, length=None, rkey=None):

    breakout = False
    iteration = 0
    # if length is None, this means we are simulating the parent
    # if length is -1, this means no length for the children has been specified
    #   and in this case we use the self_length
    sim_length = 10 if length is None else length
    if sim_length == -1:
        sim_length = r.choice_from(rkey,node.self_length)
    while breakout == False:

        loop_key = r.bind_generator_from(rkey)

        simulation = r.call_and_bind_from(
            loop_key,simulate_markov_chain,
            node=node,length=sim_length)

        if node.lengths is not None:
            if len(node.lengths) == 1:
                repeats = [ node.lengths[0] for _ in simulation  ]
            else:
                repeats = [ node.lengths[s] for s in simulation  ]
            simulation = np.repeat(simulation,repeats)
        vals = [node.values[i] for i in simulation]
        if node.post_process is not None:
            vals = node.post_process(vals)

        if node.leaf is False:
            child_lens = r.choice_from(loop_key,node.child_lengths,sim_length)
            for j,(n,l) in enumerate(zip(vals,child_lens)):
                m = simulate_markov_hierarchy(n,l)
                for i in m:
                    yield i
        else:

            yield np.array(vals)

        iteration += 1
        if length is not None:
            breakout = True


def simulate_markov_processor(node,length):
    m = simulate_markov_hierarchy(node.node,length)
    ms = []
    for i in m:
        ms += [i]

    vals = np.concatenate(ms)

    if node.pre_process is not None:
        vals = node.pre_process(vals)

    total_size = vals.size
    limit = None
    if node.length_limit is not None:
        limit = r.choice_from(node.random_key,node.length_limit)
    if limit is not None and total_size >= limit:
        vals = vals[:limit]

    reps = None
    if node.num_tiles is not None:
        reps = r.choice_from(node.random_key,node.num_tiles)
    if reps is not None:
        vals = np.tile(vals, reps)

    if node.post_process is not None:
        vals = node.post_process(vals)

    yield vals


def simulate_markov_hierarchy(node,length=None):
    if node.type == c.TYPE_GEN:
        sim = r.call_and_bind_from(
            node.random_key,simulate_markov_generator,
            node,length)
    elif node.type == c.TYPE_PROC:
        sim = simulate_markov_processor(node,length)
    for i in sim:
        yield i

def sample_markov_hierarchy(markov_tree,sample_size):

    # print('Start sampling')
    # this is the generator for the markov_tree
    full_simulation = simulate_markov_hierarchy(markov_tree)

    current = 0
    sample = np.zeros(sample_size)
    # we sample from the generator, taking care we sample only as much as required
    for i in full_simulation:
        # print('full simulation',i)
        l = i.size
        start = current
        end = start + l
        sampled_end = l
        if end >= sample_size:
            # print(sample)
            # print('last sample')
            end = sample_size
            # print(end,sample_size)
            sampled_end = end - start

        sample[start:end] = i[:sampled_end]
        current = end
        if current >= sample_size:
            break

    return sample


def sample_markov_hierarchy_with_cumsum_limit(markov_tree, limit):

    # this is the generator for the markov_tree
    full_simulation = simulate_markov_hierarchy(markov_tree)

    sum = 0
    list_samples = []
    # we sample from the generator, until we reach the desired value
    # at the end, this value is appended to the sample
    for sample in full_simulation:
        sample_sum = np.sum(sample)
        if sum+sample_sum < limit:
            list_samples.append(sample)
            sum += sample_sum
        else:
            left = limit - sum
            sample_cum = np.cumsum(sample)
            usable_sample = sample[sample_cum<left]
            list_samples.append(usable_sample)

            # appending what remains
            sum += np.sum(usable_sample)
            list_samples.append(np.array([limit - sum]))
            break

    sample = np.concatenate(list_samples)
    return sample


def generate_grid_lines( parent,limit):
    grid = sample_markov_hierarchy_with_cumsum_limit(
        parent, limit=limit).astype('int32')
    grid = np.cumsum(grid)
    grid = grid[grid < limit]

    return grid



def paint_linearly_markov_hierarchy_with_grid(markov_tree,gridy,gridx):
    height = gridy[-1]
    width = gridx[-1]

    sample = sample_markov_hierarchy(markov_tree,height*width)
    img = np.zeros((height, width))

    startx = 0
    starty = 0
    sample_index = 0
    for y in np.append(gridy, height):
        endy = y
        for x in np.append(gridx, width):
            endx = x
            gridsize = (endx-startx)*(endy-starty)
            img[starty:endy, startx:endx] = sample[sample_index,sample_index+gridsize]

            sample_index += gridsize
            startx = endx

        startx = 0
        starty = endy

    return img


def paint_linearly_markov_hierarchy(
        markov_tree,
        height, width,
        tile_height = None,
        tile_width = None):

    sample_size = height*width;
    img = sample_markov_hierarchy(markov_tree,sample_size)

    if tile_height is not None and tile_width is not None:
        img = img.reshape((-1,tile_width))
        new_img = np.zeros((height,width),dtype=img.dtype)
        num_tiles_h = height//tile_height
        num_tiles_w = width//tile_width
        for i in range(num_tiles_h):
            for j in range(num_tiles_w):
                start_h = i*tile_height
                start_w = j*tile_width
                s = np.s_[start_h:start_h+tile_height,start_w:start_w+tile_width]

                idx = (i*num_tiles_w + j)*tile_height
                new_img[s] = img[idx:idx+tile_height,:]

        return new_img
    else:
        return img.reshape((height,width))


def compute_transition_matrix(preference_matrix):
    sums = np.sum(preference_matrix, axis=1)
    transition_matrix = np.zeros_like(preference_matrix)
    mask = sums != 0
    transition_matrix[mask] = preference_matrix[mask]/sums[mask][:,None]
    return transition_matrix

class MarkovModel:

    def __init__(self,
                 preference_matrix=None,
                 start_probs=None,
                 no_start = None,
                 values=None,
                 vs=None,
                 child_lengths=-1,
                 lenghts=None,
                 self_length=None,
                 update_step=None,
                 update_fun=None,
                 parent_rkey=None,
                 post_process=None):


        ## checking all the received inputs
        if vs is not None and values is not None:
            raise Exception('You have to use either "v" or "values" to pass values. Both is not possible')

        if values is None and vs is not None:
            values = vs

        ## initializing everything
        l = len(values)
        self.values = listify(values)

        # child_lengths is one way one can deduce if is leaf node or not
        self.child_lengths = array_listify(child_lengths)
        self.lengths = array_listify_if_not_none(lenghts)
        self.self_length = array_listify_if_not_none(self_length)
        self.type = c.TYPE_GEN

        # computing the start probabilities
        if start_probs is None:
            start_prefs = np.ones(l)
        elif is_listy(start_probs) and len(start_probs) == l:
            start_prefs = start_probs
        else:
            start_prefs = np.zeros(l)
            start_probs = listify(start_probs)
            start_prefs[start_probs] = 1

        # no start is a way to specify that you do not want the model to start in a certain state
        if no_start is not None:
            no_start = listify(no_start)
            start_prefs[no_start] = 0
        self.start_probs = start_prefs / np.sum(start_prefs)

        self.leaf = markov_model_is_leaf(values)
        self.preference_matrix = np.array(preference_matrix)
        self.transition_matrix = compute_transition_matrix(self.preference_matrix)

        self.update_step = update_step
        self.update_fun = update_fun
        self.simulated_length = 0

        self.post_process = post_process

        #setup the random number generator if it wasn't already setup by someone else
        if not hasattr(self,'random_key'):
            if parent_rkey is not None:
                self.random_key = r.bind_generator_from(parent_rkey)
            else:
                self.random_key = r.bind_generator()



class SimpleProgression(MarkovModel):

    def __init__(self, values = None,**kwargs):

        values = listify(values)
        l = len(values)
        preference_matrix = np.eye(l)
        preference_matrix = np.roll(preference_matrix,1,axis=1)

        super().__init__(
            preference_matrix=preference_matrix,
            values=values,
            **kwargs)


class SimplePattern(SimpleProgression):

    def __init__(self,
                 pattern = None,
                 candidates = None,
                 **kwargs):

        # example of pattern 001100111101234321


        int_pattern = [c.PATTERN_STR_INDICES[i] for i in pattern]
        values = [ candidates[i] for i in int_pattern ]
        super().__init__(
            values=values,
            **kwargs)


class FuzzyProgression(MarkovModel):
    def __init__(self,
                 values = None,
                 positive_shifts = 1,
                 negative_shifts = 0,
                 repeat_factor = 1,
                 **kwargs):

        l = len(values)

        base = np.eye(l)
        preference_matrix = base*repeat_factor
        for i in range(positive_shifts):
            preference_matrix += np.roll(base,i+1,axis=1)
        for i in range(negative_shifts):
            preference_matrix += np.roll(base,-(i+1),axis=1)

        super().__init__(
            preference_matrix=preference_matrix,
            values=values,
            **kwargs)


class RandomMarkovModel(MarkovModel):

    def __init__(
            self,
            values=None,
            num_sinks = None,
            sinks = None,
            reduce_sinks = None,
            parent_rkey = None,
            **kwargs):

        if num_sinks is not None and sinks is not None:
            raise Exception('You have to use either "num_sinks" or "sinks" to pass values. Both is not possible')


        if parent_rkey is not None:
            self.random_key = r.bind_generator_from(parent_rkey)
        else:
            self.random_key = r.bind_generator()

        values = listify(values)
        l = len(values)
        preference_matrix = r.choice_from(
            self.random_key,np.arange(100),size=(l,l)).astype('float32')

        if num_sinks is not None:
            sinks = r.choice_from(self.random_key,np.arange(l),replace=False)
        sinks = listify(sinks)
        for s in sinks:
            arr = np.zeros(l)
            arr[s] = 1
            preference_matrix[s] = arr

        if reduce_sinks is not None:
            for s in sinks:
                preference_matrix[:,s] = preference_matrix[:,s]/reduce_sinks

        super().__init__(
            preference_matrix=preference_matrix,
            values=values,
            **kwargs)


class Processor:
    def __init__(self, node, num_tiles=None, length_limit=None,parent_rkey=None, pre_process=None, post_process=None):
        self.node = node

        self.num_tiles = listify_if_not_none(num_tiles)
        self.length_limit = listify_if_not_none(length_limit)
        self.type = c.TYPE_PROC

        self.pre_process = pre_process
        self.post_process = post_process

        if parent_rkey is not None:
            self.random_key = r.bind_generator_from(parent_rkey)
        else:
            self.random_key = r.bind_generator()


#### SHORTCUTS
Proc = Processor
MM = MarkovModel
RMM = RandomMarkovModel
SPat = SimplePattern
SProg = SimpleProgression
