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

### DATA/INPUT/SHARED by all runs section
print('PREPARING DATA SECTION')
DUMP_PREVIOUS_EXPORTS = True
START_SERVER = False
N = 10
SEED = config.get('seed',296)
HEIGHT = 500
WIDTH  = 500
SEGMENT_LENGTH = 40

UPSCALE_FACTOR_Y = c.INSTA_SIZE // HEIGHT
UPSCALE_FACTOR_X = c.INSTA_SIZE // WIDTH


COLOR_STRING = config.get(
    'color-string',
    'First:0/2bff4b/-1/00ffe1/-2/00618e/-3/bc09b6/,Second:0/ff7b60/-1/ffe175/-2/f6ffa5/-3/ff002e/')


### SETUP section
print('SETUP SECTION')
if DUMP_PREVIOUS_EXPORTS:
    file.clear_export_dir()


### FUNCTIONS section
print('FUNCTIONS SETUP')

def integrate_and_normalize(series,n):
    series_int = data.integrate_series(series, n, mean_influence=0.75)
    series_int -= np.min(series_int)
    series_int /= np.max(series_int)
    return series_int


def interpolate_colors(color_1,color_2,interpolation_sequence):
    return color_1[None,:]*(1-interpolation_sequence)[:,None] + color_2[None,:]*(interpolation_sequence)[:,None]

