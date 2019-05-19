import numpy as np
import os
import sys
import socket
import torch
import torchvision.transforms as transforms
from model.net import Net
from PIL import Image, ImageFile
from utils import recv_data


# Define socket communication parameters
# Host is localhost, both simulation and neural network containers run on same machine
HOST = '127.0.0.1'
# The port defined here is used for communication between the 2 containers
PORT = 8080
# Size of images sent by TORCS (RGB images with 640x480 resolution)
image_size = 640*480*3
# The steering angle calculated by the neural network is written to a file in a shared folder
steering_filename = '/shared_folder/steering.txt'


def steering_to_sim(angle_as_string):
    """
    Write calculated steering angle to a file in a shared folder

    :param angle_as_string: steering angle as string
    """
    f = open(steering_filename, "w")
    f.write(angle_as_string)
    os.chmod(steering_filename, 0o777)


# Initialize neural network and load pretrained weights from file
net = Net()
net.load_state_dict(torch.load('saved_models/trained_on_spring.pt'))


try:
    # Setup TCP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Connect to server
        s.connect((HOST, PORT))
        print("Welcome!")
        print("Connected to simulator, ready for image processing.")
        print("Image processing in progress, to exit simulation press Ctrl-C.")
        # Listen to socket for camera images until keyboard interruption
        while True:
            try:
                # Get camera image from socket in string format
                image_string = recv_data(s, image_size)
                # Convert image string representation to numpy array
                nparr = np.fromstring(image_string, np.uint8)
                # Reshape numpy array from row-vector to 3D array (H x W x C)
                image = nparr.reshape((480, 640, 3))
                # Received image is upside-down, flip it
                image = np.flipud(image)
                # Convert image from numpy array to PILImage
                camera_image = Image.fromarray(image).convert('RGB')

                # Crop, resize and move image to tensor
                cropped_image = transforms.functional.crop(camera_image, 200, 0, 211.2, 640)
                resized_image = transforms.functional.resize(cropped_image, (66, 200))
                camera_image = transforms.ToTensor()(resized_image).view(1, 3, 66, 200)

                # Calculate steering angle by giving camera image to neural network as input
                steering = net(camera_image)
                # Get steering angle from tensor and cut brackets from beginning and end
                steering_string = str(steering.data.tolist()[0])[1:-1]
                # Send steering angle to TORCS
                steering_to_sim(steering_string)
            except KeyboardInterrupt:
                print("\nClosing simulation, goodbye!")
                sys.exit()
except ConnectionRefusedError:
    print("The connection is refused, please start the simulation first!")
    sys.exit()