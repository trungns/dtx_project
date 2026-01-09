# DTX Product Standards - Chuẩn hóa danh mục sản phẩm

**Version:** 1.0.0
**Odoo Version:** 16.0 Community
**Mục đích:** Chuẩn hóa dữ liệu sản phẩm DTX, giảm sai sót, chuẩn bị nền tảng cho sản xuất & gia công

---

## 📋 Tổng quan

Module này giúp:
- ✅ Phân loại sản phẩm rõ ràng theo chuẩn DTX
- ✅ Giảm sai sót khi nhập liệu sản phẩm
- ✅ Kiểm tra nhanh cấu hình sản phẩm
- ✅ Áp dụng chuẩn hàng loạt qua wizard
- ✅ Chuẩn bị nền tảng cho sản xuất Kiosk & gia công thuê ngoài

**Quan trọng:** Module này **KHÔNG ép buộc** workflow - chỉ hỗ trợ và chuẩn hóa!

---

## 🏷️ Các loại sản phẩm DTX

### 1. Thiết bị quản lý theo Serial

**Khi nào dùng:**
- Mỗi thiết bị cần quản lý riêng từng chiếc
- Cần theo dõi serial number, lịch sử, bảo hành

**Ví dụ:**
- Touch screen
- Mini PC
- Máy in nhiệt
- Tablet
- QR code reader
- CCCD reader

**Cấu hình khuyến nghị:**
- ✅ Product Type: `Storable Product`
- ✅ Tracking: `By Unique Serial Number`
- ✅ Category Cost Method: `AVCO (Average Cost)`
- ✅ Can be Purchased: `True`
- ✅ Can be Sold: `True`

---

### 2. Linh kiện / vật tư tiêu hao (không quản lý Serial)

**Khi nào dùng:**
- Vật tư dùng chung
- Không cần theo dõi từng chiếc
- Quản lý theo số lượng

**Ví dụ:**
- Cáp mạng
- Vít, ốc
- Dây điện
- Đầu RJ45
- Băng keo
- USB cable

**Cấu hình khuyến nghị:**
- ✅ Product Type: `Storable Product`
- ✅ Tracking: `No Tracking`
- ✅ Category Cost Method: `AVCO (Average Cost)`
- ✅ Can be Purchased: `True`
- ❌ Can be Sold: `False` (thường không bán riêng)

---

### 3. Kiosk / Thiết bị hoàn chỉnh

**Khi nào dùng:**
- Sản phẩm cuối cùng bán cho khách hàng
- Được lắp ráp từ nhiều linh kiện
- Có thể sản xuất nội bộ hoặc thuê đối tác lắp ráp

**Ví dụ:**
- DTX Kiosk Model A (có Touch screen + Mini PC + Printer)
- DTX Check-in Station
- DTX Queue Display System

**Cấu hình khuyến nghị:**
- ✅ Product Type: `Storable Product`
- ✅ Tracking: `By Unique Serial Number` (nếu cần)
- ✅ Category Cost Method: `AVCO (Average Cost)`
- ✅ Can be Purchased: `False` (sản xuất, không mua)
- ✅ Can be Sold: `True`
- ✅ **Cần có BOM (Bill of Materials)**

---

### 4. Dịch vụ (không quản lý kho)

**Khi nào dùng:**
- Phí dịch vụ, không phải hàng hóa vật lý
- Không nhập xuất kho

**Ví dụ:**
- Phí triển khai hệ thống
- Phí vận chuyển, lắp đặt
- Phí bảo trì, hỗ trợ
- Phí đào tạo

**Cấu hình khuyến nghị:**
- ✅ Product Type: `Service`
- ✅ Tracking: `No Tracking`
- ❌ Can be Purchased: `False` (thường không mua dịch vụ)
- ✅ Can be Sold: `True`

---

## 🎯 Cách sử dụng

### Bước 1: Tạo sản phẩm mới

1. Vào **Inventory > DTX – Chuẩn hóa dữ liệu > Sản phẩm DTX**
2. Click **Create**
3. Nhập thông tin cơ bản:
   - Product Name
   - **Loại sản phẩm DTX** ← Chọn 1 trong 4 loại
   - Product Category
4. **Save**

