# Retro — M2 (Containerize + K8s)

**Ngày:** 07-08-2026

## Chạy tốt điều gì?
- Kinh nghiệm Helm từ ShortLink làm M2 nhanh: Dockerfile multi-stage + non-root, chart viết tay
  gọn, hiểu từng dòng.
- **Config qua Secret + envFrom** sạch: cùng image, đổi môi trường chỉ bằng values.
- **Toggle `enabled`** cho infra + deploy vào **namespace riêng** (`pixelpipe`) → tách bạch, tái
  dùng được cho cloud.
- `emptyDir` cho stateful dev vừa đơn giản vừa né `lost+found` (bài học từ EKS được áp dụng).

## Điều gì bất ngờ / khó?
- **CrashLoopBackOff lúc đầu**: api/worker start trước khi infra sẵn sàng → restart vài lần rồi
  ổn. Hiểu ra: đây là *ordering problem*, K8s tự chữa bằng restart, nhưng chưa "sạch".
- **Presigned URL trỏ `minio:9000`** (tên Service nội bộ) → **không mở được từ trình duyệt host**.
  Lộ ra sự khác biệt giữa *endpoint nội bộ (để lưu)* và *endpoint công khai (để tải)* — một vấn
  đề thật khi đưa object storage lên K8s.

## Nợ kỹ thuật đã ghi nhận
- Ordering: thêm **retry ở startup** hoặc **initContainer** chờ infra (thay vì crashloop).
- **Endpoint công khai cho MinIO** (ingress) để presigned URL dùng được ngoài cluster — hoặc S3 thật ở M7.
- Secret chỉ base64 → **Sealed/External Secrets** cho production.
- `config.py`/`models.py` vẫn bị copy giữa api & worker.

## Lần sau (M3 — KEDA) làm khác gì?
- Worker chưa có probe/health — cân nhắc thêm cách "biết worker còn sống".
- Nghĩ trước: KEDA scale worker theo **độ dài queue RabbitMQ**, và **scale-to-zero** khi rảnh —
  ảnh hưởng gì tới độ trễ job đầu tiên (cold start)?
- Cần một cách **bơm nhiều job** để chứng minh scale (load generator).
