import os
import numpy as np
import torch
from torch.utils.data import Dataset
from glob import glob
from tqdm import tqdm # For progress bars

class MIDIDatasetNPY(Dataset):
    def __init__(self, all_file_paths, seq_length=64, mode = "train", samples_per_epoch = 50000, files_per_epoch = 400):
        self.seq_length = seq_length
        self.mode = mode
        self.samples_per_epoch = samples_per_epoch
        self.files_per_epoch = files_per_epoch

        self.all_file_paths = all_file_paths
        self.file_paths = all_file_paths

        # Precompute sequence counts for deterministic val/test
        if mode in ["val", "test"]:
            self.file_sequence_counts = []
            for path in tqdm(self.file_paths, desc=f"Counting sequences ({mode})"):
                tokens = np.load(path, mmap_mode='r')
                count = max(len(tokens) - seq_length, 0)
                self.file_sequence_counts.append(count)
            self.total_sequences = sum(self.file_sequence_counts)
            self.cumulative_counts = np.cumsum([0] + self.file_sequence_counts)

        # Cache for file tokens
        self._cached_file_idx = None
        self._cached_tokens = None

    def _sample_files(self):
        # Randomly select files for this epoch
        paths = np.random.choice(self.all_file_paths, min(self.files_per_epoch, len(self.all_file_paths)), replace=False)
        return list(paths)

    def set_epoch_files(self):
        if self.mode == "train":
            self.file_paths = self._sample_files()
            self._cached_file_idx = None
            self._cached_tokens = None

    def __len__(self):
        if self.mode == "train":
            return self.samples_per_epoch
        else:
            return self.total_sequences

    def __getitem__(self, idx):
        if self.mode == "train":
            # Randomly pick a file and sequence
            while True:
                file_idx = np.random.randint(len(self.file_paths))
                tokens = np.load(self.file_paths[file_idx], mmap_mode='r')
                if len(tokens) <= self.seq_length:
                    continue
                start = np.random.randint(0, len(tokens) - self.seq_length - 1)
                input_seq = tokens[start:start + self.seq_length]
                target_seq = tokens[start + 1:start + self.seq_length + 1]
                break
        else:
            # Deterministic val/test
            file_idx = np.searchsorted(self.cumulative_counts, idx, side='right') - 1
            seq_idx = idx - self.cumulative_counts[file_idx]

            if file_idx != self._cached_file_idx:
                self._cached_tokens = np.load(self.file_paths[file_idx], mmap_mode='r')
                self._cached_file_idx = file_idx

            tokens = self._cached_tokens
            if len(tokens) < self.seq_length + 1:
                # skip if not enough tokens
                seq_idx = max(0, len(tokens) - self.seq_length - 1)

            input_seq = tokens[seq_idx:seq_idx + self.seq_length]
            target_seq = tokens[seq_idx + 1:seq_idx + self.seq_length + 1]

        return torch.tensor(input_seq, dtype=torch.long), torch.tensor(target_seq, dtype=torch.long)