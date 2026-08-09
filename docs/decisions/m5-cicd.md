# Decision — CI/CD pipeline (M5)

**Ngày:** 09-08-2026 · **Bối cảnh:** M5, tự động test + build + push image

## Vấn đề
Monorepo có api + worker. CI cần: chạy test **khi có PR** (chặn merge nếu đỏ) và build/push
image **khi merge main**; đồng thời né bẫy **mutable tag** (M4): cùng tag `:dev` thì rollout
không phân biệt được image cũ/mới.

## Phương án
- **Path filter (build cái gì khi đổi):** "chỉ build service đổi" (nhanh) vs "build cả 2 mỗi lần"
  (đơn giản). Rủi ro của path-filter: sửa **file dùng chung** (`config.py`/`models.py` copy ở cả
  hai) mà filter theo thư mục service → **bỏ sót build**.
- **Tag image:** `:latest`/`:dev` (mutable, đã dính bẫy) vs `:${{ github.sha }}` (bất biến).
- **Test:** unit test (không cần infra — đã thiết kế core/shell) chạy trên PR.

## Quyết định
- **Bỏ path filter — build cả 2 image mỗi lần.** Project nhỏ nên chi phí build thấp; đổi lại
  **đơn giản** và **né hẳn rủi ro bỏ sót file dùng chung**. (Khi repo lớn mới cân path filter.)
- **Tag image theo commit SHA** (bất biến) → deploy trỏ đúng 1 image, hết bẫy mutable tag.
- **Test chạy trên PR** → CI xanh mới merge vào main.

## Cạnh biên / hệ quả
- Build cả 2 mỗi lần = tốn thêm chút compute/thời gian CI — **không đáng kể** ở quy mô này.
- **SHA tag → CD/deploy phải biết trỏ tag nào**: pipeline deploy set `--set image.tag=<sha>`
  (hoặc cập nhật values). Không còn "latest" mơ hồ.
- Test unit không phủ đường-thành-công cần infra (integration) → để dành CI integration sau.

## Cách verify
- Mở PR sửa 1 dòng có lỗi test → **CI đỏ, bị chặn merge**.
- Merge main → xem Actions: 2 image `pixelpipe-api` + `pixelpipe-worker` lên GHCR **tag = SHA**.

## Làm ở đâu
M5: `ci.yml` (test 2 service + docker build) + `release.yml` (build/push tag SHA). Branch protection.
