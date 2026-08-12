# Retro — M7 (Cloud full-managed)

**Ngày:** 12-08-2026

## Chạy tốt điều gì?
- **Tái dùng module VPC/EKS từ ShortLink** → không viết lại code đã kiểm chứng.
- **Managed services as code**: S3 + RDS + Amazon MQ + ECR + IAM bằng Terraform module riêng.
- **App code gần như không đổi** — chỉ đổi config (Secret) + toggle `cloud.enabled`. Pipeline chạy
  **end-to-end trên managed services**: upload → S3 → RDS(job) → Amazon MQ → worker → S3 variants
  (xác nhận bằng `aws s3 ls`).
- **Destroy sạch, 0 orphan** (IAM user `force_destroy`, S3 `force_destroy`, ECR `force_delete`).

## Điều gì bất ngờ / khó? (gotcha chỉ cloud thật mới gặp)
1. **Amazon MQ RabbitMQ 3.13 bắt `auto_minor_version_upgrade = true`** — ràng buộc provider chỉ lộ lúc `apply`.
2. **RabbitMQ trên Amazon MQ không có `t3.micro`** → nhỏ nhất `mq.m5.large` (~$0.30/h) → "full managed có giá của nó".
3. **State lock kẹt** sau apply lỗi giữa chừng → `terraform force-unlock <id>`.
4. **S3 credential**: app hardcode `endpoint_url` (cho MinIO) → phải làm *tùy chọn* để dùng S3 thật.
5. **Presigned URL `SignatureDoesNotMatch`**: boto3 sinh endpoint kiểu cũ `s3-<region>` (gạch), SigV4
   kỵ → đặt endpoint region chuẩn `https://s3.<region>.amazonaws.com` (chấm) thì khớp.

## Nợ kỹ thuật đã ghi nhận
- **IRSA thay IAM user** cho S3 (keyless, chuẩn production) — M7 dùng IAM user cho nhanh (lab).
- **KEDA trên Amazon MQ** (`protocol: http`, management endpoint) chưa wire — cloud verify dùng
  worker 1 replica cố định. Cơ chế y hệt, chỉ đổi endpoint.
- **Alembic migration** (nợ từ M4/M6) vẫn còn.

## Bài học lớn nhất
- **Portability trả công**: nhờ config-qua-env + toggle `enabled` (thiết kế từ M2), đưa lên cloud
  chỉ là đổi values + Secret — code không đổi. Đây là "quả ngọt" của thiết kế 12-factor.
- **"Full managed" đắt hơn tưởng** (Amazon MQ m5.large) → đúng nuance đã viết trong decision:
  *lab tiết kiệm thì self-host RabbitMQ*. Quyết định managed-cả-3 đúng về kiến trúc, nhưng chi phí
  thật khiến ta hiểu vì sao "managed vs self-host" là đánh đổi, không phải luôn-chọn-managed.

## CV
*Deployed a cloud-native async pipeline to AWS EKS with fully managed backing services (S3, RDS
PostgreSQL, Amazon MQ for RabbitMQ) via Terraform; kept the app portable (config-only local↔cloud);
verified end-to-end and tore down with zero orphaned resources.*
