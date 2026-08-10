# Decision — Observability (M6)

**Ngày:** 10-08-2026 · **Bối cảnh:** M6, đo & cảnh báo cho hệ async

## Vấn đề
Hệ async cần biết: **tồn đọng** (queue dồn?), **nghiệp vụ** (xử lý mỗi ảnh nhanh/chậm?),
**thất bại** (job vào DLQ?), **năng lực** (mấy worker đang chạy?). Không đo được thì "mù".

## Phương án & phân vai (đã chốt)
- **RabbitMQ exporter** → **queue depth** + **DLQ depth** (tình trạng tồn đọng toàn hệ). RabbitMQ
  biết "có 120 message chờ" nhưng **không biết mỗi ảnh tốn bao giây**.
- **Worker tự expose metrics** (Prometheus client) → **nghiệp vụ**: thời gian xử lý/ảnh (histogram
  p95), số job done/failed/dlq. Worker chỉ biết job *nó* đang xử lý.
- **Không dùng Pushgateway**: chỉ cần khi job cực ngắn/batch biến mất trước khi scrape — không phải
  ca của ta.

## ⭐ Quyết định — xử lý scrape khi worker SCALE-TO-ZERO
Khi worker = 0 pod → **không có worker metrics để scrape** (và Prometheus báo target down). Chấp
nhận điều này, vì:
- Lúc worker = 0, thứ ta *cần biết* là **"có backlog dồn mà không ai xử lý không?"** → câu đó do
  **RabbitMQ exporter** trả lời (nó **luôn chạy**, độc lập với worker). Đây là "con mắt luôn mở".
- Worker business metrics chỉ tồn tại **khi có worker** — hợp lý, vì chỉ khi *đang xử lý* mới quan
  tâm thời gian xử lý.
- ⇒ **KHÔNG alert "worker target down"** (0 pod là trạng thái bình thường của scale-to-zero, không
  phải sự cố).

## Cảnh báo (alert) — triết lý "không tự phục hồi", không phải "vừa vượt ngưỡng"
- **QueueBacklog**: queue depth cao **liên tục > 5 phút** (`for: 5m`) → KEDA/worker không theo kịp
  (không phải spike thoáng qua — hệ vốn tự scale).
- **DLQGrowing**: DLQ depth tăng > 5 phút → job hỏng hàng loạt.
- **SlowProcessing**: p95 xử lý cao kéo dài.
Ngưỡng + `for` để tránh báo giả khi hệ đang tự scale/tự phục hồi.

## Cạnh biên / hệ quả
- Worker ephemeral: metric mất khi pod chết — chấp nhận (Prometheus đã tổng hợp theo thời gian khi
  còn scrape được; khoảng trống lúc 0 worker là *đúng thiết kế*).
- Thêm **RabbitMQ exporter** = một thành phần phải vận hành.

## Cách verify
- Bơm tải → Grafana thấy **queue depth + số worker (0→N→0) + p95 xử lý**.
- Bơm nhiều file rác → **DLQ depth tăng** → alert `DLGGrowing` bắn sau `for`.

## Làm ở đâu
M6: worker instrument (prometheus_client + /metrics) · kube-prometheus-stack · RabbitMQ metrics ·
ServiceMonitor · dashboard · PrometheusRule (alerts).
