# Decision — Config injection & vị trí infra (M2)

**Ngày:** 07-08-2026 · **Bối cảnh:** M2, đưa app lên Kubernetes

## Vấn đề
Trên K8s, api & worker cần config (DB URL, RabbitMQ URL, endpoint + key của object storage,
tên bucket/queue). Config này **khác nhau giữa local và cloud**, và một phần là **nhạy cảm**
(mật khẩu, access key). Không được hardcode vào image.

## Phương án cân nhắc — Config
- **Hardcode trong code/image**: đổi môi trường phải build lại, lộ secret. → loại.
- **ConfigMap**: hợp cho config *không* nhạy cảm, nhưng secret nên nằm ở Secret.
- **Secret + `envFrom`**: gom mọi biến vào một Secret, api/worker nạp qua `envFrom: secretRef`.

## Quyết định — Config
Dùng **Kubernetes Secret + `envFrom`**. Connection string được *lắp ráp* trong template Secret
từ `values.yaml` (host = tên Service nội bộ: `postgres`, `rabbitmq`, `minio`). App đọc qua biến
môi trường (12-factor) → **cùng một image chạy mọi môi trường, chỉ đổi values/Secret**.

**Nợ kỹ thuật:** Secret của Helm chỉ là base64 (không mã hóa at-rest mặc định). Production thật
nên dùng **Sealed Secrets / External Secrets / Vault** — để dành.

## Phương án cân nhắc — Vị trí infra (Postgres/RabbitMQ/MinIO)
- **Luôn in-cluster**: chạy local free được, nhưng không hợp production cho stateful (nên dùng
  managed: RDS, Amazon MQ, S3).
- **Luôn managed**: đúng production nhưng không chạy local free được.
- **Toggle `enabled` mỗi service**: bật in-cluster cho local, tắt + trỏ managed cho cloud.

## Quyết định — Vị trí infra
Mỗi service infra có cờ **`<svc>.enabled`**. Local minikube: bật (in-cluster). Cloud (M7): tắt,
trỏ `DATABASE_URL`/`S3_ENDPOINT`... sang RDS/S3. → **Một chart chạy cả hai**, không viết lại.

Dev dùng **`emptyDir`** cho Postgres/MinIO (ephemeral): đơn giản, và tiện thể né lỗi
`lost+found` từng gặp trên EBS. Đánh đổi: mất dữ liệu khi pod chết — chấp nhận ở dev.

## Làm ở đâu
- **M2:** Secret + envFrom + toggle enabled + emptyDir (đã làm).
- **M7:** tắt infra in-cluster, trỏ managed; cân nhắc Sealed/External Secrets.
