from __future__ import annotations

import math
import re


class FixedSizeChunker:
    """
    Chia văn bản thành các đoạn có kích thước cố định, có thể kèm phần chồng lấp.

    Quy tắc:
        - Mỗi đoạn dài tối đa chunk_size ký tự.
        - Các đoạn liền kề chia sẻ overlap ký tự.
        - Đoạn cuối chứa phần văn bản còn lại.
        - Nếu văn bản ngắn hơn chunk_size, trả về [text].
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 50) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        if len(text) <= self.chunk_size:
            return [text]

        step = self.chunk_size - self.overlap
        chunks: list[str] = []
        for start in range(0, len(text), step):
            chunk = text[start : start + self.chunk_size]
            chunks.append(chunk)
            if start + self.chunk_size >= len(text):
                break
        return chunks


class SentenceChunker:
    """
    Chia văn bản thành các đoạn có tối đa max_sentences_per_chunk câu.

    Cách nhận diện câu: tách theo ". ", "! ", "? " hoặc ".\n".
    Loại bỏ khoảng trắng thừa ở mỗi đoạn.
    """

    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []

        sentences = [
            sentence.strip()
            for sentence in re.split(r"(?<=[.!?])(?:\s+|\n+)", text)
            if sentence.strip()
        ]
        chunks: list[str] = []
        for start in range(0, len(sentences), self.max_sentences_per_chunk):
            chunk = " ".join(sentences[start : start + self.max_sentences_per_chunk]).strip()
            if chunk:
                chunks.append(chunk)
        return chunks


class RecursiveChunker:
    """
    Chia văn bản đệ quy bằng các dấu phân tách theo thứ tự ưu tiên.

    Thứ tự dấu phân tách mặc định:
        ["\n\n", "\n", ". ", " ", ""]
    """

    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(self, separators: list[str] | None = None, chunk_size: int = 500) -> None:
        self.separators = self.DEFAULT_SEPARATORS if separators is None else list(separators)
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []

        separators = self.separators or [""]
        return [chunk.strip() for chunk in self._split(text.strip(), separators) if chunk.strip()]

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        if len(current_text) <= self.chunk_size:
            return [current_text]

        if not remaining_separators:
            remaining_separators = [""]

        separator = remaining_separators[0]
        next_separators = remaining_separators[1:]

        if separator == "":
            return [
                current_text[start : start + self.chunk_size]
                for start in range(0, len(current_text), self.chunk_size)
            ]

        if separator not in current_text:
            return self._split(current_text, next_separators)

        parts = [part.strip() for part in current_text.split(separator) if part.strip()]
        chunks: list[str] = []
        buffer = ""

        for part in parts:
            candidate = part if not buffer else f"{buffer}{separator}{part}"
            if len(candidate) <= self.chunk_size:
                buffer = candidate
                continue

            if buffer:
                chunks.append(buffer)
                buffer = ""

            if len(part) <= self.chunk_size:
                buffer = part
            else:
                chunks.extend(self._split(part, next_separators))

        if buffer:
            chunks.append(buffer)

        return chunks


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Tính độ tương đồng cosine giữa hai vector.

    cosine_similarity = dot(a, b) / (||a|| * ||b||)

    Trả về 0.0 nếu một trong hai vector có độ lớn bằng 0.
    """
    magnitude_a = math.sqrt(sum(value * value for value in vec_a))
    magnitude_b = math.sqrt(sum(value * value for value in vec_b))
    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0
    return _dot(vec_a, vec_b) / (magnitude_a * magnitude_b)


class ChunkingStrategyComparator:
    """Chạy tất cả chiến lược chia đoạn có sẵn và so sánh kết quả."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
        strategies = {
            "fixed_size": FixedSizeChunker(chunk_size=chunk_size, overlap=min(50, max(0, chunk_size // 5))),
            "by_sentences": SentenceChunker(max_sentences_per_chunk=3),
            "recursive": RecursiveChunker(chunk_size=chunk_size),
        }

        comparison: dict[str, dict] = {}
        for name, chunker in strategies.items():
            chunks = chunker.chunk(text)
            total_length = sum(len(chunk) for chunk in chunks)
            comparison[name] = {
                "count": len(chunks),
                "avg_length": total_length / len(chunks) if chunks else 0,
                "chunks": chunks,
            }
        return comparison
