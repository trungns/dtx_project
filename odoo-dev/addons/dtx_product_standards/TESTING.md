# DTX Product Standards - Testing Guide

**Module:** dtx_product_standards v1.0.0
**Mục đích:** Hướng dẫn test từng tính năng

---

## 🚀 BƯỚC 1: CÀI ĐẶT MODULE

### 1.1. Login vào Odoo
- URL: http://localhost:8069
- Database: `dtx_dev`
- User: `admin`
- Password: `admin`

### 1.2. Update Apps List
1. Vào **Apps** (📦 icon)
2. Click **⟳ Update Apps List**
3. Confirm **Update**

### 1.3. Install Module
1. Xóa filter "Apps" (nếu có)
2. Search: **"DTX Product Standards"**
3. Click **Install**
4. Chờ ~30 giây
5. Verify: Status = "Installed" ✅

### 1.4. Kiểm tra Menu
1. Vào **Inventory**
2. Tìm menu **"DTX – Chuẩn hóa dữ liệu"**
3. Submenu: **"Sản phẩm DTX"**

**Nếu thấy menu → Cài đặt thành công! ✅**

---

## 🧪 BƯỚC 2: TEST SECTION A - DATA MODEL

### Test Case 2.1: Tạo sản phẩm "Thiết bị Serial"

**Mục đích:** Test field "Loại sản phẩm DTX"

**Steps:**
1. Vào **Inventory > DTX – Chuẩn hóa dữ liệu > Sản phẩm DTX**
2. Click **Create**
3. Nhập thông tin:
   ```
   Product Name: Touch Screen 15.6"
   Product Type: Storable Product
   Loại sản phẩm DTX: Thiết bị quản lý theo Serial  ← FIELD MỚI
   Can be Purchased: ✓
   Can be Sold: ✓
   Product Category: All (hoặc tạo mới "DTX Devices")
   ```
4. Scroll xuống section **"DTX - Chuẩn hóa sản phẩm"**
   ```
   ✓ Bắt buộc có hóa đơn đầu vào: ✓  ← Default checked
   Ghi chú nghiệp vụ DTX: "Touch screen cho kiosk, 1920x1080"
   ```
5. Click **Save**

**Expected Result:**
- ✅ Sản phẩm tạo thành công
- ✅ Field "Loại sản phẩm DTX" = "Thiết bị quản lý theo Serial"
- ✅ Field "Bắt buộc có hóa đơn đầu vào" = checked

---

### Test Case 2.2: Tạo sản phẩm "Linh kiện"

**Steps:**
1. Create new product:
   ```
   Product Name: Cáp HDMI 2.0m
   Product Type: Storable Product
   Loại sản phẩm DTX: Linh kiện / vật tư tiêu hao
   Can be Purchased: ✓
   Can be Sold: □ (không bán riêng)
   ```
2. Save

**Expected Result:**
- ✅ Loại DTX = "Linh kiện / vật tư tiêu hao"

---

### Test Case 2.3: Tạo sản phẩm "Kiosk"

**Steps:**
1. Create new product:
   ```
   Product Name: DTX Kiosk Model A
   Product Type: Storable Product
   Loại sản phẩm DTX: Kiosk / Thiết bị hoàn chỉnh
   Can be Purchased: □ (sản xuất, không mua)
   Can be Sold: ✓
   ```
2. Save

**Expected Result:**
- ✅ Loại DTX = "Kiosk / Thiết bị hoàn chỉnh"

---

### Test Case 2.4: Tạo sản phẩm "Dịch vụ"

**Steps:**
1. Create new product:
   ```
   Product Name: Phí lắp đặt kiosk
   Product Type: Service  ← QUAN TRỌNG
   Loại sản phẩm DTX: Dịch vụ (không quản lý kho)
   Can be Purchased: □
   Can be Sold: ✓
   ```
2. Save

**Expected Result:**
- ✅ Loại DTX = "Dịch vụ"
- ✅ Product Type = "Service"

---

## 🧪 BƯỚC 3: TEST SECTION B - CHECKLIST TAB

### Test Case 3.1: Kiểm tra tab "DTX – Kiểm tra nhanh"

**Mục đích:** Verify computed fields hiển thị đúng

**Steps:**
1. Mở sản phẩm "Touch Screen 15.6"" (đã tạo ở Test 2.1)
2. Click tab **"DTX – Kiểm tra nhanh"**

**Expected Result - Thấy 5 dòng kiểm tra:**

```
Cấu hình sản phẩm:
  ☐ Đã bật quản lý Serial?             ← Hiện CHƯA tích (vì chưa set tracking)
  ☐ Danh mục giá vốn là Bình quân?     ← Tùy category
  ☐ Kiosk đã có BOM?                   ← INVISIBLE (không phải kiosk)

Quyền mua/bán:
  ✓ Cho phép mua hàng?                 ← Đã tích (vì set purchase_ok=True)
  ✓ Cho phép bán?                      ← Đã tích (vì set sale_ok=True)
```

