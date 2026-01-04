# UAT Test Case: Contract Cost Tracking & Profit Analysis

**Module**: dtx_sales_pakd_contract v1.1.0
**Tester**: _______________________
**Date**: _______________________
**Duration**: ~30 phút
**Prerequisites**: Module đã cài đặt, có quyền DTX Sales User trở lên

---

## 📋 Kịch bản Test: Dự án "Cà phê Highlands 5 Quầy"

### Business Context
- **Đại lý (Customer)**: Công ty TNHH Highlands Coffee Vietnam
- **Khách hàng cuối (End User)**: Chi nhánh Highlands Bitexco (địa điểm lắp đặt thực tế)
- **Dự án**: Cung cấp và lắp đặt 5 quầy Kiosk tự phục vụ
- **Mục tiêu**: Test workflow từ PAKD → Chi phí thực tế → Theo dõi lãi/lỗ

**Lưu ý về cấu trúc khách hàng**:
```
Customer (partner_id)         = Công ty TNHH Highlands Coffee Vietnam (Đại lý ký HĐ)
End User (x_end_customer_id)  = Chi nhánh Highlands Bitexco (Nơi lắp đặt)
Đại lý cấp 2 (x_agent_id)     = (Để trống trong test case này)
```

---

## PHASE 1: Tạo Quotation và PAKD (10 phút)

### Step 1.1: Tạo Quotation
**Menu**: Sales → Quotations → Create

**Data nhập**:
```
Customer: Công ty TNHH Highlands Coffee Vietnam
Quotation Date: Hôm nay
```

**Order Lines** (thêm 5 dòng):

| Product | Description | Qty | Unit Price | Tax |
|---------|-------------|-----|------------|-----|
| [KIOSK] Kiosk Order & Payment | Quầy tự phục vụ Highlands | 5 | 30,000,000 | 10% VAT |

**✅ Expected**: Quotation tạo thành công, Total = 165,000,000 VND (150M + VAT 15M)

---

### Step 1.2: Điền thông tin DTX Business
**Sau field Customer**, nhập:

**Data nhập**:
```
Khách hàng cuối (End User): Chi nhánh Highlands Bitexco
  → Click "Create and Edit" nếu chưa có
  → Name: Chi nhánh Highlands Bitexco
  → Is a Company: ☐ (Không tick - vì là chi nhánh/individual location)
  → Save

Đại lý cấp 2 (nếu có): (Để trống)
```

**✅ Expected**:
- Fields hiển thị ngay sau Customer field
- Có thể tạo mới End User trực tiếp (có nút Create)
- Đại lý cấp 2 không cho tạo mới (no_create)

---

### Step 1.3: Tạo PAKD từ Quotation
**Tab**: Phương án kinh doanh (PAKD)

**Action**: Click "Tạo PAKD mới"

**✅ Expected**:
- PAKD mới được tạo với 1 dòng (5 Kiosk)
- Auto-fill: Product, Qty, Sale Unit Price, VAT 10%
- State = Draft

---

### Step 1.4: Điền giá mua dự kiến vào PAKD
**Tab PAKD Lines** (editable tree):

**Data nhập**:
```
Đơn giá nhập: 22,000,000 VND
Đơn giá HĐ: 30,000,000 VND (đã có)
VAT: 10% (đã có)
```

**✅ Expected**:
- Tổng mua (chưa VAT): 110,000,000 VND (22M × 5 - VAT đầu vào được khấu trừ)
- Tổng bán (chưa VAT): 150,000,000 VND (30M × 5)
- Lãi dự kiến: 40,000,000 VND (150M - 110M)
- Margin dự kiến: 36.36% (40M / 110M × 100)

---

### Step 1.5: Submit và Approve PAKD
**Actions**:
1. Click "Submit for Approval"
2. Click "Approve"

**✅ Expected**:
- State chuyển từ Draft → Submitted → Approved
- Header buttons thay đổi theo state

---

### Step 1.6: Apply PAKD vào Quotation
**Tab PAKD list**, click vào PAKD vừa approve:

**Action**: Click "Apply to Sales Order"

**Wizard settings**:
```
Thay thế toàn bộ dòng hiện tại: ✓ Tick
Nguồn giá: Ưu tiên đơn giá HĐ
```

**Action**: Click "Apply"

**✅ Expected**:
- Quotation lines được update với giá 30,000,000
- Chatter có message "✅ Đã apply PAKD..."
- Total vẫn = 165,000,000 VND

