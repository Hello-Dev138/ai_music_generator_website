import os
import glob

import mido

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset

from tokenizer import MidiTokenizer

import matplotlib.pyplot as plt #For data visualization
import numpy as np
import pandas as pd

class MIDIDataset(Dataset):
    def __init__(self, midi_paths, seq_length=64):
        self.seq_length = seq_length
        self.data = []
        self.data_as_string = []

        
        for path in midi_paths:
            try:
                print(f"Adding {path} to dataset...")
                tokenizer = MidiTokenizer()
                tokens = tokenizer.tokenize_file(path)  # list of token IDs
                #self.data_as_string.append(tokenizer.tokens_to_string(tokens))  # Store string representation for debugging
                if len(tokens) <= seq_length:
                    continue
                for i in range(len(tokens) - seq_length):
                    input_seq = tokens[i:i+seq_length]
                    target_token = tokens[i+seq_length]
                    self.data.append((input_seq, target_token))
            except Exception as e:
                print(f"Skipping {path} due to error: {e}")


    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        input_sequence, target_token = self.data[idx]
        input_sequence = torch.tensor(input_sequence, dtype=torch.long)
        target_token = torch.tensor(target_token, dtype=torch.long)

        return input_sequence, target_token
    
    def clear(self):
        self.data = []

    def split_X_y(self):
        X, y = zip(*self.data)
        return torch.tensor(X, dtype=torch.long), torch.tensor(y, dtype=torch.long)