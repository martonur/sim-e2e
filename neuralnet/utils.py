import json
import matplotlib.pyplot as plt
import numpy as np
import socket
import torch
from PIL import Image
from torchvision import transforms, utils


def plot_image(img):
    """
    Plot image for checking purposes
    :param img: flattened numpy array (1,200*66*3)
    """
    plt.figure(figsize=(1.5, 1.5))
    plt.imshow(img.reshape(66, 200, 3))
    plt.show()
    plt.close()


def recv_data(socket, buffer_size):
    """
    Collect connected packages and interlink them

    Needed for TCP socket communication because images can arrive in multiple packages
    :param socket: TCP client socket where we receive the packages
    :param buffer_size: Size of the whole string we are waiting for, e.g. image size here
    :return: Whole string, e.g. image data in our case
    """
    data = b''
    while len(data) < buffer_size:
        packet = socket.recv(buffer_size - len(data))
        if not packet:
            break
        data += packet
    return data


class Crop(object):
    """
    Crop the region of interest from camera image
    """
    def __init__(self):
        pass

    def __call__(self, sample):
        """
        :param sample: training data representation including camera image and steering angle
        :return: the same structure with cropped image
        """
        image = sample['image']
        steering = sample['steering']
        cropped_image = transforms.functional.crop(image, 200, 0, 211.2, 640)
        return {'image': cropped_image, 'steering': steering}


class Resize(object):
    """
    Resize the camera image to fit neural network as input
    """
    def __init__(self):
        pass

    def __call__(self, sample):
        """
        :param sample: training data representation including camera image and steering angle
        :return: the same structure with cropped image
        """
        image = sample['image']
        steering = sample['steering']
        resized_image = transforms.functional.resize(image, (66, 200))
        return {'image': resized_image, 'steering': steering}


class Standardize(object):
    """
    Standardize the camera image for better generalisation of the network
    """
    def __init__(self, mean, std):
        """
        :param mean: mean of each pixel on various maps from TORCS (1, 66*200*3) numpy array
        :param std: standard deviation of each pixel on various maps from TORCS (1, 66*200*3) numpy array
        """
        self.image_mean = mean
        self.image_std = std

    def __call__(self, sample):
        """
        :param sample: training data representation including camera image and steering angle
        :return: the same structure with cropped image
        """
        image = sample['image']
        steering = sample['steering']
        image = np.asarray(image).reshape([1, -1])
        image = image / 255
        image = (image - self.image_mean) / self.image_std
        image = image.reshape(66,200,3)
        image = Image.fromarray(np.uint8(image.reshape(66, 200, 3)*255))
        return {'image': image, 'steering': steering}


class ToTensor(object):
    def __call__(self, sample):
        """
        Moves training data (image, steering) to PyTorch tensors - it's the input of the network
        :param sample: training data representation including camera image and steering angle
        :return: the same structure represented as tensors
        """
        image, steering = sample['image'], sample['steering']
        return {'image': transforms.ToTensor()(image),
                'steering': torch.tensor(steering, dtype=torch.float32)}


class Parameters():
    """
    Class that loads hyperparameters from a json file.
    Example:
    ```
    params = Parameters(json_path)
    print(params.batch_size)
    params.batch_size = 128
    ```
    """

    def __init__(self, json_path):
        with open(json_path) as f:
            params = json.load(f)
            self.__dict__.update(params)

    def update(self, json_path):
        """Loads parameters from json file"""
        with open(json_path) as f:
            params = json.load(f)
            self.__dict__.update(params)
