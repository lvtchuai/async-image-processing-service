# ADR-0003: Object storage (MinIO local / S3 cloud) cho file

**Trạng thái:** Accepted · **Ngày:** (điền)

## Context
Cần lưu ảnh gốc + các biến thể (nhị phân, có thể lớn), truy cập qua URL, và giống nhau giữa
local và cloud.

## Decision
Dùng **object storage tương thích S3**: **MinIO** khi chạy local, **AWS S3** khi lên cloud —
cùng một API (SDK boto3), chỉ đổi endpoint. Truy cập file qua **presigned URL** có hạn.

## Alternatives đã cân nhắc
- **Lưu blob trong PostgreSQL**: DB phình to, backup nặng, không hợp file lớn. → loại.
- **Lưu trên filesystem/PVC của pod**: không chia sẻ được giữa nhiều pod, khó scale, mất khi
  pod chết. → loại.

## Consequences
- (+) Cùng code local & cloud; scale tốt; presigned URL an toàn.
- (+) Tách file (object store) khỏi metadata (DB) — đúng chuẩn.
- (−) Thêm một dependency (MinIO) khi chạy local.
