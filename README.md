# PixelPipe — Async Image Processing Service

> Upload an image, get optimized variants (thumbnail, medium, WebP) generated **asynchronously**
> by a pool of workers that **autoscale on queue depth**. Built to demonstrate production-grade
> DevOps around an event-driven, resilient architecture.

**Status:** 🚧 In design (M0). See the plan before code — this project is built design-first.

## Design docs (read these first)
- [Architecture](docs/ARCHITECTURE.md) — requirements, diagram, components, data flow
- [Architecture Decision Records](docs/adr/) — the *why* behind each choice
- [Roadmap](docs/ROADMAP.md) — milestones with Definition of Done
- [Engineering Mindset](docs/ENGINEERING-MINDSET.md) — how decisions are reasoned about (design-first, trade-offs, failure-first)

## Architecture at a glance
```
User ─▶ API (FastAPI) ─▶ RabbitMQ ─▶ Worker(s) ─▶ Object Storage (MinIO/S3)
             │                          ▲                    │
             └─▶ PostgreSQL (jobs)      └─ KEDA autoscale     └─▶ variants
```

## Tech stack
Python (FastAPI + Pillow) · RabbitMQ · MinIO/S3 · PostgreSQL · Kubernetes + Helm · **KEDA** ·
Terraform · GitHub Actions · Prometheus + Grafana.

## Why this project
Compared to a simple CRUD app, PixelPipe exercises **asynchronous processing, worker pools,
queue-based autoscaling (KEDA), retries/dead-letter queues, and object storage** — the shape of
real production systems.

## Repository structure
```
apps/       api · worker · frontend
deploy/     helm chart · keda ScaledObject
infra/      terraform
docs/       architecture · adr · roadmap
.github/    ci/cd
```
