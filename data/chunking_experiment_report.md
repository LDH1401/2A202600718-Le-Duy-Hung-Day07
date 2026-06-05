# Báo Cáo Thử Nghiệm Chunking

## Mục Đích

Báo cáo này tóm tắt một thử nghiệm nhỏ so sánh fixed-size chunking, sentence-based chunking và recursive chunking trên tài liệu nội bộ. Mục tiêu là hiểu cách ranh giới chunk ảnh hưởng đến chất lượng retrieval, khả năng giữ ngữ cảnh và mức độ hữu ích của các đoạn được trả về.

## Fixed-Size Chunking

Fixed-size chunking đơn giản để implement và tạo ra số lượng chunk dễ dự đoán. Chiến lược này hoạt động khá tốt với các tài liệu kỹ thuật dài vì mỗi chunk đều nằm dưới kích thước mục tiêu. Tuy nhiên, một số chunk cắt phần giải thích ở vị trí chưa hợp lý, đặc biệt khi một quy trình kéo dài qua nhiều câu. Trong các trường hợp đó, kết quả tìm kiếm đôi khi trả về một mảnh văn bản có nhắc đến đúng từ khóa nhưng lại thiếu hướng dẫn thực tế.

## Sentence-Based Chunking

Sentence-based chunking cải thiện khả năng đọc vì mỗi chunk được căn theo ranh giới ngôn ngữ tự nhiên. Điều này giúp việc kiểm tra thủ công dễ hơn và thường tạo ra kết quả retrieval mạch lạc hơn với các tài liệu chính sách ngắn hoặc FAQ. Nhược điểm là kích thước chunk trở nên ít đồng đều hơn, và một số phần nội dung dày đặc vẫn có thể vượt quá độ dài embedding lý tưởng khi quá nhiều câu dài được gom chung với nhau.

## Recursive Chunking

Recursive chunking mang lại sự cân bằng tốt nhất trong thử nghiệm. Chiến lược này trước tiên cố gắng tách theo các ranh giới cấu trúc lớn như đoạn văn, sau đó chỉ fallback sang các separator nhỏ hơn khi cần. Nhờ vậy, phần lớn chunk vẫn giữ được ngữ cảnh trong khi vẫn nằm trong khoảng kích thước mục tiêu. Với bộ dữ liệu được thử nghiệm, recursive chunking tạo ra các đoạn hữu ích một cách ổn định nhất cho bước hỏi đáp phía sau.

## Kết Luận

Thử nghiệm cho thấy không có một chiến lược tốt nhất cho mọi trường hợp, nhưng recursive chunking là một lựa chọn mặc định mạnh cho các bộ tài liệu kỹ thuật hỗn hợp. Tuy vậy, các nhóm vẫn nên kiểm chứng giả định này bằng chính các query của mình, vì chất lượng retrieval phụ thuộc cả vào phong cách tài liệu lẫn kiểu câu hỏi mà người dùng thật sự đặt ra.