### Bước 2: Kiểm tra cấu hình (Tab "DTX – Kiểm tra nhanh")

Sau khi tạo sản phẩm, mở tab **"DTX – Kiểm tra nhanh"** để xem:

- ✓ Đã bật quản lý Serial?
- ✓ Danh mục giá vốn là Bình quân (AVCO)?
- ✓ Kiosk đã có BOM? (chỉ hiện với Kiosk)
- ✓ Cho phép mua hàng?
- ✓ Cho phép bán?

**Lưu ý:** Tab này CHỈ để kiểm tra - KHÔNG ép buộc. Các ô tích màu xanh (✓) nghĩa là đã cấu hình đúng chuẩn.

### Bước 3: Áp dụng chuẩn DTX (Wizard)

**Dùng khi nào:**
- Đã tạo nhiều sản phẩm nhưng chưa cấu hình đầy đủ
- Muốn cấu hình hàng loạt một lúc nhiều sản phẩm

**Cách dùng:**

1. **Chọn sản phẩm cần áp dụng chuẩn:**
   - Vào **Inventory > DTX – Chuẩn hóa dữ liệu > Sản phẩm DTX**
   - Chọn checkbox các sản phẩm (hoặc không chọn gì = áp dụng cho TẤT CẢ)

2. **Chạy Wizard:**
   - Click menu **Action** (⚙️ icon)
   - Chọn **"Áp dụng chuẩn DTX"**

3. **Chọn tùy chọn:**
   - ☑ **Áp dụng quản lý Serial:** Tự động bật/tắt serial tracking
     - Thiết bị Serial → BẬT serial tracking
     - Linh kiện → TẮT serial tracking
     - Dịch vụ → Chuyển type thành "Service"
   - ☑ **Áp dụng cấu hình mua/bán:** Tự động cấu hình mua/bán
     - Thiết bị/Linh kiện/Kiosk → Cho phép MUA
     - Thiết bị/Kiosk/Dịch vụ → Cho phép BÁN

4. **Click "Áp dụng"**

5. **Xem kết quả:**
   - Tổng số sản phẩm
   - Số sản phẩm đã cập nhật
   - Số sản phẩm bỏ qua (không thể thay đổi)
   - Chi tiết từng sản phẩm

**Lưu ý quan trọng:**
- ⚠️ **KHÔNG thể thay đổi tracking** nếu sản phẩm đã có giao dịch kho
- ✓ Wizard sẽ tự động BỎ QUA các sản phẩm không thể thay đổi
- ✓ Chỉ cập nhật khi bạn tích checkbox tùy chọn

---

## ⚠️ Lưu ý để tránh nhập sai dữ liệu

### 1. Chọn đúng loại sản phẩm DTX ngay từ đầu

**Sai:**
- Tạo sản phẩm "Touch screen" nhưng không chọn loại DTX
- Chọn loại "Linh kiện" cho Touch screen (sai - phải là "Thiết bị Serial")

**Đúng:**
- Touch screen → "Thiết bị quản lý theo Serial"
- Cáp HDMI → "Linh kiện / vật tư tiêu hao"
- DTX Kiosk A → "Kiosk / Thiết bị hoàn chỉnh"
- Phí lắp đặt → "Dịch vụ"

### 2. Không thể thay đổi tracking sau khi có giao dịch kho

**Kịch bản:**
1. Tạo sản phẩm "Touch screen"
2. Nhập kho 10 chiếc (đã validate receipt)
3. Muốn bật serial tracking → **KHÔNG ĐƯỢC!**

**Giải pháp:**
- Tạo sản phẩm MỚI với serial tracking
- Hoặc đảm bảo cấu hình đúng TRƯỚC KHI nhập kho lần đầu

### 3. Danh mục sản phẩm phải dùng AVCO

**Tại sao:**
- AVCO (Average Cost) là phương pháp tính giá vốn chuẩn cho thiết bị có serial
- Đảm bảo giá vốn chính xác khi giá nhập thay đổi

**Cách kiểm tra:**
- Mở sản phẩm > Tab "DTX – Kiểm tra nhanh"
- Xem dòng "✓ Danh mục giá vốn là Bình quân (AVCO)?"
- Nếu chưa tích → vào **Inventory > Configuration > Product Categories**
- Chọn category của sản phẩm > Set **Cost Method = Average Cost (AVCO)**

