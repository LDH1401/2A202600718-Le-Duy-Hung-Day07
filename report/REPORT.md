# Báo Cáo Lab 7: Embedding & Vector Store

**Họ tên:** Lê Duy Hùng - 2A202600718
**Nhóm** C2-C401
**Ngày:** 05-06-2026

---

## 1. Warm-up (5 điểm)

### Cosine Similarity (Ex 1.1)

**High cosine similarity nghĩa là gì?**
> High cosine similarity nghĩa là hai vector embedding có hướng gần giống nhau, tức là hai đoạn văn bản có ý nghĩa/ngữ cảnh tương tự nhau. Điểm càng gần 1 thì mức độ tương đồng về nghĩa càng cao.

**Ví dụ HIGH similarity:**
- Sentence A: Python is a popular programming language for data science.
- Sentence B: Python is widely used for data analysis and machine learning.
- Tại sao tương đồng: Cả hai câu đều nói về Python và việc sử dụng Python trong lĩnh vực dữ liệu/machine learning.

**Ví dụ LOW similarity:**
- Sentence A: Python is a popular programming language for data science.
- Sentence B: The weather today is sunny and warm.
- Tại sao khác: Hai câu nói về hai chủ đề hoàn toàn khác nhau: lập trình/dữ liệu và thời tiết.

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**
> Cosine similarity tập trung vào hướng của vector, nên phù hợp để đo mức độ giống nhau về nghĩa giữa các embedding. Euclidean distance phụ thuộc nhiều hơn vào độ dài vector, trong khi với text embeddings ta thường quan tâm hai văn bản có cùng hướng ngữ nghĩa hay không.

### Chunking Math (Ex 1.2)

**Document 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:* `num_chunks = ceil((doc_length - overlap) / (chunk_size - overlap)) = ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = ceil(22.11) = 23`
> *Đáp án:* 23 chunks.

**Nếu overlap tăng lên 100, chunk count thay đổi thế nào? Tại sao muốn overlap nhiều hơn?**
> Khi overlap tăng lên 100: `ceil((10000 - 100) / (500 - 100)) = ceil(9900 / 400) = ceil(24.75) = 25`, nên số chunk tăng từ 23 lên 25. Overlap nhiều hơn giúp giữ ngữ cảnh giữa các chunk liền kề tốt hơn, nhưng đổi lại tạo ra nhiều chunk hơn và có thể làm retrieval tốn chi phí hơn.

---

## 2. Document Selection — Nhóm (10 điểm)

### Domain & Lý Do Chọn

**Domain:** Tin tức công nghệ, AI và khoa học tiếng Việt

**Tại sao nhóm chọn domain này?**
> Nhóm chọn domain tin tức công nghệ, AI và khoa học tiếng Việt vì bộ dữ liệu mới gồm 20 bài `.md` có chủ đề đa dạng nhưng vẫn cùng nhóm nội dung công nghệ. Các bài viết bao phủ AI, sản phẩm tiêu dùng, vũ trụ, sinh học, lượng tử, chuyển đổi số, tiền số và hạ tầng dữ liệu, nên phù hợp để kiểm thử semantic retrieval trên nhiều kiểu câu hỏi khác nhau. Vì toàn bộ tài liệu chính là tiếng Việt, nhóm cũng có thể đánh giá retrieval trong bối cảnh ngôn ngữ sát với người dùng Việt Nam.

### Data Inventory

