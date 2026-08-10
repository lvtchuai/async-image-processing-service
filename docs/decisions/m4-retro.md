# Retro — M4 (Retry + Dead-Letter Queue)

**Ngày:** 09-08-2026

## Chạy tốt điều gì?
- Deploy k8s thành công: ảnh tốt vẫn `done`, file rác bị loại hẳn sang **DLQ**, worker **không
  hot-loop**.
- Phân loại **lỗi độc vs lỗi tạm** chạy đúng: poison → 1 dòng `[poison->dlq]`, thẳng DLQ, không retry.

## Điều gì bất ngờ / khó?
- **Bẫy mutable tag**: image cùng tag `:dev` đã có sẵn thì k8s không pull mới → chạy code CŨ mà
  tưởng đã update. Né bằng **load-trước-restart-sau**, hoặc tag theo commit SHA.
- Debug: dấu hiệu "không có DLQ + queue rỗng + 0 worker" dẫn ra đúng nguyên nhân (image cũ).

## Nợ kỹ thuật đã ghi nhận
- Dev thì **recreate DB** để đổi schema; production cần **Alembic** (migration thật).
- (kế thừa) retry chưa có **backoff luỹ tiến**; `config.py`/`models.py` còn copy giữa api & worker.

## Lần sau (M5 — CI/CD) làm khác gì?
- Đưa test vào **CI để chặn merge nếu đỏ**.
- **Tag image theo commit SHA** — né đúng bẫy mutable tag vừa gặp.
- **Path filter**: chỉ build service nào đổi.
