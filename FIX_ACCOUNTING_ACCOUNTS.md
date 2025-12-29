# 🔧 FIX: Lỗi "Không tìm thấy tài khoản nhập kho"

## ❌ LỖI

```
Không tìm thấy tài khoản nhập kho cho sản phẩm Touch Screen 15.6".
Bạn phải xác định một tài khoản ở danh mục sản phẩm hoặc ở vị trí lưu kho
trước khi xử lý hoạt động này.
```

## 🔍 NGUYÊN NHÂN

Product Category được cấu hình với:
- `Costing Method = AVCO (Average Cost)` ✓
- `Inventory Valuation = Real Time` ✓

**NHƯNG:** Chưa có tài khoản kế toán (Stock Input/Output/Valuation accounts)

Khi valuation = **Real-time**, Odoo cần tài khoản để ghi nhận:
- Stock Input Account (nhập kho)
- Stock Output Account (xuất kho)
- Stock Valuation Account (định giá tồn kho)

---

## ✅ GIẢI PHÁP 1: CẤU HÌNH TÀI KHOẢN CHO CATEGORY (KHUYẾN NGHỊ)

### Bước 1: Mở Product Category

**Navigation:** `Inventory > Configuration > Product Categories`

**Click:** `Linh kiện DTX`

---

### Bước 2: Cấu hình Account Properties

**Tab:** `Account Properties`

**Tìm section:** `Stock Valuation`

**Kiểm tra:**
- Inventory Valuation: `Automated` ✓
- Costing Method: `Average Cost (AVCO)` ✓

**Cần cấu hình 3 tài khoản sau:**

| Field | Tài khoản | Số TK (Chart of Accounts VN) |
|-------|-----------|------------------------------|
| **Stock Valuation Account** | Hàng tồn kho | `156 - Hàng hóa` hoặc `152 - Nguyên vật liệu` |
| **Stock Journal** | Nhật ký kho | `Stock Journal` (mặc định) |
| **Stock Input Account** | Tài khoản nhập kho | `1561 - Hàng mua đang đi đường` |
| **Stock Output Account** | Tài khoản xuất kho | `632 - Giá vốn hàng bán` |

---

### Bước 3: Chọn tài khoản cụ thể

**Nếu bạn đang dùng Chart of Accounts mặc định của Odoo:**

#### **Stock Valuation Account:**
- Search: `stock` hoặc `inventory`
- Chọn: **Stock Interim (Received)** hoặc tương đương
- Ví dụ: `101200 Stock Interim (Received)`

#### **Stock Input Account:**
- Search: `stock input` hoặc `received`
- Chọn: **Stock Interim (Received)**
- Ví dụ: `101200 Stock Interim (Received)`

#### **Stock Output Account:**
- Search: `stock output` hoặc `delivered`
- Chọn: **Stock Interim (Delivered)**
- Ví dụ: `101300 Stock Interim (Delivered)`

---

### Bước 4: Save

**Click:** `Save`

---

### Bước 5: Lặp lại cho Category khác

**Cấu hình tương tự cho:**
- `Thành phẩm DTX` (category của Kiosk)

**KHÔNG CẦN** cấu hình cho:
- `Dịch vụ gia công` (vì type = Service, không nhập kho)
- `License phần mềm` (nếu type = Service)

---

## ✅ GIẢI PHÁP 2: DÙNG TÀI KHOẢN MẶC ĐỊNH (NHANH HƠN)

Nếu bạn không muốn cấu hình chi tiết, có thể dùng tài khoản mặc định:

### Tạo tài khoản đơn giản

**Navigation:** `Accounting > Configuration > Chart of Accounts`

**Click:** `Create`

**Tạo 3 tài khoản:**

#### **1. Stock Valuation Account**
| Field | Value |
|-------|-------|
| Code | 1520 |
| Account Name | Hàng tồn kho - DTX |
| Type | Current Assets |
| Reconcile | No |

#### **2. Stock Input Account**
| Field | Value |
|-------|-------|
| Code | 1521 |
| Account Name | Hàng đang về kho - DTX |
| Type | Current Assets |
| Reconcile | No |

#### **3. Stock Output Account**
| Field | Value |
|-------|-------|
| Code | 6320 |
| Account Name | Giá vốn hàng xuất - DTX |
| Type | Expenses |
| Reconcile | No |

**Sau đó quay lại Category config và chọn 3 tài khoản vừa tạo.**

---

## ✅ GIẢI PHÁP 3: TẮT REAL-TIME VALUATION (KHÔNG KHUYẾN NGHỊ)

Nếu bạn không cần kế toán real-time, có thể chuyển về Manual:

**Navigation:** `Inventory > Configuration > Product Categories`

**Click:** `Linh kiện DTX`

**Tab:** `Account Properties`

**Đổi:**
- Inventory Valuation: `Manual` (thay vì Automated)

**Click:** `Save`

**⚠️ LƯU Ý:** Cách này sẽ mất đi tính năng tự động cập nhật giá trị kho real-time.

---

## 🎯 KHUYẾN NGHỊ CỦA TÔI

**Dùng GIẢI PHÁP 1** với tài khoản mặc định của Odoo:

1. Mở Category `Linh kiện DTX`
2. Tab `Account Properties`
3. Chọn:
   - Stock Valuation Account: `Stock Interim (Received)`
   - Stock Input Account: `Stock Interim (Received)`
   - Stock Output Account: `Stock Interim (Delivered)`
4. Save
5. Lặp lại cho `Thành phẩm DTX`

**Sau đó quay lại Receipt và Validate lại.**

---

## 📝 SAU KHI FIX

**Kiểm tra:**
1. Receipt validate thành công ✓
2. Product On Hand = 3 Units ✓
3. Accounting > Journal Entries: Thấy stock entries tự động ✓

---

## 🔄 NẾU VẪN LỖI

Nếu sau khi cấu hình vẫn lỗi, kiểm tra:

### Check 1: Location có Stock Valuation Account không?

**Navigation:** `Inventory > Configuration > Locations`

**Mở:** `WH/Stock`

**Tab:** `Additional Information`

**Kiểm tra:** Valuation In/Out Account Prefix

Nếu rỗng → Không sao, dùng account từ Category.

### Check 2: Chart of Accounts đã cài chưa?

**Navigation:** `Accounting > Configuration > Settings`

**Section:** Fiscal Localization

**Kiểm tra:** Fiscal Localization Package installed

Nếu chưa → Install package cho Vietnam hoặc dùng Generic.

---

## 🚀 SCRIPT TỰ ĐỘNG (OPTIONAL)

Nếu bạn muốn, tôi có thể tạo script Python để tự động cấu hình accounts cho tất cả categories.

Cho tôi biết nếu cần!

---

**Created:** 2025-12-29
**Status:** Ready to fix
