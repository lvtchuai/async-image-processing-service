# Retro — M6 (Observability)

**Ngày:** 10-08-2026

## Chạy tốt điều gì?
- Worker được instrument bằng `prometheus_client` (`pixelpipe_jobs_total`,
  `pixelpipe_processing_seconds`) + expose `/metrics:9100`.
- **KEDA scale worker `0 → 10` (max)** dưới tải liên tục — autoscaling theo queue chạy đúng.
- ServiceMonitor `worker` được Prometheus nhận (scrape pool đăng ký).

## Điều gì bất ngờ / khó? (một buổi va 4 vấn đề vận hành THẬT)
1. **Bẫy mutable-tag (lần 3):** api chạy image cũ (`:dev`) với `broker.py` cũ → declare queue
   *không* DLX → xung đột với queue đã có DLX → `PRECONDITION_FAILED`. Fix: build tag DUY NHẤT.
2. **Migration thiếu cột `attempts`:** `create_all` không ALTER bảng cũ → INSERT lỗi
   `UndefinedColumn` → API 500. Fix tạm: `ALTER TABLE jobs ADD COLUMN attempts ...`.
3. **⭐ scale-to-zero ↔ pull-scraping:** worker sống ~20s (job siêu ngắn) nên Prometheus (scrape
   15s) rất khó bắt. Chỉ thấy metric khi **giữ tải đủ lâu**. → khẳng định vì sao cần **RabbitMQ
   làm con mắt luôn mở** (B3).
4. **⭐ Blocking I/O trong endpoint `async` → crashloop:** `upload_image` là `async def` nhưng
   gọi boto3/SQLAlchemy/pika (đều chặn) → **chặn event loop** → uvicorn không trả nổi `/healthz`
   trong 1s → liveness fail → kill (exit 137) → lặp. Fix: endpoint `async → def` (chạy threadpool)
   + nới probe (`timeoutSeconds: 5`, `failureThreshold: 6`).

## Nợ kỹ thuật đã ghi nhận
- **Alembic migration** (thay vì recreate/ALTER tay) — nợ này giờ đã cắn 2 lần.
- **Đổi workflow tag:** bỏ `:dev` cố định, dùng **tag duy nhất/SHA cho MỌI deploy** (kể cả dev).
- Fix probe hiện đang patch trên cluster (tạm) → phải đưa vào `deploy/helm/templates/api.yaml`.
- Fix `async→def` phải đưa vào `apps/api/main.py` + rebuild.

## Lần sau (M7 — Cloud) làm khác gì?
- Áp tag SHA cho mọi image (đã có sẵn ở CI M5) — hết mutable-tag.
- Cân nhắc managed (S3/RDS/Amazon MQ) để bớt vận hành stateful.
- Mang theo bài học event-loop: workload I/O-nặng thì dùng sync endpoint / threadpool đúng cách.
