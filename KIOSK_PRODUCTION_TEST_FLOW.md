# 🏭 KIOSK PRODUCTION TEST FLOW - DTX

**Mục đích:** Test toàn bộ quy trình sản xuất Kiosk từ đầu đến cuối theo nghiệp vụ DTX
**Thời gian:** ~30-45 phút
**Version:** 1.0.0
**Date:** 2025-12-29

---

## 📋 OVERVIEW

Luồng test này mô phỏng quy trình sản xuất Kiosk thực tế của DTX:

```
1. MUA LINH KIỆN → 2. NHẬN KHO → 3. TẠO BOM → 4. GIA CÔNG → 5. NHẬN KIOSK → 6. BÁN CHO KHÁCH
```

---

## ✅ CHECKLIST TRƯỚC KHI BẮT ĐẦU

Đảm bảo bạn đã:
- [ ] Docker containers đang chạy (`docker-compose ps`)
- [ ] Odoo accessible tại http://localhost:8069
- [ ] Login: `admin@dtxco.vn` / `admin`
- [ ] Module **dtx_serial_ext** đã cài đặt
- [ ] Module **dtx_product_standards** đã cài đặt
- [ ] Đã chạy script setup data: `docker-compose exec odoo python3 /mnt/scripts/setup_dtx_data.py`

---

## 🎯 TEST SCENARIO

**Mục tiêu:** DTX cần sản xuất **3 chiếc Kiosk DTX-A17** để giao cho khách hàng

**Phương thức:**
- Mua linh kiện từ nhà cung cấp
- Gửi linh kiện cho LGMEC gia công lắp ráp
- Nhận Kiosk hoàn chỉnh về kho
- Bán cho khách hàng

---

## 📦 PHASE 1: CHUẨN BỊ DỮ LIỆU CƠ BẢN

### 1.1. Kiểm tra Vendors (Nhà cung cấp)

**Navigation:** `Contacts > Contacts`

**Cần có 6 vendors sau (đã tạo bởi setup script):**

| Vendor | Vai trò | Loại |
|--------|---------|------|
| **LGMEC** | Đối tác gia công lắp ráp Kiosk | Company (is_company=True) |
| **Công ty TNHH Touch Display Việt Nam** | Nhà cung cấp màn hình cảm ứng | Company |
| **Công ty CP Thiết bị In Hà Nội** | Nhà cung cấp máy in nhiệt | Company |
| **Công ty TNHH PC Components VN** | Nhà cung cấp Mini PC | Company |
| **Công ty TNHH Camera & Security** | Nhà cung cấp Camera IP | Company |
| **Công ty TNHH NFC Technology** | Nhà cung cấp đầu đọc CCCD | Company |

**✅ Action:**
- Mở từng vendor để xem thông tin
- Kiểm tra field `Company` = ✓

---

### 1.2. Kiểm tra Product Categories

**Navigation:** `Inventory > Configuration > Product Categories`

**Cần có 4 categories:**

| Category | Costing Method | Notes |
|----------|----------------|-------|
| DTX - Thiết bị Serial | AVCO | Cho Touch screen, Mini PC, Máy in |
| DTX - Linh kiện không Serial | AVCO | Cho cáp, vật tư |
| DTX - Kiosk hoàn chỉnh | AVCO | Cho sản phẩm cuối |
| DTX - Dịch vụ | AVCO | Cho dịch vụ gia công |

**✅ Action:**
- Xác nhận tất cả categories có `Costing Method = Average Cost (AVCO)`

---

### 1.3. Kiểm tra Products (Sản phẩm)

**Navigation:** `Inventory > Products > Products`

**Filter:** Bỏ filter mặc định, chọn `All` để thấy tất cả products

**Cần có sản phẩm sau (đã tạo bởi setup script):**

#### **LINH KIỆN (5 items):**

