import numpy as np
import os
from PIL import Image
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from utils import Crop, Resize, ToTensor, Standardize

# torcs_image_mean = np.loadtxt('image_characteristics/mean.txt')
# torcs_image_std = np.loadtxt('image_characteristics/std.txt')

data_transformer = transforms.Compose([
    Crop(),
    Resize(),
    # Standardize(torcs_image_mean, torcs_image_std),
    ToTensor()
    ])


class SimulationDataset(Dataset):
    """
    Generate dataset from folder with camera images and text file containing steering angles
    """
    def __init__(self, txt_file, root_dir, transform=None):
        """
        Initialize the dataset
        :param txt_file: textfile containing the steering angles (absolut path needed)
        :param root_dir: absolute path of folder containing images and steering angles
        :param transform: the transformation classes will be applied on training camera images
        """
        self.root_dir = root_dir
        self.transform = transform
        filename = self.root_dir + "/" + txt_file
        assert os.path.isfile(filename), "No text file found at {}".format(filename)
        self.steerings_frame = np.loadtxt(filename)
        # Ignore brake and acceleration for now, maybe add recurrent structure in the future
        self.steerings_frame = self.steerings_frame[:, 0]

    def __getitem__(self, idx):
        """
        Get the 'idx'th element of dataset
        :param idx: index number of desired element
        :return: 'idx'th dataset element, a pair of camera image and steering angle
        """
        img_name = self.root_dir + "/" + str(idx) + '.png'
        image = Image.open(img_name).convert('RGB')
        steering = self.steerings_frame[idx]
        sample = {'image': image, 'steering': steering}

        if self.transform:
            sample = self.transform(sample)

        return sample

    def __len__(self):
        """
        Return length of dataset based on number of steering angles read from txt file
        :return: number of dataset elements
        """
        return len(self.steerings_frame)


def fetch_dataloader(maps, data_dir, params):
    """
    Fetches the DataLoader object for each map defined in maps
    :param maps: list of maps
    :param data_dir: directory where training data can be found
    :param params: parameters dictionary including batch size and number of workers
    :return: Dictionary of dataloaders containing each needed map
    """
    dataloaders = {}

    for map_name in ['aalborg', 'alpine_2', 'cg_1', 'spring']:
        if map_name in maps:
            path = os.path.join(data_dir, map_name)
            dl = DataLoader(SimulationDataset(txt_file='steering.txt', root_dir=path, transform=data_transformer),
                            batch_size=params.batch_size,
                            shuffle=True,
                            num_workers=params.num_workers)
            print(map_name + " dataset added")
            dataloaders[map_name] = dl

    return dataloaders
