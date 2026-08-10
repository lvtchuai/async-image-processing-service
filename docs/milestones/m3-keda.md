# M3 — KEDA autoscaling (scale-to-zero theo queue)

## Mục tiêu
Worker **tự scale theo độ dài hàng đợi RabbitMQ**, và **về 0 khi rảnh** — khác HPA-theo-CPU.

## Kiến trúc thêm vào
- **KEDA** (add-on cluster) — event-driven autoscaler.
- **ScaledObject** (`deploy/keda`): trigger `rabbitmq`, `queueLength=5`, `min=0`, `max=10`.
- Bỏ `replicas` khỏi worker Deployment → **KEDA sở hữu số replica**.

## Lệnh
```bash
# 1. cài KEDA
helm repo add kedacore https://kedacore.github.io/charts
helm repo update
helm install keda kedacore/keda -n keda --create-namespace
kubectl get pods -n keda                 # chờ operator/metrics/webhook Running

# 2. áp ScaledObject (đọc queue qua FQDN — xem chú ý)
kubectl apply -f deploy/keda/scaledobject.yaml
kubectl get scaledobject -n pixelpipe    # READY=True

# 3. demo scale: bơm nhiều job rồi xem worker 0→N→0
kubectl port-forward -n pixelpipe svc/api 8000:8000 &
for i in $(seq 1 40); do curl -s -o /dev/null -F "file=@/tmp/test.jpg;type=image/jpeg" http://localhost:8000/images & done; wait
kubectl get deploy worker -n pixelpipe -w   # thấy replicas tăng theo queue rồi tự về 0
```

## Ý nghĩa quan trọng
- **`queueLength=5`**: mục tiêu ~5 message/worker → `desired = ceil(messages/5)`. 40 job → 8 worker.
- **`min=0` (scale-to-zero)**: rảnh thì 0 worker (tiết kiệm), đổi lại **cold start** ~15-30s cho
  job đầu — chấp nhận được vì hệ **async** (xem `decisions/m3-keda-scale.md`).
- **⚠️ Gotcha FQDN**: KEDA ở namespace `keda` gọi RabbitMQ ở `pixelpipe` → host phải là **FQDN**
  `rabbitmq.pixelpipe.svc.cluster.local`, không dùng tên ngắn (cross-namespace DNS).

## Definition of Done
- [ ] Worker scale `0 → N → 0` theo tải (đã verify `0→4→6→8→0`).
