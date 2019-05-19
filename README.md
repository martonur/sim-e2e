# Welcome!

I'm Marton Szilagyi and this is my bachelor's thesis with the following title: 

### **Controlling intelligent simulation with artificial neural network**.

##### _Note that this is not the official documentation, just some info and guideline to the program._

The 2 main functions are:
* Extracting training data including first person camera image and driving commands
* Training neural networks on the saved training data and evaluating it with real-time inference

I used separate Docker environments for neural network and simulation development for
better reproducibility and isolation.

I chose TORCS (The Open Racing Car Simulator) as the simulation environment because it's
open-source, easy to modify (written in C++) and relatively lightweight.

The neural network is built with the PyTorch framework.

## Installation and testing real-time inference
I used Ubuntu 18.04 on a PC with i5-4590, GTX750 Ti 2GB and 8Gb RAM as development environment but also
tested it on Ubuntu 16.04.

1. If you have an Nvidia GPU make sure to have up-to-date drivers (396 or 410) and also nvidia docker 2.
 
    Instructions: `https://github.com/nvidia/nvidia-docker/wiki/Installation-(version-2.0)`.
    
    _Don't forget to install the repository before installing the package!_
        
    It's recommended to add nvidia as default docker runtime: 
    
    in `/etc/docker/daemon.json` set `"default-runtime": "nvidia"` and reload Docker daemon with
    `systemctl reload docker`

2. Run `setup.sh`, it will pull the 2 docker images. (needs ~11GB free space)

3. Run `xhost+` to expose the display to docker containers.

4. You will need more Terminal tabs for the next part (I recommend tmux, Tilix, Terminator or something similar).
    1. Run `docker-compose run torcs` in _docker/torcs/_
    2. In another terminal tab run `docker-compose run pytorch` in _docker/neuralnet_

5. Now that the docker containers are up and running, build TORCS in its container with `./build.sh`.

6. Start TORCS with the `torcs` command, it will set up the socket server and wait for neural network client.

7. Switch to the window of the neural network container, and run `python drive.py`. The client will connect
    to the simulation server and drive the car in its environment.