| # | Tên tài liệu | Nguồn | Số ký tự | Metadata đã gán |
|---|--------------|-------|----------|-----------------|
| 1 | Microsoft lộ kế hoạch khiến người dùng nghiện Scout | `data/01_Microsoft lộ 'kế hoạch khiến người dùng nghiện Scout'.md` | 4620 | `category=ai_agent`, `language=vi`, `source=01_Microsoft...md`, `doc_type=news_article` |
| 2 | Nhà sáng lập Google X nói về AI và cách làm mới | `data/02_Nhà sáng lập Google X 'Không thể theo lối cũ khi AI đã làm tốt hơn'.md` | 7497 | `category=ai_interview`, `language=vi`, `source=02_Nhà sáng lập...md`, `doc_type=news_article` |
| 3 | Chính phủ đặt mục tiêu có sản phẩm công nghệ chiến lược | `data/03_Chính phủ đặt mục tiêu có sản phẩm công nghệ chiến lược trong năm nay.md` | 3954 | `category=government_tech`, `language=vi`, `source=03_Chính phủ...md`, `doc_type=news_article` |
| 4 | Mỹ loại bỏ 23 triệu kg cá chép xâm hại | `data/04_Mỹ loại bỏ 23 triệu kg cá chép xâm hại.md` | 2732 | `category=environment_science`, `language=vi`, `source=04_Mỹ loại bỏ...md`, `doc_type=news_article` |
| 5 | Lần đầu chỉnh sửa chính xác gene phôi người | `data/05_Lần đầu chỉnh sửa chính xác gene phôi người.md` | 6269 | `category=biotech`, `language=vi`, `source=05_Lần đầu...md`, `doc_type=news_article` |
| 6 | AI giúp Apple App Store đạt quy mô kỷ lục | `data/06_AI giúp Apple App Store đạt quy mô kỷ lục 1,4 nghìn tỷ USD.md` | 2658 | `category=ai_economy`, `language=vi`, `source=06_AI giúp Apple...md`, `doc_type=news_article` |
| 7 | iPhone 18 Pro lộ dung lượng pin | `data/07_iPhone 18 Pro lộ dung lượng pin.md` | 1819 | `category=consumer_tech`, `language=vi`, `source=07_iPhone 18 Pro...md`, `doc_type=news_article` |
| 8 | Tai nghe chụp tai đầu tiên của Xiaomi | `data/08_Tai nghe chụp tai đầu tiên của Xiaomi giá 2,09 triệu đồng.md` | 6993 | `category=consumer_audio`, `language=vi`, `source=08_Tai nghe...md`, `doc_type=news_article` |
| 9 | Blue Origin muốn phóng lại tên lửa trước cuối năm | `data/09_Blue Origin muốn phóng lại tên lửa trước cuối năm nay.md` | 2736 | `category=space`, `language=vi`, `source=09_Blue Origin...md`, `doc_type=news_article` |
| 10 | Ứng dụng mô hình 4 lớp trong chuyển đổi số cấp xã, phường | `data/10_Ứng dụng mô hình 4 lớp trong chuyển đổi số cấp xã, phường.md` | 3671 | `category=digital_government`, `language=vi`, `source=10_Ứng dụng...md`, `doc_type=news_article` |
| 11 | Mô hình ngôn ngữ lớn tiếng Việt 120 tỷ tham số | `data/11_Mô hình ngôn ngữ lớn tiếng Việt với 120 tỷ tham số.md` | 3676 | `category=vietnamese_llm`, `language=vi`, `source=11_Mô hình...md`, `doc_type=news_article` |
| 12 | Giá tiền ảo Pi lại sập mạnh | `data/12_Giá tiền ảo Pi lại 'sập' mạnh.md` | 4628 | `category=crypto`, `language=vi`, `source=12_Giá tiền ảo Pi...md`, `doc_type=news_article` |
| 13 | Tàu quỹ đạo Sao Hỏa của NASA dừng hoạt động | `data/13_Tàu quỹ đạo Sao Hỏa của NASA dừng hoạt động sau 11 năm.md` | 2552 | `category=space`, `language=vi`, `source=13_Tàu quỹ đạo...md`, `doc_type=news_article` |
| 14 | Cần cẩu lớn nhất thế giới lắp đặt lò phản ứng hạt nhân | `data/14_Cần cẩu lớn nhất thế giới lắp đặt lò phản ứng hạt nhân.md` | 2262 | `category=nuclear_engineering`, `language=vi`, `source=14_Cần cẩu...md`, `doc_type=news_article` |
| 15 | Tham vọng xây trung tâm dữ liệu vũ trụ của Musk | `data/15_Tham vọng xây trung tâm dữ liệu vũ trụ của Musk khó thành.md` | 4914 | `category=space_ai_infrastructure`, `language=vi`, `source=15_Tham vọng...md`, `doc_type=news_article` |
| 16 | Microsoft ra chip lượng tử mới với sự trợ giúp của AI | `data/16_Microsoft ra chip lượng tử mới 'với sự trợ giúp của AI'.md` | 5198 | `category=quantum_computing`, `language=vi`, `source=16_Microsoft ra chip...md`, `doc_type=news_article` |
| 17 | Sinh viên hào hứng với AI nhưng bất định về tương lai | `data/17_'Sinh viên hào hứng với AI, nhưng thấy bất định về tương lai'.md` | 10947 | `category=ai_education`, `language=vi`, `source=17_Sinh viên...md`, `doc_type=news_article` |
| 18 | Nước sạch có thể là rủi ro khi SpaceX IPO | `data/18_Nước sạch có thể là rủi ro khi SpaceX tiến hành IPO.md` | 2336 | `category=ai_infrastructure`, `language=vi`, `source=18_Nước sạch...md`, `doc_type=news_article` |
| 19 | Microsoft ra tác nhân tự chủ tương tự OpenClaw | `data/19_Microsoft ra tác nhân tự chủ tương tự OpenClaw.md` | 3397 | `category=ai_agent`, `language=vi`, `source=19_Microsoft ra tác nhân...md`, `doc_type=news_article` |
| 20 | AI giúp công ty châu Âu không phải tìm đường đến Mỹ | `data/20_AI giúp công ty châu Âu không phải 'tìm đường' đến Mỹ.md` | 3759 | `category=ai_startup`, `language=vi`, `source=20_AI giúp công ty...md`, `doc_type=news_article` |

