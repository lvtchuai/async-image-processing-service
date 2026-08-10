# M0 — Design-first

## Mục tiêu
Ra **tài liệu thiết kế trước khi code** — tư duy senior: quyết định kiến trúc + ghi lại lý do,
để sửa sai lúc rẻ nhất (chưa gõ dòng nào).

## Sản phẩm (không có runtime, chỉ tài liệu + khung repo)
- `docs/ARCHITECTURE.md` — yêu cầu (FR/NFR), sơ đồ, thành phần, luồng dữ liệu.
- `docs/adr/` — 6 **ADR** (Architecture Decision Record): async queue, RabbitMQ, object storage,
  KEDA, Python, monorepo. Mỗi ADR: *Context → Decision → Alternatives → Consequences*.
- `docs/ROADMAP.md` — 8 milestone + Definition of Done.
- `docs/ENGINEERING-MINDSET.md` — 10 mô hình tư duy junior→senior.

## Lệnh
```bash
# dựng khung thư mục (monorepo tách theo vai trò — xem ADR-0006)
mkdir -p apps/{api,worker,frontend} deploy/{helm,keda} infra/terraform docs/adr .github/workflows
```
*`mkdir -p`: tạo cây thư mục, `-p` để tạo cả thư mục cha, không lỗi nếu đã tồn tại.*

## Ý nghĩa
**ADR là "chữ ký senior"**: nó chứng minh mỗi lựa chọn công nghệ được cân nhắc *đánh đổi*, không
chọn đại. Khi phỏng vấn hỏi "vì sao dùng RabbitMQ?", câu trả lời nằm sẵn trong ADR-0002.

## Definition of Done
- [ ] ARCHITECTURE + 6 ADR + ROADMAP viết xong, khung repo sẵn sàng.
