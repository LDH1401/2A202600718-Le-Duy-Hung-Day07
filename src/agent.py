from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    Tác nhân trả lời câu hỏi bằng cơ sở tri thức vector.

    Mẫu sinh câu trả lời tăng cường truy xuất (RAG):
        1. Truy xuất top-k đoạn liên quan từ kho.
        2. Tạo prompt với các đoạn làm ngữ cảnh.
        3. Gọi LLM để sinh câu trả lời.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        results = self.store.search(question, top_k=top_k)
        context = "\n\n".join(
            f"[{index}] {result['content']}"
            for index, result in enumerate(results, start=1)
        )
        if not context:
            context = "Không tìm thấy ngữ cảnh liên quan trong knowledge base."

        prompt = (
            "Bạn là trợ lý trả lời câu hỏi dựa trên ngữ cảnh được cung cấp.\n"
            "Chỉ dùng thông tin trong ngữ cảnh nếu có thể.\n\n"
            f"Ngữ cảnh:\n{context}\n\n"
            f"Câu hỏi: {question}\n"
            "Câu trả lời:"
        )
        return str(self.llm_fn(prompt))
