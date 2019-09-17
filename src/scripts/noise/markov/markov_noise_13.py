print('IMPORTING MODULES')
import time
import constants as c
import script_config as config
import numpy as np
import utils.generate_utils as gen
import random_manager as r
import utils.file_utils as file
import utils.data_utils as data
import utils.markov_utils as m
import utils.color_utils as color
import utils.viz_utils as viz
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter

### DATA/INPUT/SHARED by all runs section
print('PREPARING DATA SECTION')
DUMP_PREVIOUS_EXPORTS = True
SHOW_DEBUG_DATA = False
START_SERVER = False
N = 50
SEED = config.get('seed',296)
HEIGHT = 1000
WIDTH  = 1000

TO_GENERATE = int(HEIGHT * 0.8)
LEFT_OVER = HEIGHT - TO_GENERATE
NUM_REPEATS  = 10
LENGTH_REPEATS = LEFT_OVER // NUM_REPEATS

SEGMENT_LENGTH = 40


UPSCALE_FACTOR_Y = c.INSTA_SIZE // HEIGHT
UPSCALE_FACTOR_X = c.INSTA_SIZE // WIDTH


COLOR_STRING = config.get(
    'color-string',
    'First:0/fff2c9/2-1/f3ff75/3-2/a7fc4b/3-3/a0ffa8/3-4/d6ffdc/2,Second:0/84ffd4/-1/39f9ed/-2/1ddbf4/-3/1168f4/-4/1da4f2/,Third:0/fff2c9/2-1/f3ff75/3-2/a7fc4b/3-3/a0ffa8/3-4/d6ffdc/2')


### SETUP section
print('SETUP SECTION')
if DUMP_PREVIOUS_EXPORTS:
    file.clear_export_folder()


### FUNCTIONS section
print('FUNCTIONS SETUP')

def integrate_and_normalize(series,n):
    series_int = data.integrate_series(series, n, mean_influence=0.9)
    series_int = gaussian_filter(series_int,sigma=2.5)
    series_int = data.concat_signals([series_int, series_int], [1, -1])
    series_int -= np.min(series_int)
    series_int /= np.max(series_int)
    return series_int


def interpolate_colors(color_1,color_2,interpolation_sequence):
    return color_1[:,None]*(1-interpolation_sequence)[None,:] + color_2[:,None]*(interpolation_sequence)[None,:]

def compute_color_lines(color_repo,interpolation_sequence):

    palette_1 = color_repo['First']
    palette_2 = color_repo['Second']
    palette_3 = color_repo['Third']

    dict_1 = color.palette_2_color_dict(palette_1)
    dict_2 = color.palette_2_color_dict(palette_2)
    dict_3 = color.palette_2_color_dict(palette_3)

    color_start_1 = color.srgb_2_cam02(color.hex_2_rgb(dict_1[0]))
    color_start_2 = color.srgb_2_cam02(color.hex_2_rgb(dict_1[1]))
    color_start_3 = color.srgb_2_cam02(color.hex_2_rgb(dict_1[2]))
    color_start_4 = color.srgb_2_cam02(color.hex_2_rgb(dict_1[3]))


    color_middle_1 = color.srgb_2_cam02(color.hex_2_rgb(dict_2[0]))
    color_middle_2 = color.srgb_2_cam02(color.hex_2_rgb(dict_2[1]))
    color_middle_3 = color.srgb_2_cam02(color.hex_2_rgb(dict_2[2]))
    color_middle_4 = color.srgb_2_cam02(color.hex_2_rgb(dict_2[3]))


    color_end_1 = color.srgb_2_cam02(color.hex_2_rgb(dict_3[0]))
    color_end_2 = color.srgb_2_cam02(color.hex_2_rgb(dict_3[1]))
    color_end_3 = color.srgb_2_cam02(color.hex_2_rgb(dict_3[2]))
    color_end_4 = color.srgb_2_cam02(color.hex_2_rgb(dict_3[3]))

    return np.stack((
        data.interpolate([color_start_1,color_middle_1,color_end_1],interpolation_sequence),
        data.interpolate([color_start_2,color_middle_2,color_end_2],interpolation_sequence),
        data.interpolate([color_start_3,color_middle_3,color_end_3],interpolation_sequence),
        data.interpolate([color_start_4,color_middle_4,color_end_4],interpolation_sequence),
    ))


