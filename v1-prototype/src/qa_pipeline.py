from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Dict, List

from bedrock_client import BedrockClientManager
from data_ingestion import DocumentLoader
from dotenv import load_dotenv
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS

load_dotenv()


class BatteryQASystem:
    def __init__(
        self,
        data_path: str = "data/raw/",
        vectorstore_path: str = "data/embeddings/battery_vectorstore",
    ):
        self.data_path = data_path
        self.vectorstore_path = vectorstore_path

        print("Initializing Bedrock client...")
        self.bedrock_manager = BedrockClientManager()
        self.embeddings = self.bedrock_manager.get_embeddings()
        self.llm = self.bedrock_manager.get_llm()

        self.vectorstore = None
        self.qa_chain = None

    def build_vectorstore(self, force_rebuild: bool = False):
        vectorstore_file = Path(self.vectorstore_path)

        if vectorstore_file.exists() and not force_rebuild:
            print(f"Loading existing vectorstore from {self.vectorstore_path}")
            self.vectorstore = FAISS.load_local(
                self.vectorstore_path,
                self.embeddings,
                allow_dangerous_deserialization=True,
            )
            print("✅ Vectorstore loaded")
            return

        print("Building new vectorstore...")
        loader = DocumentLoader(data_path=self.data_path)
        chunks = loader.load_and_split()

        print(f"\nCreating embeddings for {len(chunks)} chunks...")

        import time

        from tqdm import tqdm

        batch_size = 50
        start_time = time.time()

        first_batch = chunks[:batch_size]
        print(f"Initializing vectorstore with first {len(first_batch)} chunks...")
        self.vectorstore = FAISS.from_documents(first_batch, self.embeddings)

        remaining_chunks = chunks[batch_size:]
        if remaining_chunks:
            print(f"Adding remaining {len(remaining_chunks)} chunks in batches...")

            for i in tqdm(
                range(0, len(remaining_chunks), batch_size), desc="Processing batches"
            ):
                batch = remaining_chunks[i : i + batch_size]
                self.vectorstore.add_documents(batch)

        elapsed = time.time() - start_time
        print(
            f"✅ Embeddings created in {elapsed:.1f}s ({len(chunks)/elapsed:.1f} chunks/sec)"
        )

        Path(self.vectorstore_path).parent.mkdir(parents=True, exist_ok=True)
        self.vectorstore.save_local(self.vectorstore_path)

        print(f"Vectorstore saved to {self.vectorstore_path}")

    def setup_qa_chain(self, k: int = 3, search_type: str = "similarity"):
        if not self.vectorstore:
            raise ValueError("Vectorstore not loaded. Call build_vectorstore() first.")

        print(f"Setting up QA chain (retrieval: top-{k}, search: {search_type})...")

        retriever = self.vectorstore.as_retriever(
            search_type=search_type, search_kwargs={"k": k}
        )

        template = """
<role>
You are a technical documentation assistant specialized in LG Energy Solution's battery technology, products, and sustainability initiatives. 
You have access to official company documents including ESG reports, annual reports, and technical specifications.
</role>

<guidelines>
1. ACCURACY: Only use information explicitly stated in the provided context
2. SPECIFICITY: Include technical terms, numerical data, and specific details
3. STRUCTURE: Organize answers with clear paragraphs or bullet points
4. SOURCES: Reference document types when making claims (e.g., "According to the ESG Report...")
5. HONESTY: If information is not in the context, state: "This information is not available in the provided documents."
6. PROFESSIONAL: Use technical language appropriate for industry professionals
</guidelines>

<context>
{context}
</context>

<question>
{question}
</question>

<answer_format>
Provide a comprehensive answer that:
- Directly addresses the question
- Includes specific data points and technical details
- Structures information clearly
- Cites relevant document sources
- Acknowledges any limitations in available information
</answer_format>

Answer:"""

        prompt = PromptTemplate(
            template=template, input_variables=["context", "question"]
        )

        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=True,
        )

        print("✅ QA chain ready")

    def ask(self, question: str, verbose: bool = True) -> Dict:
        if not self.qa_chain:
            raise ValueError("QA chain not set up. Call setup_qa_chain() first.")

        if verbose:
            print(f"\nQuestion: {question}")
            print("Searching relevant documents...")

        result = self.qa_chain.invoke({"query": question})
        answer = result["result"]
        source_docs = result["source_documents"]

        if verbose:
            print(f"\nAnswer:\n{answer}\n")
            print(f"Sources ({len(source_docs)} documents):")
            for i, doc in enumerate(source_docs, 1):
                source = doc.metadata.get("source", "Unknown")
                page = doc.metadata.get("page", "N/A")
                print(f"  {i}. {Path(source).name} (page {page})")

        return {
            "question": question,
            "answer": answer,
            "sources": [
                {"content": doc.page_content[:300] + "...", "metadata": doc.metadata}
                for doc in source_docs
            ],
        }

    def batch_ask_parallel(
        self, questions: List[str], max_workers: int = 4
    ) -> List[Dict]:
        print(
            f"\nProcessing {len(questions)} questions in parallel (max {max_workers} workers)..."
        )

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(self.ask, q, verbose=False) for q in questions]

            results = []
            for i, future in enumerate(futures, 1):
                result = future.result()
                print(f"\n{'='*60}")
                print(f"✅ Completed {i}/{len(questions)}")
                print(f"{'='*60}")
                print(f"Question: {result['question']}")
                print(f"\nAnswer:\n{result['answer']}\n")
                print(f"Sources ({len(result['sources'])} documents):")
                for j, src in enumerate(result["sources"], 1):
                    source_name = Path(src["metadata"].get("source", "Unknown")).name
                    page = src["metadata"].get("page", "N/A")
                    print(f"  {j}. {source_name} (page {page})")
                results.append(result)

        return results

    def batch_ask(self, questions: List[str], parallel: bool = True) -> List[Dict]:
        if parallel:
            return self.batch_ask_parallel(questions)

        results = []
        for i, question in enumerate(questions, 1):
            print(f"\n{'='*60}")
            print(f"Question {i}/{len(questions)}")
            print(f"{'='*60}")
            result = self.ask(question)
            results.append(result)

        return results