| Product | Category | DTX Type | Tracking | Can Purchase | Can Sell |
|---------|----------|----------|----------|--------------|----------|
| Touch Screen 21.5" | DTX - Thiết bị Serial | Thiết bị quản lý theo Serial | By Unique Serial Number | ✓ | ✓ |
| Mini PC i5 | DTX - Thiết bị Serial | Thiết bị quản lý theo Serial | By Unique Serial Number | ✓ | ✓ |
| Máy in nhiệt | DTX - Thiết bị Serial | Thiết bị quản lý theo Serial | By Unique Serial Number | ✓ | ✓ |
| Camera Webcam | DTX - Thiết bị Serial | Thiết bị quản lý theo Serial | By Unique Serial Number | ✓ | ✓ |
| CCCD Reader | DTX - Thiết bị Serial | Thiết bị quản lý theo Serial | By Unique Serial Number | ✓ | ✓ |

#### **KIOSK (1 item):**

| Product | Category | DTX Type | Tracking | Can Purchase | Can Sell |
|---------|----------|----------|----------|--------------|----------|
| DTX Kiosk A17 - Hệ thống xếp hàng thông minh | DTX - Kiosk hoàn chỉnh | Kiosk / Thiết bị hoàn chỉnh | By Unique Serial Number | ❌ | ✓ |

#### **DỊCH VỤ (1 item):**

| Product | Category | DTX Type | Product Type | Can Purchase | Can Sell |
|---------|----------|----------|--------------|--------------|----------|
| Dịch vụ gia công lắp ráp Kiosk | DTX - Dịch vụ | Dịch vụ (không quản lý kho) | Service | ✓ | ❌ |

**✅ Action:**
- Mở từng product để kiểm tra cấu hình
- Đặc biệt kiểm tra:
  - Product Type (Storable vs Service)
  - Tracking (Serial Number vs No Tracking)
  - Category đúng
  - Can Purchase / Can Sell đúng

---

## 🏭 PHASE 2: TẠO BOM TEMPLATE CHO KIOSK

**Mục tiêu:** Định nghĩa công thức sản xuất Kiosk DTX-A17

### 2.1. Tạo BOM Template

**Navigation:** `Inventory > Configuration > DTX - Công cụ > Mẫu BOM Kiosk`

**Click:** `Create`

**Nhập thông tin:**

| Field | Value |
|-------|-------|
| **Tên mẫu BOM** | BOM Template - DTX-A17 |
| **Sản phẩm Kiosk** | DTX Kiosk A17 - Hệ thống xếp hàng thông minh |
| **Đối tác gia công** | LGMEC |
| **Ghi chú** | Gia công lắp ráp Kiosk hoàn chỉnh từ 5 linh kiện |

**✅ Save**

---

### 2.2. Thêm Linh kiện vào BOM Template

**Tab:** `Linh kiện`

**Click:** `Add a line` và thêm từng linh kiện:

| STT | Linh kiện | Số lượng | Đơn vị |
|-----|-----------|----------|--------|
| 1 | Touch Screen 21.5" | 1 | Units |
| 2 | Mini PC i5 | 1 | Units |
| 3 | Máy in nhiệt | 1 | Units |
| 4 | Camera Webcam | 1 | Units |
| 5 | CCCD Reader | 1 | Units |

**Ghi chú (optional):** Có thể kéo thả để sắp xếp thứ tự

**✅ Save**

**Expected result:**
- Field `Tổng số linh kiện` = 5
- Field `BOM đã tạo` = ❌ (chưa generate BOM thực)

---

### 2.3. Generate BOM thực từ Template

**Click button:** `Tạo BOM` (màu xanh)

**Wizard hiện ra:**

**Kiểm tra thông tin:**
- BOM Template: BOM Template - DTX-A17 ✓
- Sản phẩm Kiosk: DTX Kiosk A17... ✓
- Số linh kiện: 5 ✓
- Đối tác gia công: LGMEC ✓
- Mode: Tạo mới (create) ✓

**Đọc cảnh báo:**
- ℹ️ "BOM mới sẽ được tạo"
- 🏭 "BOM sẽ được cấu hình cho subcontracting"

**Click:** `Xác nhận tạo BOM`

**Expected result:**
- Wizard chuyển sang tab "Kết quả"
- Message: "✅ BOM đã được tạo thành công cho sản phẩm DTX Kiosk A17..."
- Field `BOM đã tạo`: Hiển thị link đến BOM

**Click:** `Xem BOM`

