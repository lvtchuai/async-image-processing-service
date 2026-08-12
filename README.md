# PixelPipe — Async Image Processing Service

[![CI](https://github.com/lvtchuai/async-image-processing-service/actions/workflows/ci.yml/badge.svg)](https://github.com/lvtchuai/async-image-processing-service/actions/workflows/ci.yml)
![Kubernetes](https://img.shields.io/badge/Kubernetes-KEDA%20scale--to--zero-326CE5?logo=kubernetes&logoColor=white)
![Terraform](https://img.shields.io/badge/IaC-Terraform-7B42BC?logo=terraform&logoColor=white)
![AWS](https://img.shields.io/badge/Cloud-EKS%20%2B%20S3%20%2B%20RDS%20%2B%20Amazon%20MQ-232F3E?logo=amazonaws&logoColor=white)

> Upload an image, get optimized variants (thumbnail, medium, WebP) generated **asynchronously**
> by a pool of workers that **autoscale on queue depth (scale-to-zero)**. Built **design-first** to
> demonstrate production-grade DevOps around an event-driven, resilient architecture — and deployed
> to **real AWS with fully managed backing services**.

---

## What this project demonstrates

| Area | Highlight |
|---|---|
| 🧩 **Async architecture** | API + message queue + worker pool + object storage — the shape of real systems |
| ☸️ **Event-driven autoscaling** | KEDA scales workers **0 → 8 → 0** on RabbitMQ queue depth (scale-to-zero) |
| 🛡️ **Resilience** | Bounded **retry** + **dead-letter queue** + **idempotent** processing (deterministic keys) |
| 🔄 **CI/CD** | GitHub Actions — PR-gated tests, image publishing to GHCR, **immutable SHA tags** |
| 📊 **Observability** | App metrics + **always-on queue metrics** (RabbitMQ exporter) + Grafana dashboards + alerts |
| ☁️ **Cloud (full-managed)** | Terraform → **EKS + S3 + RDS + Amazon MQ**; applied, verified end-to-end, destroyed clean |
| 📐 **Design-first** | Architecture + **ADRs** written before code; honest **retros** of real incidents |

---

## Architecture

```
User ─▶ API (FastAPI) ─▶ RabbitMQ ─▶ Worker(s) (Pillow) ─▶ Object Storage
             │                          ▲                        │
             └─▶ PostgreSQL (job)       └─ KEDA scale 0→N        └─▶ variants (thumbnail/medium/webp)

  LOCAL:  Postgres + RabbitMQ + MinIO  (in-cluster, one Helm chart)
  CLOUD:  RDS      + Amazon MQ + S3    (managed) — same chart, cloud.enabled=true
```

**The app code is identical local vs cloud** — only config (a Kubernetes Secret) and a Helm toggle
change. That portability is the payoff of a 12-factor, config-driven design.

**Tech stack:** Python (FastAPI + Pillow) · RabbitMQ / Amazon MQ · MinIO / S3 · PostgreSQL / RDS ·
Kubernetes + Helm · **KEDA** · Terraform · GitHub Actions · Prometheus + Grafana · k6.

---

## Highlights

**Event-driven autoscaling (KEDA).** Workers scale from **zero** based on RabbitMQ queue length —
verified `0 → 4 → 6 → 8 → 0` under load. Scale-to-zero trades a small cold-start for resource
savings, which is acceptable because the whole system is async.

**Resilience by design.** Poison inputs (undecodable images) go straight to a **dead-letter queue**;
transient failures **retry up to N times** then DLQ. Processing is **idempotent** (variant keys are
derived from the job id), so at-least-once delivery is safe.

**Deployed to real AWS, then destroyed.** A single `terraform apply` provisions VPC + EKS + ECR +
S3 + RDS + Amazon MQ + IAM. The app ran on EKS using the managed services end-to-end (verified via
`aws s3 ls` showing generated variants and a working presigned URL from the browser), then
`terraform destroy` tore it all down with **zero orphaned resources**.

---

## Repository structure
```
apps/       api · worker · frontend
deploy/     helm chart · keda · monitoring
infra/      terraform (modules: vpc, eks, ecr, s3, rds, mq + environments/dev)
docs/       architecture · adr · decisions · retros · milestones (build runbooks)
.github/    ci.yml · release.yml
docker-compose.yml   # full local stack
```

## Quick start (local)
```bash
docker compose up -d                      # Postgres + RabbitMQ + MinIO
# run api + worker locally (see docs/milestones/m1-app-skeleton.md)
curl -F "file=@photo.jpg" http://localhost:8000/images     # -> job_id
```
Or deploy to Kubernetes (minikube) with autoscaling — see the milestone runbooks below.

## Documentation (three layers)
- **[Build runbooks per milestone](docs/milestones/README.md)** — *what was built + every command, explained* (M0→M7)
- **[Architecture Decision Records](docs/adr/)** + **[decisions](docs/decisions/)** — *why each choice; trade-offs*
- **[Engineering mindset](docs/ENGINEERING-MINDSET.md)** — how decisions are reasoned about

> The retros (`docs/decisions/m*-retro.md`) honestly document **real operational incidents solved**
> — mutable image tags, DB migration gaps, scale-to-zero vs pull-scraping, blocking I/O starving
> health checks, Amazon MQ constraints, Terraform state locks, presigned-URL signatures. Hitting and
> fixing these is the difference between "ran a tutorial" and "operated a real system".

---

## Engineering practices
- **Design-first:** architecture + ADRs before code; a decision entry + retro per milestone.
- **Git flow:** feature branch → PR → CI → squash-merge; `main` protected by required checks.
- **Security-minded:** non-root containers, config via Secret (no hardcoding), immutable SHA image tags, S3 access scoped by IAM (IRSA-ready).
- **Cost-disciplined cloud:** managed infra is Terraform-managed and destroyed after verification; teardown is verified against AWS, not assumed.

## Status
✅ M0–M7 complete. Optional next steps (documented as tech debt): IRSA for keyless S3, KEDA on
Amazon MQ, Alembic migrations.
