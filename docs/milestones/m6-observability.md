# M6 — Observability (metrics, dashboard, alert)

## Mục tiêu
Nhìn được sức khỏe hệ async: **queue depth** (luôn có), **thời gian xử lý** (khi có worker),
**số worker**, **DLQ**; và **cảnh báo** khi hệ không tự phục hồi.

## Kiến trúc thêm vào
- **Worker `/metrics`** (`prometheus_client`, cổng 9100): `pixelpipe_jobs_total`,
  `pixelpipe_processing_seconds`.
- **kube-prometheus-stack** (Prometheus + Grafana + Alertmanager) ở namespace `monitoring`.
- **ServiceMonitor** cho worker + rabbitmq; **RabbitMQ prometheus plugin** (cổng 15692) → queue depth.
- **Dashboard** (ConfigMap) + **PrometheusRule** (alert).

## Lệnh
```bash
# 1. cài stack giám sát
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install monitoring prometheus-community/kube-prometheus-stack \
  -n monitoring --create-namespace -f deploy/monitoring/values.yaml

# 2. dạy Prometheus scrape worker + rabbitmq + nạp dashboard/alert
kubectl apply -f deploy/monitoring/worker-servicemonitor.yaml
kubectl apply -f deploy/monitoring/rabbitmq-servicemonitor.yaml
kubectl apply -f deploy/monitoring/dashboard-configmap.yaml
kubectl apply -f deploy/monitoring/alerts.yaml

# 3. xem
kubectl port-forward -n monitoring svc/monitoring-kube-prometheus-prometheus 9090:9090  # Prometheus
kubectl port-forward -n monitoring svc/monitoring-grafana 3000:80                        # Grafana (admin/admin)
# query: rabbitmq_queue_messages   |   pixelpipe_jobs_total
```

## Ý nghĩa quan trọng
- **Mô hình PULL**: app *phơi* metric ở `/metrics`, Prometheus *chủ động ghé lấy* (scrape).
- **ServiceMonitor**: tờ khai "hãy scrape service này" (chuẩn Operator, không sửa config tay).
- **⭐ RabbitMQ = con mắt luôn mở**: worker scale-to-zero (0 pod) thì *không scrape được worker
  metrics* — nhưng **queue depth từ RabbitMQ luôn có** (RabbitMQ luôn chạy). Đây là lý do cần metric
  từ cả hai nguồn (xem `decisions/m6-observability.md`).
- **Alert theo `for: 5m`**: chỉ báo khi vấn đề *kéo dài* (hệ tự-scale nên spike thoáng qua đừng báo).

## ⚠️ 4 sự cố vận hành đã xử lý trong M6 (kho vàng phỏng vấn — xem `decisions/m6-retro.md`)
1. **Mutable-tag** (lần 3): image `:dev` cũ → queue arg mismatch. Fix: tag duy nhất.
2. **Thiếu cột `attempts`**: `create_all` không ALTER bảng cũ → 500. Fix: `ALTER TABLE` (nợ Alembic).
3. **Scale-to-zero ↔ pull-scraping**: worker sống ~20s, khó scrape → cần tải liên tục / RabbitMQ.
4. **Blocking I/O trong endpoint `async` → crashloop**: chặn event loop → `/healthz` timeout → bị
   kill. Fix: endpoint `async → def` (threadpool) + nới probe (`timeoutSeconds: 5`).

## Definition of Done
- [ ] Dashboard hiện queue depth + worker count + p95; alert `QueueBacklog`/`JobsFailingToDLQ` hoạt động.