**Kiểm tra BOM thực:**
- Product: DTX Kiosk A17 ✓
- BOM Type: Subcontracting ✓
- Subcontractor: LGMEC ✓
- Components tab: 5 linh kiện ✓

**✅ Close**

---

## 📥 PHASE 3: MUA LINH KIỆN TỪ CÁC NHÀ CUNG CẤP

**Mục tiêu:** Mua đủ 15 linh kiện (cho 3 Kiosk: 3 × 5 = 15 linh kiện) từ 5 vendors khác nhau

**Quan trọng:** Mỗi loại linh kiện mua từ vendor chuyên môn riêng!

---

### 3.1. PO #1 - Mua Touch Screen

**Navigation:** `Purchase > Orders > Purchase Orders`

**Click:** `Create`

**Nhập thông tin:**

| Field | Value |
|-------|-------|
| **Vendor** | Công ty TNHH Touch Display Việt Nam |
| **Order Date** | Hôm nay |

**Tab Order Lines - Add a line:**

| Product | Quantity | Unit Price |
|---------|----------|------------|
| Touch Screen 15.6" | 3 | 2,500,000 VND |

**Total:** 7,500,000 VND

**✅ Save** → **Confirm Order**

**Expected result:**
- Status: Purchase Order
- Smart button `Receipt` hiện ra

---

### 3.2. PO #2 - Mua Máy in nhiệt

**Navigation:** `Purchase > Orders > Purchase Orders`

**Click:** `Create`

| Field | Value |
|-------|-------|
| **Vendor** | Công ty CP Thiết bị In Hà Nội |
| **Order Date** | Hôm nay |

**Tab Order Lines:**

| Product | Quantity | Unit Price |
|---------|----------|------------|
| Thermal Printer 80mm | 3 | 1,800,000 VND |

**Total:** 5,400,000 VND

**✅ Save** → **Confirm Order**

---

### 3.3. PO #3 - Mua Mini PC

**Navigation:** `Purchase > Orders > Purchase Orders`

**Click:** `Create`

| Field | Value |
|-------|-------|
| **Vendor** | Công ty TNHH PC Components VN |
| **Order Date** | Hôm nay |

**Tab Order Lines:**

| Product | Quantity | Unit Price |
|---------|----------|------------|
| Mini PC Intel i5 | 3 | 4,500,000 VND |

**Total:** 13,500,000 VND

**✅ Save** → **Confirm Order**

---

### 3.4. PO #4 - Mua Camera

**Navigation:** `Purchase > Orders > Purchase Orders`

**Click:** `Create`

| Field | Value |
|-------|-------|
| **Vendor** | Công ty TNHH Camera & Security |
| **Order Date** | Hôm nay |

**Tab Order Lines:**

| Product | Quantity | Unit Price |
|---------|----------|------------|
| Camera IP 2MP | 3 | 1,200,000 VND |

**Total:** 3,600,000 VND

**✅ Save** → **Confirm Order**

---

### 3.5. PO #5 - Mua CCCD Reader

**Navigation:** `Purchase > Orders > Purchase Orders`

**Click:** `Create`

| Field | Value |
|-------|-------|
| **Vendor** | Công ty TNHH NFC Technology |
| **Order Date** | Hôm nay |

**Tab Order Lines:**

| Product | Quantity | Unit Price |
|---------|----------|------------|
| CCCD Reader NFC | 3 | 800,000 VND |

**Total:** 2,400,000 VND

**✅ Save** → **Confirm Order**

---

### 📊 Tổng giá trị mua linh kiện:

| Vendor | Product | Amount |
|--------|---------|--------|
| Touch Display VN | Touch Screen × 3 | 7,500,000 VND |
| Thiết bị In HN | Thermal Printer × 3 | 5,400,000 VND |
| PC Components VN | Mini PC × 3 | 13,500,000 VND |
| Camera & Security | Camera × 3 | 3,600,000 VND |
| NFC Technology | CCCD Reader × 3 | 2,400,000 VND |
| **TOTAL** | **15 linh kiện** | **32,400,000 VND** |

**Expected:** 5 Purchase Orders confirmed ✓

---

### 3.6. Nhận linh kiện vào kho (5 Receipts)

**Mục tiêu:** Nhận 15 linh kiện từ 5 vendors, mỗi linh kiện có serial riêng

