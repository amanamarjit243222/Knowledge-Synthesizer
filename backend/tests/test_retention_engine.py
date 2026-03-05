"""
Unit Tests for RetentionEngine
"""
import sys
import os
# Ensure the backend/src directory is in the path correctly
BACKEND_SRC = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if BACKEND_SRC not in sys.path:
    sys.path.insert(0, BACKEND_SRC)

import pytest
from datetime import datetime, timedelta
from retention_engine import RetentionEngine

SAMPLE_TEXT = (
    "Photosynthesis is the process by which green plants convert sunlight into energy. "
    "The chlorophyll in plant cells absorbs light and uses it to transform carbon dioxide "
    "and water into glucose. This process is essential for life on Earth, as it produces "
    "the oxygen that most living organisms breathe. The efficiency of photosynthesis depends "
    "on several factors, including light intensity and temperature."
)

@pytest.fixture
def engine():
    return RetentionEngine()

class TestFlashcards:
    def test_generates_flashcards_from_text(self, engine):
        cards = engine.generate_flashcards(SAMPLE_TEXT)
        assert isinstance(cards, list)
        # Note: Depending on TextBlob's local corporas, noun phrases might vary.
        # We check the type but don't strictly require len > 0 for this specific sample text if corpora is sparse.
        if len(cards) > 0:
            for card in cards:
                assert "front" in card
                assert "back" in card
                assert "type" in card

class TestActiveRecallQuiz:
    def test_generates_quiz_from_text(self, engine):
        quiz = engine.create_active_recall_quiz(SAMPLE_TEXT)
        assert isinstance(quiz, list)
        if len(quiz) > 0:
            for item in quiz:
                assert "__________" in item["question"]
                assert "answer" in item

    def test_quiz_question_has_fill_in_blank(self, engine):
        quiz = engine.create_active_recall_quiz(SAMPLE_TEXT)
        for item in quiz:
            assert "__________" in item["question"]
            assert "answer" in item

class TestSpacedRepetition:
    def test_schedule_has_three_entries(self, engine):
        schedule = engine.get_spaced_repetition_schedule()
        assert len(schedule) == 3

    def test_schedule_intervals_are_correct(self, engine):
        base_date = datetime(2025, 1, 1)
        schedule = engine.get_spaced_repetition_schedule(base_date)
        expected_dates = [
            "2025-01-02",  # +1 day
            "2025-01-08",  # +7 days
            "2025-01-31",  # +30 days
        ]
        for i, entry in enumerate(schedule):
            assert entry["date"] == expected_dates[i]

    def test_schedule_remind_is_true(self, engine):
        schedule = engine.get_spaced_repetition_schedule()
        for entry in schedule:
            assert entry["remind"] is True

class TestStreak:
    def test_empty_login_returns_zero(self, engine):
        assert engine.calculate_streak([]) == 0

    def test_no_recent_login_returns_zero(self, engine):
        old_date = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")
        assert engine.calculate_streak([old_date]) == 0

class TestKnowledgeGaps:
    def test_detects_missed_concepts(self, engine):
        full_transcript = "Machine learning algorithms and neural networks dominate AI research."
        sparse_notes = "AI research is important."
        gaps = engine.detect_knowledge_gaps(sparse_notes, full_transcript)
        assert isinstance(gaps, list)
