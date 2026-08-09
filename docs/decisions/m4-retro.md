# Retro — M3 (KEDA scale-to-zero)

**Ngày:** 09-08-2026

## Chạy tốt điều gì?
- deploy k8s thành công với ảnh tốt vẫn done, file rác loại hẳn DLQ không lặp

## Điều gì bất ngờ / khó?
- bẫy multable tag với image cùng tag có sẵn không pull mới mà dùng cái cũ

## Nợ kỹ thuật đã ghi nhận
- tech debt: ở dev thì recreate cho database nhưng khi production cần alembic đó chính là migration thật