**Expected Result - Thấy hướng dẫn:**
- Alert box màu xanh với tiêu đề "Tab này CHỈ để kiểm tra - KHÔNG ép buộc"
- Danh sách 4 loại sản phẩm
- Hướng dẫn dùng Wizard

---

### Test Case 3.2: Manual config Serial → Check update

**Mục đích:** Verify computed field cập nhật real-time

**Steps:**
1. Mở product "Touch Screen 15.6""
2. Tab **General Information**
3. Set **Tracking** = "By Unique Serial Number"
4. Click **Save**
5. Quay lại tab **"DTX – Kiểm tra nhanh"**

**Expected Result:**
- ✅ "Đã bật quản lý Serial?" → BẬT ✓ (màu xanh)

---

### Test Case 3.3: Kiểm tra Kiosk có BOM

**Steps:**
1. Mở product "DTX Kiosk Model A"
2. Tab **"DTX – Kiểm tra nhanh"**

**Expected Result:**
```
Cấu hình sản phẩm:
  ☐ Đã bật quản lý Serial?
  ☐ Danh mục giá vốn là Bình quân?
  ☐ Kiosk đã có BOM?                   ← HIỂN THỊ (vì là kiosk)
                                        ← Chưa tích (vì chưa tạo BOM)
```

---

## 🧪 BƯỚC 4: TEST SECTION C - WIZARD

### Test Case 4.1: Wizard "Áp dụng chuẩn DTX" - Apply cho 1 sản phẩm

**Mục đích:** Test wizard với sản phẩm đã chọn

**Setup:**
1. Đảm bảo đã tạo product "Touch Screen 15.6"" (từ Test 2.1)
2. Đảm bảo Tracking = "No Tracking" (chưa bật serial)

**Steps:**
1. Vào **Inventory > DTX – Chuẩn hóa dữ liệu > Sản phẩm DTX**
2. Chọn checkbox product "Touch Screen 15.6""
3. Click **Action** (⚙️ icon) > **"Áp dụng chuẩn DTX"**

**Wizard hiển thị:**
```
Tùy chọn áp dụng:
  ✓ Áp dụng quản lý Serial
  ✓ Áp dụng cấu hình mua/bán

Sản phẩm áp dụng:
  [Touch Screen 15.6"]  ← Pre-filled từ selection
```

4. Verify 2 checkbox đã tích
5. Click **"Áp dụng"**

**Expected Result - Wizard hiển thị kết quả:**
```
Thống kê:
  Tổng số sản phẩm: 1
  Đã cập nhật: 1
  Bỏ qua: 0

Chi tiết:
  === KẾT QUẢ ÁP DỤNG CHUẨN DTX ===

  Tổng số sản phẩm: 1
  Đã cập nhật: 1
  Bỏ qua: 0

  Chi tiết cập nhật:
  ✓ Touch Screen 15.6": Serial tracking: BẬT
```

6. Click **"Đóng"**
7. Mở lại product "Touch Screen 15.6""

**Verify:**
- ✅ Tracking = "By Unique Serial Number"
- ✅ Tab "DTX – Kiểm tra nhanh" > "Đã bật quản lý Serial?" = ✓

---

### Test Case 4.2: Wizard - Apply cho TẤT CẢ sản phẩm

**Mục đích:** Test wizard áp dụng hàng loạt

**Setup:**
1. Tạo thêm product "Mini PC Intel i5":
   ```
   Product Name: Mini PC Intel i5
   Loại sản phẩm DTX: Thiết bị quản lý theo Serial
   Tracking: No Tracking  ← Để chưa bật
   ```

2. Tạo product "Dây nguồn":
   ```
   Product Name: Dây nguồn 1.5m
   Loại sản phẩm DTX: Linh kiện / vật tư tiêu hao
   Tracking: Serial Number  ← Để SAI để test wizard tự sửa
   ```

**Steps:**
1. Vào **Inventory > DTX – Chuẩn hóa dữ liệu > Sản phẩm DTX**
2. KHÔNG chọn checkbox sản phẩm nào
3. Click **Action** > **"Áp dụng chuẩn DTX"**

**Wizard hiển thị:**
```
Sản phẩm áp dụng:
  [trống]  ← Không có sản phẩm pre-filled
```

4. Click **"Áp dụng"**

**Expected Result:**
```
Thống kê:
  Tổng số sản phẩm: 4-5  ← Tùy số sản phẩm đã tạo
  Đã cập nhật: 2+
  Bỏ qua: X

Chi tiết:
  ✓ Mini PC Intel i5: Serial tracking: BẬT
  ✓ Dây nguồn 1.5m: Serial tracking: TẮT  ← Tự động TẮT vì là linh kiện
  ...
```

**Verify:**
1. Mở "Mini PC Intel i5" → Tracking = "By Unique Serial Number"
2. Mở "Dây nguồn 1.5m" → Tracking = "No Tracking" (đã tự động tắt!)

---

### Test Case 4.3: Wizard - Không thể thay đổi tracking (có stock move)

**Mục đích:** Test wizard bỏ qua sản phẩm đã có giao dịch kho

**Setup:**
1. Tạo product mới:
   ```
   Product Name: Máy in nhiệt
   Loại sản phẩm DTX: Thiết bị quản lý theo Serial
   Tracking: No Tracking
   ```

