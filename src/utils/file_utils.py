import constants as C
import imageio
import os.path
import shutil
import time


def load_image(path):
    return imageio.imread(path)

def save_image(path,img,format='jpg',**kwargs):
    imageio.imsave(path+'.'+format,img,format,**kwargs)

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

def get_files(path):
    return [
        f for f in os.listdir(path)
        if os.path.isfile(os.path.join(path, f))
    ]


def create_dir_if_necessary(path):
    if not os.path.exists(path):
        os.mkdir(path)


def move_files_from_to(old_path,new_path,dir_name):
    files = get_files(old_path)
    if len(files) > 0:
        create_dir_if_necessary(os.path.join(new_path,dir_name))
        files_old_path = [ os.path.join(old_path,file) for file in files ]
        files_new_path = [ os.path.join(new_path,dir_name,file) for file in files ]
        [shutil.move(i,j) for i,j in zip(files_old_path,files_new_path)]

def clear_export_dir():
    print('CLEARING EXPORT DIR')
    create_dir_if_necessary(C.PATH_FOLDER_EXPORTS)
    create_dir_if_necessary(C.PATH_FOLDER_DUMP)
    move_files_from_to(
        C.PATH_FOLDER_EXPORTS,
        C.PATH_FOLDER_DUMP,
        str(int(round(time.time() * 1000))))
    print('DONE CLEARING EXPORT DIR')