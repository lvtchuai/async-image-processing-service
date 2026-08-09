# Decision — Scale-to-zero cho worker bằng KEDA (M3)

**Ngày:** 08-08-2026 · **Bối cảnh:** M3, KEDA autoscale worker theo độ dài queue

## Vấn đề (trade-off cốt lõi)
Nếu **0 worker** đang chạy mà có job mới → xuất hiện **độ trễ cold start** (chờ K8s tạo pod +
worker nối RabbitMQ ≈ vài–vài chục giây), nhưng **tiết kiệm tài nguyên** khi rảnh. Ngược lại
**giữ ≥1 worker** thì job đầu xử lý ngay, nhưng **luôn tốn tài nguyên** dù không có việc.

## Phương án
- **`minReplicaCount: 1`** (giữ 1 worker ấm): độ trễ thấp, nhưng always-on tốn tài nguyên; và
  làm mất điểm nhấn "event-driven, scale-to-zero".
- **`minReplicaCount: 0`** (scale-to-zero): tiết kiệm tối đa, nhưng job đầu chịu cold start.

## Quyết định
Chọn **`minReplicaCount: 0`** (scale-to-zero). **Vì sao chấp nhận cold start:** hệ thống *vốn
đã bất đồng bộ* (ADR-0001) — người dùng nhận `job_id` và *poll status sau*, đã chấp nhận độ trễ.
Thêm vài–vài chục giây cold start **không phá vỡ hợp đồng nào**. Với workload xử lý ảnh (không
real-time), tiết kiệm tài nguyên đáng giá hơn độ trễ job đầu.
> Nếu là workload có SLA độ trễ chặt (vd < 1s), sẽ chọn `min=1`. Ở đây bản chất async cho phép `min=0`.

**Tham số scale (KEDA RabbitMQ scaler):**
- Trigger: `queueLength` của queue `image_jobs`, `value: 5` → mục tiêu ~5 message chờ/worker;
  dồn nhiều hơn thì bung thêm worker.
- `maxReplicaCount: 10` (trần bảo vệ tài nguyên).
- `pollingInterval: 15s` (KEDA bao lâu kiểm queue một lần), `cooldownPeriod: 60s` (chờ trước khi
  co về 0).

## Cạnh biên / hệ quả
- **Độ trễ phát hiện**: KEDA poll mỗi 15s → scale-from-zero có thể trễ tới ~15s + thời gian tạo
  pod. Chấp nhận (async).
- **KEDA sở hữu số replica** (qua HPA ngầm) → phải **bỏ `replicas` khỏi Deployment worker**, nếu
  không mỗi lần `helm upgrade` sẽ giành quyền với KEDA.
- Idempotency (M1) làm việc scale-up an toàn: nhiều worker xử lý song song, key theo `job_id` nên
  không đụng nhau.

## Cách verify
Bơm nhiều job (loop upload) → xem `worker` replicas đi **0 → N** khi queue dồn, rồi **N → 0** sau
khi hết việc + hết cooldown. Ghi lại timeline làm bằng chứng.

## Làm ở đâu
- **M3:** cài KEDA, `ScaledObject` + `TriggerAuthentication`, bỏ `replicas` khỏi worker, verify.
- Sau: có thể thêm scale theo nhiều trigger (vd cả độ trễ), hoặc scale API theo request.
