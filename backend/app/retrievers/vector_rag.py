from __future__ import annotations

import os
import pickle

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from app.core.config import settings
from app.tools.file_processor import FileProcessor


class VectorRAGStore:
    def __init__(self):
        self.vector_store_dir = settings.VECTOR_STORE_DIR
        self.index_path = os.path.join(self.vector_store_dir, "index.faiss")
        self.metadata_path = os.path.join(self.vector_store_dir, "metadata.pkl")
        self.model = None
        self.index = None
        self.metadata = []
        self.chunk_embeddings = None
        self.active_document = None
        os.makedirs(self.vector_store_dir, exist_ok=True)
        self.load_index()

    def set_active_document(self, filename: str) -> None:
        self.active_document = filename

    def _ensure_model(self) -> None:
        if self.model is None:
            self.model = SentenceTransformer("all-mpnet-base-v2", device="cpu")

    def _embedding_dimension(self) -> int:
        self._ensure_model()
        return self.model.get_sentence_embedding_dimension()

    def _ensure_chunk_embeddings(self) -> None:
        if self.chunk_embeddings is not None:
            return

        if not self.metadata:
            self.chunk_embeddings = np.empty((0, self._embedding_dimension()), dtype="float32")
            return

        self._ensure_model()
        texts = [chunk.get("text", "") for chunk in self.metadata]
        self.chunk_embeddings = np.asarray(self.model.encode(texts, normalize_embeddings=True), dtype="float32")

    def _deduplicate_metadata(self, chunks):
        deduplicated = []
        seen_keys = set()
        for chunk in chunks:
            key = (chunk.get("filename"), chunk.get("chunk_index"))
            if key in seen_keys:
                continue

            seen_keys.add(key)
            deduplicated.append(chunk)

        return deduplicated

    def load_index(self) -> None:
        """Load all indexed documents from metadata file."""
        if os.path.exists(self.metadata_path):
            with open(self.metadata_path, "rb") as handle:
                loaded = pickle.load(handle)

            if isinstance(loaded, dict):
                self.metadata = loaded.get("metadata", [])
                self.active_document = loaded.get("active_document")
            else:
                self.metadata = loaded

        if not self.active_document and self.metadata:
            self.active_document = self.metadata[-1].get("filename")

        if self.metadata:
            self.metadata = self._deduplicate_metadata(self.metadata)

        # DON'T filter by active_document - keep ALL documents for search
        # if self.active_document:
        #     self.metadata = [chunk for chunk in self.metadata if chunk.get("filename") == self.active_document]
        #     self.metadata = self._deduplicate_metadata(self.metadata)

        self.chunk_embeddings = None
        self.index = None

        if self.metadata:
            self.save_index()

    def save_index(self) -> None:
        if self.index is not None:
            faiss.write_index(self.index, self.index_path)

        with open(self.metadata_path, "wb") as handle:
            pickle.dump({"metadata": self.metadata, "active_document": self.active_document}, handle)

    def _embed_texts(self, texts):
        self._ensure_model()
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        return np.asarray(embeddings, dtype="float32")

    def index_chunks(self, chunks) -> int:
        """Index new chunks and ADD them to existing metadata."""
        if not chunks:
            return 0

        # Load existing metadata first
        self.load_index()

        self._ensure_model()
        texts = [chunk["text"] for chunk in chunks]
        new_embeddings = self._embed_texts(texts)

        # Add new chunks to metadata
        for chunk in chunks:
            self.metadata.append(
                {
                    "filename": chunk.get("filename"),
                    "text": chunk.get("text"),
                    "chunk_index": chunk.get("chunk_index"),
                    "metadata": chunk.get("metadata", {}),
                }
            )

        # Rebuild embeddings for ALL chunks
        all_texts = [chunk.get("text", "") for chunk in self.metadata]
        self.chunk_embeddings = self._embed_texts(all_texts)

        # Rebuild FAISS index with all embeddings
        self.index = faiss.IndexFlatIP(self.chunk_embeddings.shape[1])
        self.index.add(self.chunk_embeddings)

        self.active_document = chunks[0].get("filename")
        self.save_index()
        return len(chunks)

    def index_file(self, file_path: str) -> int:
        processor = FileProcessor()
        chunks = processor.process_file(file_path)
        return self.index_chunks(chunks)

    def search(self, query: str, top_k: int = 5, filename: str | None = None):
        """Search for relevant chunks. If filename is None, search ALL documents."""
        if not self.metadata:
            return []

        self._ensure_model()
        self._ensure_chunk_embeddings()

        query_embedding = np.asarray(self.model.encode([query], normalize_embeddings=True), dtype="float32")
        
        # If filename specified, search only that file
        if filename:
            candidate_indices = [index for index, chunk in enumerate(self.metadata) if chunk.get("filename") == filename]
        else:
            # Search ALL documents
            candidate_indices = list(range(len(self.metadata)))

        if not candidate_indices:
            return []

        candidate_embeddings = self.chunk_embeddings[candidate_indices]
        scores = np.dot(candidate_embeddings, query_embedding.T).reshape(-1)
        sorted_indices = np.argsort(scores)[::-1][: min(top_k, len(scores))]

        results = []
        for sorted_index in sorted_indices:
            actual_index = candidate_indices[int(sorted_index)]
            chunk = self.metadata[actual_index]
            results.append(
                {
                    "score": float(scores[sorted_index]),
                    "filename": chunk.get("filename"),
                    "chunk_index": chunk.get("chunk_index"),
                    "text": chunk.get("text"),
                    "metadata": chunk.get("metadata", {}),
                }
            )

        return results

    def has_documents(self) -> bool:
        return len(self.metadata) > 0


vector_rag = VectorRAGStore()
