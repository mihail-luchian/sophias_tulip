import constants as C
import imageio
import os.path
import shutil
import time
import script_config as config
import random_manager as r
from tensorflow import keras


def load_image(path):
    return imageio.imread(path)

def save_image(path,img,format='jpg',**kwargs):
    imageio.imsave(path+'.'+format,img,format,**kwargs)


def import_image(name):
    files = get_files_in_path(C.PATH_FOLDER_IMPORT)
    for file in files:
        if file.startswith(name):
           return load_image(os.path.join(C.PATH_FOLDER_IMPORT,file))


def export_image(file_name,img,format='jpg',**kwargs):
    save_image(
        os.path.join(C.PATH_FOLDER_EXPORTS,file_name),
        img,
        format,**kwargs)

def export_animation(file_name,animation,loop = 1,fps=25):
    writer = imageio.get_writer(os.path.join(C.PATH_FOLDER_EXPORTS,file_name), fps=fps)
    for cycle in range(loop):
        for i in range(animation.shape[0]):
            writer.append_data(animation[i])
    writer.close()


# simple functions to load images that come with the scripts
def load_tulip():
    return load_image(C.PATH_FILE_TULIP)

def load_tulip_low():
    return load_image(C.PATH_FILE_TULIP_LOW)

def load_keukenhof():
    return load_image(C.PATH_FILE_KEUKENHOF)

def load_keukenhof_low():
    return load_image(C.PATH_FILE_KEUKENHOF_LOW)


def create_dir_if_necessary(path):
    if not os.path.exists(path):
        os.mkdir(path)


def move_files_from_to(old_path,new_path,dir_name):
    files = get_files_in_path(old_path)
    if len(files) > 0:
        create_dir_if_necessary(os.path.join(new_path,dir_name))
        files_old_path = [ os.path.join(old_path,file) for file in files ]
        files_new_path = [ os.path.join(new_path,dir_name,file) for file in files ]
        [shutil.move(i,j) for i,j in zip(files_old_path,files_new_path)]


def check_wip_dirs():
    create_dir_if_necessary(C.PATH_FOLDER_WIP)
    create_dir_if_necessary(C.PATH_FOLDER_EXPORTS)
    create_dir_if_necessary(C.PATH_FOLDER_DUMP)
    create_dir_if_necessary(C.PATH_FOLDER_IMPORT)
    create_dir_if_necessary(C.PATH_FOLDER_LOGS)
    create_dir_if_necessary(C.PATH_FOLDER_NNETS)


def clear_logs_folder():
    clear_contents_in_folder(C.PATH_FOLDER_LOGS)


def clear_contents_in_folder(path):
    files = get_files_in_path(path)
    folders = get_folders_in_path(path)

    for file in files:
        os.remove(os.path.join(path,file))

    for folder in folders:
        shutil.rmtree(os.path.join(path,folder))


def clear_export_folder():
    move_files_from_to(
        C.PATH_FOLDER_EXPORTS,
        C.PATH_FOLDER_DUMP,
        str(int(round(time.time() * 1000))))


def get_files_in_path(path):
    return [
        f for f in os.listdir(path)
        if os.path.isfile(os.path.join(path, f))
    ]


def get_folders_in_path(path):
    return [
        file for file in os.listdir(path)
        if os.path.isdir(os.path.join(path,file))]

def save_nnet(model, rgen, prefix =''):
    path = os.path.join(
        C.PATH_FOLDER_NNETS,generate_net_name(rgen,prefix)+'.h5')
    # print(path)
    model.save(path)

def load_nnet(rgen,prefix,custom_objects=None):
    path = os.path.join(
        C.PATH_FOLDER_NNETS,generate_net_name(rgen,prefix)+'.h5')
    # print(path)
    return keras.models.load_model(path,custom_objects=custom_objects)

def generate_net_name(rgen,prefix):
    submission_num = config.get(C.CONFIG_KEY_SUBMISSION,0)
    base_seed = r.get_start_seed(rgen)
    return f'{prefix}_{submission_num}_{base_seed}'