**QUAN TRỌNG:** Mỗi linh kiện quản lý theo Serial cần nhập Serial Number riêng!

---

#### **Receipt #1: Touch Screen từ Touch Display VN**

**Navigation:** `Purchase > Orders > Purchase Orders`

**Mở PO:** Touch Display VN

**Click smart button:** `Receipt`

**Tab Detailed Operations:**

**Click vào dòng "Touch Screen 15.6" - Done: 0/3**

**Xóa dòng mặc định, thêm 3 serial:**

| Lot/Serial Number | Quantity |
|-------------------|----------|
| TS-DTX-001 | 1 |
| TS-DTX-002 | 1 |
| TS-DTX-003 | 1 |

**Click:** `Save` → `Validate`

**Expected:** Receipt Done ✓

---

#### **Receipt #2: Thermal Printer từ Thiết bị In HN**

**Mở PO:** Thiết bị In HN → Click `Receipt`

**Serial numbers:**

| Lot/Serial Number | Quantity |
|-------------------|----------|
| PRINTER-DTX-001 | 1 |
| PRINTER-DTX-002 | 1 |
| PRINTER-DTX-003 | 1 |

**Click:** `Save` → `Validate`

---

#### **Receipt #3: Mini PC từ PC Components VN**

**Mở PO:** PC Components VN → Click `Receipt`

**Serial numbers:**

| Lot/Serial Number | Quantity |
|-------------------|----------|
| PC-DTX-001 | 1 |
| PC-DTX-002 | 1 |
| PC-DTX-003 | 1 |

**Click:** `Save` → `Validate`

---

#### **Receipt #4: Camera từ Camera & Security**

**Mở PO:** Camera & Security → Click `Receipt`

**Serial numbers:**

| Lot/Serial Number | Quantity |
|-------------------|----------|
| CAM-DTX-001 | 1 |
| CAM-DTX-002 | 1 |
| CAM-DTX-003 | 1 |

**Click:** `Save` → `Validate`

---

#### **Receipt #5: CCCD Reader từ NFC Technology**

**Mở PO:** NFC Technology → Click `Receipt`

**Serial numbers:**

| Lot/Serial Number | Quantity |
|-------------------|----------|
| CCCD-DTX-001 | 1 |
| CCCD-DTX-002 | 1 |
| CCCD-DTX-003 | 1 |

**Click:** `Save` → `Validate`

---

### 3.7. Kiểm tra kho

**Navigation:** `Inventory > Products > Products`

**Kiểm tra từng sản phẩm:**

| Product | On Hand | Serials |
|---------|---------|---------|
| Touch Screen 15.6" | 3 Units | TS-DTX-001, 002, 003 |
| Thermal Printer 80mm | 3 Units | PRINTER-DTX-001, 002, 003 |
| Mini PC Intel i5 | 3 Units | PC-DTX-001, 002, 003 |
| Camera IP 2MP | 3 Units | CAM-DTX-001, 002, 003 |
| CCCD Reader NFC | 3 Units | CCCD-DTX-001, 002, 003 |

**✅ Expected:** 15 linh kiện đã vào kho với 15 serial numbers ✓

---

### 3.8. Tạo Vendor Bills (5 bills)

**Mục tiêu:** Tạo hóa đơn cho 5 vendors

**Lặp lại cho từng PO:**

1. **Purchase > Orders > Purchase Orders**
2. **Mở PO** (Touch Display VN / Thiết bị In HN / PC Components VN / Camera & Security / NFC Technology)
3. **Click:** `Create Bill`
4. **Kiểm tra thông tin** → **Confirm**

**Expected:** 5 Vendor Bills Posted ✓

| Vendor | Amount |
|--------|--------|
| Touch Display VN | 7,500,000 VND |
| Thiết bị In HN | 5,400,000 VND |
| PC Components VN | 13,500,000 VND |
| Camera & Security | 3,600,000 VND |
| NFC Technology | 2,400,000 VND |
| **TOTAL** | **32,400,000 VND** |

---

## 🏭 PHASE 4: GIA CÔNG KIOSK TẠI LGMEC

**Mục tiêu:** Gửi 15 linh kiện cho LGMEC, nhận về 3 Kiosk hoàn chỉnh

