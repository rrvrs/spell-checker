import numpy as np
from typing import List, Tuple, Dict, Set
from collections import defaultdict
import re


class EditDistanceCalculator:
    """Advanced edit distance calculator with multiple algorithms and optimizations"""
    
    def __init__(self, config):
        self.config = config
        self.max_distance = config.get('max_distance', 2)
        self.allow_transpose = config.get('allow_transpose', True)
        self.substitution_cost = config.get('substitution_cost', 1)
        self.insertion_cost = config.get('insertion_cost', 1)
        self.deletion_cost = config.get('deletion_cost', 1)
        self.transpose_cost = config.get('transpose_cost', 1)
        self.keyboard_layout = self._build_keyboard_layout()
        
    def _build_keyboard_layout(self) -> Dict[str, Set[str]]:
        """Build keyboard layout for weighted corrections based on key proximity"""
        layout = {
            'q': {'w', 'a'}, 'w': {'q', 'e', 's'}, 'e': {'w', 'r', 'd'},
            'r': {'e', 't', 'f'}, 't': {'r', 'y', 'g'}, 'y': {'t', 'u', 'h'},
            'u': {'y', 'i', 'j'}, 'i': {'u', 'o', 'k'}, 'o': {'i', 'p', 'l'},
            'p': {'o', 'l'}, 'a': {'q', 's', 'z'}, 's': {'a', 'w', 'd', 'x'},
            'd': {'s', 'e', 'f', 'c'}, 'f': {'d', 'r', 'g', 'v'},
            'g': {'f', 't', 'h', 'b'}, 'h': {'g', 'y', 'j', 'n'},
            'j': {'h', 'u', 'k', 'm'}, 'k': {'j', 'i', 'l'}, 'l': {'k', 'o', 'p'},
            'z': {'a', 's', 'x'}, 'x': {'z', 's', 'd', 'c'}, 'c': {'x', 'd', 'f', 'v'},
            'v': {'c', 'f', 'g', 'b'}, 'b': {'v', 'g', 'h', 'n'}, 'n': {'b', 'h', 'j', 'm'},
            'm': {'n', 'j', 'k'}
        }
        return layout
        
    def levenshtein_distance(self, word1: str, word2: str) -> int:
        """Standard Levenshtein distance"""
        if len(word1) < len(word2):
            return self.levenshtein_distance(word2, word1)

        if len(word2) == 0:
            return len(word1)

        previous_row = range(len(word2) + 1)
        for i, c1 in enumerate(word1):
            current_row = [i + 1]
            for j, c2 in enumerate(word2):
                insertions = previous_row[j + 1] + self.insertion_cost
                deletions = current_row[j] + self.deletion_cost
                substitutions = previous_row[j] + (self.substitution_cost if c1 != c2 else 0)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]
        
    def damerau_levenshtein_distance(self, word1: str, word2: str) -> int:
        """Damerau-Levenshtein distance including transpositions"""
        len1, len2 = len(word1), len(word2)
        
        chars = set(word1 + word2)
        char_array = {char: 0 for char in chars}
        
        max_dist = len1 + len2
        H = [[max_dist for _ in range(len2 + 2)] for _ in range(len1 + 2)]
        
        H[0][0] = max_dist
        for i in range(0, len1 + 1):
            H[i + 1][0] = max_dist
            H[i + 1][1] = i
        for j in range(0, len2 + 1):
            H[0][j + 1] = max_dist
            H[1][j + 1] = j
            
        for i in range(1, len1 + 1):
            DB = 0
            for j in range(1, len2 + 1):
                k = char_array[word2[j - 1]]
                l = DB
                if word1[i - 1] == word2[j - 1]:
                    cost = 0
                    DB = j
                else:
                    cost = 1
                    
                H[i + 1][j + 1] = min(
                    H[i][j] + cost,  # substitution
                    H[i + 1][j] + self.insertion_cost,  # insertion
                    H[i][j + 1] + self.deletion_cost,  # deletion
                    H[k][l] + (i - k - 1) + 1 + (j - l - 1)  # transposition
                )
                
            char_array[word1[i - 1]] = i
            
        return H[len1 + 1][len2 + 1]
        
    def weighted_edit_distance(self, word1: str, word2: str) -> float:
        """Weighted edit distance considering keyboard proximity"""
        if len(word1) < len(word2):
            return self.weighted_edit_distance(word2, word1)

        if len(word2) == 0:
            return len(word1)

        previous_row = list(range(len(word2) + 1))
        for i, c1 in enumerate(word1):
            current_row = [i + 1]
            for j, c2 in enumerate(word2):
                if c1 == c2:
                    sub_cost = 0
                elif c2 in self.keyboard_layout.get(c1, set()): # Adjacent keys cost less
                    sub_cost = 0.5
                else:
                    sub_cost = self.substitution_cost
                    
                insertions = previous_row[j + 1] + self.insertion_cost
                deletions = current_row[j] + self.deletion_cost
                substitutions = previous_row[j] + sub_cost
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]
        
    def phonetic_distance(self, word1: str, word2: str) -> int:
        """Simple phonetic distance for common misspellings"""
        phonetic_map = {
            'ph': 'f', 'tion': 'shun', 'sion': 'zhun', 'ough': 'uff',
            'augh': 'aff', 'eigh': 'ay', 'ight': 'ite', 'kn': 'n',
            'wr': 'r', 'mb': 'm', 'bt': 't'
        }
        
        def normalize_phonetic(word):
            for pattern, replacement in phonetic_map.items():
                word = word.replace(pattern, replacement)
            return word
            
        norm1 = normalize_phonetic(word1.lower())
        norm2 = normalize_phonetic(word2.lower())
        
        return self.levenshtein_distance(norm1, norm2)
        
    def get_candidates_by_distance(self, word: str, vocabulary: Set[str], 
                                 max_candidates: int = 20) -> List[Tuple[str, float]]:
        """Get candidates sorted by various distance metrics"""
        candidates = []
        
        for vocab_word in vocabulary:
            if abs(len(word) - len(vocab_word)) > self.max_distance:
                continue
                
            if self.allow_transpose:
                distance = self.damerau_levenshtein_distance(word, vocab_word)
            else:
                distance = self.levenshtein_distance(word, vocab_word)
                
            if distance <= self.max_distance:
                weighted_dist = self.weighted_edit_distance(word, vocab_word)
                phonetic_dist = self.phonetic_distance(word, vocab_word)
                
                final_score = (0.5 * distance + 0.3 * weighted_dist + 0.2 * phonetic_dist)
                candidates.append((vocab_word, final_score))
                
        candidates.sort(key=lambda x: x[1])
        return candidates[:max_candidates]
        
    def get_edit_operations(self, word1: str, word2: str) -> List[str]:
        """Get the sequence of edit operations to transform word1 to word2"""
        len1, len2 = len(word1), len(word2)
        dp = [[0] * (len2 + 1) for _ in range(len1 + 1)]
        
        for i in range(len1 + 1):
            dp[i][0] = i
        for j in range(len2 + 1):
            dp[0][j] = j
            
        for i in range(1, len1 + 1):
            for j in range(1, len2 + 1):
                if word1[i-1] == word2[j-1]:
                    dp[i][j] = dp[i-1][j-1]
                else:
                    dp[i][j] = 1 + min(
                        dp[i-1][j],      # deletion
                        dp[i][j-1],      # insertion
                        dp[i-1][j-1]     # substitution
                    )
        
        operations = []
        i, j = len1, len2
        
        while i > 0 or j > 0:
            if i > 0 and j > 0 and word1[i-1] == word2[j-1]:
                i -= 1
                j -= 1
            elif i > 0 and j > 0 and dp[i][j] == dp[i-1][j-1] + 1:
                operations.append(f"substitute '{word1[i-1]}' -> '{word2[j-1]}' at position {i-1}")
                i -= 1
                j -= 1
            elif i > 0 and dp[i][j] == dp[i-1][j] + 1:
                operations.append(f"delete '{word1[i-1]}' at position {i-1}")
                i -= 1
            elif j > 0 and dp[i][j] == dp[i][j-1] + 1:
                operations.append(f"insert '{word2[j-1]}' at position {i}")
                j -= 1
                
        return list(reversed(operations))
        
    def analyze_error_patterns(self, corrections: List[Tuple[str, str]]) -> Dict:
        """Analyze patterns in correction pairs to identify common errors"""
        patterns = defaultdict(int)
        operation_counts = defaultdict(int)
        
        for original, corrected in corrections:
            operations = self.get_edit_operations(original, corrected)
            for op in operations:
                operation_counts[op] += 1

                if 'substitute' in op:
                    patterns['substitution'] += 1
                elif 'delete' in op:
                    patterns['deletion'] += 1
                elif 'insert' in op:
                    patterns['insertion'] += 1
                    
        return {
            'pattern_counts': dict(patterns),
            'most_common_operations': dict(sorted(operation_counts.items(), 
                                                key=lambda x: x[1], reverse=True)[:10])
        } 