# ADR-0002: RabbitMQ làm message broker

**Trạng thái:** Accepted · **Ngày:** (điền)

## Context
Cần một hàng đợi để API đẩy job và worker lấy job, có hỗ trợ **retry** và **dead-letter queue**,
và có thể **autoscale worker theo độ dài hàng đợi**.

## Decision
Dùng **RabbitMQ**: hàng đợi thật, hỗ trợ **manual ack** (chịu lỗi worker chết), **DLQ** gốc,
và có **KEDA scaler** sẵn.

## Alternatives đã cân nhắc
- **Redis (list/stream)**: nhẹ, đơn giản, cũng có KEDA scaler — nhưng cơ chế DLQ/retry phải tự
  làm, kém tường minh. Phù hợp nếu muốn tối giản.
- **Kafka**: mạnh cho event streaming/throughput cực lớn, nhưng **nặng và thừa** cho hàng đợi
  job đơn giản; vận hành phức tạp. → loại (over-engineering).
- **AWS SQS**: tốt trên cloud nhưng khóa nhà cung cấp; khó chạy local giống production. → loại.

## Consequences
- (+) DLQ + retry rõ ràng; ack thủ công đảm bảo không mất job khi worker chết.
- (+) KEDA scale theo `queueLength` gọn gàng.
- (−) Thêm một stateful service phải vận hành (RabbitMQ).
