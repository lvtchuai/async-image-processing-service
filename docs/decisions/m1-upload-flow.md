# Decision — Thứ tự thao tác khi upload & cách chịu lỗi (M1)

**Ngày:** (điền) · **Bối cảnh:** M1, endpoint `POST /images`

## Vấn đề
Khi nhận một ảnh, API phải làm 3 việc trên 3 hệ thống khác nhau: (a) lưu file gốc vào object
storage, (b) tạo job record trong Postgres, (c) đẩy message vào RabbitMQ. **Không có transaction
nguyên tử xuyên 3 hệ thống** → nếu API chết giữa chừng sẽ để lại trạng thái dở.

## Phương án cân nhắc
- Thứ tự (c)→(b)→(a) hoặc enqueue sớm: rủi ro **message trỏ tới file/record chưa tồn tại** →
  worker nhận job nhưng không tìm thấy ảnh. Xấu.
- Thứ tự **(a) storage → (b) DB → (c) enqueue**: enqueue cuối cùng.

## Quyết định
Chọn **(a) → (b) → (c)** — *tạo "con trỏ" (message) sau khi thứ nó trỏ tới đã tồn tại.*
→ **Không bao giờ có message trỏ tới file/record không tồn tại.**

## Chế độ lỗi & xử lý
| Chết sau bước | Để lại gì | Mức độ | Xử lý |
|---|---|---|---|
| (a) | File mồ côi trên storage | Vô hại (tốn ít dung lượng) | Sweep định kỳ / lifecycle rule (sau) |
| (b) | Job kẹt `queued`, không có message | Khó chịu (user chờ mãi) | **Reconciler** quét job cũ chưa xong → enqueue lại (M4) |

**Nguyên tắc rút ra:**
- Queue giao **at-least-once** → worker **phải idempotent** (chạy lại không nhân đôi/hỏng).
- Idempotency "miễn phí" bằng cách đặt **object key theo `job_id` cố định**
  (`{job_id}/thumbnail.jpg`...) → xử lý lại chỉ ghi đè đúng file.
- Không làm được atomic xuyên hệ thống → mục tiêu là **mảnh sót vô hại + cứu được**, không phải
  "không có mảnh sót".

## Làm ở đâu
- **M1:** đúng thứ tự (a→b→c) + trường `status` (queued/processing/done/failed) + key theo
  `job_id`. Chưa cần reconciler.
- **M4:** reconciler cứu job kẹt + retry + dead-letter queue + chính thức hóa idempotency.

## Nâng cấp tương lai (biết để nói khi phỏng vấn)
**Transactional Outbox**: ghi job record + dòng outbox trong *cùng một transaction DB* (atomic
thật), một tiến trình riêng đọc outbox rồi publish → xóa hẳn khe hở "chết trước khi enqueue".
Chưa cần ở quy mô này.
