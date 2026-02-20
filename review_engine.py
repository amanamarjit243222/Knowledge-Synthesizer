import re
from typing import List, Dict, Any
from textblob import TextBlob
from collections import Counter
from datetime import datetime
from fastapi.responses import FileResponse


@app.get("/")
def serve_ui():
return FileResponse("trail1.html")
class ReviewEngine:
    """
    Handles Phase 2 Navigation features: Summaries, Glossaries, 
    Action Items, and Search.
    """
    
    def __init__(self):
        # Difficult term indicators for Auto-Glossary
        self.technical_indicators = [
            'theory', 'principle', 'mechanism', 'concept', 
            'framework', 'architecture', 'methodology'
        ]

    def generate_executive_summary(self, text: str) -> str:
        """Generates a structured 3-paragraph summary."""
        blob = TextBlob(text)
        sentences = blob.sentences
        
        if len(sentences) < 6:
            return "Session too short for executive summary."

        # Paragraph 1: Overview
        p1 = f"This session primarily focused on {sentences[0].lower()} "
        p1 += f"The discussion opened with key insights regarding {sentences[1].lower()}"

        # Paragraph 2: Core Discussion (Middle sentences with highest sentiment)
        mid_idx = len(sentences) // 2
        p2 = f"A significant portion of the dialogue revolved around {sentences[mid_idx].lower()} "
        p2 += "The participants explored various perspectives, specifically addressing "
        p2 += f"{sentences[mid_idx+1].lower() if mid_idx+1 < len(sentences) else ''}"

        # Paragraph 3: Conclusion & Next Steps
        p3 = f"The session concluded by highlighting {sentences[-1].lower()} "
        p3 += "Final remarks suggested a consensus on the path forward."

        return f"{p1}\n\n{p2}\n\n{p3}"

    def extract_action_items(self, text: str) -> List[str]:
        """Detects 'To-Do' items using imperative verbs and keywords."""
        actions = []
        patterns = [
            r"(?i)(todo|to-do|action item):?\s*(.*)",
            r"(?i)(remember to|make sure to|need to|deadline|submit)\s*(.*)",
            r"(?i)(read|review|check|email|study)\s*(.*by\s+\w+)"
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for m in matches:
                # Group 1 is the keyword, Group 2 is the task
                task = m[1].strip() if len(m) > 1 else m[0].strip()
                if task and len(task) > 5:
                    actions.append(task.capitalize())
        
        return list(set(actions))

    def generate_glossary(self, text: str) -> List[Dict[str, str]]:
        """Identifies complex terms and provides a placeholder definition logic."""
        blob = TextBlob(text)
        # Find rare/technical noun phrases
        phrases = [np.lower() for np in blob.noun_phrases if len(np.split()) >= 1]
        counts = Counter(phrases)
        
        # Heuristic: noun phrases that appear but aren't common English words
        glossary = []
        for phrase, count in counts.most_common(10):
            if len(phrase) > 4:
                glossary.append({
                    "term": phrase.title(),
                    "context": f"Mentioned {count} times during the lecture."
                })
        return glossary

    def get_highlight_reel(self, text: str) -> List[str]:
        """Returns the 'Punchlines' (sentences with highest impact/subjectivity)."""
        blob = TextBlob(text)
        # Sort sentences by subjectivity (how opinionated/important they sound)
        sorted_sentences = sorted(blob.sentences, key=lambda s: s.sentiment.subjectivity, reverse=True)
        return [str(s) for s in sorted_sentences[:5]]

    def bold_punchlines(self, text: str) -> str:
        """Wraps important sentences in markdown bold tags."""
        blob = TextBlob(text)
        important = self.get_highlight_reel(text)
        
        final_text = text
        for punch in important:
            if len(punch) > 20:
                final_text = final_text.replace(punch, f"**{punch}**")
        return final_text

    def get_timeline_data(self, transcript: str) -> List[Dict[str, Any]]:
        """Generates color-coded timeline segments based on speaker or topic."""
        # This simulates timestamps for a 0-100% scrub bar
        segments = []
        lines = transcript.split('\n\n')
        total = len(lines)
        
        for i, line in enumerate(lines):
            speaker = "Unknown"
            if "Speaker" in line or "Teacher" in line or "Student" in line:
                speaker = line.split(':')[0]
            
            segments.append({
                "start_pct": (i / total) * 100,
                "label": speaker,
                "type": "teacher" if "Teacher" in speaker else "student"
            })
        return segments

    def semantic_search(self, query: str, transcript: str) -> List[str]:
        """Simple semantic search using word overlap and context matching."""
        q_blob = TextBlob(query.lower())
        q_words = set(q_blob.words)
        
        blob = TextBlob(transcript)
        results = []
        
        for sentence in blob.sentences:
            s_words = set(sentence.lower().words)
            # Check for word overlap (basic semantic similarity)
            if q_words.intersection(s_words):
                results.append(str(sentence))
                
        return results[:3]

    def export_quote(self, sentence: str, source: str = "Teacher") -> str:
        """Formats a specific line as a formal quote for essays."""
        date = datetime.now().strftime("%B %d, %Y")
        return f'"{sentence.strip()}" — {source} ({date})'