2. Nhập kho sản phẩm này (tạo stock move):
   - Vào **Inventory > Operations > Receipts**
   - Click **Create**
   - Add product "Máy in nhiệt", qty=1
   - Click **Validate** (tạo stock move!)

**Steps:**
1. Chọn product "Máy in nhiệt"
2. Action > "Áp dụng chuẩn DTX"
3. Click "Áp dụng"

**Expected Result:**
```
Chi tiết:
  ✓ Máy in nhiệt: Serial tracking: BỎ QUA (đã có giao dịch kho)

Bỏ qua: 1
```

**Verify:**
- Tracking vẫn = "No Tracking" (KHÔNG đổi được)

---

## 🧪 BƯỚC 5: TEST TREE VIEW & FILTERS

### Test Case 5.1: Tree view hiển thị cột DTX Type

**Steps:**
1. Vào **Inventory > DTX – Chuẩn hóa dữ liệu > Sản phẩm DTX**
2. View = Tree (list view)

**Expected Result:**
- ✅ Cột "Loại sản phẩm DTX" hiển thị (optional show)
- ✅ Hiển thị label tiếng Việt cho từng sản phẩm

---

### Test Case 5.2: Filters hoạt động

**Steps:**
1. Click vào search box
2. Click **Filters** dropdown

**Expected Result - Thấy 4 filters:**
- Thiết bị Serial
- Linh kiện
- Kiosk
- Dịch vụ
- Yêu cầu hóa đơn đầu vào

**Test filter:**
1. Click "Thiết bị Serial"
2. Chỉ hiển thị sản phẩm có loại = "Thiết bị quản lý theo Serial"

---

### Test Case 5.3: Group By

**Steps:**
1. Search box > **Group By** > **"Loại sản phẩm DTX"**

**Expected Result:**
- Sản phẩm được nhóm theo 4 loại DTX
- Mỗi nhóm hiển thị label tiếng Việt

---

## 📊 CHECKLIST TỔNG HỢP

### Section A: Data Model
- [x] Field `x_dtx_type` hiển thị với 4 options tiếng Việt
- [x] Field `x_dtx_requires_vendor_bill` default=True
- [x] Field `x_dtx_notes` hoạt động
- [x] Tạo được 4 loại sản phẩm khác nhau

### Section B: Checklist Tab
- [x] Tab "DTX – Kiểm tra nhanh" hiển thị
- [x] 5 computed fields hoạt động đúng
- [x] Fields update real-time khi thay đổi cấu hình
- [x] Hướng dẫn hiển thị rõ ràng

### Section C: Wizard
- [x] Wizard mở từ Action menu
- [x] Apply cho sản phẩm đã chọn
- [x] Apply cho TẤT CẢ sản phẩm
- [x] Tự động bật/tắt serial tracking đúng
- [x] Tự động config mua/bán đúng
- [x] Bỏ qua sản phẩm có stock move
- [x] Hiển thị kết quả chi tiết

### UI/UX
- [x] Menu "DTX – Chuẩn hóa dữ liệu" hiển thị
- [x] Tree view có cột DTX Type
- [x] Filters hoạt động
- [x] Group By hoạt động
- [x] Help text hiển thị đủ

---

## 🐛 TROUBLESHOOTING

### Issue 1: Module không xuất hiện trong Apps

**Solution:**
```bash
# 1. Check logs
docker-compose logs -f odoo | grep -i error

# 2. Verify file permissions
ls -la /Users/trungns/dtx_project/odoo-dev/addons/dtx_product_standards/

# 3. Restart Odoo
docker-compose restart odoo

# 4. Update Apps List again
```

---

### Issue 2: Tab "DTX – Kiểm tra nhanh" không hiển thị

**Check:**
1. Module đã install? → Apps > DTX Product Standards > Status = Installed
2. Product form đã refresh? → F5
3. Có notebook tag trong form? → Nên có tabs khác (Sales, Purchase, etc.)

---

### Issue 3: Wizard không xuất hiện trong Action menu

**Check:**
1. Đã chọn sản phẩm trong list view? → Checkbox
2. Có quyền Inventory Manager? → Settings > Users
3. Force refresh: Ctrl+F5

---

### Issue 4: Computed fields không update

**Check:**
1. Product đã Save? → Click Save button
2. Tracking field có đúng? → General Info tab
3. Force recompute:
   ```python
   # Settings > Technical > Python Code
   product = env['product.template'].browse([PRODUCT_ID])
   product._compute_dtx_checklist()
   ```

---

## ✅ KẾT QUẢ MONG ĐỢI SAU KHI TEST XONG

Nếu TẤT CẢ test cases pass:
- ✅ Module hoạt động 100%
- ✅ Sẵn sàng để production
- ✅ Có thể tiếp tục implement Section D (BOM Template)

Nếu có lỗi:
- ⚠️ Ghi lại test case nào failed
- ⚠️ Copy error message
- ⚠️ Report để fix

---

**DTX Product Standards - Testing Guide v1.0.0**
**Last Updated:** 2025-12-25
