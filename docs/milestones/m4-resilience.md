# M4 — Resilience (retry + dead-letter queue)

## Mục tiêu
Chịu lỗi khi worker xử lý thất bại: **retry** lỗi tạm, đẩy **DLQ** lỗi độc — không mất job, không hot-loop.

## Kiến trúc thêm vào
- Cột **`attempts`** trong bảng `jobs` (đếm số lần thử).
- Queue `image_jobs` khai báo **`x-dead-letter-exchange`** → **DLQ** `image_jobs_dlq`.
- Worker **phân loại lỗi**: độc (`UnidentifiedImageError`) → DLQ ngay; tạm → retry tới 4 lần → DLQ.
  Dùng `basic_nack(requeue=True/False)`.

## Lệnh
```bash
# 1. dev local: dựng lại infra SẠCH (đổi schema + queue args cần fresh)
docker compose down -v && docker compose up -d
#    -v: xoá volume -> DB/queue tạo mới với cấu trúc mới

# 2. (sửa code: models thêm attempts, broker/worker khai báo DLX) rồi test:
python worker.py         # terminal worker
# ảnh tốt -> done; file rác (ép type=image/jpeg) -> failed + vào DLQ, KHÔNG lặp
echo "not an image" > /tmp/garbage.txt
curl -F "file=@/tmp/garbage.txt;type=image/jpeg" http://localhost:8000/images

# 3. đưa lên k8s (rebuild + recreate infra để có schema/DLX mới)
docker build -t pixelpipe-api:dev apps/api && docker build -t pixelpipe-worker:dev apps/worker
minikube image load pixelpipe-api:dev; minikube image load pixelpipe-worker:dev
kubectl delete pod -n pixelpipe -l app=postgres   # fresh -> bảng có attempts
kubectl delete pod -n pixelpipe -l app=rabbitmq   # fresh -> queue có DLX
kubectl rollout restart deploy/api deploy/worker -n pixelpipe
```

## Ý nghĩa quan trọng
- **DLX + `basic_nack(requeue=False)`**: message bị từ chối tự chuyển sang DLQ (điểm dừng cuối).
- **`requeue=True`**: trả message về queue để thử lại (đếm bằng `attempts`, cap 4 lần).
- **Idempotent (M1)** làm retry an toàn: chạy lại chỉ ghi đè cùng key.
- **⚠️ Đổi `arguments` của queue đang tồn tại → RabbitMQ báo `PRECONDITION_FAILED`** → phải xoá/
  tạo lại queue (chi tiết: `decisions/m4-retry-dlq.md`).

## Definition of Done
- [ ] Ảnh tốt → done; file rác → DLQ + `failed`, worker không hot-loop.
