# backend/utils/spellchecker.py

import re
import os
import yaml
import string
import nltk
from collections import Counter, defaultdict
from nltk.util import ngrams
from nltk.tokenize import word_tokenize
from nltk.corpus import words
from backend.utils.helpers import load_medical_terms, edit_distance_candidates

nltk.download('punkt', quiet=True)

class SpellChecker:
    def __init__(self, config):
        self.config = config
        self.ngram_size = config['ngram']['size']
        self.min_freq = config['ngram']['min_freq_threshold']
        self.corpus_path = config['corpus']['merged_corpus']
        self.medical_terms = load_medical_terms(config['domain']['medical_terms_file'])
        self.domain_weight = config['domain']['domain_weight']
        self.vocab = set()
        self.word_freq = Counter()
        self.ngram_freq = defaultdict(Counter)
        self.build_models()

    def build_models(self):
        with open(self.corpus_path, 'r', encoding='utf-8') as f:
            text = f.read().lower()

        tokens = word_tokenize(text)
        self.vocab = set(tokens)
        self.word_freq.update(tokens)

        for ngram in ngrams(tokens, self.ngram_size):
            prefix = ngram[:-1]
            next_word = ngram[-1]
            self.ngram_freq[prefix][next_word] += 1

    def check_text(self, text, model_type="bigram"):
        tokens = word_tokenize(text.lower())
        corrected_tokens = []
        error_list = []

        for i, word in enumerate(tokens):
            if word in self.vocab or not word.isalpha():
                corrected_tokens.append(word)
                continue

            candidates = edit_distance_candidates(word, self.vocab, self.config['edit_distance'])
            scored = []

            for cand in candidates:
                score = self.word_freq[cand] + 1  # base frequency

                if tuple(tokens[i - self.ngram_size + 1:i]) in self.ngram_freq:
                    score += self.ngram_freq[tuple(tokens[i - self.ngram_size + 1:i])][cand]

                if cand in self.medical_terms:
                    score *= self.domain_weight

                scored.append((cand, score))

            scored.sort(key=lambda x: x[1], reverse=True)

            if scored:
                best = scored[0][0]
                confidence = round(scored[0][1] / sum(s for _, s in scored), 2)
                corrected_tokens.append(best)

                suggestions = [
                    {"word": w, "score": round(s / sum(x[1] for x in scored), 2)}
                    for w, s in scored[:self.config['error_handling']['max_suggestions']]
                ]

                error_list.append({
                    "original": word,
                    "suggestions": suggestions,
                    "position": i,
                    "confidence": confidence,
                    "type": "typo"  # could extend with homophone, etc.
                })
            else:
                corrected_tokens.append(word)

        return {
            "corrected_text": ' '.join(corrected_tokens),
            "errors": error_list
        }
