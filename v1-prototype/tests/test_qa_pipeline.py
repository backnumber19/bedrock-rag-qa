import os
import sys
from pathlib import Path

import pytest

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from qa_pipeline import BatteryQASystem


class TestBatteryQASystem:

    @pytest.fixture
    def qa_system(self):
        system = BatteryQASystem(
            data_path="data/raw/",
            vectorstore_path="data/embeddings/battery_vectorstore",
        )
        return system

    def test_initialization(self, qa_system):
        assert qa_system is not None
        assert qa_system.bedrock_manager is not None
        assert qa_system.embeddings is not None
        assert qa_system.llm is not None
        assert qa_system.vectorstore is None
        assert qa_system.qa_chain is None

    def test_load_vectorstore(self, qa_system):
        qa_system.build_vectorstore()

        assert qa_system.vectorstore is not None
        results = qa_system.vectorstore.similarity_search("battery", k=1)
        assert len(results) > 0

    def test_setup_qa_chain(self, qa_system):
        qa_system.build_vectorstore()
        qa_system.setup_qa_chain(k=3)

        assert qa_system.qa_chain is not None

    def test_ask_single_question(self, qa_system):
        qa_system.build_vectorstore()
        qa_system.setup_qa_chain(k=3)

        question = "What is NCM battery?"
        result = qa_system.ask(question, verbose=False)

        assert "question" in result
        assert "answer" in result
        assert "sources" in result

        assert result["question"] == question
        assert len(result["answer"]) > 0
        assert len(result["sources"]) > 0
        assert len(result["sources"]) <= 3  # k=3

    def test_batch_ask(self, qa_system):
        qa_system.build_vectorstore()
        qa_system.setup_qa_chain(k=2)

        questions = ["What is NCM battery?", "What are the main products?"]

        results = qa_system.batch_ask(questions)

        assert len(results) == len(questions)
        for i, result in enumerate(results):
            assert result["question"] == questions[i]
            assert len(result["answer"]) > 0

    def test_different_k_values(self, qa_system):
        qa_system.build_vectorstore()

        for k in [1, 2, 3, 5]:
            qa_system.setup_qa_chain(k=k)
            result = qa_system.ask("What is battery?", verbose=False)

            assert len(result["sources"]) <= k


class TestBatteryQASystemIntegration:
    def test_full_pipeline(self):
        qa_system = BatteryQASystem()
        qa_system.build_vectorstore()
        assert qa_system.vectorstore is not None

        qa_system.setup_qa_chain(k=3)
        assert qa_system.qa_chain is not None

        result = qa_system.ask("What is LG Energy Solution?", verbose=False)

        assert result is not None
        assert len(result["answer"]) > 10
        assert len(result["sources"]) > 0

        for source in result["sources"]:
            assert "metadata" in source
            assert "content" in source
