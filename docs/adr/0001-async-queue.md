# ADR-0001: Xử lý ảnh bất đồng bộ qua message queue

**Trạng thái:** Accepted · **Ngày:** 07-08-2026

## Context
Xử lý ảnh tốn CPU và thời gian (100ms–vài giây/ảnh). Làm đồng bộ trong HTTP request gây
timeout, không chịu được tải đột biến, và trải nghiệm kém.

## Decision
Tách xử lý khỏi request: API chỉ **nhận + enqueue**, một pool **worker** xử lý nền. Người dùng
nhận `job_id` ngay và hỏi trạng thái sau (polling / webhook sau này).

## Alternatives đã cân nhắc
- **Đồng bộ trong request**: đơn giản nhưng không scale, dễ timeout. → loại.
- **Background task trong process API** (vd FastAPI BackgroundTasks): không bền — API restart là
  mất job, không scale worker độc lập. → loại.

## Consequences
- (+) Chịu tải đột biến (queue làm bộ đệm), scale worker độc lập với API.
- (+) Chịu lỗi: retry/DLQ.
- (−) Phức tạp hơn: thêm broker, cần theo dõi queue, xử lý idempotent.
