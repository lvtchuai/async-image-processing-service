# M7 — Cloud (full-managed trên AWS) · Runbook đầy đủ

> Toàn bộ lệnh đã dùng để đưa PixelPipe từ local lên AWS thật, kèm giải thích ngắn.
> Gồm cả các lệnh **xử lý sự cố** gặp trong lúc deploy (đánh dấu 🔧).

## Kiến trúc
```
        Terraform provision
                │
   ┌────────────┴─────────────┐
   ▼                          ▼
EKS (stateless)          AWS Managed
├── API                  ├── S3          (ảnh gốc + biến thể)
├── Worker               ├── RDS Postgres (jobs metadata/status)
└── (KEDA - optional)    └── Amazon MQ    (queue image_jobs, AMQPS 5671)
```
**Nguyên tắc:** một Helm chart + một image chạy cả local lẫn cloud — chỉ khác `values` + Secret
(cờ `cloud.enabled`). App code **không đổi** khi lên cloud.

---

## Phase 1 — An toàn + prereqs
```bash
aws sts get-caller-identity          # xác nhận ĐÚNG account cá nhân (không phải công ty)
terraform version                    # >= 1.5
aws configure set region ap-southeast-1
```

## Phase 2 — Remote state (S3 + DynamoDB)
```bash
ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
BUCKET=pixelpipe-tfstate-$ACCOUNT
aws s3api create-bucket --bucket $BUCKET --region ap-southeast-1 \
  --create-bucket-configuration LocationConstraint=ap-southeast-1     # nơi lưu state
aws s3api put-bucket-versioning --bucket $BUCKET --versioning-configuration Status=Enabled
aws s3api put-public-access-block --bucket $BUCKET \
  --public-access-block-configuration BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
aws s3api put-bucket-encryption --bucket $BUCKET \
  --server-side-encryption-configuration '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'
aws dynamodb create-table --table-name pixelpipe-tf-locks \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST --region ap-southeast-1              # khóa state chống 2 người apply
```
*State remote = nhiều người/máy dùng chung an toàn, versioned, mã hóa.*

## Phase 3 — Modules
```bash
cd infra/terraform
mkdir -p modules environments/dev
cp -r ../../../url-shortener-devops/infra/terraform/modules/vpc modules/vpc   # TÁI DÙNG (đã kiểm chứng)
cp -r ../../../url-shortener-devops/infra/terraform/modules/eks modules/eks
# viết mới: modules/{ecr,s3,rds,mq}/main.tf + versions.tf
```
*Tái dùng module vpc/eks từ ShortLink → không viết lại code đã chạy thật. Chỉ viết module managed mới.*

## Phase 4 — Wiring + validate
```bash
cd environments/dev
# main.tf gọi vpc→eks→ecr/s3/rds/mq (truyền vpc_id, subnet_ids, vpc_cidr) + IAM user cho S3
terraform init          # cấu hình backend S3 + tải module
terraform validate      # kiểm cú pháp (miễn phí)
```

## Phase 5 — Provision (TÍNH TIỀN, ~30-40')
```bash
terraform plan          # xem trước ~70-80 tài nguyên
terraform apply         # gõ yes -> dựng thật
```

**🔧 Sự cố gặp phải + cách xử lý:**
```bash
# (1) MQ báo "must have autoMinorVersionUpgrade=true"
#     -> sửa modules/mq/main.tf: auto_minor_version_upgrade = true

# (2) MQ báo "RabbitMQ does not support mq.t3.micro"
aws mq describe-broker-instance-options --engine-type RabbitMQ \
  --query "BrokerInstanceOptions[].HostInstanceType"     # xem type hợp lệ -> mq.m5.large (nhỏ nhất)

# (3) State lock kẹt sau apply lỗi giữa chừng
terraform force-unlock <LOCK_ID>       # gỡ khóa cũ (lock id in trong thông báo lỗi)

# rồi apply lại (idempotent -> chỉ tạo cái còn thiếu)
terraform apply
```

## Phase 6 — Build/push ECR + kubectl
```bash
REGION=ap-southeast-1; ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
ECR=$ACCOUNT.dkr.ecr.$REGION.amazonaws.com

# lấy giá trị từ outputs
S3_AK=$(terraform output -raw s3_access_key)
S3_SK=$(terraform output -raw s3_secret_key)
S3_BUCKET=$(terraform output -raw s3_bucket)
RDS_HOST=$(terraform output -raw rds_host)
MQ_HOST=$(terraform output -raw mq_amqps | sed -E 's#amqps://##; s#:5671$##')

# đăng nhập ECR + build cho ĐÚNG kiến trúc node EKS (amd64) + push
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ECR
docker build --platform linux/amd64 -t $ECR/pixelpipe-api:v1 apps/api
docker build --platform linux/amd64 -t $ECR/pixelpipe-worker:v1 apps/worker
docker push $ECR/pixelpipe-api:v1
docker push $ECR/pixelpipe-worker:v1

# trỏ kubectl vào EKS
aws eks update-kubeconfig --name pixelpipe-eks --region $REGION
kubectl get nodes
```
*`--platform linux/amd64`: node EKS là amd64 — build sai kiến trúc → pod CrashLoop "exec format error".*

