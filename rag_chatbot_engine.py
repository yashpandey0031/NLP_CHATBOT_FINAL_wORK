from __future__ import annotations
import json, requests
from pathlib import Path
from typing import Generator, Tuple
import faiss, numpy as np
from sentence_transformers import SentenceTransformer

DEFAULT_DATA_FILE = "coral_chatbot_qa_updated (2).json"
MODEL_NAME = "all-MiniLM-L6-v2"
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2"   # change to whichever you pulled


class CoralRAGChatbot:
    def __init__(
        self,
        data_file: str = DEFAULT_DATA_FILE,
        top_k: int = 3,
        score_threshold: float = 0.3,
        ollama_model: str = OLLAMA_MODEL,
    ) -> None:
        self.top_k = top_k
        self.score_threshold = score_threshold
        self.ollama_model = ollama_model
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

    def _build_prompt(self, query: str, contexts: list[str]) -> str:
        context_block = "\n\n".join(
            f"[{i+1}] {ctx}" for i, ctx in enumerate(contexts)
        )
        return f"""You are ReefMind, a coral reef expert assistant.
Use ONLY the context below to answer the question.
If the context doesn't contain enough information, say so clearly.
Do not make up facts about corals.

Context:
{context_block}

Question: {query}

Answer:"""

    def retrieve_contexts(self, query: str) -> list[dict[str, float | str]]:
        query_vec = self.model.encode([query], normalize_embeddings=True)
        query_vec = np.array(query_vec, dtype=np.float32)

        scores, indices = self.index.search(query_vec, k=self.top_k)
        contexts: list[dict[str, float | str]] = []

        for idx, score in zip(indices[0], scores[0]):
            if score > self.score_threshold:
                contexts.append({
                    "text": self.answers[int(idx)],
                    "score": float(score),
                })

        return contexts

    def generate(self, query: str, contexts: list[dict[str, float | str]]) -> Generator[str, None, None]:
        context_texts = [str(item["text"]) for item in contexts]

        if not context_texts:
            yield "Sorry, I couldn't find relevant coral information for that question."
            return

        prompt = self._build_prompt(query, context_texts)
        response = requests.post(
            OLLAMA_URL,
            json={"model": self.ollama_model, "prompt": prompt, "stream": True},
            stream=True,
            timeout=60,
        )
        if response.status_code == 404:
            try:
                error_message = response.json().get("error", "Model not found in Ollama.")
            except ValueError:
                error_message = response.text or "Model not found in Ollama."
            raise RuntimeError(error_message)

        response.raise_for_status()

        for line in response.iter_lines():
            if line:
                chunk = json.loads(line)
                if token := chunk.get("response"):
                    yield token
                if chunk.get("done"):
                    break

    def ask(self, query: str) -> Generator[str, None, None]:
        """Yields streamed tokens from Ollama."""
        greetings = {"hi", "hello", "hey", "hii", "helo"}
        cleaned = query.strip().lower()

        if cleaned in greetings:
            yield "Hi! I'm ReefMind, your coral reef assistant. What would you like to know?"
            return

        if len(cleaned.split()) == 1 and cleaned not in greetings:
            yield "Could you ask a full question? E.g. 'What is coral bleaching?'"
            return

        contexts = self.retrieve_contexts(query)
        yield from self.generate(query, contexts)