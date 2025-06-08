# Sample Test Files for Spellchecker

This directory contains various test files to evaluate the spellchecker's performance across different types of errors and content.

## Test Files

### 1. `medical_errors.txt`
- **Purpose**: Test medical terminology spelling corrections
- **Content**: Patient medical report with common medical misspellings
- **Error types**: Medical terms, drug names, anatomical terms, clinical terminology
- **Key misspellings**: diabetis→diabetes, patiant→patient, medecations→medications, etc.

### 2. `general_errors.txt`
- **Purpose**: Test general English spelling corrections
- **Content**: Business memorandum with common spelling mistakes
- **Error types**: Common English words, business terminology
- **Key misspellings**: neccessary→necessary, ocurr→occur, managment→management, etc.

### 3. `homophone_errors.txt`
- **Purpose**: Test homophone detection and context-aware corrections
- **Content**: Medical case study with homophone confusion
- **Error types**: Medical homophones (ileum/ilium), common homophones (their/there)
- **Special focus**: Context-dependent corrections

### 4. `mixed_content.txt`
- **Purpose**: Test performance on mixed medical and general content
- **Content**: Healthcare administration newsletter
- **Error types**: Combination of medical terms, administrative language, and general errors
- **Complexity**: High - tests the system's ability to handle diverse vocabulary

### 5. `clean_medical.txt`
- **Purpose**: Baseline comparison with correctly spelled medical text
- **Content**: Properly formatted medical report
- **Expected result**: No corrections needed
- **Use case**: Testing false positive rate

### 6. `typo_variations.txt`
- **Purpose**: Test different types of typographical errors
- **Error categories**:
  - Transposition errors (swapped characters)
  - Insertion errors (extra characters)
  - Deletion errors (missing characters)
  - Substitution errors (wrong characters)
  - Keyboard proximity errors
  - Phonetic errors
  - Double letter confusion
  - Common ending errors

### 7. `sample.txt` (original)
- **Purpose**: Simple test with basic errors
- **Content**: Short text with common misspellings

### 8. `sample.docx` (original)
- **Purpose**: Test DOCX file format support
- **Content**: Document with spelling errors in DOCX format

## Usage

These files can be used to:
1. Test the spellchecker through the web interface (upload individually)
2. Test batch processing (select multiple files)
3. Run automated tests using `test_spellchecker.py`
4. Evaluate accuracy across different error types
5. Benchmark performance on various text lengths

## Expected Results

- **Medical files**: Should show high accuracy with medical term prioritization
- **General files**: Should handle common English errors effectively
- **Homophone files**: Should demonstrate context awareness
- **Clean files**: Should produce minimal false positives
- **Typo variations**: Should handle all major error types

## Testing Strategy

1. **Individual Testing**: Upload each file separately to analyze specific error types
2. **Batch Testing**: Process all files together to test system scalability
3. **Model Comparison**: Test with both bigram and trigram models
4. **Performance Metrics**: Monitor processing time and accuracy rates 