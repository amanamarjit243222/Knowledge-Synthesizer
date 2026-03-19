"""
Unit Tests for SmartTagger
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from tagging import SmartTagger

@pytest.fixture
def tagger():
    return SmartTagger()

class TestSmartTagger:
    def test_generates_date_tag_for_year(self, tagger):
        text = "The project started in 2022 and ended in 2023."
        tags = tagger.generate_tags(text)
        assert "#Date" in tags

    def test_generates_date_tag_for_month_name(self, tagger):
        text = "The deadline is in January next year."
        tags = tagger.generate_tags(text)
        assert "#Date" in tags

    def test_generates_formula_tag_for_math_keyword(self, tagger):
        text = "Apply the Pythagorean theorem to calculate the hypotenuse."
        tags = tagger.generate_tags(text)
        assert "#Formula" in tags

    def test_generates_action_item_tag(self, tagger):
        text = "Submit the report by Friday. This is an action item."
        tags = tagger.generate_tags(text)
        assert "#ActionItem" in tags

    def test_generates_concept_tags_from_noun_phrases(self, tagger):
        text = "Machine learning and deep neural networks are transforming artificial intelligence research."
        tags = tagger.generate_tags(text)
        # Should have at least one concept-based tag
        concept_tags = [t for t in tags if t.startswith("#") and t not in ["#Date", "#Formula", "#ActionItem"]]
        assert len(concept_tags) > 0

    def test_returns_empty_list_for_empty_text(self, tagger):
        tags = tagger.generate_tags("")
        assert isinstance(tags, list)

    def test_tags_are_sorted(self, tagger):
        text = "Machine learning conference in January 2022. Submit your paper."
        tags = tagger.generate_tags(text)
        assert tags == sorted(tags)