### 4. Kiosk cần có BOM

**Nếu sản phẩm là Kiosk:**
- Phải tạo BOM (Bill of Materials) để biết lắp ráp từ linh kiện gì
- Tab "DTX – Kiểm tra nhanh" sẽ cảnh báo nếu chưa có BOM

**BOM Template (Section D) sẽ được implement sau khi confirm**

---

## 📊 Workflow khuyến nghị

### Workflow 1: Nhập thiết bị Serial mới

```
1. Tạo sản phẩm:
   - Loại DTX: "Thiết bị quản lý theo Serial"
   - Tracking: "By Unique Serial Number"
   - Category: AVCO

2. Tạo PO (Purchase Order)
   - Nhập 5 chiếc Touch screen

3. Validate Receipt
   - Nhập serial cho từng chiếc: SN001, SN002, SN003, SN004, SN005

4. Vendor Bill
   - Tạo bill cho PO
   - State tự động: "Invoice Linked" (nếu dùng dtx_serial_ext)
```

### Workflow 2: Sản xuất Kiosk

```
1. Tạo sản phẩm Finished Kiosk:
   - Loại DTX: "Kiosk / Thiết bị hoàn chỉnh"

2. Tạo BOM cho Kiosk:
   - 1x Touch screen
   - 1x Mini PC
   - 1x Thermal Printer
   - 2x USB Cable
   - ... (các linh kiện khác)

3. Tạo Manufacturing Order
   - Odoo tự động trừ linh kiện ra khỏi kho
   - Tạo 1 Kiosk finished product vào kho
```

---

## 🏭 BOM Template - Quản lý sản xuất Kiosk (Section D)

### Mục đích

BOM Template giúp bạn quản lý **danh sách linh kiện** để lắp ráp Kiosk theo tư duy **giống Excel** - đơn giản, không ERP hóa phức tạp.

**Khi nào cần:**
- Sản xuất Kiosk nội bộ
- Gia công thuê ngoài (gửi linh kiện cho đối tác lắp ráp)
- Cần biết 1 Kiosk cần linh kiện gì và số lượng bao nhiêu

### Cách sử dụng BOM Template

#### Bước 1: Tạo BOM Template

1. **Vào menu:**
   - Inventory > DTX – Chuẩn hóa dữ liệu > **Mẫu BOM Kiosk**

2. **Click Create** và nhập thông tin:
   ```
   Tên mẫu BOM: "BOM Kiosk Model A"
   Sản phẩm hoàn chỉnh (Kiosk): [Chọn sản phẩm Kiosk đã tạo]
   Đối tác gia công: [Để trống nếu sản xuất nội bộ]
   ```

3. **Tab "Linh kiện"** - Thêm linh kiện:
   - Click "Add a line"
   - Chọn linh kiện (Touch screen, Mini PC, v.v.)
   - Nhập số lượng (số lượng cho **1 Kiosk**)
   - Lặp lại cho tất cả linh kiện

   **Ví dụ:**
   ```
   Touch Screen 15.6"    : 1 chiếc
   Mini PC Intel i5      : 1 chiếc
   Thermal Printer       : 1 chiếc
   USB Cable 1.5m        : 2 chiếc
   Cáp HDMI             : 1 chiếc
   Vít M4               : 20 chiếc
   ```

4. **Click Save**

#### Bước 2: Tạo BOM thực tế

1. **Trong form BOM Template, click button "Tạo BOM"**

2. **Wizard hiển thị:**
   - Tên mẫu BOM
   - Sản phẩm Kiosk
   - Số lượng linh kiện
   - Chế độ: Tạo mới / Cập nhật

3. **Click "Xác nhận tạo BOM"**

4. **Kết quả:**
   - BOM thực tế được tạo trong module Manufacturing
   - Có thể xem BOM: Click button "Xem BOM"

#### Bước 3: Sản xuất Kiosk

**Sau khi có BOM, bạn có thể:**

1. **Tạo Manufacturing Order (MO):**
   - Manufacturing > Operations > Manufacturing Orders
   - Create > Chọn sản phẩm Kiosk
   - Số lượng: 5 (ví dụ sản xuất 5 Kiosk)
   - Confirm

