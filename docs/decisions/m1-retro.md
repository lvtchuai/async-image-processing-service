# Retro — M1 (App skeleton)

**Ngày:** (điền)

## Chạy tốt điều gì?
- **Thiết kế trước, code sau** thật sự có tác dụng: quyết định thứ tự `a→b→c` (lưu file → tạo
  record → enqueue) đã chốt *trước* khi viết endpoint, nên lúc code chỉ việc hiện thực + comment
  trỏ về decision entry. Không phải "code xong rồi mới nghĩ nếu lỗi thì sao".
- **Functional core / imperative shell**: tách `process_image` (hàm thuần) khỏi I/O làm test
  nhanh, không cần hạ tầng. Có test ngay từ đầu — khác ShortLink phải chữa CI đỏ sau.
- **Idempotency "miễn phí"** nhờ đặt object key theo `job_id` — xử lý lại chỉ ghi đè.

## Điều gì bất ngờ / khó?
- Chỉ một câu hỏi "nếu chết giữa chừng?" kéo ra cả chuỗi khái niệm: không có atomic xuyên 3 hệ
  thống → chấp nhận mảnh sót vô hại → at-least-once → **worker phải idempotent** → reconciler/outbox.
- Nhận ra **`VARIANTS` bị lặp (coupling)** giữa API và worker — hai bên phải đồng ý key giống nhau.
- Lỗi nhỏ mất thời gian: đặt nhầm tên file `models.py` → `ModuleNotFoundError`.

## Nợ kỹ thuật đã ghi nhận (có ý thức)
- `publish_job` mở connection RabbitMQ mới mỗi lần gọi (chưa tối ưu).
- Khi worker lỗi: mark `failed` + ack (drop) — chưa phân biệt lỗi tạm (retry) vs lỗi độc (DLQ).
- `config.py` / `models.py` bị copy giữa api và worker.

## Lần sau (M2) làm khác gì?
- Cân nhắc **package chung** để hết lặp `config`/`models` (hoặc chấp nhận vì self-contained image).
- Viết Dockerfile multi-stage + non-root ngay (đã có kinh nghiệm từ ShortLink).
- Nghĩ trước: **config khác nhau local vs K8s** — tiêm qua env/Secret, không hardcode.
- **Từ M2: mỗi milestone một branch + PR** (bắt đầu kỷ luật process trên repo này).
