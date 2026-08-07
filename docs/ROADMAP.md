# PixelPipe — Roadmap

> Chia theo milestone. Mỗi milestone làm qua **1 branch → PR → CI → merge**, có **Definition
> of Done** rõ ràng. Không nhảy milestone — mỗi cái dựa trên cái trước.

| # | Milestone | Mục tiêu | Definition of Done | Dòng CV |
|---|---|---|---|---|
| **M0** | **Design** | Tài liệu thiết kế + cấu trúc repo | ARCHITECTURE + 6 ADR + ROADMAP được duyệt; khung thư mục sẵn | *Designed the system up front (architecture + ADRs) before implementation* |
| **M1** | **App skeleton (local)** | API + worker + queue + storage + DB chạy bằng docker-compose | Upload 1 ảnh local → nhận job_id → nhận về thumbnail/webp; status chuyển queued→done | *Built an async image-processing pipeline (API + workers + RabbitMQ + object storage)* |
| **M2** | **Containerize + K8s** | Dockerize + Helm chart, deploy lên minikube | Mọi service Running trên minikube; upload hoạt động qua cluster | *Deployed a multi-service app to Kubernetes with Helm* |
| **M3** | **KEDA autoscaling** ⭐ | Worker tự scale theo độ dài hàng đợi | Bơm nhiều job → worker scale lên (và về 0 khi hết); có bằng chứng | *Implemented event-driven worker autoscaling with KEDA (scale-to-zero on queue depth)* |
| **M4** | **Resilience** | Retry + dead-letter queue + idempotent | Job lỗi được retry; job "độc" vào DLQ; xử lý lại không hỏng dữ liệu | *Designed for resilience: retries, dead-letter queue, idempotent processing* |
| **M5** | **CI/CD** | GitHub Actions: test/build/push, path filter | PR chạy CI theo service đổi; merge main push image | *Built CI/CD with GitHub Actions (path-filtered, image publishing)* |
| **M6** | **Observability** | Metrics (queue depth, latency, DLQ), dashboard, alert | Grafana thấy queue depth + worker count + p95; alert khi DLQ tăng | *Instrumented queue/latency metrics; dashboards and alerts* |
| **M7** | **IaC + Cloud (tùy chọn)** | Terraform dựng hạ tầng; deploy thật rồi destroy | Apply → app chạy trên cloud từ registry thật → destroy sạch | *Provisioned cloud infra as code (Terraform) with cost-disciplined lifecycle* |

## Nguyên tắc xuyên suốt (khác project cũ — "chỉn chu hơn")
1. **Thiết kế trước, code sau** — M0 xong mới sang M1 (đang làm điều này).
2. **Test từ đầu**: viết test cùng lúc với code (không để CI đỏ vì thiếu test như lần trước).
3. **ADR cho mọi quyết định lớn** — thêm ADR mới khi phát sinh.
4. **Mỗi milestone = một PR có mô tả rõ** (làm gì, vì sao, verify sao).
5. **Kỷ luật chi phí**: dev trên local (minikube + MinIO), cloud chỉ ở M7 và destroy ngay.

## Thứ tự ưu tiên nếu thiếu thời gian
M1 → M2 → **M3 (điểm nhấn)** → M6 (observability) là bộ khung tối thiểu ấn tượng.
M4, M5, M7 làm sau để "chỉn chu" đầy đủ.
