# ADR-0006: Monorepo với ranh giới rõ ràng

**Trạng thái:** Accepted · **Ngày:** (điền)

## Context
Project có nhiều thành phần (api, worker, frontend, hạ tầng, deploy). Cần cấu trúc dễ điều
hướng và dễ CI/CD.

## Decision
**Monorepo** với thư mục tách theo vai trò:
```
apps/       code ứng dụng (api, worker, frontend)
deploy/     Helm chart + KEDA manifest
infra/      Terraform
docs/       ARCHITECTURE, ADR, ROADMAP
.github/    CI/CD
```

## Alternatives đã cân nhắc
- **Nhiều repo** (mỗi service một repo): phù hợp team lớn, nhưng với một người thì tốn công đồng
  bộ version, khó theo dõi. → loại.

## Consequences
- (+) Một chỗ nhìn toàn cảnh; CI/CD dùng path filter để build đúng service thay đổi.
- (−) Repo lớn dần; cần path filter trong CI để không build thừa.
