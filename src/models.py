from dataclasses import dataclass, field


@dataclass
class Document:
    """
    Tài liệu văn bản với metadata tùy chọn.

    Các trường:
        id:       Chuỗi định danh duy nhất.
        content:  Nội dung văn bản thô.
        metadata: Metadata dạng key-value bất kỳ (ví dụ: source, date, author).
    """

    id: str
    content: str
    metadata: dict = field(default_factory=dict)