### Metadata Schema

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho retrieval? |
|----------------|------|---------------|-------------------------------|
| `category` | string | `ai_agent`, `space`, `biotech`, `crypto` | Giúp lọc theo chủ đề khi query hỏi về một mảng cụ thể như AI, vũ trụ, sinh học hay tiền số. |
| `language` | string | `vi` | Toàn bộ bộ dữ liệu chính là tiếng Việt, trường này giúp giữ khả năng mở rộng nếu sau này thêm tài liệu tiếng Anh. |
| `source` | string | `data/11_Mô hình ngôn ngữ lớn tiếng Việt với 120 tỷ tham số.md` | Giúp truy vết câu trả lời về bài gốc để kiểm tra chunk nào hỗ trợ gold answer. |
| `doc_type` | string | `news_article` | Giúp phân biệt nhóm bài báo với các tài liệu mẫu cũ như notes, playbook hoặc design docs. |

---

## 3. Chunking Strategy — Cá nhân chọn, nhóm so sánh (15 điểm)

### Baseline Analysis

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Strategy | Chunk Count | Avg Length | Preserves Context? |
|-----------|----------|-------------|------------|-------------------|
| Mô hình ngôn ngữ lớn tiếng Việt với 120 tỷ tham số | FixedSizeChunker (`fixed_size`) | 9 | 452.9 | Trung bình: chunk đều nhưng có thể cắt ngang ý. |
| Mô hình ngôn ngữ lớn tiếng Việt với 120 tỷ tham số | SentenceChunker (`by_sentences`) | 7 | 522.9 | Tốt: giữ ranh giới câu, nhưng một số chunk hơi dài. |
| Mô hình ngôn ngữ lớn tiếng Việt với 120 tỷ tham số | RecursiveChunker (`recursive`) | 12 | 304.5 | Tốt nhất: ưu tiên giữ đoạn văn và kiểm soát kích thước. |
| Microsoft ra chip lượng tử mới với sự trợ giúp của AI | FixedSizeChunker (`fixed_size`) | 12 | 479.0 | Trung bình: ổn về kích thước nhưng dễ cắt giữa câu. |
| Microsoft ra chip lượng tử mới với sự trợ giúp của AI | SentenceChunker (`by_sentences`) | 10 | 517.7 | Khá tốt: dễ đọc nhưng chunk dài hơn mục tiêu. |
| Microsoft ra chip lượng tử mới với sự trợ giúp của AI | RecursiveChunker (`recursive`) | 15 | 344.7 | Tốt nhất: chia theo cấu trúc đoạn, ít mất ngữ cảnh. |
| Sinh viên hào hứng với AI nhưng bất định về tương lai | FixedSizeChunker (`fixed_size`) | 25 | 485.9 | Trung bình: phù hợp bài dài nhưng đôi khi cắt ngang câu hỏi/phỏng vấn. |
| Sinh viên hào hứng với AI nhưng bất định về tương lai | SentenceChunker (`by_sentences`) | 27 | 403.2 | Tốt: giữ câu hỏi và câu trả lời rõ hơn fixed-size. |
| Sinh viên hào hứng với AI nhưng bất định về tương lai | RecursiveChunker (`recursive`) | 34 | 320.0 | Tốt nhất: giữ đoạn hỏi-đáp nhỏ, dễ retrieve đúng chi tiết. |

