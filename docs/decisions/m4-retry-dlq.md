# Decision — Retry & Dead-Letter Queue (M4)

**Ngày:** 09-08-2026 · **Bối cảnh:** M4, chịu lỗi khi worker xử lý thất bại

## Vấn đề
Hiện worker lỗi → mark `failed` + ack (drop) → **mất job**, không thử lại. Nhưng:
- Có **lỗi tạm thời** (MinIO/DB/network chập chờn) — retry là khỏi.
- Có **lỗi độc / deterministic** (ảnh hỏng, không decode được) — retry cùng input **chắc chắn lại
  lỗi**, vô ích, và nếu requeue mãi sẽ **hot-loop chặn cả queue**.
- Nếu drop hết thì mất job; nếu retry mù quáng thì kẹt.

## Phương án
Phân loại lỗi *trước*, retry **có giới hạn** (không mù quáng), và **DLQ là điểm dừng cuối cùng**
— không phải nơi ném mọi lỗi vào.

## Quyết định
**Phân loại theo loại exception:**
- **Lỗi độc** (vd `PIL.UnidentifiedImageError` / decode fail) → **không retry**, đẩy thẳng DLQ +
  mark `failed`. (Retry vô ích — insight cốt lõi.)
- **Lỗi tạm** (storage/DB/network) → **retry tối đa 4 lần**; vẫn lỗi → DLQ + `failed`.

**Cơ chế (RabbitMQ):**
- Queue `image_jobs` khai báo với `x-dead-letter-exchange` trỏ tới **DLQ** `image_jobs_dlq`.
- Đếm số lần thử bằng cột **`attempts`** trong bảng `jobs` (tăng mỗi lần xử lý).
- Worker: lỗi tạm & `attempts < 4` → `basic_nack(requeue=True)` (thử lại). Lỗi độc hoặc hết lượt →
  `basic_nack(requeue=False)` → RabbitMQ tự dead-letter sang DLQ.

## Cạnh biên / hệ quả
- **`requeue=True` retry NGAY, không delay** → nếu lỗi tạm kéo dài có thể quay vòng nhanh. Cap 4
  lần giữ an toàn. *Backoff luỹ tiến (retry qua queue TTL)* là nâng cấp sau — ghi nợ.
- **Idempotency (M1)** làm retry an toàn: key theo `job_id`, chạy lại chỉ ghi đè.
- Heuristic "độc vs tạm" theo exception **không hoàn hảo** (vài lỗi tạm có thể bị xếp nhầm) —
  chấp nhận, tinh chỉnh khi gặp thực tế.
- Đổi `arguments` của queue đang tồn tại → RabbitMQ báo lỗi; phải **xoá queue cũ** (hoặc rabbitmq
  fresh) khi thêm DLX.

## Cách verify
- Upload **ảnh hợp lệ** → `done` như cũ.
- Upload **file rác** (bytes không phải ảnh) → **không hot-loop**; kết thúc ở `failed` + message
  nằm trong **DLQ** (xem RabbitMQ UI queue `image_jobs_dlq`).
- (Nếu mô phỏng được lỗi tạm) → thấy `attempts` tăng rồi thành công/hết lượt.

## Làm ở đâu
- **M4:** thêm cột `attempts`; khai báo DLX cho queue + tạo DLQ; logic phân loại/retry/DLQ trong
  worker; test cho nhánh poison. Backoff luỹ tiến để dành.
