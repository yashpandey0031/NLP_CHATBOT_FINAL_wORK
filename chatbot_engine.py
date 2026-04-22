
from __future__ import annotations

import json
from pathlib import Path
from typing import Tuple

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


DEFAULT_DATA_FILE = "coral_chatbot_qa_updated (2).json"
MODEL_NAME = "all-MiniLM-L6-v2"


class CoralChatbot:
    def __init__(self, data_file: str = DEFAULT_DATA_FILE, threshold: float = 0.4) -> None:
        self.threshold = threshold
        self.data_path = Path(data_file)

        if not self.data_path.is_absolute():
            self.data_path = Path(__file__).resolve().parent / self.data_path

        self.questions, self.answers = self._load_data(self.data_path)
        self.model = SentenceTransformer(MODEL_NAME)
        self.index = self._load_or_build_index()

    @staticmethod
    def _load_data(path: Path) -> Tuple[list[str], list[str]]:
        if not path.exists():
            raise FileNotFoundError(f"Dataset file not found: {path}")

        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        qa_pairs = data.get("coral_chatbot_qa", [])
        if not qa_pairs:
            raise ValueError("Dataset has no 'coral_chatbot_qa' entries.")

        questions = [item["question"] for item in qa_pairs if "question" in item and "answer" in item]
        answers = [item["answer"] for item in qa_pairs if "question" in item and "answer" in item]

        if not questions:
            raise ValueError("No valid question/answer pairs found in dataset.")

        return questions, answers

    def _build_index(self, questions: list[str]) -> faiss.IndexFlatIP:
        question_embeddings = self.model.encode(questions, normalize_embeddings=True)
        question_embeddings = np.array(question_embeddings, dtype=np.float32)

        dimension = question_embeddings.shape[1]
        index = faiss.IndexFlatIP(dimension)
        index.add(question_embeddings)
        return index

    def _cache_paths(self) -> tuple[Path, Path]:
        cache_dir = Path(__file__).resolve().parent / ".cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir / "coral_index.faiss", cache_dir / "coral_index_meta.json"

    def _cache_signature(self) -> dict[str, int | str]:
        stat = self.data_path.stat()
        return {
            "model": MODEL_NAME,
            "data_path": str(self.data_path.resolve()),
            "data_mtime_ns": stat.st_mtime_ns,
            "data_size": stat.st_size,
            "qa_count": len(self.questions),
        }

    def _load_or_build_index(self) -> faiss.IndexFlatIP:
        index_path, meta_path = self._cache_paths()
        current_signature = self._cache_signature()

        if index_path.exists() and meta_path.exists():
            try:
                cached_signature = json.loads(meta_path.read_text(encoding="utf-8"))
                if cached_signature == current_signature:
                    index = faiss.read_index(str(index_path))
                    if index.ntotal == len(self.questions):
                        return index
            except (json.JSONDecodeError, OSError, RuntimeError, ValueError):
                pass

        index = self._build_index(self.questions)
        faiss.write_index(index, str(index_path))
        meta_path.write_text(json.dumps(current_signature, indent=2), encoding="utf-8")
        return index

    def ask(self, query: str) -> tuple[str, float]:
        greetings = {"hi", "hello", "hey", "hii", "helo"}
        cleaned = query.strip().lower()

        if cleaned in greetings:
            query = "Hi! What can you help me with?"
        elif len(cleaned.split()) == 1 and cleaned not in greetings:
            return (
                "Could you ask a full question? For example: 'What corals are found in Australia?' "
                "or 'What is coral bleaching?'",
                0.0,
            )

        query_vec = self.model.encode([query], normalize_embeddings=True)
        query_vec = np.array(query_vec, dtype=np.float32)

        scores, indices = self.index.search(query_vec, k=1)
        best_match_idx = int(indices[0][0])
        best_score = float(scores[0][0])

        if best_score < self.threshold:
            return (
                "Sorry, I'm only trained on coral topics. Try asking about a coral species, "
                "reef habitats, or coral facts!",
                best_score,
            )

        return self.answers[best_match_idx], best_score
