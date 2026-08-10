# M2 — Containerize + Kubernetes

## Mục tiêu
Đóng gói api & worker thành image, chạy toàn hệ trên K8s (minikube) bằng Helm chart.

## Kiến trúc thêm vào
- **Dockerfile** cho api & worker: **multi-stage** (image gọn) + **non-root** (`appuser`).
- **Helm chart** (`deploy/helm`): Deployment/Service cho api, worker; infra in-cluster
  (postgres/rabbitmq/minio) **bật/tắt được** qua `values`; **config tiêm qua Secret** (`envFrom`).
- Deploy vào **namespace riêng** `pixelpipe`.

## Lệnh
```bash
# 1. build 2 image (LOAD trước, restart sau — tránh bẫy mutable tag)
docker build -t pixelpipe-api:dev apps/api
docker build -t pixelpipe-worker:dev apps/worker

# 2. nạp image vào minikube (cluster không thấy image máy bạn)
minikube image load pixelpipe-api:dev
minikube image load pixelpipe-worker:dev

# 3. kiểm chart trước khi deploy
helm lint ./deploy/helm                 # bắt lỗi cú pháp chart
helm template pp ./deploy/helm | less   # xem YAML sẽ sinh ra (không đụng cluster)

# 4. deploy (install nếu chưa có, upgrade nếu đã có)
helm upgrade --install pp ./deploy/helm -n pixelpipe --create-namespace
#    -n: namespace; --create-namespace: tạo ns nếu chưa có

# 5. kiểm tra
kubectl get pods -n pixelpipe            # chờ tất cả Running (api/worker có thể crashloop chờ infra)

# 6. thử app qua cluster
kubectl port-forward -n pixelpipe svc/api 8000:8000   # đường hầm tạm host->service
curl -F "file=@/tmp/test.jpg;type=image/jpeg" http://localhost:8000/images
```

## Ý nghĩa quan trọng
- **`minikube image load`**: bắt buộc vì cluster chạy trong VM riêng, không dùng Docker máy bạn.
- **`helm upgrade --install`**: một lệnh dùng mãi (idempotent).
- **`envFrom: secretRef`**: app đọc config (DB URL, S3 key...) từ Secret → **cùng image chạy mọi
  môi trường**, không hardcode (xem `decisions/m2-config-and-infra.md`).
- **`emptyDir`** cho postgres/minio (dev): ephemeral, đơn giản, né lỗi `lost+found` của volume thật.

## Definition of Done
- [ ] Mọi pod Running; upload qua cluster ra `done`.