### 4.1. Tạo Purchase Order cho gia công (Subcontracting)

**Navigation:** `Purchase > Orders > Purchase Orders`

**Click:** `Create`

**Nhập thông tin:**

| Field | Value |
|-------|-------|
| **Vendor** | LGMEC |
| **Order Date** | Hôm nay |

**Tab Order Lines - Add a line:**

| Product | Quantity | Unit Price |
|---------|----------|------------|
| DTX Kiosk A17 - Hệ thống xếp hàng thông minh | 3 | 2,000,000 VND |

**Ghi chú:**
- Unit Price = Phí gia công lắp ráp (2 triệu/Kiosk)
- Odoo sẽ TỰ ĐỘNG tạo "Subcontracting" receipt do BOM Type = Subcontracting

**✅ Save**

**Click:** `Confirm Order`

**Expected result:**
- Status: Purchase Order
- Smart button `Receipt` hiện ra (1)
- Smart button `Resupply` hiện ra (1) ← **ĐÂY LÀ ĐIỂM KHÁC BIỆT CỦA SUBCONTRACTING!**

---

### 4.2. Gửi linh kiện cho LGMEC (Resupply)

**Click smart button:** `Resupply`

**Expected:**
- Transfer type: **Delivery Order**
- Destination: LGMEC/Subcontracting
- Products: 5 loại linh kiện × 3 = 15 dòng

**Tab Detailed Operations:**

**Odoo yêu cầu chọn Serial Number cụ thể để gửi cho LGMEC**

#### **Touch Screen (3 chiếc):**

**Click dòng "Touch Screen 21.5" - Done: 0/3**

**Tab "Detailed Operations":**

**Xóa dòng mặc định, chọn 3 serial đã nhập kho:**

| Lot/Serial Number | Quantity |
|-------------------|----------|
| TS-DTX-001 | 1 |
| TS-DTX-002 | 1 |
| TS-DTX-003 | 1 |

**Click:** `Save`

#### **Lặp lại cho 4 sản phẩm còn lại:**

**Mini PC:**
- PC-DTX-001, PC-DTX-002, PC-DTX-003

**Máy in nhiệt:**
- PRINTER-DTX-001, PRINTER-DTX-002, PRINTER-DTX-003

**Camera:**
- CAM-DTX-001, CAM-DTX-002, CAM-DTX-003

**CCCD Reader:**
- CCCD-DTX-001, CCCD-DTX-002, CCCD-DTX-003

---

### 4.3. Validate Resupply (Gửi linh kiện đi)

**Kiểm tra:**
- Tất cả dòng: Done 3/3 ✓

**Click:** `Validate`

**Expected result:**
- Status: Done
- 15 linh kiện đã rời kho `WH/Stock` → LGMEC/Subcontracting

**✅ Kiểm tra kho:**

**Navigation:** `Inventory > Products > Products > Touch Screen 21.5"`

**Tab Inventory:**
- On Hand: 0 Units ✓ (vì đã gửi hết cho LGMEC)

---

### 4.4. Nhận Kiosk hoàn chỉnh từ LGMEC

**Quay lại Purchase Order (LGMEC):**

**Click smart button:** `Receipt`

**Expected:**
- Transfer type: **Receipt**
- Source: LGMEC
- Product: DTX Kiosk A17 × 3

**Tab Detailed Operations:**

**QUAN TRỌNG:** Nhập Serial Number cho 3 Kiosk hoàn chỉnh!

**Click dòng "DTX Kiosk A17" - Done: 0/3**

**Tab "Detailed Operations":**

**Xóa dòng mặc định, thêm 3 serial mới:**

| Lot/Serial Number | Quantity |
|-------------------|----------|
| KIOSK-A17-001 | 1 |
| KIOSK-A17-002 | 1 |
| KIOSK-A17-003 | 1 |

**Click:** `Save` (trong popup)

**Click:** `Validate`

**Expected result:**
- Status: Done
- 3 Kiosk đã vào kho `WH/Stock`

**✅ Kiểm tra kho:**

**Navigation:** `Inventory > Products > Products > DTX Kiosk A17`

**Tab Inventory:**
- On Hand: 3 Units ✓