2. **Odoo tự động:**
   - Tính toán linh kiện cần thiết (5 Kiosk × BOM)
   - Trừ linh kiện ra khỏi kho khi MO hoàn tất
   - Tạo 5 Kiosk vào kho

### Gia công thuê ngoài (Subcontracting)

**Khi nào dùng:**
- Không tự lắp ráp, gửi cho đối tác gia công

**Cách cấu hình:**

1. **Tạo BOM Template:**
   - Chọn **Đối tác gia công**: [Tên đối tác]

2. **Click "Tạo BOM":**
   - BOM sẽ được cấu hình type = "subcontract"

3. **Quy trình:**
   - Tạo Purchase Order với đối tác gia công
   - Sản phẩm: Kiosk hoàn chỉnh (giá = phí gia công)
   - Odoo tự động:
     - Gửi linh kiện cho đối tác (theo BOM)
     - Nhận Kiosk hoàn chỉnh về kho

**Lưu ý:** Odoo 16 Community có hỗ trợ subcontracting cơ bản. Nếu cần tính năng nâng cao, nâng cấp lên Enterprise.

### Cập nhật BOM Template

**Khi linh kiện thay đổi:**

1. Mở BOM Template
2. Sửa danh sách linh kiện (thêm/xóa/đổi số lượng)
3. Save
4. Click button **"Cập nhật BOM"**
5. Confirm → BOM thực tế sẽ được cập nhật

**Lưu ý:**
- BOM cũ sẽ bị ghi đè (các dòng linh kiện cũ bị xóa)
- Manufacturing Order đã tạo TRƯỚC ĐÓ không bị ảnh hưởng
- MO mới sẽ dùng BOM đã cập nhật

---

## 🔧 Technical Details

### Database Fields

**product.template:**
- `x_dtx_type`: Selection (4 values)
- `x_dtx_requires_vendor_bill`: Boolean
- `x_dtx_notes`: Text
- `x_dtx_check_serial_enabled`: Boolean (computed)
- `x_dtx_check_avco_costing`: Boolean (computed)
- `x_dtx_check_has_bom`: Boolean (computed)
- `x_dtx_check_can_purchase`: Boolean (computed)
- `x_dtx_check_can_sell`: Boolean (computed)

**dtx.bom.template:**
- `name`: Char (required)
- `finished_product_tmpl_id`: Many2one product.template
- `component_line_ids`: One2many dtx.bom.template.line
- `subcontractor_id`: Many2one res.partner
- `bom_id`: Many2one mrp.bom (link to generated BOM)
- `bom_exists`: Boolean (computed)

**dtx.bom.template.line:**
- `component_product_id`: Many2one product.product
- `quantity`: Float
- `sequence`: Integer
- `notes`: Char

### Access Rights

- **Inventory Manager:** Full access to product standards wizard
- **Inventory User:** Read-only access to product standards wizard
- **Manufacturing Manager:** Full access to BOM templates
- **Manufacturing User:** Can create/edit BOM templates (no delete)

---

## 📞 Support

**Issues during usage:**

1. Kiểm tra logs:
   ```bash
   docker-compose logs -f odoo | grep "dtx_product_standards"
   ```

2. Verify module installed:
   - Apps > Search "DTX Product Standards"
   - Status: Installed ✅

3. Check menu visible:
   - Inventory > DTX – Chuẩn hóa dữ liệu
   - Should see: "Sản phẩm DTX"

---

## 📝 Version History

### Version 1.1.0 (Current)
- ✅ Section A: Data Model (4 loại sản phẩm DTX)
- ✅ Section B: Checklist tab (5 checks)
- ✅ Section C: Wizard "Áp dụng chuẩn DTX"
- ✅ Section D: BOM Template for Kiosk
  - Model: dtx.bom.template & dtx.bom.template.line
  - Wizard: Generate/Update mrp.bom from template
  - Subcontracting support (basic)
- ✅ Menu & Access rights
- ✅ Full documentation

### Version 1.0.0
- Initial release with Sections A, B, C
- BOM Template not yet implemented

---

**DTX Product Standards v1.1.0**
**Last Updated:** 2025-12-25
