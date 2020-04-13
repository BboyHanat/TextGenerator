"""
Name : BackgroundImgProvider.py
Author  : Hanat
Time    : 2019-09-19 16:50
Desc:
"""
import os
import cv2
import math
import numpy as np
from utils.random_tools import Random
from PIL import Image


class DirImageGen(object):

    def __init__(self, image_list: list, len_range=(2, 15)):
        """

        :param character_seq:
        :param batch_size:
        """
        self._image_list = image_list
        # random.shuffle(self.character_seq)
        self._len_range = len_range
        self.get_next = self._get_next_image()
        self._imgs_length = len(self._image_list)

    def _get_next_image(self):
        seek = 0
        while True:
            if seek == self._imgs_length:
                seek = 0
            print("test:", self._image_list[seek])
            yield cv2.imread(self._image_list[seek])
            seek += 1


class GenrateGaussImage(object):

    def __init__(self, width_range=(1000, 1500), height_range=(1000, 1500)):
        """

        :param width_range: generate image width size range
        :param height_range: generate image height size range
        """
        self._width_range = width_range
        self._height_range = height_range
        self.get_next = self.get_gauss_image()

    def get_gauss_image(self):
        while True:
            bg = self.apply_gauss_blur()
            yield cv2.cvtColor(bg, cv2.COLOR_GRAY2BGR)

    def apply_gauss_blur(self, ks=None):
        """

        :param ks: guass kernal window size
        :return:
        """
        bg_high = Random.random_float(220, 255)
        bg_low = bg_high - Random.random_float(1, 60)
        width = Random.random_int(self._width_range[0], self._width_range[1])
        height = Random.random_int(self._height_range[0], self._height_range[1])
        img = np.random.randint(bg_low, bg_high, (height, width)).astype(np.uint8)
        if ks is None:
            ks = [7, 9, 11, 13]
        k_size = Random.random_choice_list(ks)
        sigmas = [0, 1, 2, 3, 4, 5, 6, 7]
        sigma = 0
        if k_size <= 3:
            sigma = Random.random_choice_list(sigmas)
        img = cv2.GaussianBlur(img, (k_size, k_size), sigma)
        return img


class GenrateQuasicrystalImage(object):

    def __init__(self, width_range=(1000, 1500), height_range=(1000, 1500)):
        """

        :param width_range: generate image width size range
        :param height_range: generate image height size range
        """
        self._width_range = width_range
        self._height_range = height_range
        self.get_next = self.get_quasicrystal_image()

    def get_quasicrystal_image(self):
        while True:
            bg = self.apply_quasicrystal()
            yield bg

    def apply_quasicrystal(self):
        """
            Create a background with quasicrystal (https://en.wikipedia.org/wiki/Quasicrystal)
        """
        width = Random.random_int(self._width_range[0], self._width_range[1])
        height = Random.random_int(self._height_range[0], self._height_range[1])

        image = np.zeros((height, width, 3), dtype=np.uint8)
        rotation_count = Random.random_int(10, 20)
        y_vec = np.arange(start=0, stop=width, dtype=np.float32)
        x_vec = np.arange(start=0, stop=height, dtype=np.float32)

        grid = np.meshgrid(y_vec, x_vec)
        y_matrix = np.reshape(np.asarray(grid[0]) / (width - 1) * 4 * math.pi - 2 * math.pi, (height, width, 1))
        x_matrix = np.reshape(np.asarray(grid[1]) / (height - 1) * 4 * math.pi - 2 * math.pi, (height, width, 1))
        y_matrix_3d = np.repeat(y_matrix, rotation_count, axis=-1)
        x_matrix_3d = np.repeat(x_matrix, rotation_count, axis=-1)

        rotation_vec = np.arange(start=0, stop=rotation_count, dtype=np.float32)
        rotation_vec = np.reshape(rotation_vec, newshape=(1, 1, rotation_count))

        for k in range(3):
            frequency = Random.random_float(0, 1) * 30 + 20  # frequency
            phase = Random.random_float(0, 1) * 2 * math.pi  # phase

            r = np.hypot(x_matrix_3d, y_matrix_3d)
            a = np.arctan2(y_matrix_3d, x_matrix_3d) + (rotation_vec * math.pi * 2.0 / rotation_count)
            z = np.cos(r * np.sin(a) * frequency + phase)
            z = np.sum(z, axis=-1)

            c = 255 - np.round(255 * z / rotation_count)
            c = np.asarray(c, dtype=np.uint8)
            image[:, :, k] = c

        return image


class BackgroundImgProvider(object):

    def __init__(self, bg_img_conf):
        self.gen = self.get_generator(bg_img_conf)

    def get_generator(self, bg_img_conf):
        """
        generator
        :param bg_img_conf:
        :return:
        """
        gen_probability = []
        all_generator = []
        for item in bg_img_conf:
            t = item['type']
            probability = float(item['probability'])
            if t == 'from_dir':
                bg_img_dir = item['dir']
                img_path_list = [os.path.join(bg_img_dir, img) for img in os.listdir(bg_img_dir) if ('.DS' not in img)]
                dir_img_gen = DirImageGen(img_path_list)
                all_generator.append(dir_img_gen)
            elif t == 'from_generate':
                width_range = eval(item['width_range'])
                height_range = eval(item['height_range'])
                gauss_img_gen = GenrateGaussImage(width_range=width_range, height_range=height_range)
                all_generator.append(gauss_img_gen)
            gen_probability.append(probability)

        value_list = gen_probability
        len_gen = len(all_generator)
        while True:
            index = Random.random_choice(list(value_list))
            if index <= len_gen and all_generator[index]:
                np_img = all_generator[index].get_next.__next__()
                np_img = np_img[..., ::-1]
                img = Image.fromarray(np_img, mode='RGB')
                yield img

    def generator(self):
        return self.gen.__next__()
