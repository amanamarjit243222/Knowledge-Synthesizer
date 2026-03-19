import re
from typing import List, Tuple
from textblob import TextBlob
from collections import Counter

class Chapterizer:
    """
    Detects topic shifts in a transcript and inserts automatic headers.
    Uses 'Jaccard Similarity' on sliding windows of text to find where
    vocabulary changes significantly.
    """
    
    def __init__(self, window_size=2, threshold=0.15):
        """
        window_size: Number of sentences to group together for comparison.
        threshold: Similarity score below which a new chapter is created (0.0 to 1.0).
                   Lower = Fewer chapters (stricter). Higher = More chapters.
        """
        self.window_size = window_size
        self.threshold = threshold

    def add_chapters(self, transcript: str) -> str:
        """
        Takes a raw transcript (with or without speaker labels) and returns
        a version with [TOPIC: ...] headers inserted.
        """
        if not transcript or len(transcript) < 50:
            return transcript

        # 1. Split into sentences (preserving speaker labels if possible)
        # We assume sentences might be split by newlines or standard punctuation
        blob = TextBlob(transcript)
        sentences = blob.sentences
        
        if len(sentences) < self.window_size * 2:
            return f"[TOPIC: General Discussion]\n\n{transcript}"

        # 2. Create Blocks (windows of sentences)
        blocks = []
        raw_blocks = [] # To reconstruct text later
        
        for i in range(0, len(sentences), self.window_size):
            # Group 'window_size' sentences into one block
            chunk = sentences[i : i + self.window_size]
            text_chunk = " ".join([str(s) for s in chunk])
            
            blocks.append(self._get_word_set(text_chunk))
            raw_blocks.append(text_chunk)

        # 3. Detect Shifts
        chaptered_text = []
        
        # Always start with an Intro
        first_topic = self._generate_title(raw_blocks[0])
        chaptered_text.append(f"\n[TOPIC: {first_topic}]")
        chaptered_text.append(raw_blocks[0])

        for i in range(1, len(blocks)):
            prev_block = blocks[i-1]
            curr_block = blocks[i]
            
            # Calculate Similarity (Jaccard Index)
            # Intersection of words / Union of words
            intersection = len(prev_block.intersection(curr_block))
            union = len(prev_block.union(curr_block))
            
            similarity = intersection / union if union > 0 else 0.0
            
            # If similarity is VERY low, it's a topic shift
            if similarity < self.threshold:
                # Generate a title for the new section
                title = self._generate_title(raw_blocks[i])
                chaptered_text.append(f"\n\n[TOPIC: {title}]")
            
            chaptered_text.append(raw_blocks[i])

        return "\n".join(chaptered_text)

    def _get_word_set(self, text: str) -> set:
        """Extracts unique meaningful words (nouns/verbs) for comparison."""
        # Simple stopword list
        stops = {'the', 'is', 'at', 'which', 'on', 'and', 'a', 'an', 'in', 'to', 'of', 'for', 'it', 'this', 'that', 'with', 'i', 'you', 'we', 'are'}
        
        blob = TextBlob(text.lower())
        # Filter for words longer than 3 chars that aren't stopwords
        words = {w for w in blob.words if len(w) > 3 and w not in stops}
        return words

    def _generate_title(self, text: str) -> str:
        """Extracts the most frequent noun to use as a header."""
        blob = TextBlob(text)
        nouns = blob.noun_phrases
        
        if not nouns:
            # Fallback to most frequent regular word
            words = [w.lower() for w in blob.words if len(w) > 4]
            if words:
                return Counter(words).most_common(1)[0][0].title()
            return "Discussion"
            
        # Return most common noun phrase
        counts = Counter(nouns)
        return counts.most_common(1)[0][0].title()
