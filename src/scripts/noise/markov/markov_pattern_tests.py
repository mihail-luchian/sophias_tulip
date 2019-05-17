import constants as c
import script_config as config
import numpy as np
import random_manager as r
import utils.file_utils as file
import utils.data_utils as data
import utils.markov_utils as m
import utils.color_utils as color
import utils.viz_utils as viz
import matplotlib.pyplot as plt

r.init_def_generator(10)

# pattern = m.MarkovModel(
#     values = [0,1,2,3,4,5,6,7,8],
#     start_probs=0,
#     preference_matrix=data.str2mat(
#         '0: 1-1 2-1, 1: 3-1 4-1, 2: 5-1 6-1, 3: 7-1, 4: 7-1, 5: 8-1, 6: 8-1, 7: 0-1, 8: 0-1'),
#     self_length=5)
#
#
# parent = m.SProg(values=pattern,self_length=10)
# sample = m.sample_markov_hierarchy(parent,5*10).reshape(10,5)
#
# print(sample)

pattern = m.MarkovModel(
    values=[-1,0,1],
    start_probs=1,
    preference_matrix=data.str2mat('1-1,0-1 1-15 2-1,1-1')
)
sample = m.sample_markov_hierarchy(pattern,1000)
sample = np.cumsum(sample)

plt.plot(sample)
plt.show()
