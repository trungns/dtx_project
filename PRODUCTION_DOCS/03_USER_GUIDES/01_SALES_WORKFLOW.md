# QUY TRÌNH BÁN HÀNG - DTX ODOO 16

**Phiên bản**: 2.0.0
**Cập nhật**: 2026-01-09

---

## TỔNG QUAN QUY TRÌNH

```
Quotation → PAKD (so sánh giá) → Confirm SO → Ký hợp đồng
→ Triển khai → Nghiệm thu → Invoice → Thu tiền
```

---

## BƯỚC 1: TẠO QUOTATION (BÁO GIÁ)

**Menu**: Sales → Quotations → Create

**Điền thông tin**:
1. Customer (Khách hàng)
2. End Customer (Khách hàng cuối - nếu bán qua đại lý)
3. Payment Terms (Điều khoản thanh toán): 30 Days
4. Thêm sản phẩm vào Order Lines

**Ví dụ**:
- Product: Self-service Kiosk - Complete System
- Quantity: 10
- Unit Price: 25,000,000 VND
- Tax: VAT 10%

**Lưu**: Click Save

**Trạng thái**: Quotation (Draft)

---

## BƯỚC 2: TẠO PAKD (PHƯƠNG ÁN KINH DOANH)

**Mục đích**: So sánh nhiều phương án giá để chọn phương án tối ưu

Chi tiết: [02_PAKD_MANAGEMENT.md](02_PAKD_MANAGEMENT.md)

**Tóm tắt**:
1. Mở Quotation → Click "Tạo PAKD mới"
2. Điền giá nhập, giá bán, giá HĐ cho từng sản phẩm
3. Hệ thống tự tính lợi nhuận và tỷ lệ lãi
4. Submit → Đợi phê duyệt
5. Sau khi duyệt → Apply vào Quotation

---

## BƯỚC 3: CONFIRM SALE ORDER

**Sau khi apply PAKD**:
1. Kiểm tra lại Order Lines và Total
2. Click **Confirm**
3. Trạng thái chuyển thành: **Sales Order**

**Điền thông tin hợp đồng**:
- Tab "Hợp đồng":
  - Số hợp đồng: HĐ/2026/VNPAY/001
  - Ngày ký: 05/01/2026
  - Ngày hết hạn: 05/01/2027
  - Upload file scan hợp đồng (PDF)

**Điền thông tin tạm ứng** (nếu có):
- Số tiền tạm ứng: 50,000,000 VND
- Ngày tạm ứng: 01/01/2026

---

## BƯỚC 4: TRIỂN KHAI

### 4.1. Giao hàng (Delivery)

**Menu**: Mở SO → Click Smart Button "Delivery"

**Steps**:
1. Kiểm tra sản phẩm trong Delivery Order
2. Click **Check Availability** (nếu hàng đã có trong kho)
3. Click **Validate**
4. Trạng thái: **Done**

### 4.2. Triển khai tại site

Tracking bằng:
- **Internal Notes** trên SO
- Hoặc tạo **Project** riêng

---

## BƯỚC 5: NGHIỆM THU

**Quy trình**:
1. Khách hàng kiểm tra và ký Biên bản nghiệm thu
2. Upload biên bản vào Chatter của SO
3. Ghi chú: "✅ Nghiệm thu hoàn tất ngày XX/XX/2026"

**Quan trọng**: Chỉ được xuất Invoice SAU KHI nghiệm thu!

---

## BƯỚC 6: XUẤT INVOICE

**Menu**: Mở SO → Click "Create Invoice"

**Chọn**:
- Regular Invoice (hóa đơn thường)
- Hoặc Down Payment (invoice tạm ứng - nếu cần)

**Click**: Create and View Invoice

**Kiểm tra**:
- Invoice Lines từ SO
- Total đúng
- VAT đúng

**Confirm**: Click Confirm → Invoice state = Posted

---

## BƯỚC 7: THU TIỀN

### 7.1. Thanh toán đủ (Full Payment)