### Strategy Của Tôi

**Loại:** FixedSizeChunker kích thước lớn (`chunk_size=600`, `overlap=100`) — Thành viên 2

**Mô tả cách hoạt động:**
> Strategy của tôi dùng `FixedSizeChunker(chunk_size=600, overlap=100)`. Cách này chia văn bản thành các chunk tối đa 600 ký tự, trong đó hai chunk liền kề chồng lấp 100 ký tự để giảm nguy cơ mất ngữ cảnh ở ranh giới cắt. So với fixed-size nhỏ của thành viên 1, cấu hình này tạo ít chunk hơn và mỗi chunk chứa nhiều thông tin hơn. Mục tiêu của tôi là kiểm tra xem chunk lớn có giúp retrieval giữ đủ bối cảnh cho các câu hỏi tổng hợp hay không.

**Tại sao tôi chọn strategy này cho domain nhóm?**
> Bộ dữ liệu của nhóm gồm các bài báo tiếng Việt, trong đó nhiều câu hỏi benchmark yêu cầu tổng hợp nhiều chi tiết trong cùng một bài hoặc nhiều bài. Chunk lớn có thể giữ nhiều câu liên quan trong cùng một đơn vị retrieval, giúp agent có thêm ngữ cảnh khi trả lời các câu hỏi tổng hợp. Tôi chọn overlap 100 ký tự để các ý nằm gần ranh giới chunk vẫn có cơ hội xuất hiện ở cả hai chunk liền kề.

**Code snippet (nếu custom):**
```python
from src import FixedSizeChunker

chunker = FixedSizeChunker(chunk_size=600, overlap=100)
chunks = chunker.chunk(article_text)
```

### So Sánh: Strategy của tôi vs Baseline

| Tài liệu | Strategy | Chunk Count | Avg Length | Retrieval Quality? |
|-----------|----------|-------------|------------|--------------------|
| Mô hình ngôn ngữ lớn tiếng Việt với 120 tỷ tham số | best baseline: SentenceChunker | 7 | 522.9 | Khá: giữ câu đầy đủ nhưng chunk hơi dài, có thể chứa nhiều ý. |
| Mô hình ngôn ngữ lớn tiếng Việt với 120 tỷ tham số | **của tôi: FixedSizeChunker 600/100** | 8 | 547.0 | Khá: giữ nhiều bối cảnh quanh chi tiết "120 tỷ tham số", nhưng có thể cắt ngang đoạn tự nhiên. |
| Microsoft ra chip lượng tử mới với sự trợ giúp của AI | best baseline: SentenceChunker | 10 | 517.7 | Khá: readable nhưng có nguy cơ gom nhiều thông tin kỹ thuật vào một chunk. |
| Microsoft ra chip lượng tử mới với sự trợ giúp của AI | **của tôi: FixedSizeChunker 600/100** | 11 | 563.5 | Khá: chunk lớn giữ được nhiều chi tiết kỹ thuật, nhưng độ tập trung thấp hơn recursive. |
| Sinh viên hào hứng với AI nhưng bất định về tương lai | best baseline: SentenceChunker | 27 | 403.2 | Tốt: giữ câu hỏi/trả lời trong bài phỏng vấn tương đối rõ. |
| Sinh viên hào hứng với AI nhưng bất định về tương lai | **của tôi: FixedSizeChunker 600/100** | 22 | 593.0 | Khá: ít chunk hơn và giữ nhiều ngữ cảnh phỏng vấn, nhưng có thể cắt giữa câu hỏi và câu trả lời. |