## Phase 7 — Deploy cloud (tắt infra in-cluster, Secret trỏ AWS)
```bash
DB_PASS='PixelPipeDB_2026!'; MQ_PASS='PixelPipeMQpass2026'      # đúng mật khẩu trong terraform.tfvars
DATABASE_URL="postgresql+psycopg2://pixel:${DB_PASS}@${RDS_HOST}:5432/pixelpipe"
RABBITMQ_URL="amqps://pixel:${MQ_PASS}@${MQ_HOST}:5671/"        # amqps = TLS (Amazon MQ bắt buộc)

helm upgrade --install pp ./deploy/helm -n pixelpipe --create-namespace \
  -f deploy/helm/values-cloud.yaml \
  --set api.image=$ECR/pixelpipe-api --set api.tag=v1 \
  --set worker.image=$ECR/pixelpipe-worker --set worker.tag=v1 \
  --set-string cloud.databaseUrl="$DATABASE_URL" \
  --set-string cloud.rabbitmqUrl="$RABBITMQ_URL" \
  --set-string cloud.s3Bucket="$S3_BUCKET" \
  --set-string cloud.s3AccessKey="$S3_AK" \
  --set-string cloud.s3SecretKey="$S3_SK"

kubectl get pods -n pixelpipe        # CHỈ api + worker (không còn postgres/rabbitmq/minio)
```
*`values-cloud.yaml`: `enabled=false` cho 3 infra + `cloud.enabled=true`. Giá trị nhạy cảm qua `--set` (không commit).*

## Phase 8 — Verify + Destroy
```bash
# --- verify pipeline chạy trên managed services ---
kubectl port-forward -n pixelpipe svc/api 8000:8000 &
curl -F "file=@/tmp/test.jpg;type=image/jpeg" http://localhost:8000/images   # -> job_id
curl http://localhost:8000/images/<job_id>                                   # -> done
aws s3 ls s3://$S3_BUCKET --recursive        # thấy original + thumbnail + medium + webp -> PIPELINE OK

# --- presigned URL mở từ browser (giải quyết gotcha M2) ---
aws s3 presign s3://$S3_BUCKET/<job_id>/thumbnail.jpg --region ap-southeast-1 --expires-in 3600
#   -> mở URL bằng browser: HTTP 200, endpoint s3.ap-southeast-1.amazonaws.com (không còn hostname nội bộ)

# --- DESTROY (DỪNG TIỀN) ---
helm uninstall pp -n pixelpipe               # gỡ app khỏi EKS trước
cd infra/terraform/environments/dev
terraform destroy                            # ~20-30' (EKS/RDS/MQ tear down chậm)

# --- verify destroy sạch (KHÔNG dừng ở terraform destroy) ---
aws eks list-clusters --region ap-southeast-1
aws rds describe-db-instances --region ap-southeast-1 --query "DBInstances[].DBInstanceIdentifier"
aws mq list-brokers --region ap-southeast-1 --query "BrokerSummaries[].BrokerName"
aws ec2 describe-nat-gateways --region ap-southeast-1 --filter "Name=tag:Project,Values=pixelpipe" \
  --query "NatGateways[?State!='deleted'].NatGatewayId"
aws s3 ls | grep pixelpipe-images || echo "no app bucket"     # tất cả PHẢI rỗng
```
*🔧 Nếu destroy kẹt `DependencyViolation` (ENI EKS sót): chờ 2-3' rồi `terraform destroy` lại.*

---

## Bài học local → cloud (tóm tắt)
| Điểm | Ý nghĩa |
|---|---|
| **Toggle `cloud.enabled`** | Cùng chart chạy local (in-cluster) lẫn cloud (managed) |
| **Amazon MQ = AMQPS (TLS 5671)** | `RABBITMQ_URL=amqps://...`; pika tự bật SSL → code không đổi |
| **S3 credential** | IAM user (lab) / IRSA (production keyless); bỏ `endpoint_url` để dùng S3 thật |
| **Presigned endpoint** | Dùng `s3.<region>` (chấm) → SigV4 khớp; `s3-<region>` (gạch) gây SignatureDoesNotMatch |
| **Kỷ luật chi phí** | EKS+RDS+MQ+NAT theo giờ → apply→verify→**destroy**→verify destroy |

## Nợ / nâng cấp (documented)
- IRSA thay IAM user keys (keyless).
- KEDA trên Amazon MQ (`protocol: http`, management endpoint) — verify hiện dùng worker 1 replica.
- Alembic migration thay recreate DB.

Chi tiết quyết định & bài học: [`../decisions/m7-cloud.md`](../decisions/m7-cloud.md) · [`../decisions/m7-retro.md`](../decisions/m7-retro.md)