### GENERATE SECTION
print('GENERATE SECTION')

for current_iteration in range(N):
    print('CURRENT_ITERATION:',current_iteration)

    def generate_full_image(color_string,seed):
        r.init_def_generator(seed)

        image = np.zeros((HEIGHT,WIDTH,3))
        plots = []
        loop_key = r.bind_generator()
        setup_key = r.bind_generator()


        p1 = m.MarkovModel(
                values=[0.1,-0.1],
                preference_matrix=data.str2mat('1 5, 5 1'),
                self_length=SEGMENT_LENGTH,
                parent_rkey=r.bind_generator_from(setup_key)

            )

        p2 = m.MarkovModel(
            values=[-0.1, 0.1],
            preference_matrix=data.str2mat('1 5, 5 1'),
            self_length=SEGMENT_LENGTH,
            parent_rkey=r.bind_generator_from(setup_key)

        )

        num_coefs = 12
        vs = np.sin(np.linspace(0, 1, num_coefs) * np.pi * 2) * 0.1
        p3 = m.SimpleProgression(
            values=vs,
            start_probs=0,
            self_length=[num_coefs],
            parent_rkey=r.bind_generator_from(loop_key)
        )

        p = m.MarkovModel(
            values=[p1, p2, p3],
            start_probs=2,
            preference_matrix=data.str2mat(
                '0 1 2, 1 0 2, 1 1 4'),
            self_length=HEIGHT//SEGMENT_LENGTH+1,
            parent_rkey=r.bind_generator_from(setup_key)
        )

        num_samples_1 = HEIGHT//2
        sample_scale_1 = m.sample_markov_hierarchy(p, num_samples_1)
        sample_2 = m.sample_markov_hierarchy(p, num_samples_1)
        sample_3 = m.sample_markov_hierarchy(p, num_samples_1)

        # interpolation_h_1 = integrate_and_normalize(sample_scale_1,2)
        # interpolation_h_2 = integrate_and_normalize(sample_2,2)
        interpolation_color = integrate_and_normalize(sample_3,2)

        color_repo = color.build_color_repository(color_string)
        meta = color.get_meta_from_palette(
            color_repo['First'],
            keys=[0,1,2,3],
            meta_cast_function=int)
        print(meta)
        color_lines = compute_color_lines(color_repo,interpolation_color)
        print(color_lines.shape)

        # plt.plot(interpolation_h_1)
        # plt.plot(interpolation_h_2)
        # plt.plot(interpolation_color)
        # plt.show()


        scale_1_freq = r.choice_from(setup_key,config.get('scale-1-freq-options',[0.025]))
        scale_2_freq = r.choice_from(setup_key,config.get('scale-2-freq-options',[0.02]))
        scale_1_scale = r.choice_from(setup_key,config.get('scale-1-scale-options',[0.02]))
        scale_2_scale = r.choice_from(setup_key,config.get('scale-2-scale-options',[0.02]))
        num_sin_coeffs = r.choice_from(setup_key,config.get('num-sin-coefficients-options',[18]))

        f1_scale = r.choice_from(setup_key,config.get('f1-scale-options',[0.2]))
        f2_scale = r.choice_from(setup_key,config.get('f2-scale-options',[0.4]))
        f3_scale = r.choice_from(setup_key,config.get('f3-scale-options',[0.15]))


        for current_row in range(HEIGHT):

            loop_key = r.reset_key(loop_key)

            # self_length = SEGMENT_LENGTH+int(10*np.sin(np.pi*i*0.01))
            self_length = SEGMENT_LENGTH
            # scale_1 = 0.1 * (1 - interpolation_h_1[current_row]) + 0.15 * interpolation_h_1[current_row]
            scale_1 = 0.1 + scale_1_scale * np.sin(np.pi * current_row * scale_1_freq )
            scale_2 = 0.1 + scale_2_scale * np.sin(np.pi * current_row * scale_2_freq )
            p1 = m.MarkovModel(
                values=[scale_1, -scale_2],
                preference_matrix=data.str2mat('1 5, 5 1'),
                self_length=self_length,
                parent_rkey=r.bind_generator_from(loop_key)

            )

            p2 = m.MarkovModel(
                values=[-scale_1, scale_2],
                preference_matrix=data.str2mat('1 5, 5 1'),
                self_length=self_length,
                parent_rkey=r.bind_generator_from(loop_key)

            )

            zeros = m.MarkovModel(
                values=[0,0],
                preference_matrix=data.str2mat('1 1, 1 1'),
                self_length=self_length*3,
                parent_rkey=r.bind_generator_from(loop_key)

            )

            jumps = m.MarkovModel(
                values=[-0.5, 0.5],
                preference_matrix=data.str2mat('1 1, 1 1'),
                self_length=1,
                parent_rkey=r.bind_generator_from(loop_key)

            )

            num_coefs = num_sin_coeffs
            vs = np.sin(np.linspace(0, 1, num_coefs) * np.pi * 2)*0.1
            p3 = m.SimpleProgression(
                values=vs,
                start_probs=0,
                self_length=[num_coefs],
                parent_rkey=r.bind_generator_from(loop_key)
            )

            p = m.MarkovModel(
                values=[p1, p2, p3, jumps, zeros],
                start_probs=2,
                preference_matrix=data.str2mat(
                    '0 1 2 2 1, 1 0 2 2 1, 1 1 4 2 2, 1 1 2 0 0, 1 1 1 1 2'),
                self_length=WIDTH//SEGMENT_LENGTH+1,
                parent_rkey=r.bind_generator_from(loop_key)
            )

            num_samples_1 = WIDTH//4
            num_samples_2 = WIDTH//3
            sample_x_up = m.sample_markov_hierarchy(p, num_samples_1)
            sample_x_down = m.sample_markov_hierarchy(p, num_samples_2)

            sample_x_up_int = data.integrate_series(sample_x_up,2,mean_influence=1)
            sample_x_down_int = data.integrate_series(sample_x_down,2,mean_influence=1)

            f1 = 0.5 + f1_scale * np.sin(np.pi * current_row * 0.002 )
            f2 = -1 - f2_scale * np.sin(np.pi * current_row * 0.002 )
            f3 = 0.3 + f3_scale * np.sin(np.pi * current_row * 0.001 )

            sample_x_up_int = data.concat_signals(
                [sample_x_up_int]*4,
                [f1,f2,f1,f2])

            sample_x_down_int = data.concat_signals(
                [sample_x_down_int,sample_x_down_int,sample_x_down_int],
                [f3, f1, f3])
            sample_x_down_int = np.r_[sample_x_down_int[0],sample_x_down_int]


            # roll_distance = 500 + int((interpolation_h_2[current_row]-0.5)*250)
            # roll_distance = 500 + int(current_row)
            # print(roll_distance)
            # sample_x_down_int = np.roll(sample_x_down_int, roll_distance)


            sample_x = sample_x_up_int + sample_x_down_int
            interpolation_sequence = sample_x[:HEIGHT]


            interpolation_sequence = gaussian_filter(interpolation_sequence,sigma=1)
            interpolation_sequence -= np.min(interpolation_sequence)
            interpolation_sequence /= np.max(interpolation_sequence)
            # interpolation_sequence = data.ease_inout_sin(interpolation_sequence)
            interpolation_sequence *= 3

            # interpolation_sequence *= 2
            # print(interpolation_sequence)

            gradient = data.interpolate(
                color_lines[:,current_row,:],
                interpolation_sequence,
                value_influences=meta
            )
            gradient = color.cam02_2_srgb(gradient)
            image[current_row] = gradient

            plots += [np.copy(interpolation_sequence)]

        image = data.upscale_nearest(image,ny=UPSCALE_FACTOR_Y,nx=UPSCALE_FACTOR_X)
        image[image<0] = 0
        image[image>255] = 255

        if SHOW_DEBUG_DATA is True:
            viz.animate_plots_y(plots)

        return image

    if START_SERVER is True:
        viz.start_image_server(
            generate_full_image,
            COLOR_STRING,
            SEED+current_iteration)
        break
    else:
        image = generate_full_image(COLOR_STRING,SEED+current_iteration)
        file.export_image(
            '%d_%d_%d' % (current_iteration,SEED+current_iteration,int(round(time.time() * 1000))),
            image.astype('uint8'),format='png')


