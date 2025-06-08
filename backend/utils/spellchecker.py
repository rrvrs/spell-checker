import re
import os
import yaml
import string
import nltk
from collections import Counter, defaultdict
from nltk.util import ngrams
from nltk.tokenize import word_tokenize
from nltk.corpus import words
from backend.utils.helpers import load_medical_terms
from backend.utils.frequency_manager import FrequencyManager
from backend.utils.edit_distance import EditDistanceCalculator
from backend.utils.homophone_detector import HomophoneDetector

nltk.download('punkt_tab', quiet=True)

class SpellChecker:
    def __init__(self, config):
        self.config = config
        self.ngram_size = config['ngram']['size']
        self.min_freq = config['ngram']['min_freq_threshold']
        self.corpus_path = config['corpus']['merged_corpus']
        self.medical_terms = load_medical_terms(config['domain']['medical_terms_file'])
        self.domain_weight = config['domain']['domain_weight']
        self.frequency_manager = FrequencyManager(config)
        self.edit_distance_calc = EditDistanceCalculator(config['edit_distance'])
        self.homophone_detector = HomophoneDetector()
        self.vocab = set()
        self.word_freq = Counter()
        self.ngram_freq = defaultdict(Counter)
        
        self.build_models()

    def build_models(self):
        """Build comprehensive language models"""
        with open(self.corpus_path, 'r', encoding='utf-8') as f:
            text = f.read().lower()

        self.frequency_manager.build_frequency_models(text)
        
        tokens = word_tokenize(text)
        self.vocab = set(tokens)
        self.word_freq = self.frequency_manager.word_freq
        
        for ngram in ngrams(tokens, self.ngram_size):
            prefix = ngram[:-1]
            next_word = ngram[-1]
            self.ngram_freq[prefix][next_word] += 1

    def check_text(self, text, model_type="bigram"):
        """Enhanced spell checking with advanced algorithms"""
        tokens = word_tokenize(text.lower())
        corrected_tokens = []
        error_list = []

        for i, word in enumerate(tokens):
            context = [tokens[j] for j in range(max(0, i-2), i) if tokens[j].isalpha()]
            
            if word in self.vocab or not word.isalpha():
                if word.isalpha() and self.config['error_handling']['error_types'].get('homophone', True):
                    is_homophone, homophone_candidates = self.homophone_detector.is_homophone_error(
                        word, context, self.vocab
                    )
                    if is_homophone:
                        homophone_scores = self.homophone_detector.score_homophone_candidates(
                            homophone_candidates, context
                        )
                        if homophone_scores and homophone_scores[0][1] > 0.7:
                            suggestions = [{
                                "word": candidate,
                                "score": score,
                                "frequency_score": self.frequency_manager.get_frequency_score(
                                    candidate, context, model_type
                                ),
                                "edit_distance": 0,
                                "is_medical": candidate in self.medical_terms
                            } for candidate, score in homophone_scores[:self.config['error_handling']['max_suggestions']]]
                            
                            error_list.append({
                                "original": word,
                                "suggestions": suggestions,
                                "position": i,
                                "confidence": homophone_scores[0][1],
                                "type": "homophone",
                                "context": context
                            })
                            
                corrected_tokens.append(word)
                continue
            
            candidates_with_distance = self.edit_distance_calc.get_candidates_by_distance(
                word, self.vocab, self.config['ngram']['max_candidates']
            )
            
            scored = []
            for candidate, edit_distance in candidates_with_distance:
                freq_score = self.frequency_manager.get_frequency_score(
                    candidate, context, model_type
                )
                
                domain_multiplier = 1.0
                if candidate in self.medical_terms:
                    domain_multiplier = self.domain_weight

                final_score = (freq_score * domain_multiplier) / (1 + edit_distance)
                
                scored.append((candidate, final_score, freq_score, edit_distance))

            scored.sort(key=lambda x: x[1], reverse=True)

            if scored:
                best = scored[0][0]
                total_score = sum(s[1] for s in scored)
                confidence = round(scored[0][1] / total_score, 3) if total_score > 0 else 0
                
                corrected_tokens.append(best)

                suggestions = []
                for candidate, final_score, freq_score, edit_dist in scored[:self.config['error_handling']['max_suggestions']]:
                    suggestions.append({
                        "word": candidate,
                        "score": round(final_score / total_score, 3) if total_score > 0 else 0,
                        "frequency_score": round(freq_score, 6),
                        "edit_distance": edit_dist,
                        "is_medical": candidate in self.medical_terms
                    })

                error_type = self._classify_error_type(word, best)

                error_list.append({
                    "original": word,
                    "suggestions": suggestions,
                    "position": i,
                    "confidence": confidence,
                    "type": error_type,
                    "context": context
                })
            else:
                corrected_tokens.append(word)

        return {
            "corrected_text": ' '.join(corrected_tokens),
            "errors": error_list,
            "statistics": self._get_correction_statistics(error_list)
        }
        
    def _classify_error_type(self, original: str, corrected: str) -> str:
        """Classify the type of error based on the correction"""
        homophones = self.homophone_detector.get_homophones(original)
        if corrected.lower() in [h.lower() for h in homophones]:
            return "homophone"
            
        operations = self.edit_distance_calc.get_edit_operations(original, corrected)
        
        if not operations:
            return "no_error"
        
        if any("transpose" in op.lower() for op in operations):
            return "transposition"
        elif len(operations) == 1:
            if "substitute" in operations[0]:
                return "substitution"
            elif "delete" in operations[0]:
                return "deletion"
            elif "insert" in operations[0]:
                return "insertion"
        
        phonetic_distance = self.edit_distance_calc.phonetic_distance(original, corrected)
        if phonetic_distance < len(operations):
            return "phonetic"
            
        return "typo"
        
    def _get_correction_statistics(self, error_list: list) -> dict:
        """Get statistics about the corrections made"""
        if not error_list:
            return {"total_errors": 0}
            
        error_types = {}
        confidence_scores = []
        medical_corrections = 0
        
        for error in error_list:
            error_type = error["type"]
            error_types[error_type] = error_types.get(error_type, 0) + 1
            confidence_scores.append(error["confidence"])
            
            if error["suggestions"] and error["suggestions"][0].get("is_medical", False):
                medical_corrections += 1
                
        return {
            "total_errors": len(error_list),
            "error_types": error_types,
            "average_confidence": round(sum(confidence_scores) / len(confidence_scores), 3),
            "medical_corrections": medical_corrections,
            "medical_correction_rate": round(medical_corrections / len(error_list), 3)
        }
        
    def get_model_statistics(self) -> dict:
        """Get comprehensive statistics about the language models"""
        freq_stats = self.frequency_manager.get_statistics()
        
        return {
            "frequency_model": freq_stats,
            "edit_distance_config": {
                "max_distance": self.edit_distance_calc.max_distance,
                "allow_transpose": self.edit_distance_calc.allow_transpose,
                "keyboard_weighted": True
            },
            "domain_info": {
                "medical_terms_count": len(self.medical_terms),
                "domain_weight": self.domain_weight
            }
        }
        
    def evaluate_on_test_set(self, test_corrections: list) -> dict:
        """Evaluate the spellchecker on a test set of known corrections"""
        results = {
            "accuracy": 0,
            "total_tests": len(test_corrections),
            "correct_predictions": 0,
            "error_analysis": {}
        }
        
        correct = 0
        for original, expected in test_corrections:
            result = self.check_text(original)
            if result["errors"]:
                predicted = result["errors"][0]["suggestions"][0]["word"]
                if predicted == expected:
                    correct += 1
                    
        results["correct_predictions"] = correct
        results["accuracy"] = round(correct / len(test_corrections), 3) if test_corrections else 0
        
        if test_corrections:
            results["error_analysis"] = self.edit_distance_calc.analyze_error_patterns(test_corrections)
            
        return results