def compute_color_lines(color_string,interpolation_sequence):

    color_repo = color.build_color_repository(color_string)

    palette_1 = color_repo['First']
    palette_2 = color_repo['Second']

    dict_1 = color.palette_2_color_dict(palette_1)
    dict_2 = color.palette_2_color_dict(palette_2)

    color_start_1 = color.srgb_2_cam02(color.hex_2_rgb(dict_1[0]))
    color_start_2 = color.srgb_2_cam02(color.hex_2_rgb(dict_1[1]))
    color_start_3 = color.srgb_2_cam02(color.hex_2_rgb(dict_1[2]))
    color_start_4 = color.srgb_2_cam02(color.hex_2_rgb(dict_1[3]))


    color_end_1 = color.srgb_2_cam02(color.hex_2_rgb(dict_2[0]))
    color_end_2 = color.srgb_2_cam02(color.hex_2_rgb(dict_2[1]))
    color_end_3 = color.srgb_2_cam02(color.hex_2_rgb(dict_2[2]))
    color_end_4 = color.srgb_2_cam02(color.hex_2_rgb(dict_2[3]))


    return np.stack((
        interpolate_colors(color_start_1,color_end_1,interpolation_sequence),
        interpolate_colors(color_start_2,color_end_2,interpolation_sequence),
        interpolate_colors(color_start_3,color_end_3,interpolation_sequence),
        interpolate_colors(color_start_4,color_end_4,interpolation_sequence),
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

        p3 = m.SimpleProgression(
            values=[-0.1, -0.05, 0, 0.05, 0.1, 0, 0.05, 0.1, 0, -0.1, -0.05, 0],
            start_probs=[0,6],
            self_length=[12,24],
            parent_rkey=r.bind_generator_from(setup_key)
        )

        p = m.MarkovModel(
            values=[p1, p2, p3],
            start_probs=2,
            preference_matrix=data.str2mat(
                '0 1 2, 1 0 2, 1 1 4'),
            self_length=HEIGHT//SEGMENT_LENGTH+1,
            parent_rkey=r.bind_generator_from(setup_key)
        )

        num_samples = HEIGHT
        sample_scale_1 = m.sample_markov_hierarchy(p, HEIGHT)
        sample_2 = m.sample_markov_hierarchy(p, HEIGHT)
        sample_3 = m.sample_markov_hierarchy(p, HEIGHT)

        interpolation_h_1 = integrate_and_normalize(sample_scale_1,3)
        interpolation_h_2 = integrate_and_normalize(sample_2,2)
        interpolation_color = integrate_and_normalize(sample_3,2)


        color_lines = compute_color_lines(color_string,interpolation_color)
        print(color_lines.shape)
        # plt.plot(interpolation_color)
        # plt.plot(interpolation_h_2)
        # plt.show()

        for current_row in range(HEIGHT):

            loop_key = r.reset_key(loop_key)

            # self_length = SEGMENT_LENGTH+int(10*np.sin(np.pi*i*0.01))
            self_length = SEGMENT_LENGTH
            scale_1 = 0.1 * (1 - interpolation_h_1[current_row]) + 0.15 * interpolation_h_1[current_row]
            # scale_2 = 0.1 * (1 - interpolation_h_2[i]) + 0.15 * interpolation_h_2[i]
            # scale_1 = 0.1 + 0.05*np.sin(np.pi*i*0.01)
            scale_2 = 0.1 + 0.02 * np.sin(
                np.pi * current_row * 0.0001 + (np.pi + np.pi * current_row) * 0.015)
            # print(self_length)
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

            t1 = 0.05
            t2 = 0.1
            num_coefs = 18
            vs = np.sin(np.linspace(0, 1, num_coefs) * np.pi * 2)
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
                    '0 1 1, 1 0 1, 1 1 1'),
                self_length=WIDTH//SEGMENT_LENGTH+1,
                parent_rkey=r.bind_generator_from(loop_key)
            )

            num_samples = WIDTH
            sample_x_up = m.sample_markov_hierarchy(p, num_samples)
            # sample_x_down = m.sample_markov_hierarchy(p, num_samples*2)

            sample_x_up += (current_row / HEIGHT + 0.5) * 0.5 * np.roll(
                # sample_x_up, 250 + int(np.sin((current_row/300)**2)*30))
                sample_x_up, 250 + int((interpolation_h_2[current_row]-0.5)*60))

            sample_x_up_int = data.integrate_series(sample_x_up,2,mean_influence=1)
            interpolation = np.linspace(0, 1, WIDTH)
            sample_x_up_int = (
                    sample_x_up_int * (1 - interpolation)
                    +
                    (1 - sample_x_up_int) * interpolation
            )

            # sample_x_down_int = data.integrate_series(sample_x_down,2,mean_influence=1)
            # sample_x_down_int = -sample_x_down_int + sample_x_up_int[-1]

            # sample_x = np.concatenate((sample_x_up_int,sample_x_down_int))
            # sample_x = sample_x-sample_x[0]
            # sample_x /= np.max(np.abs(sample_x))
            #
            # mask = np.logical_and(sample_x < 0.01,sample_x > -0.01)
            # arg_0 = WIDTH + np.argmax(mask[WIDTH+1:])
            # sample_x = sample_x[:arg_0]

            sample_x = sample_x_up_int
            interpolation_sequence = sample_x[:WIDTH]

            interpolation_sequence -= np.min(interpolation_sequence)
            interpolation_sequence /= np.max(interpolation_sequence)
            # interpolation_sequence = data.ease_inout_sin(interpolation_sequence)
            interpolation_sequence *= 3

            # interpolation_sequence *= 2
            # print(interpolation_sequence)

            color_1 = color_lines[0, current_row]
            color_2 = color_lines[1, current_row]
            color_3 = color_lines[2, current_row]
            color_4 = color_lines[3, current_row]

            gradient_1 = color_1[None,:]*(1-interpolation_sequence)[:,None] + color_2[None,:]*interpolation_sequence[:,None]
            gradient_2 = color_2[None,:]*(1-interpolation_sequence+1)[:,None] + color_3[None,:]*(interpolation_sequence-1)[:,None]
            gradient_3 = color_3[None,:]*(2-interpolation_sequence+1)[:,None] + color_4[None,:]*(interpolation_sequence-2)[:,None]

            mask_1 = np.logical_and(interpolation_sequence>=0,interpolation_sequence<=1)[:,None]
            mask_2 = np.logical_and(interpolation_sequence>=1,interpolation_sequence<=2)[:,None]
            mask_3 = np.logical_and(interpolation_sequence>=2,interpolation_sequence<=3)[:,None]

            gradient = gradient_1*mask_1 + gradient_2*mask_2 + gradient_3*mask_3
            gradient = gradient[None,:,:]

            gradient = color.cam02_2_srgb(gradient)
            image[current_row] = gradient

            plots += [np.copy(interpolation_sequence)]

        image = data.upscale_nearest(image,ny=UPSCALE_FACTOR_Y,nx=UPSCALE_FACTOR_X)
        image[image<0] = 0
        image[image>255] = 255

        num_imgs = 0
        t = []
        # viz.animate_plots_y(plots)
        # for p in plots:
        #     t += [p]
        #     num_imgs += 1
        #     if num_imgs > 100:
        #         num_imgs = 0
        #         viz.animate_plots(t)
        #         t = []

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

    # viz.animate_plots(plots,interval=100)