### So Sánh Với Thành Viên Khác

**Cách chấm:** Chạy cùng 5 benchmark queries của nhóm trên từng strategy, lấy top-3 retrieved chunks. `Retrieval Score = số query có ít nhất 1 chunk đúng gold answer trong top-3 / 5 * 10`. Query #3 dùng `metadata_filter={"category": "space"}`. Kết quả dưới đây chạy bằng `_mock_embed`, nên score dùng để so sánh tương đối giữa strategy, chưa phải chất lượng semantic retrieval thật.

| Thành viên | Strategy | Retrieval Score (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Nguyễn Văn Đoan - 2A202600795| FixedSizeChunker nhỏ (`chunk_size=200`, `overlap=20`) | 4.0 | Tạo chunk rất ngắn, trung bình khoảng 197 ký tự/chunk, nên dễ bắt các chi tiết nhỏ và ít gom nhiều ý không liên quan. | Tạo nhiều chunk nhất (488 chunks cho 20 bài), dễ làm mất ngữ cảnh ở các câu hỏi tổng hợp. Chỉ hit query #2 và #3. |
| Lê Duy Hùng - 2A202600718 | FixedSizeChunker lớn (`chunk_size=600`, `overlap=100`) | 6.0 | Ít chunk hơn nhiều (181 chunks), trung bình khoảng 568 ký tự/chunk, giữ được nhiều bối cảnh hơn cho các câu hỏi cần tổng hợp như query #5. | Vẫn có rủi ro cắt ngang câu/đoạn vì chia theo ký tự. Query #1 và #4 bị lệch top-3, cho thấy chunk lớn không tự giải quyết được vấn đề embedding yếu. |
| Phạm Thị Tuyết Nga - 2A202600877 | SentenceChunker (`max_sentences_per_chunk=3`) | 4.0 | Không cắt giữa câu, chunk dễ đọc khi kiểm tra thủ công; phù hợp khi câu trả lời nằm gọn trong 2-3 câu liên tiếp. | Độ dài chunk không đều và vẫn có thể thiếu bối cảnh với bài phỏng vấn hoặc câu hỏi nhiều ý. Chỉ hit query #2 và #3 trong lượt chạy này. |
| Trần Hoàng Đạt - 2A202600807 | RecursiveChunker (`chunk_size=500`) | 6.0 | Cân bằng tốt giữa kích thước và mạch văn: ưu tiên tách theo đoạn/dòng trước khi phải cắt nhỏ hơn. Hit query #2, #3 và #5 giống strategy của tôi. | Tạo nhiều chunk hơn strategy của tôi (252 chunks), nên chi phí index/search cao hơn và vẫn thất bại ở query #1, #4 với mock embedding. |
| Tạ Duy Xuân - 2A202600970 | Paragraph/Markdown Chunker (`chunk_size=500`) | 6.0 | Giữ đoạn Markdown tự nhiên, dễ truy vết về bài gốc và dễ đọc khi giải thích kết quả retrieval. Kết quả ngang RecursiveChunker trên benchmark hiện tại. | Vì các bài báo chủ yếu là đoạn văn thường, strategy này chưa tạo khác biệt lớn so với recursive; cần thêm heading/metadata chi tiết hơn để mạnh hơn. |

**Strategy nào tốt nhất cho domain này? Tại sao?**
> Trong lượt chạy benchmark hiện tại, `FixedSizeChunker(chunk_size=600, overlap=100)`, `RecursiveChunker(chunk_size=500)` và `Paragraph/Markdown Chunker` cùng đạt 6.0/10. Nếu chỉ chọn một strategy mặc định cho domain bài báo tiếng Việt, tôi nghiêng về `RecursiveChunker` hoặc `Paragraph/Markdown Chunker` vì chúng giữ cấu trúc đoạn tự nhiên hơn, dễ kiểm tra grounding hơn và ít cắt ngang ý hơn fixed-size. Strategy của tôi vẫn có lợi thế khi câu hỏi cần nhiều bối cảnh trong cùng một chunk, ví dụ query #5 về tác động của AI lên học tập/làm việc. Metadata filtering cũng rất hữu ích: ở query #3, các strategy đều trả về 3/3 chunk thuộc nhóm bài không gian khi lọc `category=space`.

---

## 4. My Approach — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi implement các phần chính trong package `src`.

### Chunking Functions

**`SentenceChunker.chunk`** — approach:
> Tôi dùng regex `(?<=[.!?])(?:\s+|\n+)` để tách văn bản tại khoảng trắng hoặc xuống dòng sau các dấu kết thúc câu như `.`, `!`, `?`. Sau khi tách, tôi `strip()` từng câu để bỏ khoảng trắng thừa và loại bỏ chuỗi rỗng. Cuối cùng, tôi gom các câu theo `max_sentences_per_chunk` để mỗi chunk giữ được ý trọn vẹn hơn so với cắt theo ký tự.

**`RecursiveChunker.chunk` / `_split`** — approach:
> `RecursiveChunker` chia văn bản theo thứ tự separator ưu tiên: đoạn văn, dòng, câu, khoảng trắng, rồi cuối cùng là cắt theo ký tự nếu không còn separator phù hợp. Base case là khi đoạn hiện tại có độ dài nhỏ hơn hoặc bằng `chunk_size`, lúc đó trả về ngay đoạn đó. Nếu một phần vẫn quá dài, `_split` tiếp tục gọi đệ quy với separator tiếp theo để cố gắng giữ cấu trúc văn bản tự nhiên nhất có thể.

### EmbeddingStore

**`add_documents` + `search`** — approach:
> Trong `add_documents`, tôi tạo một record chuẩn hóa cho mỗi `Document`, gồm `id`, `doc_id`, `content`, `metadata` và `embedding`. Mỗi document được embed bằng `embedding_fn` rồi lưu vào `_store` trong bộ nhớ; nếu ChromaDB có sẵn thì code cũng thử add vào collection nhưng vẫn giữ bản in-memory để test ổn định. Trong `search`, tôi embed query, tính tích vô hướng giữa query embedding và từng document embedding, sort score giảm dần rồi trả về `top_k`.

**`search_with_filter` + `delete_document`** — approach:
> `search_with_filter` thực hiện filter metadata trước, sau đó mới chạy similarity search trên tập record đã lọc. Cách này giúp query chỉ so sánh với các tài liệu đúng điều kiện, ví dụ đúng `department` hoặc `lang`. `delete_document` tìm tất cả record có `metadata["doc_id"]` trùng với `doc_id`, xóa khỏi `_store`, trả về `True` nếu có xóa và `False` nếu không tìm thấy.

### KnowledgeBaseAgent

**`answer`** — approach:
> `KnowledgeBaseAgent.answer` trước tiên gọi `store.search(question, top_k)` để lấy các chunk liên quan nhất. Sau đó tôi ghép các chunk thành phần `Ngữ cảnh`, đánh số từng chunk để prompt rõ ràng hơn, rồi thêm câu hỏi của người dùng ở cuối prompt. Cuối cùng, prompt được truyền vào `llm_fn` và kết quả trả về được ép thành string để đảm bảo `answer()` luôn trả về chuỗi.

### Test Results

```
============================== 42 passed in 0.14s ==============================
```

**Số tests pass:** 42 / 42

---

## 5. Similarity Predictions — Cá nhân (5 điểm)

| Pair | Sentence A | Sentence B | Dự đoán | Actual Score | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Python is a popular programming language for data science. | Python is widely used for data analysis and machine learning. | high | 0.0925 | Một phần |
| 2 | To reset your password, click the forgot password link. | Users can recover a forgotten password from the login page. | high | -0.1194 | Không |
| 3 | Vector stores retrieve documents by comparing embeddings. | A vector database searches for similar text using embedding similarity. | high | 0.1679 | Có |
| 4 | The billing invoice contains an unexpected charge. | The marketing team planned a social media campaign. | low | 0.1716 | Không |
| 5 | The weather today is sunny and warm. | Database indexes improve query performance. | low | -0.0394 | Có |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn nghĩa?**
> Kết quả bất ngờ nhất là pair 4: hai câu gần như không liên quan về nghĩa nhưng lại có score cao nhất trong 5 cặp. Nguyên nhân là lab đang dùng `_mock_embed`, vector được tạo ổn định từ hash của text chứ không thật sự học nghĩa ngôn ngữ. Điều này cho thấy muốn đánh giá semantic similarity nghiêm túc thì nên dùng embedding backend thật như local Sentence Transformers hoặc OpenAI embeddings.

---

## 6. Results — Cá nhân (10 điểm)

Chạy 5 benchmark queries của nhóm trên implementation cá nhân của bạn trong package `src`. **5 queries phải trùng với các thành viên cùng nhóm.**

### Benchmark Queries & Gold Answers (nhóm thống nhất)

| # | Query | Gold Answer |
|---|-------|-------------|
| 1 | Trong bộ tài liệu, Microsoft đang phát triển hoặc công bố những sản phẩm AI nào và mục tiêu của chúng là gì? | Microsoft Scout - trợ lý giữ chân người dùng (bài 01); chip lượng tử mới "với sự trợ giúp của AI" (bài 16); tác nhân tự chủ tương tự OpenClaw (bài 19). |
| 2 | Những tổ chức hoặc doanh nghiệp nào đang đầu tư mạnh vào AI, và họ tập trung vào những lĩnh vực hoặc ứng dụng nào? | Apple (App Store tích hợp AI - bài 06); Google X (AI thay lối làm cũ - bài 02); Microsoft (Scout, chip lượng tử, tác nhân tự chủ - bài 01/16/19); công ty châu Âu dùng AI mở rộng sang Mỹ (bài 20); Việt Nam phát triển LLM 120 tỷ tham số (bài 11). |
| 3 | Những dự án liên quan đến không gian vũ trụ trong tập tài liệu đang đối mặt với những cơ hội hoặc thách thức gì? `metadata_filter={"category": "space"}` | Blue Origin muốn phóng lại tên lửa trước cuối năm (bài 09); tàu quỹ đạo Sao Hỏa của NASA dừng hoạt động sau 11 năm (bài 13); tham vọng trung tâm dữ liệu vũ trụ của Musk khó thành (bài 15); rủi ro nước sạch khi SpaceX IPO (bài 18). |
| 4 | Những đột phá khoa học hoặc công nghệ mới nào được đề cập trong bộ tài liệu, và chúng có thể tạo ra những tác động gì trong tương lai? | Lần đầu chỉnh sửa chính xác gene phôi người (bài 05); chip lượng tử mới của Microsoft (bài 16); LLM tiếng Việt 120 tỷ tham số (bài 11); lắp đặt lò phản ứng hạt nhân bằng cần cẩu lớn nhất thế giới (bài 14). |
| 5 | Những bài viết nào cho thấy AI đang tác động đến cách con người học tập, làm việc hoặc vận hành tổ chức? Hãy tổng hợp các tác động chính. | Sinh viên hào hứng với AI nhưng bất định về tương lai (bài 17); Google X - không thể theo lối cũ khi AI làm tốt hơn (bài 02); ứng dụng mô hình 4 lớp trong chuyển đổi số cấp xã/phường (bài 10); AI giúp công ty châu Âu mở rộng sang Mỹ (bài 20). |

### Kết Quả Của Tôi

| # | Query | Top-1 Retrieved Chunk (tóm tắt) | Score | Relevant? | Agent Answer (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Trong bộ tài liệu, Microsoft đang phát triển hoặc công bố những sản phẩm AI nào và mục tiêu của chúng là gì? | Bài 18 - SpaceX IPO/nước sạch, chunk nói về rào cản pháp lý và kế hoạch huy động vốn. | 0.4144 | Không; Top-3 cũng không có bài 01/16/19. | Mock LLM chỉ preview prompt từ context sai, nên chưa trả lời đúng các sản phẩm AI của Microsoft. |
| 2 | Những tổ chức hoặc doanh nghiệp nào đang đầu tư mạnh vào AI, và họ tập trung vào những lĩnh vực hoặc ứng dụng nào? | Bài 09 - Blue Origin/SpaceX, chunk nói về năng lực phóng tải trọng nặng. | 0.2947 | Một phần; Top-3 có bài 02 liên quan AI/Google X. | Mock LLM preview context gồm Blue Origin, gene editing và Google X; chỉ có một phần context đúng. |
| 3 | Những dự án liên quan đến không gian vũ trụ trong tập tài liệu đang đối mặt với những cơ hội hoặc thách thức gì? | Bài 09 - Blue Origin, chunk nói các bể nhiên liệu, tháp nước và phần cứng còn trong tình trạng tốt sau sự cố. | 0.1751 | Có; chạy với `metadata_filter={"category": "space"}`, Top-3 gồm bài 09 và 15. | Mock LLM trong `KnowledgeBaseAgent` chưa nhận filter, nhưng kết quả search filtered có context đúng về Blue Origin và trung tâm dữ liệu vũ trụ. |
| 4 | Những đột phá khoa học hoặc công nghệ mới nào được đề cập trong bộ tài liệu, và chúng có thể tạo ra những tác động gì trong tương lai? | Bài 01 - Microsoft Scout/OpenClaw, chunk nói về các sản phẩm tác nhân AI như NemoClaw. | 0.3378 | Không; Top-3 không có bài 05/11/14/16 theo gold answer. | Mock LLM preview context thiên về AI agent và giáo dục AI, chưa retrieve đúng các đột phá khoa học/công nghệ trong gold answer. |
| 5 | Những bài viết nào cho thấy AI đang tác động đến cách con người học tập, làm việc hoặc vận hành tổ chức? Hãy tổng hợp các tác động chính. | Bài 02 - Google X/Sebastian Thrun, chunk nói về giáo dục, tư duy phản biện và thiết kế lại cách dạy học khi có AI. | 0.2266 | Có; Top-3 có bài 02 và 17, đều liên quan đến tác động của AI lên học tập/tư duy. | Mock LLM preview context đúng hướng: AI ảnh hưởng giáo dục, tư duy phản biện và năng lực đánh giá thông tin. |

**Bao nhiêu queries trả về chunk relevant trong top-3?** 3 / 5

**Ghi chú:** Kết quả trên chạy bằng `_mock_embed`, nên điểm similarity và thứ hạng retrieval chưa phản ánh semantic search thật. Một số query bị lệch rõ ràng vì mock embedding tạo vector từ hash của text, không hiểu nghĩa tiếng Việt.

---

## 7. What I Learned (5 điểm — Demo)

**Điều hay nhất tôi học được từ thành viên khác trong nhóm:**
> *Viết 2-3 câu:*

**Điều hay nhất tôi học được từ nhóm khác (qua demo):**
> *Viết 2-3 câu:*

**Nếu làm lại, tôi sẽ thay đổi gì trong data strategy?**
> *Viết 2-3 câu:*

---

## Tự Đánh Giá

| Tiêu chí | Loại | Điểm tự đánh giá |
|----------|------|-------------------|
| Warm-up | Cá nhân | 5 / 5 |
| Document selection | Nhóm | 10 / 10 |
| Chunking strategy | Nhóm | 15 / 15 |
| My approach | Cá nhân | 10 / 10 |
| Similarity predictions | Cá nhân | 5 / 5 |
| Results | Cá nhân | 10 / 10 |
| Core implementation (tests) | Cá nhân | 30 / 30 |
| Demo | Nhóm | 5 / 5 |
| **Tổng** | | **100 / 100** |