---

## PHASE 2: Confirm và Import Chi phí (10 phút)

### Step 2.1: Confirm Quotation
**Action**: Click "Confirm"

**✅ Expected**:
- State chuyển Draft → Sales Order
- SO number được generate (ví dụ: S00123)

---

### Step 2.2: Điền thông tin Hợp đồng
**Tab**: Hợp đồng

**Data nhập**:
```
Số hợp đồng: HĐ-HL-2026-001
Ngày ký HĐ: Hôm nay
Ngày hết hạn HĐ: +365 ngày
```

**File scan**: Upload 1 file PDF giả (hoặc screenshot)

**✅ Expected**: Fields lưu thành công

---

### Step 2.3: Import chi phí từ PAKD
**Tab**: Chi phí hợp đồng

**Action**: Click "Import chi phí từ PAKD"

**✅ Expected**:
- Notification "Đã import 1 dòng chi phí từ PAKD..."
- 1 dòng xuất hiện với:
  - Product: [KIOSK] Kiosk Order & Payment
  - Qty: 5
  - Đơn giá dự kiến: 22,000,000
  - Đơn giá thực tế: 22,000,000 (copy từ dự kiến)
  - Tổng dự kiến: 110,000,000
  - Tổng thực tế: 110,000,000
  - Chênh lệch: 0
  - Loại chi phí: Từ PAKD

---

## PHASE 3: Cập nhật Chi phí Thực tế (5 phút)

### Step 3.1: Điều chỉnh giá thực tế (Giá tăng)
**Scenario**: Vendor tăng giá từ 22M lên 23.5M/chiếc

**Action**: Trong tab "Chi phí hợp đồng", edit dòng Kiosk:
```
Đơn giá thực tế: 23,500,000
```

**✅ Expected**:
- Tổng thực tế: 117,500,000 (23.5M × 5)
- Chênh lệch: +7,500,000 (màu đỏ - vượt dự kiến)
- Tổng chi phí (footer): 117,500,000

---

### Step 3.2: Thêm chi phí phát sinh
**Scenario**: Phải mua thêm phần mềm quản lý không nằm trong PAKD

**Action**: Thêm dòng mới trong tree view:
```
Product: [SERVICE] Software License
Mô tả: Phần mềm quản lý Kiosk
Số lượng: 1
ĐVT: Unit
Đơn giá dự kiến: 0 (để trống)
Đơn giá thực tế: 5,000,000
Loại chi phí: Phát sinh
```

**✅ Expected**:
- Dòng mới màu đỏ (decoration-danger cho chi phí phát sinh)
- Tổng dự kiến: 110,000,000 (không đổi)
- Tổng thực tế: 122,500,000 (117.5M + 5M)
- Chênh lệch: +12,500,000
- Tổng chi phí (footer): 122,500,000

---

## PHASE 4: Tạo Invoice và Thanh toán (5 phút)

### Step 4.1: Tạo Invoice
**Tab**: Other Info (hoặc từ smart button "Invoices")

**Action**:
1. Click "Create Invoice"
2. Click "Confirm"

**✅ Expected**:
- Invoice được tạo với Total = 165,000,000 VND
- Invoice state = Posted

---

### Step 4.2: Đánh dấu đã thanh toán
**Invoice Form**:

**Action**: Click "Register Payment"

**Payment details**:
```
Payment Date: Hôm nay
Amount: 165,000,000
Journal: Bank
```

**Action**: Click "Create Payment"

**✅ Expected**:
- Invoice Payment State = Paid
- Invoice Date được ghi nhận

---

## PHASE 5: Kiểm tra Danh sách Hợp đồng (5 phút)

### Step 5.1: Vào menu Hợp đồng
**Menu**: Sales → Hợp đồng

**✅ Expected**:
- Menu hiển thị trong Sales
- List view mở ra với filter "Đơn hàng" active

---

### Step 5.2: Tìm hợp đồng vừa tạo
**Search**: Gõ "HĐ-HL-2026-001" hoặc "Highlands"

**✅ Expected**: Record xuất hiện với các giá trị:

