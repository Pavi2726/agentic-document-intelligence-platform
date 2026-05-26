import os
from typing import Any, Dict, List

import docx2txt
import pypdf
from langchain_text_splitters import RecursiveCharacterTextSplitter


class FileProcessor:
    def __init__(self, chunk_size: int = 300, chunk_overlap: int = 40):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            is_separator_regex=False,
        )

    def extract_text(self, file_path: str) -> str:
        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".txt":
            with open(file_path, "r", encoding="utf-8") as handle:
                return handle.read()

        if ext == ".pdf":
            reader = pypdf.PdfReader(file_path)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            return text

        if ext == ".docx":
            return docx2txt.process(file_path)

        raise ValueError(f"Unsupported file format: {ext}")

    def chunk_text(self, text: str) -> List[str]:
        return self.text_splitter.split_text(text)

    def process_file(self, file_path: str) -> List[Dict[str, Any]]:
        filename = os.path.basename(file_path)
        raw_text = self.extract_text(file_path)
        chunks = self.chunk_text(raw_text)

        processed_chunks = []
        for index, chunk in enumerate(chunks):
            processed_chunks.append(
                {
                    "filename": filename,
                    "chunk_index": index,
                    "text": chunk,
                    "metadata": {"source": filename, "chunk": index},
                }
            )

        return processed_chunks
