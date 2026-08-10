# Decision — Observability (M6)

**Ngày:** <điền> · **Bối cảnh:** M6, đo & cảnh báo cho hệ async

> Điền vào các `<...>`. Câu hỏi gợi ý (in nghiêng) là *cái cần nghĩ*.

## Vấn đề
<*Hệ async này cần đo GÌ để biết nó khỏe? Nghĩ theo: throughput, tồn đọng, thất bại, tài nguyên.
Cụ thể: queue depth, thời gian xử lý mỗi ảnh (p95), tỉ lệ job vào DLQ, số worker theo thời gian.*>

## Phương án
- **Nguồn metric**: <*app tự expose (Prometheus client trong worker) vs RabbitMQ exporter (queue
  depth) vs cả hai? Cái nào cho metric nghiệp vụ (thời gian xử lý/ảnh)?*>
- ⭐ **Scrape worker khi nó SCALE-TO-ZERO**: <*Worker có thể = 0 pod. Prometheus scrape AI khi
  không có pod nào? → có nên đẩy metric qua Pushgateway, hay chấp nhận chỉ đo queue-depth từ
  RabbitMQ khi worker vắng? Đây là mâu thuẫn thật giữa scale-to-zero và pull-based monitoring.*>

## Quyết định
<*Chốt: đo gì, từ đâu; xử lý bài toán scrape-khi-scale-to-zero ra sao.*>

## Cảnh báo (alert)
<*Alert KHI NÀO? Gợi ý: DLQ tăng (job hỏng hàng loạt); queue dồn mãi không giảm (worker chết /
KEDA không scale); p95 xử lý vọt. Ngưỡng + thời gian giữ (`for`) bao lâu để tránh báo giả?*>

## Cạnh biên / hệ quả
<*Metric từ worker ephemeral có bị mất khi pod chết? Pushgateway thêm thành phần phải vận hành?*>

## Cách verify
<*Bơm tải → Grafana thấy queue depth + số worker + p95. Ép nhiều job hỏng → thấy DLQ rate tăng +
alert bắn.*>

## Làm ở đâu
<*M6: instrument worker/queue metrics + dashboard + alert rules.*>