**Click:** `3 Units`

**Expected:** Thấy 3 serial:
- KIOSK-A17-001
- KIOSK-A17-002
- KIOSK-A17-003

---

### 4.5. Tạo Vendor Bill cho gia công

**Quay lại Purchase Order (LGMEC):**

**Click button:** `Create Bill`

**Kiểm tra:**
- Vendor: LGMEC ✓
- Product: DTX Kiosk A17 × 3 ✓
- Unit Price: 2,000,000 VND ✓
- Total: 6,000,000 VND ✓

**Click:** `Confirm`

**Expected result:**
- Status: Posted

---

## 🎁 PHASE 5: BÁN KIOSK CHO KHÁCH HÀNG

**Mục tiêu:** Bán 3 Kiosk đã sản xuất cho khách hàng

### 5.1. Tạo Customer (Khách hàng)

**Navigation:** `Contacts > Contacts`

**Click:** `Create`

**Nhập thông tin:**

| Field | Value |
|-------|-------|
| **Name** | Công ty ABC |
| **Company** | ✓ (check) |
| **Phone** | 0909123456 |
| **Email** | abc@example.com |

**✅ Save**

---

### 5.2. Tạo Sales Order

**Navigation:** `Sales > Orders > Quotations`

**Click:** `Create`

**Nhập thông tin:**

| Field | Value |
|-------|-------|
| **Customer** | Công ty ABC |
| **Order Date** | Hôm nay |

**Tab Order Lines - Add a line:**

| Product | Quantity | Unit Price |
|---------|----------|------------|
| DTX Kiosk A17 - Hệ thống xếp hàng thông minh | 3 | 50,000,000 VND |

**Expected calculation:**
- Subtotal: 150,000,000 VND

**✅ Save**

**Click:** `Confirm`

**Expected result:**
- Status: Sales Order
- Smart button `Delivery` hiện ra

---

### 5.3. Giao hàng cho khách

**Click smart button:** `Delivery`

**Validation:** Click vào Delivery Order (WH/OUT/XXXXX)

**Tab Detailed Operations:**

**Click dòng "DTX Kiosk A17" - Done: 0/3**

**Tab "Detailed Operations":**

**Xóa dòng mặc định, chọn 3 serial đã sản xuất:**

| Lot/Serial Number | Quantity |
|-------------------|----------|
| KIOSK-A17-001 | 1 |
| KIOSK-A17-002 | 1 |
| KIOSK-A17-003 | 1 |

**Click:** `Save`

**Click:** `Validate`

**Expected result:**
- Status: Done
- 3 Kiosk đã rời kho `WH/Stock` → Khách hàng

**✅ Kiểm tra kho:**

**Navigation:** `Inventory > Products > Products > DTX Kiosk A17`

**Tab Inventory:**
- On Hand: 0 Units ✓ (đã giao hết)

---

### 5.4. Tạo Invoice cho khách hàng

**Quay lại Sales Order:**

**Click button:** `Create Invoice`

**Invoice Method:** Regular invoice

**Click:** `Create Draft Invoice`

**Kiểm tra:**
- Customer: Công ty ABC ✓
- Product: DTX Kiosk A17 × 3 ✓
- Unit Price: 50,000,000 VND ✓
- Total: 150,000,000 VND ✓

**Click:** `Confirm`

**Expected result:**
- Status: Posted

**✅ Optional:** Click `Register Payment` để đánh dấu khách đã thanh toán

---

## 🔍 PHASE 6: KIỂM TRA TRUY XUẤT NGUỒN GỐC (TRACEABILITY)

**Mục tiêu:** Kiểm tra khả năng truy vết linh kiện từ Kiosk

### 6.1. Truy vết Serial Number của Kiosk

**Navigation:** `Inventory > Products > Lots/Serial Numbers`

**Search:** `KIOSK-A17-001`

**Mở Serial Number:**

**Tab "Traceability":**

**Expected:** Thấy toàn bộ lịch sử chuyển động:
1. Received from LGMEC (WH/IN/XXX)
2. Delivered to Công ty ABC (WH/OUT/XXX)

**Tab "Purchase Orders":**
- PO từ LGMEC ✓

**Tab "Sales Orders":**
- SO bán cho Công ty ABC ✓

