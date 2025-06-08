# test_spellchecker.py
"""
Test suite for evaluating the spellchecker performance
"""

import yaml
from backend.utils.spellchecker import SpellChecker
import json
import time

# Load configuration
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Common medical misspellings for testing
medical_test_cases = [
    # (misspelled, correct)
    ("diabetis", "diabetes"),
    ("nuemonia", "pneumonia"),
    ("astma", "asthma"),
    ("alzhiemers", "alzheimers"),
    ("parkinsons desease", "parkinsons disease"),
    ("hipertension", "hypertension"),
    ("artritis", "arthritis"),
    ("catract", "cataract"),
    ("hemmorhage", "hemorrhage"),
    ("seizur", "seizure"),
]

# General misspellings
general_test_cases = [
    ("recieve", "receive"),
    ("occured", "occurred"),
    ("definately", "definitely"),
    ("seperate", "separate"),
    ("neccessary", "necessary"),
    ("accomodate", "accommodate"),
    ("embarass", "embarrass"),
    ("priviledge", "privilege"),
    ("concensus", "consensus"),
    ("ocurrance", "occurrence"),
]

# Homophone test cases
homophone_test_cases = [
    ("The ilium bone is part of the pelvis", "ilium"),  # Should not change
    ("The ileum is part of small intestine", "ileum"),  # Should not change
    ("Their going to the hospital", "They're"),  # Should suggest correction
    ("The patience was discharged", "patient"),  # Should suggest correction
]

def test_accuracy(spellchecker, test_cases, test_name="General"):
    """Test accuracy on known misspellings"""
    print(f"\n{'='*50}")
    print(f"Testing {test_name} Accuracy")
    print(f"{'='*50}")
    
    correct = 0
    total = len(test_cases)
    
    for misspelled, expected in test_cases:
        start_time = time.time()
        result = spellchecker.check_text(misspelled)
        end_time = time.time()
        
        # Check if correction was made
        corrected_text = result['corrected_text'].lower()
        errors = result.get('errors', [])
        
        # For single word tests
        if len(misspelled.split()) == 1:
            is_correct = expected.lower() in corrected_text
        else:
            is_correct = expected.lower() in corrected_text
        
        if is_correct:
            correct += 1
            status = "✓"
        else:
            status = "✗"
            
        # Get top suggestion if available
        top_suggestion = ""
        confidence = 0
        if errors and errors[0]['suggestions']:
            top_suggestion = errors[0]['suggestions'][0]['word']
            confidence = errors[0]['suggestions'][0]['score']
            
        print(f"{status} '{misspelled}' -> '{corrected_text}' (expected: '{expected}')")
        print(f"   Top suggestion: {top_suggestion} (confidence: {confidence:.2%})")
        print(f"   Processing time: {(end_time - start_time)*1000:.2f}ms")
        
    accuracy = correct / total
    print(f"\nAccuracy: {correct}/{total} = {accuracy:.2%}")
    
    return accuracy

def test_context_awareness(spellchecker):
    """Test context-aware corrections"""
    print(f"\n{'='*50}")
    print(f"Testing Context Awareness")
    print(f"{'='*50}")
    
    context_tests = [
        {
            "text": "The patient has a broken humerous",
            "expected_correction": "humerus",
            "context": "medical"
        },
        {
            "text": "That was a humerous joke",
            "expected_correction": "humorous",
            "context": "general"
        },
        {
            "text": "The docter prescribed medication",
            "expected_correction": "doctor",
            "context": "medical"
        },
    ]
    
    for test in context_tests:
        result = spellchecker.check_text(test['text'])
        print(f"\nText: '{test['text']}'")
        print(f"Corrected: '{result['corrected_text']}'")
        print(f"Expected word: '{test['expected_correction']}' (context: {test['context']})")
        
        if result['errors']:
            print("Errors found:")
            for error in result['errors']:
                print(f"  - '{error['original']}' at position {error['position']}")
                print(f"    Type: {error['type']}")
                print(f"    Top suggestions:")
                for i, sugg in enumerate(error['suggestions'][:3]):
                    print(f"      {i+1}. {sugg['word']} ({sugg['score']:.2%})")

def test_performance(spellchecker):
    """Test performance on larger texts"""
    print(f"\n{'='*50}")
    print(f"Testing Performance")
    print(f"{'='*50}")
    
    # Sample medical text with errors
    medical_text = """
    The patiant presented with seveer hedache and nasea. Initial diagnosos 
    suggested migriane, but furthur examination reveeled hypertention. 
    The docter prescribed apropriate medecation for blood presure control.
    Followup apointment scheduled for next weak to moniter progress.
    """
    
    start_time = time.time()
    result = spellchecker.check_text(medical_text, model_type="bigram")
    bigram_time = time.time() - start_time
    
    start_time = time.time()
    result_trigram = spellchecker.check_text(medical_text, model_type="trigram")
    trigram_time = time.time() - start_time
    
    print(f"Text length: {len(medical_text)} characters")
    print(f"Bigram model time: {bigram_time*1000:.2f}ms")
    print(f"Trigram model time: {trigram_time*1000:.2f}ms")
    print(f"Errors found (bigram): {len(result['errors'])}")
    print(f"Errors found (trigram): {len(result_trigram['errors'])}")
    
    # Show statistics
    if result['statistics']:
        print(f"\nError Statistics:")
        stats = result['statistics']
        print(f"  Total errors: {stats['total_errors']}")
        print(f"  Average confidence: {stats['average_confidence']:.2%}")
        print(f"  Medical corrections: {stats['medical_corrections']}")
        print(f"  Error types: {stats['error_types']}")

def main():
    """Run all tests"""
    print("Initializing spellchecker...")
    spellchecker = SpellChecker(config)
    print("Spellchecker initialized!")
    
    # Get model statistics
    model_stats = spellchecker.get_model_statistics()
    print(f"\nModel Statistics:")
    print(f"  Vocabulary size: {model_stats['frequency_model']['vocabulary_size']:,}")
    print(f"  Total words: {model_stats['frequency_model']['total_words']:,}")
    print(f"  Unique bigrams: {model_stats['frequency_model']['unique_bigrams']:,}")
    print(f"  Unique trigrams: {model_stats['frequency_model']['unique_trigrams']:,}")
    
    # Run tests
    medical_accuracy = test_accuracy(spellchecker, medical_test_cases, "Medical Terms")
    general_accuracy = test_accuracy(spellchecker, general_test_cases, "General Terms")
    
    # Test context awareness
    test_context_awareness(spellchecker)
    
    # Test performance
    test_performance(spellchecker)
    
    # Summary
    print(f"\n{'='*50}")
    print(f"Test Summary")
    print(f"{'='*50}")
    print(f"Medical terms accuracy: {medical_accuracy:.2%}")
    print(f"General terms accuracy: {general_accuracy:.2%}")
    print(f"Overall accuracy: {(medical_accuracy + general_accuracy) / 2:.2%}")
    
    # Test the evaluation method
    print(f"\n{'='*50}")
    print(f"Testing Built-in Evaluation Method")
    print(f"{'='*50}")
    
    all_test_cases = medical_test_cases + general_test_cases
    eval_results = spellchecker.evaluate_on_test_set(all_test_cases)
    print(f"Built-in evaluation results:")
    print(f"  Accuracy: {eval_results['accuracy']:.2%}")
    print(f"  Correct predictions: {eval_results['correct_predictions']}/{eval_results['total_tests']}")

if __name__ == "__main__":
    main() 