import re
import string
from typing import Dict, List
from collections import Counter
import math


class AIDetectionService:
    """
    Service for detecting AI-generated text
    Uses heuristic analysis and pattern matching
    """
    
    def __init__(self):
        # Common patterns in AI-generated text
        self.ai_patterns = [
            r'\b(as an AI|I am an AI|I\'m an AI|language model|AI assistant)\b',
            r'\b(I don\'t have|I cannot|I can\'t) (personal|opinions|feelings|emotions|access)\b',
            r'\b(it\'s important to note|it\'s worth noting|it should be noted)\b',
            r'\b(in conclusion|to summarize|in summary|to sum up)\b',
            r'\b(delve into|dive into|exploring|understanding|navigating)\b',
            r'\b(embark on|journey into|landscape of|realm of|world of)\b',
            r'\b(comprehensive guide|step-by-step|detailed overview)\b',
            r'\b(ensure that|make sure|it is crucial|vital to)\b',
            r'\b(ranging from .* to|from .* to .*)\b',
            r'\b(whether you\'re|whether it\'s|regardless of)\b',
            r'\b(first and foremost|last but not least)\b',
            r'\b(pros and cons|advantages and disadvantages)\b',
            r'\b(cutting-edge|state-of-the-art|revolutionary)\b',
            r'\b(game-changer|paradigm shift|transforms the way)\b',
        ]
        
        # Transition words commonly used by AI
        self.ai_transitions = [
            'however', 'furthermore', 'moreover', 'additionally', 'consequently',
            'therefore', 'thus', 'hence', 'nevertheless', 'nonetheless',
            'meanwhile', 'subsequently', 'accordingly', 'likewise', 'similarly'
        ]
        
        # Overused AI words
        self.ai_buzzwords = [
            'leverage', 'optimize', 'utilize', 'facilitate', 'implement',
            'demonstrate', 'indicate', 'comprehensive', 'significant',
            'substantial', 'optimal', 'crucial', 'vital', 'essential',
            'robust', 'seamless', 'innovative', 'revolutionize', 'enhance',
            'streamline', 'dynamic', 'versatile', 'efficient', 'effective'
        ]
    
    def analyze_text(self, text: str) -> Dict:
        """
        Analyze text for AI-generated content indicators
        
        Args:
            text: Text to analyze
            
        Returns:
            Dict with analysis results including probability score
        """
        if not text or len(text.strip()) < 50:
            return {
                "success": False,
                "error": "Text too short for analysis (minimum 50 characters)"
            }
        
        # Calculate various metrics
        pattern_score = self._check_ai_patterns(text)
        structure_score = self._analyze_structure(text)
        vocabulary_score = self._analyze_vocabulary(text)
        consistency_score = self._analyze_consistency(text)
        repetition_score = self._check_repetition(text)
        
        # Weighted average of scores (more weight on patterns and vocabulary)
        overall_score = (
            pattern_score * 0.35 +
            vocabulary_score * 0.25 +
            structure_score * 0.20 +
            consistency_score * 0.15 +
            repetition_score * 0.05
        )
        
        # Determine confidence level (adjusted thresholds)
        if overall_score >= 0.55:
            likelihood = "High"
            message = "This text shows strong indicators of being AI-generated"
        elif overall_score >= 0.35:
            likelihood = "Medium"
            message = "This text shows moderate indicators of being AI-generated"
        elif overall_score >= 0.20:
            likelihood = "Low"
            message = "This text shows some indicators of being AI-generated"
        else:
            likelihood = "Very Low"
            message = "This text appears to be human-written"
        
        return {
            "success": True,
            "ai_probability": round(overall_score * 100, 2),
            "likelihood": likelihood,
            "message": message,
            "metrics": {
                "pattern_score": round(pattern_score * 100, 2),
                "vocabulary_score": round(vocabulary_score * 100, 2),
                "structure_score": round(structure_score * 100, 2),
                "consistency_score": round(consistency_score * 100, 2),
                "repetition_score": round(repetition_score * 100, 2)
            },
            "indicators": self._get_indicators(text),
            "statistics": {
                "word_count": len(text.split()),
                "sentence_count": len(re.split(r'[.!?]+', text)),
                "avg_sentence_length": self._avg_sentence_length(text),
                "unique_word_ratio": self._unique_word_ratio(text)
            }
        }
    
    def _check_ai_patterns(self, text: str) -> float:
        """Check for common AI patterns in text"""
        text_lower = text.lower()
        score = 0.0
        
        # Check for explicit AI patterns (very strong indicator)
        pattern_matches = 0
        for pattern in self.ai_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                pattern_matches += 1
        
        # Strong boost for explicit AI patterns
        if pattern_matches > 0:
            score += min(pattern_matches * 0.25, 0.8)
        
        # Check for transition words (moderate indicator)
        words = text_lower.split()
        if words:
            transition_count = sum(1 for word in words if word.strip(string.punctuation) in self.ai_transitions)
            transition_ratio = transition_count / len(words)
            
            # AI uses transitions 5-15% of the time
            if transition_ratio >= 0.08:
                score += min(transition_ratio * 3, 0.5)
            elif transition_ratio >= 0.05:
                score += 0.2
        
        return min(score, 1.0)
    
    def _analyze_structure(self, text: str) -> float:
        """Analyze text structure for AI characteristics"""
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        
        if len(sentences) < 2:
            return 0.2
        
        score = 0.0
        
        # AI text tends to have very consistent sentence lengths
        lengths = [len(s.split()) for s in sentences]
        avg_length = sum(lengths) / len(lengths)
        variance = sum((l - avg_length) ** 2 for l in lengths) / len(lengths)
        std_dev = math.sqrt(variance)
        
        # Calculate coefficient of variation
        cv = std_dev / avg_length if avg_length > 0 else 1.0
        
        # LOW variance = HIGH AI likelihood (very consistent)
        # Human text typically has CV > 0.4, AI text < 0.35
        if cv < 0.30:
            score += 0.6  # Very AI-like consistency
        elif cv < 0.40:
            score += 0.4  # Somewhat consistent
        else:
            score += 0.1  # More human-like variation
        
        # AI text often has medium-length sentences (12-20 words)
        medium_length_count = sum(1 for length in lengths if 12 <= length <= 20)
        medium_ratio = medium_length_count / len(lengths)
        
        if medium_ratio > 0.6:
            score += 0.4  # Very consistent medium lengths
        elif medium_ratio > 0.4:
            score += 0.2
        
        return min(score, 1.0)
    
    def _analyze_vocabulary(self, text: str) -> float:
        """Analyze vocabulary for AI characteristics"""
        words = re.findall(r'\b\w+\b', text.lower())
        
        if len(words) < 10:
            return 0.2
        
        score = 0.0
        unique_words = set(words)
        diversity = len(unique_words) / len(words)
        
        # Check for AI buzzwords
        buzzword_count = sum(1 for word in words if word in self.ai_buzzwords)
        buzzword_ratio = buzzword_count / len(words)
        
        if buzzword_ratio > 0.03:  # More than 3% buzzwords
            score += 0.5
        elif buzzword_ratio > 0.02:
            score += 0.3
        elif buzzword_ratio > 0.01:
            score += 0.15
        
        # Check for overly formal academic words
        formal_words = [
            'utilize', 'facilitate', 'implement', 'demonstrate', 'indicate',
            'comprehensive', 'significant', 'substantial', 'optimal', 'crucial',
            'moreover', 'furthermore', 'subsequently', 'consequently', 'nevertheless'
        ]
        formal_count = sum(1 for word in words if word in formal_words)
        formal_ratio = formal_count / len(words)
        
        if formal_ratio > 0.04:
            score += 0.4
        elif formal_ratio > 0.02:
            score += 0.2
        
        # AI tends to have moderate diversity (0.45-0.65)
        # Too high or too low is more human
        if 0.45 <= diversity <= 0.65:
            score += 0.3
        
        return min(score, 1.0)
    
    def _analyze_consistency(self, text: str) -> float:
        """Analyze consistency patterns typical of AI"""
        score = 0.0
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        
        # Check for consistent punctuation
        punctuation_count = text.count(',') + text.count(';') + text.count(':')
        words_count = len(text.split())
        punctuation_ratio = punctuation_count / words_count if words_count > 0 else 0
        
        # AI tends to have very consistent punctuation (0.08-0.15)
        if 0.08 <= punctuation_ratio <= 0.15:
            score += 0.5
        elif 0.05 <= punctuation_ratio <= 0.18:
            score += 0.25
        
        # Check for paragraph consistency
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        if len(paragraphs) > 1:
            para_lengths = [len(p.split()) for p in paragraphs]
            para_avg = sum(para_lengths) / len(para_lengths)
            para_variance = sum((l - para_avg) ** 2 for l in para_lengths) / len(para_lengths)
            para_std = math.sqrt(para_variance)
            para_cv = para_std / para_avg if para_avg > 0 else 1.0
            
            # LOW paragraph variation = HIGH AI likelihood
            if para_cv < 0.25:
                score += 0.5  # Very consistent paragraphs
            elif para_cv < 0.40:
                score += 0.3
        
        return min(score, 1.0)
    
    def _check_repetition(self, text: str) -> float:
        """Check for repetitive patterns typical of AI"""
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        
        if len(sentences) < 3:
            return 0.0
        
        score = 0.0
        
        # Check for sentences starting with same words
        starts = [s.split()[0].lower() if s.split() else '' for s in sentences]
        start_counts = Counter(starts)
        
        # AI often starts multiple sentences the same way
        for count in start_counts.values():
            if count > 2:
                score += 0.3
                break
        
        # Check for repeated phrases
        bigrams = []
        for sentence in sentences:
            words = sentence.lower().split()
            if len(words) >= 2:
                bigrams.extend([f"{words[i]} {words[i+1]}" for i in range(len(words)-1)])
        
        if bigrams:
            bigram_counts = Counter(bigrams)
            repeated = sum(1 for count in bigram_counts.values() if count > 2)
            if repeated > 0:
                score += min(repeated * 0.2, 0.5)
        
        return min(score, 1.0)
    
    def _get_indicators(self, text: str) -> List[str]:
        """Get specific indicators found in the text"""
        indicators = []
        text_lower = text.lower()
        words = text_lower.split()
        
        # Check for explicit AI patterns
        if re.search(r'\b(as an AI|I am an AI|language model|AI assistant)\b', text_lower):
            indicators.append("❌ Contains explicit AI self-reference phrases")
        
        if re.search(r'\b(it\'s important to note|it\'s worth noting|it should be noted)\b', text_lower):
            indicators.append("⚠️ Uses common AI hedging phrases")
        
        if re.search(r'\b(delve into|dive into|embark on|journey into|landscape of)\b', text_lower):
            indicators.append("⚠️ Uses AI-typical metaphorical language")
        
        # Check buzzwords
        if words:
            buzzword_count = sum(1 for word in words if word.strip(string.punctuation) in self.ai_buzzwords)
            buzzword_ratio = buzzword_count / len(words)
            if buzzword_ratio > 0.02:
                indicators.append(f"⚠️ High usage of AI buzzwords ({buzzword_count} instances)")
        
        # Check transition words
        if words:
            transition_count = sum(1 for word in words if word.strip(string.punctuation) in self.ai_transitions)
            transition_ratio = transition_count / len(words)
            if transition_ratio > 0.07:
                indicators.append(f"⚠️ Excessive formal transition words ({round(transition_ratio*100, 1)}%)")
        
        # Check structure consistency
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        if len(sentences) > 2:
            lengths = [len(s.split()) for s in sentences]
            avg_length = sum(lengths) / len(lengths)
            variance = sum((l - avg_length) ** 2 for l in lengths) / len(lengths)
            std_dev = math.sqrt(variance)
            cv = std_dev / avg_length if avg_length > 0 else 1.0
            
            if cv < 0.30:
                indicators.append("⚠️ Unnaturally consistent sentence structure")
        
        # Check for balanced paragraphs
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        if len(paragraphs) > 2:
            para_lengths = [len(p.split()) for p in paragraphs]
            if max(para_lengths) - min(para_lengths) < 30:
                indicators.append("⚠️ Uniformly balanced paragraph lengths")
        
        # Check repetitive starts
        if len(sentences) > 3:
            starts = [s.split()[0].lower() if s.split() else '' for s in sentences]
            start_counts = Counter(starts)
            max_repeat = max(start_counts.values())
            if max_repeat > 2:
                most_common_word = max(start_counts, key=start_counts.get)
                indicators.append(f"⚠️ Repetitive sentence openings ('{most_common_word}' used {max_repeat} times)")
        
        if not indicators:
            indicators.append("✓ No strong AI indicators detected")
        
        return indicators
    
    def _avg_sentence_length(self, text: str) -> float:
        """Calculate average sentence length"""
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        if not sentences:
            return 0
        total_words = sum(len(s.split()) for s in sentences)
        return round(total_words / len(sentences), 2)
    
    def _unique_word_ratio(self, text: str) -> float:
        """Calculate ratio of unique words to total words"""
        words = re.findall(r'\b\w+\b', text.lower())
        if not words:
            return 0
        return round(len(set(words)) / len(words), 2)


# Create singleton instance
ai_detection_service = AIDetectionService()
