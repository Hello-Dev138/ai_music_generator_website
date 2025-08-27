import os
import glob

import mido

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from .tokenizer_class import MidiTokenizer

import matplotlib.pyplot as plt #For data visualization
import numpy as np
import pandas as pd

from tqdm import tqdm # For progress bars

class MIDIDataset(Dataset):
    def __init__(self, tokens_file, seq_length=64):
        self.seq_length = seq_length
        self.data = torch.load(tokens_file)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        input_sequence, target_sequence = self.data[idx]
        input_sequence = torch.tensor(input_sequence, dtype=torch.long)
        target_sequence = torch.tensor(target_sequence, dtype=torch.long)

        return input_sequence, target_sequence
    
    def clear(self):
        self.data = []

    def split_X_y(self):
        X, y = zip(*self.data)
        return torch.stack([torch.tensor(x, dtype=torch.long)for x in X]), torch.tensor(y, dtype=torch.long)
    