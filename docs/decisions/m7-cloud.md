# Decision — Cloud infra (M7)

**Ngày:** 10-08-2026 · **Bối cảnh:** M7, đưa lên cloud thật bằng Terraform

## Vấn đề
Lên cloud thì 3 stateful (RabbitMQ, object storage, Postgres) đặt ở đâu: **self-host trên K8s**
(như dev) hay dùng **managed** (Amazon MQ / S3 / RDS)? Đây là quyết định **cửa một chiều** về vận hành.

## Quyết định (managed cho cả 3 — mô phỏng production đầy đủ)

| Thành phần | Local (dev) | Cloud (M7) | Vì sao |
|---|---|---|---|
| Object storage | MinIO | **Amazon S3** | ADR-0003 đã theo chuẩn S3-compatible → đổi endpoint+credentials, không sửa kiến trúc app |
| Database | Postgres container | **Amazon RDS PostgreSQL** | DB chứa metadata/trạng thái job → mất DB nặng hơn mất pod → giao backup/recovery/HA cho managed |
| Message broker | RabbitMQ container | **Amazon MQ for RabbitMQ** | Tập trung vào app/scaling/IaC thay vì tự vận hành RabbitMQ cluster |

### Kiến trúc cloud
```
EKS (stateless workload)
├── PixelPipe API
├── PixelPipe Worker
├── HPA
└── KEDA
        │  scale theo queue
        ▼
AWS Managed Services
├── S3               → image objects (original + variants)
├── RDS PostgreSQL   → jobs metadata / status
└── Amazon MQ        → image_jobs queue (+ DLQ)
```

### Nguyên tắc
**Kubernetes tập trung chạy stateless application.** Stateful khó backup/recover/vận hành thì ưu
tiên managed khi lên production. S3 và RDS là 2 quyết định rõ ràng nhất (dữ liệu cần độ bền cao).
RabbitMQ linh hoạt hơn: production dùng Amazon MQ, lab tiết kiệm có thể self-host — M7 này chọn
**Amazon MQ** để mô phỏng production đầy đủ.

## Cạnh biên / hệ quả

### Presigned URL — giải quyết gotcha M2
```
Local:  Browser → http://minio:9000/...        (❌ browser ngoài cluster không resolve DNS nội bộ)
Cloud:  Browser → https://<bucket>.s3.<region>.amazonaws.com/...   (✅ endpoint public của S3)
```
Presigned URL dùng endpoint public S3 → browser ngoài EKS truy cập trực tiếp được → **hết gotcha
M2** (internal Kubernetes hostname). Bucket vẫn **Block Public Access = enabled**; presigned chỉ
cấp quyền *tạm thời* cho đúng object.

### KEDA + Amazon MQ
- Worker vẫn consume qua **AMQP** tới Amazon MQ.
- KEDA RabbitMQ scaler dùng connection string/credentials của broker → **không còn**
  `rabbitmq.pixelpipe.svc.cluster.local`, thay bằng **endpoint Amazon MQ**.
- Amazon MQ (managed) → KEDA scaler nên dùng **`protocol: http`** (management API HTTPS) thay vì
  amqp thuần.
- Credentials để trong **Kubernetes Secret / AWS Secrets Manager**, không hardcode trong Helm values.

### Chi phí (nhớ destroy)
```
EKS control plane   → theo giờ          NAT Gateway     → theo giờ + traffic
EC2 worker nodes    → theo giờ          Load Balancer   → theo giờ
RDS instance        → theo giờ          RDS storage     → theo dung lượng
Amazon MQ broker    → theo giờ          Amazon MQ storage → theo dung lượng
S3                  → storage + requests + transfer
```
⚠️ **NAT Gateway, RDS, Amazon MQ, Load Balancer, EKS** vẫn phát sinh tiền dù không có request →
đặc biệt phải destroy. Kỷ luật: **apply → verify → experiment → destroy → verify-destroy** (kiểm
thực tế trên AWS, không dừng ở `terraform destroy`).

## Cách verify (tóm tắt — chi tiết ở milestone doc)
1. **Provision:** `terraform init/plan/apply` → VPC, EKS, S3, RDS, Amazon MQ, IAM, Security Groups.
2. **Deploy:** tắt infra in-cluster (`postgres/rabbitmq/minio.enabled=false`), trỏ `DATABASE_URL`→RDS,
   `RABBITMQ_URL`→Amazon MQ, S3 bucket/region → S3; `helm upgrade`.
3. **App:** upload ảnh → S3 (original) → RDS `queued` → Amazon MQ → Worker → S3 (variants) → RDS `done`.
   Kiểm: `aws s3 ls s3://<bucket> --recursive` thấy original/thumbnail/medium/webp.
4. **Presigned URL:** mở từ browser ngoài → HTTP 200; URL **không chứa** `minio`/`localhost`/`*.svc.cluster.local`.
5. **KEDA:** bơm nhiều job → `kubectl get pods -w` thấy worker scale lên rồi về.
6. **Destroy:** `terraform destroy` + kiểm thủ công:
   `aws eks list-clusters` · `aws rds describe-db-instances` · `aws mq list-brokers` ·
   `aws s3 ls` · `aws ec2 describe-nat-gateways` · `aws elbv2 describe-load-balancers`.

## Làm ở đâu
Terraform (`infra/terraform`) provision toàn bộ:
```
infra/terraform/
├── modules/{vpc, eks, ecr, s3, rds, mq}     # tái dùng vpc/eks từ ShortLink
└── environments/dev/                        # main.tf gọi module + backend S3 + tfvars
```
Cùng **một Helm chart** phục vụ 2 môi trường qua toggle `enabled`:
```
LOCAL:  EKS/minikube + Postgres + RabbitMQ + MinIO (in-cluster)
CLOUD:  EKS + API + Worker   |   AWS: RDS + Amazon MQ + S3 (managed)
```
Đây là bước chuyển của PixelPipe từ **"chạy được trên Kubernetes"** sang **"thiết kế để vận hành
trên cloud"**.
