import os
import json
import pickle
import math
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Optional
import numpy as np


class FrequencyManager:
    """Advanced frequency dictionary manager with statistical methods"""
    
    def __init__(self, config):
        self.config = config
        self.word_freq = Counter()
        self.unigram_freq = Counter()
        self.bigram_freq = defaultdict(Counter)
        self.trigram_freq = defaultdict(Counter)
        self.total_words = 0
        self.vocabulary_size = 0
        self.smoothing_method = config['ngram'].get('smoothing', 'add-one')
        
    def build_frequency_models(self, corpus_text: str):
        """Build comprehensive frequency models from corpus"""
        from nltk.tokenize import word_tokenize
        from nltk.util import ngrams
        
        tokens = word_tokenize(corpus_text.lower())
        self.total_words = len(tokens)
        
        self.unigram_freq.update(tokens)
        self.vocabulary_size = len(self.unigram_freq)
        
        bigrams = list(ngrams(tokens, 2))
        for prev_word, curr_word in bigrams:
            self.bigram_freq[prev_word][curr_word] += 1
            
        trigrams = list(ngrams(tokens, 3))
        for w1, w2, w3 in trigrams:
            self.trigram_freq[(w1, w2)][w3] += 1
            
        self.word_freq = self.unigram_freq
        
    def get_word_probability(self, word: str) -> float:
        """Get probability of a word using unigram model with smoothing"""
        count = self.unigram_freq.get(word, 0)
        
        if self.smoothing_method == 'add-one':
            return (count + 1) / (self.total_words + self.vocabulary_size)
        elif self.smoothing_method == 'good-turing':
            return self._good_turing_probability(word)
        else:
            return count / self.total_words if self.total_words > 0 else 0
            
    def get_conditional_probability(self, word: str, context: List[str], model_type: str = 'bigram') -> float:
        """Get conditional probability P(word|context) with smoothing"""
        if model_type == 'bigram' and len(context) >= 1:
            prev_word = context[-1]
            numerator = self.bigram_freq[prev_word].get(word, 0)
            denominator = self.unigram_freq.get(prev_word, 0)
            
            if self.smoothing_method == 'add-one':
                numerator += 1
                denominator += self.vocabulary_size
                
            return numerator / denominator if denominator > 0 else self.get_word_probability(word)
            
        elif model_type == 'trigram' and len(context) >= 2:
            prev_context = tuple(context[-2:])
            numerator = self.trigram_freq[prev_context].get(word, 0)
            denominator = sum(self.trigram_freq[prev_context].values())
            
            if self.smoothing_method == 'add-one':
                numerator += 1
                denominator += self.vocabulary_size
                
            return numerator / denominator if denominator > 0 else self.get_conditional_probability(word, context[-1:], 'bigram')
            
        return self.get_word_probability(word)
        
    def _good_turing_probability(self, word: str) -> float:
        """Good-Turing smoothing for better probability estimation"""
        count = self.unigram_freq.get(word, 0)
        if count == 0:
            n1 = sum(1 for c in self.unigram_freq.values() if c == 1)
            return n1 / self.total_words
        return count / self.total_words
        
    def get_perplexity(self, test_tokens: List[str], model_type: str = 'bigram') -> float:
        """Calculate perplexity for model evaluation"""
        log_prob_sum = 0
        n_tokens = len(test_tokens)
        
        for i, token in enumerate(test_tokens):
            if model_type == 'bigram' and i > 0:
                prob = self.get_conditional_probability(token, [test_tokens[i-1]], 'bigram')
            elif model_type == 'trigram' and i > 1:
                prob = self.get_conditional_probability(token, test_tokens[i-2:i], 'trigram')
            else:
                prob = self.get_word_probability(token)
                
            if prob > 0:
                log_prob_sum += math.log(prob)
            else:
                log_prob_sum += math.log(1e-10)
                
        avg_log_prob = log_prob_sum / n_tokens
        return math.exp(-avg_log_prob)
        
    def get_frequency_score(self, word: str, context: List[str], model_type: str = 'bigram') -> float:
        """Get comprehensive frequency-based score for spell correction"""
        # Base frequency score
        unigram_prob = self.get_word_probability(word)
        
        # Contextual probability
        if context:
            contextual_prob = self.get_conditional_probability(word, context, model_type)
        else:
            contextual_prob = unigram_prob
            
        unigram_weight = 0.3
        context_weight = 0.7
        
        final_score = (unigram_weight * unigram_prob) + (context_weight * contextual_prob)
        return final_score
        
    def save_models(self, filepath: str):
        """Save frequency models to disk"""
        models = {
            'unigram_freq': dict(self.unigram_freq),
            'bigram_freq': {k: dict(v) for k, v in self.bigram_freq.items()},
            'trigram_freq': {k: dict(v) for k, v in self.trigram_freq.items()},
            'total_words': self.total_words,
            'vocabulary_size': self.vocabulary_size,
            'config': self.config
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(models, f)
            
    def load_models(self, filepath: str):
        """Load frequency models from disk"""
        with open(filepath, 'rb') as f:
            models = pickle.load(f)
            
        self.unigram_freq = Counter(models['unigram_freq'])
        self.bigram_freq = defaultdict(Counter)
        for k, v in models['bigram_freq'].items():
            self.bigram_freq[k] = Counter(v)
            
        self.trigram_freq = defaultdict(Counter)
        for k, v in models['trigram_freq'].items():
            self.trigram_freq[k] = Counter(v)
            
        self.total_words = models['total_words']
        self.vocabulary_size = models['vocabulary_size']
        self.word_freq = self.unigram_freq
        
    def get_statistics(self) -> Dict:
        """Get comprehensive statistics about the frequency models"""
        return {
            'total_words': self.total_words,
            'vocabulary_size': self.vocabulary_size,
            'unique_bigrams': len(self.bigram_freq),
            'unique_trigrams': len(self.trigram_freq),
            'most_common_words': self.unigram_freq.most_common(10),
            'smoothing_method': self.smoothing_method
        } 