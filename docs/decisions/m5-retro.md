# Retro — M5 (CI/CD)

**Ngày:** 10-08-2026

## Chạy tốt điều gì?
- CI/CD chạy: PR-gated test + CD push **2 image lên GHCR, tag theo SHA** (né bẫy mutable tag M4).
- Branch protection bắt buộc CI xanh mới merge được.

## Điều gì bất ngờ / khó?
- **Bug branch-protection repo solo**: bật "Require approvals" nhưng GitHub **không cho tự duyệt
  PR của mình** → kẹt không merge được. Bài học: repo solo thì **require status checks, KHÔNG
  require approvals** (approvals dành cho team).

## Nợ kỹ thuật đã ghi nhận
- (kế thừa) migration: dev recreate DB, production cần Alembic.
- CI mới có **unit test**; chưa có **integration test** (đường thành công cần infra) — để dành.

## Lần sau (M6 — Observability) làm khác gì?
- Xử lý bài toán **scrape khi worker scale-to-zero** (0 pod thì Prometheus scrape ai?).
- Alert theo triết lý "không tự phục hồi", dùng `for` để tránh báo giả.
