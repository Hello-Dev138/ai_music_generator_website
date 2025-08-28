from .lstm_class import MidiLSTM
from AI_TRAINING import MidiTokenizer
import torch
from tqdm import tqdm
import torch
import torch.nn.functional as F

class AIGenerator:
    def __init__(self, token_ids, tokens_to_gen = 100, use_first_n_tokens = 10, type_gen = "melody", top_k = 10, temperature = 1.0,): # use_first_n_tokens  is the number of tokens to use as the original sequence for generation
        self.token_ids = token_ids[:use_first_n_tokens] if len(token_ids) >= use_first_n_tokens else token_ids
        self.use_first_n_tokens = use_first_n_tokens
        self.vocab_size = MidiTokenizer().tokenizer.vocab_size
        self.model = MidiLSTM(vocab_size=self.vocab_size)
        if type_gen == "melody":
            self.model.load_state_dict(torch.load(r"C:\Users\rober\OneDrive\Documents\0.School\WILLIAM PERKIN\Comp\1. NEA project prototype\AI_MODELS\best_models\melody_prediction_monophonic.pt"))
            self.monophonic = True # Means that only one note can be played at a time
        else:
            self.model.load_state_dict(torch.load(r"C:\Users\rober\OneDrive\Documents\0.School\WILLIAM PERKIN\Comp\1. NEA project prototype\AI_MODELS\best_models\accompaniment_prediction.pt"))
            self.monophonic = False # Means that more than one note can be played at a time
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.model.eval()

        self.tokens_to_generate = tokens_to_gen

        # For randomness in generated music
        self.temperature = temperature # Controls the randomness of the predictions, the higher the value, the more random
        self.top_k = top_k # Keep only the top_k predictions to introduce randomness

        # Constants
        self.SEQUENCE_LENGTH = 64 # The length of sequences this ai was trained on
        self.NGRAM_SIZE = 4 # Size of n-grams to avoid repetition
        self.NGRAM_PENALTY = 1e9 # Penalty to penalize repeated n-grams

    def _get_recent_ngrams(self):
        ngrams = {} # Dictionary mapping each n-gram (tuple of tokens) to its frequency count
        for i in range(len(self.token_ids) - self.NGRAM_SIZE + 1): # Extract all possible n-grams from the current sequence
            g = tuple(self.token_ids[i:i+self.NGRAM_SIZE]) # Form the n-gram with the length of NGRAM_SIZE as an immutable tuple (good for dictionary key)
            ngrams[g] = ngrams.get(g, 0) + 1 # Increment the count of this n-gram if it has already been seen, or initialize it to 1
        return ngrams

    def get_monophonic(self):
        return self.monophonic
    
    def generate(self):
        with torch.no_grad():
            for i in tqdm(range(self.tokens_to_generate), desc="Predicting:", unit="predictions"):
                logits = self.model(torch.tensor(self.token_ids[-self.SEQUENCE_LENGTH:], dtype=torch.long).unsqueeze(0).to(self.device))
                logits = logits[0, -1]  # Get the logits for the last time step
                
                # Apply n-gram penalty
                if len(self.token_ids) >= self.NGRAM_SIZE:
                    recent_ngrams = self._get_recent_ngrams() # Get the recent n-grams from the current sequence
                    for token_id in range(len(logits)):
                        ngram = tuple(self.token_ids[-(self.NGRAM_SIZE-1):] + [token_id]) # Form the n-gram with the current token
                        if ngram in recent_ngrams:
                            logits[token_id] -= self.NGRAM_PENALTY  # Reduce the probability of repeated n-grams

                # Apply temperature
                logits = logits / self.temperature # This will change the logits by scaling them according to the temperature to introduce randomness

                # Apply top-k filtering
                top_k_values, topk_indices = torch.topk(logits, self.top_k) # Will return the top_k number of values that are most likely
                filtered_logits = torch.full_like(logits, float('-inf')) # Will create a new tensor with the same shape as logits, filled with -inf
                filtered_logits[topk_indices] = logits[topk_indices] # Will only replace the top_k logits (in this new tensor) with their original values so that other values cant be picked

                # Convert to probabilities and sample them
                probs = F.softmax(filtered_logits, dim=-1) # Convert logits to probabilities by applying softmax (will make sure that 0 < probability < 1 and that they sum to 1)
                next_token = torch.multinomial(probs, 1).item() # Stochastic sampling to predict one token from the probability distribution of the top_k tokens
                
                self.token_ids.append(next_token) # Add the predicted token_id to the sequence

    def get_generated_token_ids(self):
        return self.token_ids