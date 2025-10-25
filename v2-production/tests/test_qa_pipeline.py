import os
import sys
from pathlib import Path

import pytest

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)
from qa_pipeline import ProductionQASystem


@pytest.fixture
def qa_system():
    return ProductionQASystem()


def test_single_query(qa_system):
    result = qa_system.ask("What is LG Energy Solution?")

    assert result["status"] == "success"
    assert "answer" in result
    assert len(result["answer"]) > 0
    assert result["elapsed_time"] > 0


def test_batch_queries(qa_system):
    questions = ["What are the main products?", "What is the revenue?"]

    results = qa_system.ask_batch(questions)

    assert len(results) == 2
    assert all(r["status"] == "success" for r in results)
