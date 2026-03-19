"""
Integration Tests for the FastAPI /synthesize endpoint.
Requires: pip install httpx pytest
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from fastapi.testclient import TestClient

# We import the app from main.py
from main import app

client = TestClient(app)

class TestSynthesizeEndpoint:
    def test_synthesize_with_valid_text(self):
        """Should return a full analysis object for a text input."""
        response = client.post("/synthesize", data={
            "text": "Quantum computing leverages the principles of quantum mechanics to process information exponentially faster than classical computers.",
            "inputType": "text"
        })
        assert response.status_code == 200
        body = response.json()
        assert "analysis" in body
        assert "graph" in body
        assert "tags" in body["analysis"]
        assert "flashcards" in body["analysis"]["retention"]

    def test_synthesize_with_empty_text_returns_400(self):
        """Should return 400 error for empty or missing text."""
        response = client.post("/synthesize", data={
            "text": "",
            "inputType": "text"
        })
        assert response.status_code == 400

    def test_synthesize_response_has_graph_nodes(self):
        """Should extract graph nodes from the content."""
        response = client.post("/synthesize", data={
            "text": "Artificial intelligence and machine learning are transforming data science and software engineering.",
            "inputType": "text"
        })
        assert response.status_code == 200
        graph = response.json()["graph"]
        assert "nodes" in graph
        assert len(graph["nodes"]) >= 1

    def test_synthesize_tags_are_a_list(self):
        """Tags should always be a list."""
        response = client.post("/synthesize", data={
            "text": "Submit the project by the January 2025 deadline.",
            "inputType": "text"
        })
        assert response.status_code == 200
        assert isinstance(response.json()["analysis"]["tags"], list)
