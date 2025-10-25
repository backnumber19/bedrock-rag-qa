# src/qa_pipeline.py
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List

from bedrock_kb_client import BedrockKBClient
from logger import get_logger

logger = get_logger(__name__)


class ProductionQASystem:
    def __init__(self, verbose: bool = False):
        self.client = BedrockKBClient()
        self.verbose = verbose

    def ask(self, question: str) -> Dict:
        if self.verbose:
            logger.info(f"Processing question: {question[:50]}...")

        start_time = time.time()

        try:
            result = self.client.retrieve_and_generate(question)
            elapsed = time.time() - start_time

            if self.verbose:
                logger.info(f"Question processed in {elapsed:.2f}s")

            return {
                "question": question,
                "answer": result["answer"],
                "citations": result["citations"],
                "elapsed_time": elapsed,
                "status": "success",
            }

        except Exception as e:
            logger.error(f"Error processing question: {e}")
            return {"question": question, "error": str(e), "status": "error"}

    def ask_batch(self, questions: List[str], max_workers: int = 4) -> List[Dict]:
        if self.verbose:
            logger.info(f"Processing {len(questions)} questions in parallel")

        start_time = time.time()

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(self.ask, questions))

        elapsed = time.time() - start_time

        if self.verbose:
            logger.info(f"Batch completed in {elapsed:.2f}s")

        return results

    def print_result(self, result: Dict, show_citations: bool = True):
        """Pretty print a single result"""
        print(f"\nQuestion: {result['question']}")
        print("-" * 80)

        if result["status"] == "success":
            print(f"\nAnswer:\n{result['answer']}\n")
            print(
                f"Time: {result['elapsed_time']:.2f}s | Citations: {len(result['citations'])}"
            )

            if show_citations and result["citations"]:
                print("\nSources:")
                for i, citation in enumerate(result["citations"][:3], 1):
                    if "retrievedReferences" in citation:
                        for ref in citation["retrievedReferences"]:
                            if "location" in ref and "s3Location" in ref["location"]:
                                uri = ref["location"]["s3Location"].get("uri", "N/A")
                                filename = uri.split("/")[-1] if "/" in uri else uri
                                print(f"  {i}. {filename}")
        else:
            print(f"\nError: {result.get('error', 'Unknown error')}")

    def print_batch_summary(self, results: List[Dict]):
        """Print batch processing summary"""
        total_time = sum(r["elapsed_time"] for r in results if r["status"] == "success")
        success_count = sum(1 for r in results if r["status"] == "success")

        print("\n" + "=" * 80)
        print("BATCH SUMMARY")
        print("=" * 80)
        print(f"Total questions: {len(results)}")
        print(f"Success: {success_count}/{len(results)}")
        print(f"Total time: {total_time:.2f}s")
        print(f"Average time: {total_time/len(results):.2f}s per question")
        print("=" * 80)


if __name__ == "__main__":
    # CLI mode: verbose logging
    qa = ProductionQASystem(verbose=True)

    print("=" * 80)
    print("PRODUCTION QA SYSTEM TEST")
    print("=" * 80)

    # Single question
    print("\n[1] Single Question Test")
    result = qa.ask("What is LG Energy Solution's main business?")
    qa.print_result(result)

    # Batch questions
    print("\n\n[2] Batch Questions Test")
    questions = [
        "What are the main products?",
        "What is the ESG strategy?",
        "What are the financial highlights?",
        "What is the revenue in 2024?",
        "What is the market share?",
    ]

    results = qa.ask_batch(questions)

    for r in results:
        qa.print_result(r, show_citations=False)

    qa.print_batch_summary(results)