**Menu**: Mở Invoice → Click "Register Payment"

**Điền**:
- Journal: Bank hoặc Cash
- Amount: (auto-fill = full amount)
- Payment Date: Ngày thu tiền
- Memo: "Thanh toán HĐ VNPAY"

**Click**: Create Payment

**Kết quả**:
- Invoice Payment Status = **Paid**
- SO Lifecycle State = **Paid**
- AR Residual = 0

### 7.2. Thanh toán từng đợt (Partial Payment)

**Ví dụ**: Thanh toán 50% trước, 50% sau

**Đợt 1**:
- Register Payment với Amount = 50% total
- Invoice Status = **Partial**

**Đợt 2**:
- Register Payment với Amount = 50% còn lại
- Invoice Status = **Paid**

---

## LIFECYCLE STATE (TRẠNG THÁI VÒNG ĐỜI)

Hệ thống tự động tracking qua 7 trạng thái:

| State | Ý nghĩa | Màu sắc |
|-------|---------|---------|
| **quotation** | Đang báo giá | Blue |
| **confirmed** | Đã confirm SO, chưa giao hàng | Blue |
| **working** | Đang giao hàng | Orange |
| **delivered** | Đã giao hàng đủ | Green |
| **invoiced** | Đã invoice, chưa thanh toán | Orange |
| **paid** | Đã thanh toán đủ | Green |
| **cancelled** | Hủy | Grey |

**Xem Lifecycle State**: Sales → Hợp đồng (Contract List)

---

## CÔNG NỢ (AR - ACCOUNTS RECEIVABLE)

### AR Residual (Công nợ còn lại)

**Công thức**:
```
AR Residual = Invoice Residual - Advance Amount
```

**Ví dụ**:
- Invoice: 100M, Đã thanh toán: 70M, Tạm ứng: 10M
- → AR = (100M - 70M) - 10M = **20M** (khách còn nợ 20M)

### AR Status

- **ok**: Không quá hạn
- **due_soon**: Sắp đến hạn (< 7 ngày)
- **overdue**: Quá hạn

**Xem AR**: Sales → Hợp đồng hoặc mở SO kiểm tra fields:
- AR Residual Total
- AR Max Days Overdue
- AR Status

Chi tiết: [05_AR_MANAGEMENT.md](05_AR_MANAGEMENT.md)

---

## HOA HỒNG (COMMISSION)

Nếu có hoa hồng cho KH hoặc người giới thiệu:

**Nhập tại**: SO → Tab "Hợp đồng" → Section "Chi phí cho KH/Người giới thiệu"

- Hoa hồng KH: 3,000,000
- Hoa hồng người GT: 2,000,000
- → Tổng HH: 5,000,000 (tự động tính)
- → Lãi ròng = Lãi - Tổng HH (tự động tính)

Chi tiết: [06_COMMISSION_TRACKING.md](06_COMMISSION_TRACKING.md)

---

## CHECKLIST ĐẦY ĐỦ

- [ ] Tạo Quotation
- [ ] Tạo PAKD và phê duyệt
- [ ] Apply PAKD vào Quotation
- [ ] Confirm Sale Order
- [ ] Điền thông tin hợp đồng (số HĐ, ngày ký, file scan)
- [ ] Giao hàng (Validate Delivery)
- [ ] Triển khai tại site
- [ ] Nghiệm thu (Upload biên bản)
- [ ] Xuất Invoice
- [ ] Thu tiền (Register Payment)
- [ ] Kiểm tra Lifecycle State = Paid
- [ ] Kiểm tra AR Residual = 0

---

## TROUBLESHOOTING

### Không tạo được PAKD

→ Kiểm tra SO có ít nhất 1 dòng sản phẩm

### Apply PAKD bị lỗi

→ Kiểm tra PAKD đã approve chưa

### Invoice không tạo được

→ Kiểm tra Delivery đã Done chưa

### Payment không match với Invoice

→ Kiểm tra Journal và Amount

---

**DTX Odoo 16 - Sales Workflow Guide**
