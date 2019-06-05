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

for i in range(1):
    r.init_def_generator(181)

    factor_1 = np.sin(np.pi*2*i/100)*0.2
    factor_2 = np.sin(np.pi*2*i/250)*0.2
    self_length_1 = [10]
    self_length_2 = [10]

    p1 = m.MarkovModel(
        values = [-0.01,-0.01],
        preference_matrix=data.str2mat('1 1, 1 1'),
        self_length=self_length_1
    )

    p2 = m.MarkovModel(
        values = [-0.02,-0.02],
        preference_matrix=data.str2mat('1 1, 1 1'),
        self_length = self_length_1
    )

    p3 = m.MarkovModel(
        values = [0.01,0.01],
        preference_matrix=data.str2mat('1 1, 1 1'),
        self_length=self_length_1
    )

    p4 = m.MarkovModel(
        values = [0.02,0.02],
        preference_matrix=data.str2mat('1 1, 1 1'),
        self_length=self_length_1
    )

    p5 = m.SimpleProgression(
        values = [-0.02,-0.01,0,0.01,0.02,0.02,0.01,0,-0.01,-0.02],self_length=self_length_2)

    p = m.MarkovModel(
        values=[p1,p2,p3,p4,p5],
        preference_matrix=data.str2mat(
            ' 1 0 1 0 1, 0 0 0 0 1, 1 0 1 0 1, 0 0 0 0 1 ,1 1 1 1 1 '),
        )

    num_samples = 1000
    sample_x = m.sample_markov_hierarchy(p, num_samples)
    sample_x_1 = np.cumsum(sample_x)
    sample_x_2 = np.cumsum(sample_x_1)
    sample_x_2 /= np.max(np.abs(sample_x_2))

    plt.plot(sample_x_2 + i * 0.05,label=str(i), c='b', alpha=0.1)

# plt.legend()
plt.show()