**Tab "Vendor Bills":**
- Bill từ LGMEC (2,000,000 VND) ✓

**Tab "Customer Invoices":**
- Invoice cho Công ty ABC (50,000,000 VND) ✓

---

### 6.2. Truy vết linh kiện gốc

**Search serial:** `TS-DTX-001`

**Mở Serial Number:**

**Expected:**
1. Received from Supplier A (WH/IN/XXX)
2. Delivered to LGMEC/Subcontracting (Resupply)

**Tab "Purchase Orders":**
- PO từ Supplier A ✓

**Tab "Vendor Bills":**
- Bill từ Supplier A (2,500,000 VND) ✓

**✅ PASSED:** Hệ thống truy vết được toàn bộ nguồn gốc linh kiện!

---

## 📊 PHASE 7: KIỂM TRA BÁO CÁO & KHO

### 7.1. Inventory Valuation (Giá trị kho)

**Navigation:** `Inventory > Reporting > Inventory Valuation`

**Expected:**
- Touch Screen: 0 Units, Value: 0 VND ✓
- Mini PC: 0 Units, Value: 0 VND ✓
- DTX Kiosk A17: 0 Units, Value: 0 VND ✓

**Tất cả đã xuất hết!**

---

### 7.2. Stock Moves (Lịch sử chuyển động)

**Navigation:** `Inventory > Reporting > Stock Moves`

**Filter:** Product = DTX Kiosk A17

**Expected:** Thấy 6 moves (3 IN + 3 OUT):
1. WH/IN/XXX: KIOSK-A17-001 (Received from LGMEC)
2. WH/IN/XXX: KIOSK-A17-002 (Received from LGMEC)
3. WH/IN/XXX: KIOSK-A17-003 (Received from LGMEC)
4. WH/OUT/XXX: KIOSK-A17-001 (Delivered to Công ty ABC)
5. WH/OUT/XXX: KIOSK-A17-002 (Delivered to Công ty ABC)
6. WH/OUT/XXX: KIOSK-A17-003 (Delivered to Công ty ABC)

---

### 7.3. Purchase Analysis

**Navigation:** `Purchase > Reporting > Purchase Analysis`

**Expected:** 6 Purchase Orders:
1. Touch Display VN: 7,500,000 VND
2. Thiết bị In HN: 5,400,000 VND
3. PC Components VN: 13,500,000 VND
4. Camera & Security: 3,600,000 VND
5. NFC Technology: 2,400,000 VND
6. LGMEC: 6,000,000 VND (gia công)

**Total Purchase:** 38,400,000 VND

---

### 7.4. Sales Analysis

**Navigation:** `Sales > Reporting > Sales Analysis`

**Expected:** 1 Sales Order:
- Công ty ABC: 150,000,000 VND

**Gross Profit:** 150M - 38.4M = **111,600,000 VND** 🎉

---

## ✅ TEST COMPLETION CHECKLIST

Đánh dấu các bước đã hoàn thành:

### **Phase 1: Chuẩn bị dữ liệu**
- [ ] Vendors (LGMEC, Supplier A) ✓
- [ ] Product Categories (4 categories) ✓
- [ ] Products (7 products) ✓

### **Phase 2: Tạo BOM**
- [ ] BOM Template created ✓
- [ ] 5 Components added ✓
- [ ] BOM generated from template ✓
- [ ] BOM Type = Subcontracting ✓

### **Phase 3: Mua linh kiện**
- [ ] PO created for Supplier A ✓
- [ ] 15 linh kiện received with serial ✓
- [ ] Vendor Bill posted ✓

### **Phase 4: Gia công**
- [ ] PO created for LGMEC ✓
- [ ] Resupply 15 linh kiện to LGMEC ✓
- [ ] Receipt 3 Kiosk from LGMEC ✓
- [ ] Vendor Bill posted (gia công) ✓

### **Phase 5: Bán hàng**
- [ ] Customer created ✓
- [ ] Sales Order created ✓
- [ ] 3 Kiosk delivered with serial ✓
- [ ] Customer Invoice posted ✓

### **Phase 6: Traceability**
- [ ] Kiosk serial traceability ✓
- [ ] Component serial traceability ✓

