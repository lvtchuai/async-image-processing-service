# Decision — Cloud infra (M7)

**Ngày:** <điền> · **Bối cảnh:** M7, đưa lên cloud thật bằng Terraform

> Điền vào các `<...>`. Câu hỏi gợi ý (in nghiêng) là *cái cần nghĩ*.

## Vấn đề
<*Lên cloud thì 3 stateful (RabbitMQ, object storage, Postgres) đặt ở đâu: SELF-HOST trên K8s
(như dev) hay dùng MANAGED (Amazon MQ / S3 / RDS)? Đây là quyết định cửa-một-chiều về vận hành.*>

## Phương án (cho từng stateful)
- **Object storage**: <*MinIO self-host vs **S3 managed**. ADR-0003 đã chọn S3-compatible → S3 gần
  như hiển nhiên. Đánh đổi?*>
- **Database**: <*Postgres in-cluster vs **RDS**. Backup/HA/migration — ai lo?*>
- **Message broker**: <*RabbitMQ self-host vs Amazon MQ. Chi phí vs công vận hành vs khóa nhà cung cấp.*>

## Quyết định
<*Chốt từng cái + VÌ SAO. Nguyên tắc: managed cho thứ khó vận hành (DB, storage); cân nhắc chi phí.*>

## Cạnh biên / hệ quả
<*Presigned URL giờ trỏ S3 công khai (giải quyết gotcha M2)? KEDA scaler trỏ Amazon MQ được không?
Chi phí theo giờ của cái gì? Nhớ kỷ luật apply→verify→destroy như ShortLink.*>

## Cách verify
<*Terraform apply → app chạy trên EKS, ảnh lưu S3 thật, presigned URL mở được từ ngoài → destroy
sạch, kiểm không còn tài nguyên tính tiền.*>

## Làm ở đâu
<*M7: Terraform (VPC/EKS/S3/RDS...), tắt infra in-cluster (toggle enabled=false), deploy, destroy.*>
