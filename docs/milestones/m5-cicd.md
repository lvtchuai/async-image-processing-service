# M5 — CI/CD (GitHub Actions)

## Mục tiêu
Mỗi PR chạy test tự động (chặn merge nếu đỏ); merge main → build & push image **tag theo SHA**.

## Kiến trúc thêm vào
- `.github/workflows/ci.yml`: 3 job — test api, test worker, build 2 image (chạy trên PR).
- `.github/workflows/release.yml`: build & push image lên **GHCR**, tag `${{ github.sha }}`.
- **Branch protection** trên `main`: bắt buộc CI xanh mới merge.
- Quyết định: **bỏ path filter** (project nhỏ, build cả 2 cho đơn giản + né bẫy file dùng chung).

## Lệnh
```bash
# 1. tạo workflow, mở PR để CI chạy
git checkout -b feat/m5-cicd
git add .github/workflows/ci.yml
git commit -m "M5: CI"
git push -u origin feat/m5-cicd
gh pr create --fill          # tạo Pull Request từ CLI
gh pr checks --watch         # theo dõi 3 job CI tới khi xanh

# 2. thêm CD + merge -> release chạy
git add .github/workflows/release.yml && git commit -m "M5: CD" && git push
gh pr merge --squash --delete-branch   # gộp commit, xoá branch
gh run watch                           # xem Release build/push GHCR

# 3. kiểm image trên GHCR
gh api user/packages?package_type=container --jq '.[].name'
```

## Ý nghĩa quan trọng
- **`gh` (GitHub CLI)**: thao tác PR/checks/merge từ terminal, không cần mở web.
- **Tag `github.sha`** (bất biến): mỗi commit một image riêng → **hết bẫy mutable tag** (dev đã
  dính 3 lần). Deploy trỏ đúng 1 image, rollback chính xác.
- **GHCR + `GITHUB_TOKEN`**: push image bằng token tự cấp mỗi run — chỉ cần
  `permissions: packages: write`, không phải tạo secret.
- **Branch protection repo solo**: bật **status checks**, KHÔNG bật "require approvals" (không tự
  duyệt PR của mình được).

## Definition of Done
- [ ] PR có test đỏ → bị chặn merge; merge main → 2 image lên GHCR tag SHA.
