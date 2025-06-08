
class HomophoneDetector:
    """Detect and handle homophones for better spell correction"""
    
    def __init__(self):
        self.homophone_groups = {
            'ileum': ['ilium'],
            'ilium': ['ileum'],
            'humerus': ['humorous'],
            'humorous': ['humerus'],
            'mucus': ['mucous'],
            'mucous': ['mucus'],
            'perineal': ['peroneal'],
            'peroneal': ['perineal'],
            'discreet': ['discrete'],
            'discrete': ['discreet'],
            'aphagia': ['aphasia'],
            'aphasia': ['aphagia'],
            'their': ['there', 'theyre'],
            'there': ['their', 'theyre'],
            'theyre': ['their', 'there'],
            'to': ['too', 'two'],
            'too': ['to', 'two'],
            'two': ['to', 'too'],
            'your': ['youre'],
            'youre': ['your'],
            'its': ['its'],
            'its': ['its'],
            'affect': ['effect'],
            'effect': ['affect'],
            'accept': ['except'],
            'except': ['accept'],
            'principal': ['principle'],
            'principle': ['principal'],
            'complement': ['compliment'],
            'compliment': ['complement'],
            'stationary': ['stationery'],
            'stationery': ['stationary']
        }
        
    def get_homophones(self, word: str) -> list:
        """Get homophones for a given word"""
        return self.homophone_groups.get(word.lower(), [])
        
    def is_homophone_error(self, original: str, context: list, vocabulary: set) -> tuple:
        """Check if the word might be a homophone error"""
        homophones = self.get_homophones(original)
        
        valid_homophones = [h for h in homophones if h in vocabulary]
        
        if valid_homophones:
            return True, valid_homophones
            
        return False, []
        
    def score_homophone_candidates(self, candidates: list, context: list) -> list:
        """Score homophone candidates based on context"""
        scored = []
        for candidate in candidates:
            score = 0.5
            if any(medical_word in context for medical_word in ['patient', 'diagnosis', 'treatment', 'medical']):
                if candidate in ['ileum', 'ilium', 'humerus', 'mucus', 'mucous', 'perineal', 'peroneal']:
                    score = 0.8
                    
            scored.append((candidate, score))
            
        return sorted(scored, key=lambda x: x[1], reverse=True) 