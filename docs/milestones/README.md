# PixelPipe — Sổ tay xây dựng theo Milestone

> Bộ tài liệu này ghi lại **quá trình xây từng milestone**: mục tiêu, kiến trúc thêm vào, và
> **các lệnh kèm giải thích ngắn**. Để bạn (và người khác) hiểu hệ thống *được dựng ra sao*.
> Muốn hiểu *vì sao* mỗi quyết định → xem `../decisions/`.

## Bức tranh tổng thể
```
User → API (FastAPI) ──enqueue──▶ RabbitMQ ──consume──▶ Worker (Pillow) ──▶ Object Storage (MinIO/S3)
              │                       ▲                        │                       │
              └─▶ PostgreSQL (job)    └─ KEDA scale 0→N        └─ status done/failed   └─▶ variants
                                         (theo queue depth)
   Observability: Prometheus (queue + worker metrics) → Grafana + Alertmanager
```

## Lộ trình
| M | Nội dung | File |
|---|---|---|
| M0 | Design-first (architecture, ADR, roadmap) | [m0-design.md](m0-design.md) |
| M1 | App skeleton chạy local (docker-compose) | [m1-app-skeleton.md](m1-app-skeleton.md) |
| M2 | Containerize + Kubernetes (Helm) | [m2-containerize-k8s.md](m2-containerize-k8s.md) |
| M3 | KEDA autoscaling (scale-to-zero theo queue) | [m3-keda.md](m3-keda.md) |
| M4 | Resilience (retry + dead-letter queue) | [m4-resilience.md](m4-resilience.md) |
| M5 | CI/CD (GitHub Actions, GHCR, SHA tag) | [m5-cicd.md](m5-cicd.md) |
| M6 | Observability (metrics, dashboard, alert) | [m6-observability.md](m6-observability.md) |
| M7 | Cloud full-managed (EKS + S3 + RDS + Amazon MQ) | [m7-cloud.md](m7-cloud.md) |

## Quy ước
- Lệnh chạy **local dev**: trong `apps/*` với venv Python.
- Lệnh chạy **cluster**: `kubectl`/`helm`, namespace `pixelpipe` (app) và `monitoring` (observability).
- Mỗi milestone làm qua **branch → PR → merge**.
