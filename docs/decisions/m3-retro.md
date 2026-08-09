# Retro — M3 (KEDA scale-to-zero)

**Ngày:** 09-08-2026

## Chạy tốt điều gì?
- Worker scale **0 → 4 → 8 → 0** khớp công thức (40 job ÷ value 5 = 8). Scale-to-zero hoạt động
  đúng: khi rảnh về 0 (tiết kiệm tài nguyên), có job thì bung ra.
- Trade-off cold start đúng như dự đoán trong decision: lúc worker = 0, job đầu chờ ~15–30s rồi
  mới chạy — chấp nhận được vì hệ thống async.

## Điều gì bất ngờ / khó?
- **Cross-namespace DNS**: KEDA ở ns `keda` gọi RabbitMQ ở ns `pixelpipe` bằng tên ngắn không
  phân giải được → phải dùng **FQDN** `rabbitmq.pixelpipe.svc.cluster.local`.
- Cold start lúc worker = 0 chạy khá chậm (đúng bản chất scale-from-zero).

## Nợ kỹ thuật đã ghi nhận
- Worker **chưa có health/probe** — chưa có cách "biết worker treo" (không phải chết hẳn).
- `ScaledObject` áp bằng `kubectl` (ngoài Helm chart) — có thể template vào chart sau.
- (Kế thừa) presigned URL trỏ endpoint nội bộ; `config.py`/`models.py` còn copy giữa api & worker.

## Lần sau (M4 — retry + DLQ) làm khác gì?
- Hiện worker lỗi chỉ **mark `failed` + ack (drop)** → mất job, không thử lại. M4 thêm **retry**
  (lỗi tạm) + **dead-letter queue** (lỗi độc), và chính thức hóa idempotency.