### **Phase 7: Reporting**
- [ ] Inventory Valuation ✓
- [ ] Stock Moves ✓
- [ ] Purchase Analysis ✓
- [ ] Sales Analysis ✓

---

## 🎯 EXPECTED OUTCOMES

Sau khi hoàn thành test flow này, bạn đã:

✅ **Nghiệp vụ:**
- Hiểu rõ quy trình sản xuất Kiosk của DTX
- Biết cách sử dụng Subcontracting trong Odoo
- Quản lý được Serial Number cho từng linh kiện & Kiosk

✅ **Kỹ thuật:**
- Test được toàn bộ 2 modules (dtx_serial_ext + dtx_product_standards)
- Kiểm tra được BOM Template → BOM real
- Xác minh traceability hoạt động đúng
- Hiểu được luồng Purchase → Inventory → Sales

✅ **Data:**
- 2 Vendors
- 7 Products (5 components + 1 Kiosk + 1 Service)
- 18 Serial Numbers (15 linh kiện + 3 Kiosk)
- 2 Purchase Orders
- 1 Sales Order
- 3 Vendor Bills
- 1 Customer Invoice

---

## 🐛 TROUBLESHOOTING

### **Vấn đề 1: Không thấy smart button "Resupply"**

**Nguyên nhân:** BOM Type không phải Subcontracting

**Fix:**
1. Inventory > Products > Bill of Materials
2. Mở BOM của DTX Kiosk A17
3. Kiểm tra field `BoM Type` = `Subcontracting`
4. Nếu không, click Edit → Chọn `Subcontracting` → Save
5. Quay lại PO và F5 (refresh)

---

### **Vấn đề 2: Không nhập được Serial Number**

**Nguyên nhân:** Product không có Tracking = By Unique Serial Number

**Fix:**
1. Inventory > Products > Products
2. Mở product (vd: Touch Screen)
3. Tab `Inventory`
4. Kiểm tra field `Tracking` = `By Unique Serial Number`
5. Nếu không, chỉnh lại (nếu product chưa có stock move)

---

### **Vấn đề 3: Serial Number bị trùng**

**Nguyên nhân:** Nhập trùng serial trong 2 lần khác nhau

**Fix:**
- Odoo sẽ báo lỗi khi Validate
- Đổi serial thành unique (thêm số thứ tự khác)

---

### **Vấn đề 4: Không tạo được BOM từ Template**

**Nguyên nhân:**
- Template chưa có linh kiện
- Product không phải loại "Storable Product"

**Fix:**
1. Kiểm tra Template có ít nhất 1 component
2. Kiểm tra Finished Product Type = `Storable Product`

---

## 📝 NOTES & BEST PRACTICES

### **Về Serial Number:**
- Đặt tên có quy tắc: `PREFIX-DTX-XXX`
- Prefix cho từng loại: `TS` (Touch), `PC` (Mini PC), `KIOSK` (Kiosk)
- Số thứ tự: 001, 002, 003...

### **Về BOM:**
- Luôn dùng BOM Template trước khi generate BOM thực
- Dễ update và maintain hơn việc edit BOM trực tiếp

### **Về Subcontracting:**
- Vendor PHẢI là Company (is_company = True)
- BOM Type PHẢI là Subcontracting
- Odoo tự động tạo Resupply delivery

### **Về Vendor Bills:**
- Luôn create bill từ PO (không tạo manual)
- Đảm bảo link với PO để traceability hoạt động

---

## 🚀 NEXT STEPS

Sau khi test thành công, bạn có thể:

1. **Test case nâng cao:**
   - Sản xuất nhiều loại Kiosk khác nhau
   - Test với nhiều subcontractor
   - Test return/refund flow

2. **Customize thêm:**
   - Thêm fields vào Serial Number (warranty date, etc.)
   - Tạo report custom cho Kiosk
   - Thêm automation rules

3. **Training users:**
   - Ghi lại video demo flow này
   - Tạo SOP (Standard Operating Procedure)
   - Train nhân viên kho/mua hàng

---

**Document Version:** 1.0.0
**Created:** 2025-12-29
**Author:** DTX Team
**Status:** ✅ Ready for testing

🍀 **Good luck with testing!**
