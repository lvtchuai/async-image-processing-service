# Engineering Mindset — cách tư duy khi làm PixelPipe

> Mục tiêu của project này không chỉ là ra sản phẩm, mà là **luyện tư duy kỹ sư**. Artifact
> copy được; mindset thì không. Tài liệu này là "la bàn" — đọc lại trước mỗi milestone.

## Vì sao mindset > artifact
- Kỹ năng ("em dùng được K8s") thì ai học vài tháng cũng có.
- Tư duy ("vì sao em chọn cách này, đánh đổi gì, hỏng thế nào") mới cho biết bạn xử lý được
  vấn đề **chưa từng gặp**. Đó là thứ senior được trả lương, và là thứ phỏng vấn thật sự đo.

---

## 10 mô hình tư duy (junior → senior)

| # | Tư duy | Junior nghĩ | Senior nghĩ |
|---|---|---|---|
| 1 | **Trade-off, không "tốt nhất"** | "Tool nào xịn nhất?" | "Xịn nhất *cho ràng buộc nào*? Đánh đổi gì?" |
| 2 | **Cửa một chiều vs hai chiều** | Quyết định nào cũng như nhau | Việc *đảo được* thì làm nhanh; việc *khó đảo* (schema DB, public API, tốn tiền cloud) thì cân nhắc kỹ |
| 3 | **Nghĩ lỗi trước (failure-first)** | Làm happy path, lỗi tính sau | "Cái này hỏng kiểu gì?" — timeout, retry, mất kết nối, input độc — thiết kế cho lỗi *trước* |
| 4 | **Blast radius** | "Chạy là được" | "Nếu sai, hỏng tới đâu, ai chịu?" — cô lập thiệt hại (tách env, flag, canary) |
| 5 | **YAGNI + để lại 'seam'** | Xây cho tương lai tưởng tượng | Không over-engineer, nhưng để *đường nối sạch* để đổi rẻ (vd queue tách worker → đổi ngôn ngữ worker sau mà không đụng phần khác) |
| 6 | **Đo, đừng đoán** | "Chắc là chạy" | Chứng minh: load test, đọc metric, xem log. Niềm tin không phải bằng chứng |
| 7 | **Viết cho người đọc sau** | Code cho máy chạy | Code + doc cho *người kế tiếp* (hoặc chính mình 6 tháng sau). Không viết ra = chưa làm |
| 8 | **Đồng cảm vận hành** | "Deploy xong là hết việc" | "Ai trực 3h sáng? Nó có observable, debug được, có runbook không?" |
| 9 | **Kết quả, không phải task** | "Em đóng xong ticket" | "Hệ thống có *đáng tin* không? Người dùng có *được phục vụ* không?" |
| 10 | **Biết dừng** | Làm tới hoàn hảo | "Đủ tốt" + lặp lại nhanh > hoàn hảo mà không ship |

---

## Bộ câu hỏi senior — hỏi ở mỗi thay đổi

**TRƯỚC khi làm:**
- Mình đang giải *vấn đề thật* nào? (không phải "làm tính năng cho vui")
- Có những phương án nào? Mỗi cái đánh đổi gì?
- Quyết định này *đảo được* không? (một chiều thì cẩn thận hơn)
- Nó *hỏng kiểu gì*? Mình xử lý lỗi đó ra sao?
- Mình sẽ *biết nó chạy đúng* bằng cách nào? (đo cái gì)

**TRONG khi làm:**
- Đây có phải *cách đơn giản nhất* mà chạy được không? (hay mình đang phức tạp hóa?)
- Mình đang *giả định* điều gì? Giả định đó đúng không?

**SAU khi làm:**
- Nó có làm đúng ý mình định? (verify bằng chứng, không "chắc vậy")
- Mình *học* được gì? Lần sau làm khác chỗ nào?
- Đã *ghi lại* quyết định + bài học chưa?

---

## Cách luyện trong PixelPipe (nghi thức mỗi milestone)

1. **Trước khi code**: viết một "decision entry" ngắn (5 dòng) — vấn đề / phương án / chọn gì +
   vì sao / hỏng kiểu gì / verify sao. Quyết định lớn → nâng thành **ADR**.
2. **Mentor phản biện trước, giải pháp sau**: khi làm cùng, sẽ bị hỏi *"vì sao?"* và *"nếu…thì
   sao?"* trước khi có đáp án — để bạn *tự nghĩ ra*, không bị đút.
3. **Sau mỗi milestone**: retro 3 dòng — cái gì chạy tốt / cái gì bất ngờ / lần sau đổi gì.
4. **Ghi lại**: ADR cho quyết định, lessons-learned cho sự cố. Repo là bộ nhớ ngoài của bạn.

## Dấu hiệu bạn đang tiến bộ
- Bắt đầu tự hỏi "đánh đổi gì?" trước khi chọn — không cần ai nhắc.
- Nghĩ tới lỗi/vận hành *trước* khi code happy path.
- Giải thích được *vì sao không chọn* phương án kia, không chỉ *chọn gì*.
- Thấy khó chịu khi một quyết định không được ghi lại.

> Khi những điều trên thành phản xạ, bạn **là** senior trong tư duy — dù CV ghi "junior".
> Và đó chính là điều làm người phỏng vấn nhớ bạn.
