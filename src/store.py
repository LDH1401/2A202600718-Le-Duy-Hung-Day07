from __future__ import annotations

from typing import Any, Callable

from .chunking import _dot
from .embeddings import _mock_embed
from .models import Document


class EmbeddingStore:
    """
    Kho vector dành cho các đoạn văn bản.

    Thử dùng ChromaDB nếu có; nếu không thì chuyển sang kho trong bộ nhớ.
    Tham số embedding_fn cho phép truyền mock embeddings khi chạy test.
    """

    def __init__(
        self,
        collection_name: str = "documents",
        embedding_fn: Callable[[str], list[float]] | None = None,
    ) -> None:
        self._embedding_fn = embedding_fn or _mock_embed
        self._collection_name = collection_name
        self._use_chroma = False
        self._store: list[dict[str, Any]] = []
        self._collection = None
        self._next_index = 0

        try:
            import chromadb

            client = chromadb.Client()
            self._collection = client.get_or_create_collection(name=collection_name)
            self._use_chroma = True
        except Exception:
            self._use_chroma = False
            self._collection = None

    def _make_record(self, doc: Document) -> dict[str, Any]:
        metadata = dict(doc.metadata or {})
        metadata["doc_id"] = doc.id
        record_id = f"{self._collection_name}-{id(self)}-{self._next_index}"
        self._next_index += 1
        return {
            "id": record_id,
            "doc_id": doc.id,
            "content": doc.content,
            "metadata": metadata,
            "embedding": self._embedding_fn(doc.content),
        }

    def _search_records(self, query: str, records: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
        if top_k <= 0:
            return []

        query_embedding = self._embedding_fn(query)
        scored_results: list[dict[str, Any]] = []
        for record in records:
            score = _dot(query_embedding, record["embedding"])
            scored_results.append(
                {
                    "id": record["id"],
                    "doc_id": record["doc_id"],
                    "content": record["content"],
                    "metadata": dict(record["metadata"]),
                    "score": float(score),
                }
            )

        scored_results.sort(key=lambda result: result["score"], reverse=True)
        return scored_results[:top_k]

    def add_documents(self, docs: list[Document]) -> None:
        """
        Tạo embedding cho nội dung của từng tài liệu rồi lưu lại.

        Với ChromaDB: dùng collection.add(ids=[...], documents=[...], embeddings=[...])
        Với kho trong bộ nhớ: thêm các dict vào self._store
        """
        records = [self._make_record(doc) for doc in docs]
        self._store.extend(records)

        if self._use_chroma and self._collection is not None and records:
            try:
                self._collection.add(
                    ids=[record["id"] for record in records],
                    documents=[record["content"] for record in records],
                    embeddings=[record["embedding"] for record in records],
                    metadatas=[record["metadata"] for record in records],
                )
            except Exception:
                self._use_chroma = False

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """
        Tìm top_k tài liệu tương đồng nhất với truy vấn.

        Với kho trong bộ nhớ: tính tích vô hướng giữa embedding của truy vấn và mọi embedding đã lưu.
        """
        return self._search_records(query, self._store, top_k)

    def get_collection_size(self) -> int:
        """Trả về tổng số đoạn đang được lưu."""
        return len(self._store)

    def search_with_filter(self, query: str, top_k: int = 3, metadata_filter: dict = None) -> list[dict]:
        """
        Tìm kiếm với bước lọc metadata tùy chọn trước khi tìm kiếm.

        Trước tiên lọc các đoạn đã lưu bằng metadata_filter, sau đó chạy tìm kiếm độ tương đồng.
        """
        if not metadata_filter:
            return self.search(query, top_k=top_k)

        filtered_records = [
            record
            for record in self._store
            if all(record["metadata"].get(key) == value for key, value in metadata_filter.items())
        ]
        return self._search_records(query, filtered_records, top_k)

    def delete_document(self, doc_id: str) -> bool:
        """
        Xóa tất cả đoạn thuộc về một tài liệu.

        Trả về True nếu có đoạn được xóa, ngược lại trả về False.
        """
        ids_to_delete = [
            record["id"]
            for record in self._store
            if record["metadata"].get("doc_id") == doc_id
        ]
        if not ids_to_delete:
            return False

        self._store = [
            record
            for record in self._store
            if record["metadata"].get("doc_id") != doc_id
        ]

        if self._use_chroma and self._collection is not None:
            try:
                self._collection.delete(ids=ids_to_delete)
            except Exception:
                self._use_chroma = False

        return True
