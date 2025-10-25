import contextlib
import os
import sys
from pathlib import Path
from typing import List

import fitz
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter


@contextlib.contextmanager
def suppress_stderr():
    with open(os.devnull, "w") as devnull:
        old_stderr = sys.stderr
        sys.stderr = devnull
        try:
            yield
        finally:
            sys.stderr = old_stderr


class DocumentLoader:
    def __init__(self, data_path: str = "data/raw/"):
        self.data_path = data_path

    def _load_pdf_with_pymupdf(self, pdf_path: str) -> List[Document]:
        documents = []

        with fitz.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf):
                text = page.get_text()
                if text.strip():
                    doc = Document(
                        page_content=text,
                        metadata={"source": pdf_path, "page": page_num},
                    )
                    documents.append(doc)

        return documents

    def _load_pdfs(self) -> List[Document]:
        """PDF 파일들을 로드"""
        path = Path(self.data_path)

        if path.is_file():
            print(f"Loading single PDF: {path.name}")
            documents = self._load_pdf_with_pymupdf(str(path))
            print(f"✅ Loaded {len(documents)} pages")

        elif path.is_dir():
            print(f"Loading PDFs from directory: {self.data_path}")
            pdf_files = list(path.glob("**/*.pdf"))
            documents = []

            for pdf_file in pdf_files:
                print(f"{pdf_file.name}... ", end="", flush=True)
                try:
                    docs = self._load_pdf_with_pymupdf(str(pdf_file))
                    print(f"✅ {len(docs)} pages")
                    documents.extend(docs)
                except Exception as e:
                    print(f"❌ Error: {str(e)}")

            print(f"✅ Total: {len(documents)} pages from {len(pdf_files)} PDFs")
        else:
            raise ValueError(f"Path does not exist: {self.data_path}")

        return documents

    def _split_documents(
        self,
        documents: List[Document],
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ) -> List[Document]:
        """문서를 청크로 분할"""
        print(
            f"Splitting documents (chunk_size={chunk_size}, overlap={chunk_overlap})..."
        )

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
            length_function=len,
        )

        chunks = text_splitter.split_documents(documents)
        print(f"✅ Created {len(chunks)} chunks")

        return chunks

    def load_and_split(
        self, chunk_size: int = 1000, chunk_overlap: int = 200
    ) -> List[Document]:
        """문서 로드 및 분할"""
        documents = self._load_pdfs()
        chunks = self._split_documents(documents, chunk_size, chunk_overlap)
        return chunks


if __name__ == "__main__":
    loader = DocumentLoader(data_path="data/raw/")
    chunks = loader.load_and_split()

    print(f"\nFirst chunk preview:")
    print(f"Content: {chunks[0].page_content[:200]}...")
    print(f"Metadata: {chunks[0].metadata}")
