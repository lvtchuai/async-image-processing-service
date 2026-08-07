# PixelPipe — Architecture

> Dịch vụ **xử lý ảnh bất đồng bộ**: người dùng upload ảnh → hệ thống tạo các biến thể
> (thumbnail, ảnh vừa, WebP) ở chế độ nền → trả về khi xong. Thiết kế để **co giãn theo tải**
> và **chịu lỗi**. Đây là tài liệu thiết kế — đọc trước khi build.

## 1. Vấn đề & vì sao async
Xử lý ảnh (resize, nén, đổi định dạng) **tốn CPU và mất thời gian**. Nếu làm đồng bộ trong
request HTTP → request treo lâu, timeout, không chịu được tải đột biến. Giải pháp: **tách xử
lý ra khỏi request** bằng hàng đợi + worker nền. API trả lời ngay ("đã nhận, đang xử lý"),
worker xử lý sau, người dùng hỏi trạng thái khi cần. → xem [ADR-0001](adr/0001-async-queue.md).

## 2. Yêu cầu

### Functional (chức năng)
- **FR1**: Upload một ảnh (`POST /images`) → nhận về `job_id` + trạng thái `queued`.
- **FR2**: Hệ thống tạo các biến thể: `thumbnail` (150px), `medium` (800px), `webp`.
- **FR3**: Truy vấn trạng thái + URL kết quả (`GET /images/{job_id}`).
- **FR4**: Tải ảnh gốc/biến thể qua URL (presigned, có hạn).
- **FR5** (tùy chọn): trang web tối giản để upload + xem kết quả.

### Non-functional (phi chức năng — phần DevOps ăn điểm)
- **NFR1 — Scalable**: worker **tự co giãn theo độ dài hàng đợi** (KEDA), không phải theo CPU.
- **NFR2 — Resilient**: job lỗi được **retry**; job "độc" (poison) đẩy vào **dead-letter queue**;
  xử lý **idempotent** (chạy lại không hỏng dữ liệu).
- **NFR3 — Observable**: đo được queue depth, thời gian xử lý (p95), tỉ lệ thành công/lỗi; có
  dashboard + alert.
- **NFR4 — Secure**: không hardcode secret; upload/download qua **presigned URL**; validate
  input (kích thước, định dạng, chống file độc).
- **NFR5 — Reproducible**: hạ tầng bằng IaC; deploy bằng CI/CD; chạy được local lẫn cloud.

## 3. Sơ đồ kiến trúc

```
                   ┌─────────────┐   1. POST ảnh
   Người dùng ────▶│  API (FastAPI)│──────────────┐
        ▲          └──────┬────────┘              │ 2. lưu file gốc
        │ 5. GET status   │ 3. tạo job (DB)       ▼
        │    + URLs       │ 4. enqueue     ┌──────────────┐
        │                 ▼                │ Object Store │
        │          ┌────────────┐          │ (MinIO / S3) │
        │          │ PostgreSQL │          └──────▲───────┘
        │          │ (job meta) │                 │ 8. lưu biến thể
        │          └──────▲─────┘                 │
        │                 │ 7. cập nhật status     │
        │          ┌──────┴───────┐   6. lấy job   │
        └──────────│   Worker(s)  │◀───────────────┘
                   │  (resize...) │◀── consume ── ┌──────────────┐
                   └──────────────┘               │  RabbitMQ    │
                          ▲                        │ (queue+DLQ)  │
                          │ KEDA scale theo         └──────────────┘
                          │ độ dài queue
                   ┌──────┴───────┐
                   │     KEDA     │
                   └──────────────┘
```

## 4. Thành phần & trách nhiệm

| Thành phần | Trách nhiệm | Trạng thái |
|---|---|---|
| **API** (FastAPI) | Nhận upload, lưu gốc, tạo job record, enqueue, trả status | Stateless (scale bằng HPA) |
| **Worker** (Python) | Consume queue, xử lý ảnh (Pillow), lưu biến thể, cập nhật DB | Stateless (scale bằng **KEDA theo queue**) |
| **RabbitMQ** | Hàng đợi job + dead-letter queue | Stateful |
| **Object Storage** | Lưu ảnh gốc + biến thể (MinIO local / S3 cloud) | Stateful |
| **PostgreSQL** | Metadata job (id, status, URLs, timestamps) | Stateful |
| **KEDA** | Tự scale worker theo độ dài hàng đợi | Add-on cluster |

## 5. Luồng dữ liệu

**Happy path:** upload → API lưu gốc vào storage + tạo job `queued` + enqueue → worker consume
→ tạo biến thể → lưu storage → cập nhật job `done` + URLs → người dùng GET thấy `done`.

**Failure path:** worker lỗi khi xử lý → message được **requeue/retry** (n lần); quá số lần →
đẩy vào **DLQ** + job `failed`. Worker chết giữa chừng → message không được ack → RabbitMQ
giao lại cho worker khác (nhờ ack thủ công). Xử lý **idempotent** theo `job_id` để retry an toàn.

## 6. Tech stack (tóm tắt — chi tiết ở ADR)

| Lớp | Chọn | ADR |
|---|---|---|
| API + Worker | Python (FastAPI + Pillow) | [0005](adr/0005-language.md) |
| Message broker | RabbitMQ | [0002](adr/0002-broker.md) |
| Object storage | MinIO (local) / AWS S3 (cloud) | [0003](adr/0003-storage.md) |
| Database | PostgreSQL | — |
| Worker autoscaling | KEDA (queue depth) | [0004](adr/0004-keda.md) |
| Orchestration | Kubernetes + Helm | — |
| IaC | Terraform | — |
| CI/CD | GitHub Actions | — |
| Observability | Prometheus + Grafana (+ Loki bonus) | — |

## 7. Bảo mật
- Presigned URL cho upload/download (không lộ credential storage).
- Validate: giới hạn dung lượng, whitelist định dạng (jpg/png/webp), kiểm magic bytes.
- Secret qua Kubernetes Secret / Secrets Manager, không commit.
- Worker chạy non-root; giới hạn tài nguyên (tránh 1 ảnh lớn ngốn hết RAM).

## 8. Observability (đo gì)
- **Queue depth** (số job chờ) — chính cho KEDA + alert.
- **Processing latency p95** mỗi ảnh.
- **Success/fail rate**, số message vào DLQ.
- **Worker count** theo thời gian (chứng minh KEDA scale).
- Logs tập trung (Loki) — trace một job qua các bước.
