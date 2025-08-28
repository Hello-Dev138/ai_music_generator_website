import torch
import torch.nn as nn

# Create a simple LSTM model for MIDI sequence prediction
class MidiLSTM(nn.Module):
    """
    vocab_size: Size of the vocabulary (number of unique MIDI tokens)
    embed_size: Size of the embedding vector for each token
    hidden_size: Size of the hidden state in the LSTM
    num_layers: Number of LSTM layers
    dropout: Dropout rate applied to the LSTM outputs
    """ 
    def __init__(self, vocab_size = 264, embed_size = 256, hidden_size=512, num_layers=2, dropout=0.2):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_size) # Each token is mapped to an embedding vector so that model can learn relationships between tokens
        self.lstm = nn.LSTM(input_size = embed_size, hidden_size = hidden_size, num_layers = num_layers,
                            dropout=dropout, batch_first=True) # Initializes a multi-layer LSTM
        self.fc = nn.Linear(hidden_size, vocab_size) # Fully connected layer to map LSTM output to vocabulary size; predicts the next token in the sequence
        self.init_weights()

    def init_weights(self):
        # Embeddings
        nn.init.uniform_(self.embedding.weight, -0.1, 0.1) # Keeps embeddings short and balanced at the start so model doesnt explode with huge values

        # Forget gate bias = 1, controls how much memory to keep. This stabilizes training
        for names in self.lstm._all_weights:
            for name in filter(lambda n: "bias" in n, names):
                bias = getattr(self.lstm, name) # Get the bias tensor
                n = bias.size(0) # Get the number of biases
                start, end = n // 4, n // 2 # Forget gate is the second quarter of the biases
                nn.init.constant_(bias.data[start:end], 1.0) # Keeps forget gate bias high to retain memory

        # Fully connected layer so each input node is connected to each output node
        nn.init.xavier_uniform_(self.fc.weight) # Start weights at the right scale for smoother training
        nn.init.zeros_(self.fc.bias) # Sets the bias to 0 so that the model learns all bias based on the dataset

    def forward(self, x, return_last=False):
        x = self.embedding(x)            # Converts tokens to vectors: [B, seq_len] → [B, seq_len, embed]
        out, _ = self.lstm(x)            # out: [B, seq_len, hidden]
        # _ is the hidden state and cell state, which we ignore here
        logits = self.fc(out)  # predict each next token at every step: [B, seq_len, vocab_size]
        if return_last:
            return logits[:, -1, :]  # return only last time step's logits: [B, vocab_size]
        return logits