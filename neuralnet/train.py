import argparse
import model.data_loader as data_loader
import os
import torch
import torch.nn as nn
from model.net import Net
from utils import Parameters

# Add option to change directory paths containing training data from command line by arguments
parser = argparse.ArgumentParser()
parser.add_argument('--data_dir', default='/training_data/kate/', help="Directory containing the dataset")
parser.add_argument('--model_dir', default='experiments/base_model/', help="Directory containing params.json")


def train(model, optimizer, dataloaders, loss_function, params):
    """
    Function for training the neural network
    :param model: Neural network, [ torch.nn.Module ]
    :param optimizer: Parameter optimizer of model, [ torch.optim ]
    :param dataloaders: Training data fetcher, [ torch.utils.data.DataLoader ]
    :param loss_function: Function that takes neuralnet outputs and ground truth and computes the loss for the batch
    :param params: Hyperparameters, [ Parameters ]
    """
    # Set network to train mode
    model.train()
    # Define variable with large value which will be updated on first loss calculation
    best_loss = 10000
    # Run training loop for epoch number defined by params
    for epoch in range(params.num_epochs):
        print("epoch #", epoch + 1)
        running_loss = 0.0
        # It's possible to train on more maps at the same time
        for map_name in dataloaders:
            print("Current training map name: " + map_name)
            for i, data in enumerate(dataloaders[map_name]):
                # Get the neural network's inputs - camera images and labels - steering angles
                inputs, labels = data['image'], data['steering']
                inputs, labels = inputs.to(device), labels.to(device)
                # forward + backward + optimize
                # Forward propagation, calculate neural network outputs on batch of camera images
                outputs = net(inputs)
                # Calculate loss between nn outputs and ground truth steering angle labels
                loss = loss_function(outputs.view(outputs.size()[0]), labels)
                # Save model to file if it's the best so far
                if loss < best_loss:
                    torch.save(net.state_dict(), 'saved_models/trained_model.pt')
                    best_loss = loss.item()
                # Zero the parameter gradients
                optimizer.zero_grad()
                # Backpropagation, adjust the weight of neurons by calculating the gradient of the loss function
                loss.backward()
                # Update the parameters based on the computed gradients
                optimizer.step()
                running_loss += loss.item()
                # Print running loss every 5 batches
                if i % 5 == 4:  # print every 5 mini-batches
                    print('[%d, %5d] loss: %.8f' %
                          (epoch + 1, i + 1, running_loss / 5))
                    running_loss = 0.0


if __name__ == '__main__':
    try:
        print("Welcome!")
        print("Setting up training parameters for training, press Ctrl-C to abort")
        # Get command line arguments
        args = parser.parse_args()

        # Get hyperparameters for neural network training
        json_path = os.path.join(args.model_dir, 'params.json')
        assert os.path.isfile(json_path), "No json configuration file found at {}".format(json_path)
        params = Parameters(json_path)

        # Check if Nvidia GPU is available with CUDA, set seed to be able to reproduce results
        if torch.cuda.is_available():
            device = torch.device("cuda:0")
            torch.cuda.manual_seed(314)
        else:
            device = torch.device("cpu")
        torch.manual_seed(314)

        print("Used device: ", device)
        print("Setting up dataloaders...")
        # Get dataloaders for listed maps
        dataloaders = data_loader.fetch_dataloader(['spring', 'aalborg'], args.data_dir, params)
        print("- done.")

        # Initialize neural network
        net = Net()
        net.to(device)
        # Create a criterion that measures the mean squared error between n elements in the input x and target y.
        loss_function = nn.MSELoss()
        # Add stochastic gradient-based optimization
        optimizer = torch.optim.Adam(net.parameters())
        print("Starting training for " + str(params.num_epochs) + " epochs")
        train(net, optimizer, dataloaders, loss_function, params)
    except KeyboardInterrupt:
        print("\nTraining interrupted, goodbye!")