| Field | Expected Value | Actual Value | ✓/✗ |
|-------|----------------|--------------|-----|
| Dự án | S00123 | _________ | ☐ |
| Khách hàng | Highlands Coffee Vietnam | _________ | ☐ |
| End user | Chi nhánh Highlands Bitexco | _________ | ☐ |
| Trạng thái | Sales Order (badge xanh) | _________ | ☐ |
| Doanh thu dự kiến | 150,000,000 | _________ | ☐ |
| Doanh thu thực tế | 150,000,000 | _________ | ☐ |
| Ngày thanh toán | Hôm nay | _________ | ☐ |
| Chi phí | 122,500,000 | _________ | ☐ |
| Lãi | 27,500,000 | _________ | ☐ |
| Lãi (%) | 22.45% | _________ | ☐ |
| Hợp đồng số | HĐ-HL-2026-001 | _________ | ☐ |
| Ngày ký HĐ | Hôm nay | _________ | ☐ |

**Calculation Check**:
```
Doanh thu thực tế: 150,000,000 (từ invoice paid, chưa VAT)
Chi phí thực tế:   122,500,000 (117.5M Kiosk + 5M Software, chưa VAT)
Lãi:                27,500,000 (150M - 122.5M)
Lãi %:              22.45% (27.5M / 122.5M × 100)
```

---

### Step 5.3: Test Filters
**Test các filter sau**:

| Filter | Expected | Actual | ✓/✗ |
|--------|----------|--------|-----|
| Có số hợp đồng | Hiển thị record | _______ | ☐ |
| Đã thanh toán | Hiển thị record | _______ | ☐ |
| Lãi > 0 | Hiển thị record | _______ | ☐ |
| Lỗ | Không hiển thị | _______ | ☐ |

---

### Step 5.4: Test Group By
**Group by**: Khách hàng

**✅ Expected**:
- Records group theo partner_id
- Hiển thị "Highlands Coffee Vietnam (1)"
- Sum doanh thu, chi phí, lãi correct

---

### Step 5.5: Test Columns Optional
**Action**: Click icon cột (⚙️) để show/hide columns

**Test**:
- Hide "Doanh thu dự kiến" → Column ẩn
- Show "Ngày ban giao thực tế" → Column hiện

**✅ Expected**: Columns toggle correct

---

## PHASE 6: Edge Cases (Nếu còn thời gian)

### Test 6.1: Import chi phí 2 lần
**Scenario**: Import lại chi phí từ PAKD

**Action**: Click "Import chi phí từ PAKD" lần 2

**✅ Expected**:
- Chi phí "Từ PAKD" cũ bị xóa
- Chi phí "Phát sinh" được GIỮ LẠI
- Import lại chi phí từ PAKD với giá dự kiến ban đầu

---

### Test 6.2: Hợp đồng chưa thanh toán
**Create new quotation** tương tự nhưng:
- Confirm thành SO
- Tạo invoice nhưng KHÔNG thanh toán
- Vào menu Hợp đồng

**✅ Expected**:
- Doanh thu thực tế = 0
- Ngày thanh toán = trống
- Lãi = âm (nếu có chi phí)
- Filter "Chưa thanh toán" hiển thị record này

---

### Test 6.3: Security - Sales User chỉ thấy của mình
**Login as**: User khác (Sales User role)

**Action**: Vào Sales → Hợp đồng

**✅ Expected**: Chỉ thấy hợp đồng do user đó tạo (record rules hoạt động)

---

## 📊 Test Summary

**Total Tests**: 25+
**Passed**: _____
**Failed**: _____
**Blocked**: _____

---

## ✅ Sign-off Criteria

Module v1.1.0 PASS nếu:
- ☐ Tất cả Phase 1-5 hoàn thành không lỗi
- ☐ Calculation lãi/lỗ chính xác 100%
- ☐ Import chi phí từ PAKD hoạt động
- ☐ Chi phí phát sinh được track riêng
- ☐ Menu Hợp đồng hiển thị đúng data
- ☐ Filters và Group By hoạt động
- ☐ Security rules hoạt động (nếu test được)

---

## 🐛 Issues Found

| # | Description | Severity | Status |
|---|-------------|----------|--------|
| 1 | ___________ | ________ | ______ |
| 2 | ___________ | ________ | ______ |
| 3 | ___________ | ________ | ______ |

---

## 📝 Notes

**Tester Notes**:
```
_______________________________________________________________
_______________________________________________________________
_______________________________________________________________
```

**Screenshots** (nếu cần):
- [ ] Contract list view
- [ ] Chi phí hợp đồng tab
- [ ] Profit calculation

---

**Approved By**: _______________________
**Date**: _______________________
**Signature**: _______________________
