import numpy as np
import sys
import socket
from PIL import Image
from utils import recv_data


# Define socket communication parameters
# Host is localhost, both simulation and neural network containers run on same machine
HOST = '127.0.0.1'
# The port defined here is used for communication between the 2 containers
PORT = 8080
# Size of images sent by TORCS (RGB images with 640x480 resolution)
image_size = 640*480*3
# Current frame number synchronized with the simulator
frame_number = 0


# Setup TCP socket
try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Connect to server
        s.connect((HOST, PORT))
        print("Welcome!")
        print("Connected to simulator, ready for image extraction.")
        print("Image extraction in progress, to exit simulation press Ctrl-C.")
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

                camera_image.save("/image_extraction/" + str(frame_number) + ".png")
                frame_number += 1

            except KeyboardInterrupt:
                print("\nClosing simulation, goodbye!")
                sys.exit()
except ConnectionRefusedError:
    print("The connection is refused, please start the simulation first!")
    sys.exit()