# ADR-0005: Python (FastAPI + Pillow) cho API và Worker

**Trạng thái:** Accepted · **Ngày:** (điền)

## Context
Cần ngôn ngữ viết nhanh cho cả API và worker xử lý ảnh, có thư viện ảnh tốt, và expose
`/metrics` cho Prometheus dễ dàng.

## Decision
Dùng **Python**: **FastAPI** cho API (async, tự expose metrics), **Pillow** cho xử lý ảnh ở
worker. Đồng nhất một ngôn ngữ → chia sẻ code (models, config) dễ.

## Alternatives đã cân nhắc
- **Go cho worker** (hiệu năng ảnh tốt hơn, binary nhỏ): mạnh nhưng chậm phát triển hơn và
  trùng lặp code với API Python. Có thể cân nhắc tối ưu sau. → chưa cần.
- **Node.js**: hợp nếu frontend-heavy; xử lý ảnh CPU-bound không phải thế mạnh. → loại.

## Consequences
- (+) Phát triển nhanh, một ngôn ngữ, hệ sinh thái ảnh + metrics tốt.
- (−) Xử lý ảnh Python chậm hơn Go/libvips; chấp nhận được ở quy mô này (có thể đổi worker sau
  mà không đụng phần còn lại — nhờ tách qua queue).
