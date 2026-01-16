# Master Data Configuration Checklist

**Mục đích**: Hướng dẫn chuẩn hóa và cấu hình Master Data khi triển khai DTX modules trên Odoo 16 production environment

**Đối tượng**: Administrator, Implementation Team

**Thời điểm**: Trước khi đưa hệ thống vào sử dụng chính thức, sau khi cài đặt modules

---

## Tổng Quan Các Module DTX

| Module | Version | Mục đích |
|--------|---------|----------|
| dtx_product_standards | 1.3.0 | Chuẩn hóa sản phẩm (Serial Devices, Components, Kiosk, Services, Subscription) |
| dtx_serial_ext | 2.5.0 | Quản lý lifecycle thiết bị, tracking serial/lot, hóa đơn MISA |
| dtx_sales_pakd_contract | 1.8.1 | PAKD, Contract, AR Aging, Subscription Lifecycle, Commission |

---

## PHẦN I: CẤU HÌNH HỆ THỐNG CƠ BẢN

### 1. Inventory Settings (Bắt buộc)

**Đường dẫn**: `Settings > Inventory > Traceability`

- ✅ **Lots & Serial Numbers**: Enable
  - Cho phép tracking serial cho thiết bị
  - Bắt buộc cho dtx_serial_ext module

- ✅ **Storage Locations**: Enable
  - Quản lý kho chi tiết (Stock, Production, Subcontracted...)
  - Bắt buộc cho lifecycle state tracking

**Đường dẫn**: `Settings > Inventory > Operations`

- ✅ **Multi-Step Routes**: Enable (nếu sử dụng Delivery Orders)
- ✅ **Batch Transfers**: Optional (nếu cần xuất hàng loạt)

### 2. Manufacturing Settings (Nếu sản xuất Kiosk)

**Đường dẫn**: `Settings > Manufacturing`

- ✅ **Work Orders**: Enable (nếu có quy trình sản xuất phức tạp)
- ✅ **Subcontracting**: Enable (nếu có gia công thuê ngoài)
- ✅ **By-Products**: Optional

### 3. Sales Settings

**Đường dẫn**: `Settings > Sales > Quotations & Orders`

- ✅ **Product Variants**: Enable (nếu có variant của sản phẩm)
- ✅ **Quotation Templates**: Optional
- ✅ **Lock Confirmed Sales**: Recommended (tránh sửa SO đã xác nhận)

### 4. Accounting Settings

**Đường dẫn**: `Settings > Accounting > Taxes`

- ✅ **Tax Return Periodicity**: Monthly/Quarterly
- ✅ Cấu hình các mức VAT: 0%, 5%, 8%, 10%

**Đường dẫn**: `Settings > Accounting > Invoicing`

- ✅ **Cash Rounding**: Optional
- ✅ **Invoice Terms**: Cấu hình payment terms mặc định

---

## PHẦN II: MASTER DATA - PRODUCT CATEGORIES

### 1. Chuẩn Hóa Product Categories

**Đường dẫn**: `Inventory > Configuration > Product Categories`

**Cấu trúc đề xuất:**

```
All / Saleable
├── DTX - Serial Devices (Thiết bị có serial)
│   ├── Màn hình cảm ứng
│   ├── Mini PC
│   ├── Máy in
│   ├── Máy đọc thẻ
│   └── Camera
│
├── DTX - Components (Linh kiện)
│   ├── RAM
│   ├── SSD
│   ├── Nguồn điện
│   └── Cáp kết nối
│
├── DTX - Kiosk (Sản phẩm hoàn chỉnh)
│   ├── Kiosk thường
│   ├── Kiosk cao cấp
│   └── Kiosk tùy chỉnh
│
├── DTX - Services (Dịch vụ)
│   ├── Lắp đặt
│   ├── Bảo hành mở rộng
│   ├── Bảo trì định kỳ
│   └── Đào tạo
│
└── DTX - Subscription (Phần mềm thuê bao)
    ├── DiHub License
    └── SeQMS Online License
```

**Cấu hình cho mỗi Category:**

| Category | Product Type | Tracking | Costing | Routes |
|----------|-------------|----------|---------|--------|
| Serial Devices | Storable | By Unique Serial | Average Cost | Buy, MTO |
| Components | Storable | None/Lot | Average Cost | Buy |
| Kiosk | Storable | By Unique Serial | Average Cost | Manufacture |
| Services | Service | None | - | - |
| Subscription | Service | None | - | - |

**Lưu ý quan trọng:**

- ⚠️ **Serial Devices & Kiosk**: PHẢI set `Tracking = By Unique Serial Number`
- ⚠️ **Costing Method**: Nên dùng `Average Cost` cho tất cả storable products
- ⚠️ **Category routes** sẽ được kế thừa xuống products

### 2. Cấu Hình Costing Method

**Đường dẫn từng product**: `Product > Inventory tab > Costing Method`

**Khuyến nghị:**
- ✅ **Average Cost**: Cho tất cả thiết bị, linh kiện, kiosk
  - Tự động tính giá vốn trung bình
  - Phù hợp với nhập hàng nhiều lần từ nhiều vendor
- ❌ **Standard Price**: KHÔNG dùng (giá cố định không linh hoạt)
- ❌ **FIFO**: KHÔNG dùng (phức tạp không cần thiết cho DTX)

**Sau khi set Costing Method:**

```bash
# Recompute cost cho tất cả products (nếu cần)
Settings > Technical > Scheduled Actions
> "Update Cost" job
```

---

## PHẦN III: MASTER DATA - UNITS OF MEASURE

### 1. Product UoM (Đơn vị tính)

**Đường dẫn**: `Inventory > Configuration > UoM`

**Units cần thiết:**

| Category | Unit | Ratio | Type |
|----------|------|-------|------|
| Unit | Unit(s) | 1.0 | Reference |
| Weight | kg | 1.0 | Reference |
| Length | meter | 1.0 | Reference |
| Time | Month(s) | 1.0 | Reference |
| Time | Year(s) | 12.0 | Bigger |

**Lưu ý:**
- ⚠️ **Subscription products**: Dùng UoM = `Month(s)`
- ⚠️ **Serial devices**: Dùng UoM = `Unit(s)`
- ⚠️ **Components**: Dùng UoM phù hợp (Unit, kg, meter...)

### 2. Default UoM cho từng Product Category

Cấu hình mặc định:

```
Serial Devices → Units
Components → Units (hoặc kg nếu bán theo trọng lượng)
Kiosk → Units
Services → Units/Hours
Subscription → Months
```

---

## PHẦN IV: MASTER DATA - VENDORS & CUSTOMERS

### 1. Vendor Configuration

**Đường dẫ**: `Contacts > Vendors`

**Thông tin bắt buộc:**

- ✅ Name (Tên công ty)
- ✅ Tax ID (Mã số thuế)
- ✅ Address (Địa chỉ đầy đủ)
- ✅ Phone, Email
- ✅ Company Type: Company
- ✅ Tag: "Vendor" hoặc "Supplier"

**Payment Terms:**

```
- Net 30 days (Thanh toán sau 30 ngày)
- Net 15 days
- Immediate Payment (Thanh toán ngay)
- 50% Deposit (50% đặt cọc, 50% khi giao hàng)
```

**Đường dẫn**: `Accounting > Configuration > Payment Terms`

### 2. Customer Configuration

**Đường dẫn**: `Contacts > Customers`

**Phân loại customers:**

- ✅ **Direct Customer**: Khách hàng mua trực tiếp
- ✅ **Reseller/Agent**: Đại lý
- ✅ **End User**: Khách hàng cuối (nếu bán qua đại lý)

**Customer Tags (đề xuất):**

```
- VIP Customer
- Government
- Education
- Healthcare
- Retail
- Reseller Level 1
- Reseller Level 2
```

**Đường dẫn**: `Contacts > Configuration > Contact Tags`

---

## PHẦN V: MASTER DATA - PRODUCTS

### 1. Serial Devices (Thiết bị có serial)

**Đường dẫn**: `Inventory > Products > Products > Create`

**Cấu hình bắt buộc:**

```
General Tab:
- Product Name: Màn hình cảm ứng 19" ASUS
- Can be Sold: ✅
- Can be Purchased: ✅
- Product Type: Storable Product
- Part Number: AS-19T-VT190 (new in v1.3.0)
- Country of Origin: Taiwan (new in v1.3.0)

Inventory Tab:
- Tracking: By Unique Serial Number ⚠️ BẮT BUỘC
- Costing Method: Average Cost
- Routes: Buy, Make to Order (nếu cần)

Purchase Tab:
- Vendor: Chọn vendor mặc định
- Vendor Product Code: Mã SP của vendor
- Price: Giá nhập

Sales Tab:
- Sales Price: Giá bán
- Customer Taxes: VAT 10%
```

**DTX Standards Tab** (Tự động với dtx_product_standards):

```
- Product Type DTX: serial_device ✅
- Requires Serial Tracking: Yes (auto from tracking)
```

### 2. Components (Linh kiện)

**Cấu hình tương tự Serial Devices NHƯNG:**

```
Inventory Tab:
- Tracking: None HOẶC By Lots (nếu cần tracking theo lô)
- Costing Method: Average Cost

DTX Standards Tab:
- Product Type DTX: component
- Requires Serial Tracking: No
```

**Ví dụ Components:**

```
- RAM DDR4 8GB Kingston
- SSD 256GB Samsung
- Nguồn 12V 5A
- Cáp HDMI 2m
```

### 3. Kiosk (Sản phẩm hoàn chỉnh)

**Cấu hình:**

```
General Tab:
- Product Name: Kiosk Quản lý hàng đợi KS-001
- Product Type: Storable Product
- Part Number: DTX-KIOSK-001
- Country of Origin: Vietnam

Inventory Tab:
- Tracking: By Unique Serial Number ⚠️ BẮT BUỘC
- Costing Method: Average Cost
- Routes: Manufacture (⚠️ Quan trọng)

DTX Standards Tab:
- Product Type DTX: kiosk
- Has BOM Template: ✅ (nếu có BOM)
```

**BOM Configuration** (Bill of Materials):

**Đường dẫn**: `Manufacturing > Products > Bills of Materials > Create`

```
Product: Kiosk KS-001
BOM Type: Manufacture this product
Quantity: 1.0

Components:
- Màn hình 19" x 1
- Mini PC x 1
- Máy in x 1
- RAM DDR4 8GB x 2
- SSD 256GB x 1
- ... (các linh kiện khác)
```

**Hoặc dùng BOM Template** (dtx_product_standards module):

**Đường dẫn**: `Inventory > Configuration > DTX - Công cụ > BOM Templates`

### 4. Services (Dịch vụ)

**Cấu hình:**

```
General Tab:
- Product Name: Dịch vụ lắp đặt Kiosk
- Can be Sold: ✅
- Can be Purchased: ❌ (thường không mua dịch vụ)
- Product Type: Service

Sales Tab:
- Sales Price: 2,000,000 VND
- Service Tracking: Nothing (hoặc Timesheets nếu cần)

DTX Standards Tab:
- Product Type DTX: service
```

**Ví dụ Services:**

```
- Lắp đặt Kiosk (1 lần)
- Bảo hành mở rộng (12 tháng)
- Bảo trì định kỳ (1 tháng)
- Đào tạo sử dụng (1 ngày)
- Vận chuyển & lắp đặt
```

### 5. Subscription Products (Phần mềm thuê bao)

**Cấu hình (NEW in v1.3.0):**

```
General Tab:
- Product Name: DiHub License - 10 devices
- Can be Sold: ✅
- Can be Purchased: ❌
- Product Type: Service
- Part Number: DIHUB-LIC-10
- Country of Origin: Vietnam

Sales Tab:
- Sales Price: 5,000,000 VND
- UoM: Month(s) ⚠️ BẮT BUỘC

DTX Standards Tab:
- Product Type DTX: subscription ✅
- Base Price (per device/month): 500,000 VND
- Default Duration (months): 12
```

**Ví dụ Subscription Products:**

```
- DiHub License - 10 devices (12 months)
- DiHub License - 50 devices (12 months)
- SeQMS Online License - 10 devices (12 months)
- SeQMS Online License - 50 devices (12 months)
```

---

## PHẦN VI: MASTER DATA - LOCATIONS (KHO)

### 1. Warehouse Structure

**Đường dẫn**: `Inventory > Configuration > Locations`

**Cấu trúc đề xuất:**

```
Physical Locations
├── DTX Warehouse (Kho chính)
│   ├── Stock (Tồn kho)
│   ├── Pre-Production (Chuẩn bị sản xuất)
│   ├── Production (Đang sản xuất)
│   ├── Quality Control (Kiểm tra chất lượng)
│   └── Packing Zone (Khu đóng gói)
│
├── Virtual Locations
│   ├── Vendor Location (Từ nhà cung cấp)
│   ├── Customers (Đến khách hàng)
│   ├── Subcontracted Location (Gia công thuê ngoài)
│   └── Production (Location ảo cho sản xuất)
│
└── Inventory Loss (Hao hụt)
```

**Location Types:**

| Location | Location Type | Usage |
|----------|---------------|-------|
| Stock | Internal | Tồn kho chính |
| Pre-Production | Internal | Linh kiện đã lấy ra chuẩn bị |
| Production | Internal | Đang sản xuất (virtual or internal) |
| Quality Control | Internal | Kiểm tra trước xuất |
| Subcontracted | Internal | Hàng gia công bên ngoài |
| Customers | Customer | Đã bán cho khách |
| Vendors | Supplier | Mua từ vendor |

**Lưu ý:**
- ⚠️ **Lifecycle State** của dtx_serial_ext sẽ tự động xác định dựa trên location
- ⚠️ Devices ở location "Production" → lifecycle = `in_production`
- ⚠️ Devices ở location "Customers" → lifecycle = `delivered`

---

## PHẦN VII: MASTER DATA - TAXES (THUẾ)

### 1. VAT Configuration

**Đường dẫn**: `Accounting > Configuration > Taxes`

**Các mức thuế cần tạo:**

#### A. Sales Taxes (Thuế đầu ra)

```
1. VAT 0% (Sales)
   - Tax Type: Sales
   - Tax Computation: Percentage of Price
   - Amount: 0%
   - Tax Scope: Services

2. VAT 5% (Sales)
   - Tax Type: Sales
   - Tax Computation: Percentage of Price
   - Amount: 5%
   - Tax Scope: Goods

3. VAT 8% (Sales)
   - Tax Type: Sales
   - Tax Computation: Percentage of Price
   - Amount: 8%
   - Tax Scope: Goods

4. VAT 10% (Sales)
   - Tax Type: Sales
   - Tax Computation: Percentage of Price
   - Amount: 10%
   - Tax Scope: Goods (Default cho DTX devices)
```

#### B. Purchase Taxes (Thuế đầu vào)

```
1. VAT 0% (Purchase)
   - Tax Type: Purchase
   - Tax Computation: Percentage of Price
   - Amount: 0%

2. VAT 5% (Purchase)
   - Tax Type: Purchase
   - Tax Computation: Percentage of Price
   - Amount: 5%

3. VAT 8% (Purchase)
   - Tax Type: Purchase
   - Tax Computation: Percentage of Price
   - Amount: 8%

4. VAT 10% (Purchase)
   - Tax Type: Purchase
   - Tax Computation: Percentage of Price
   - Amount: 10%
```

### 2. Tax Mapping trong PAKD

**dtx_sales_pakd_contract module** tự động map VAT % sang account.tax:

```
PAKD Line VAT % → Odoo Tax
0% → VAT 0% (Sales)
5% → VAT 5% (Sales)
8% → VAT 8% (Sales)
10% → VAT 10% (Sales)
```

**Lưu ý:**
- ⚠️ Nếu bạn có tên thuế khác (ví dụ "Thuế GTGT 10%"), module sẽ tìm tax có rate = 10%
- ⚠️ Đảm bảo có ít nhất 1 tax cho mỗi mức % bạn dùng trong PAKD

---

## PHẦN VIII: MASTER DATA - USERS & PERMISSIONS

### 1. User Groups (Security Groups)

**Đường dẫn**: `Settings > Users & Companies > Groups`

**DTX Security Groups** (tự động tạo bởi dtx_sales_pakd_contract):

```
1. DTX - CEO (Full access)
   - Full access to PAKD, Contract Costs, Commission
   - Can see all Sale Orders
   - Can approve PAKD

2. DTX - Sales Director (Giám đốc kinh doanh)
   - Full access to PAKD, Contract Costs
   - Can see all Sale Orders
   - Can approve PAKD
   - Can manage subscriptions

3. DTX - Chief Accountant (Kế toán trưởng)
   - Read/Write Contract Costs
   - Read-only PAKD
   - Access to AR Aging report
   - Subscription finance tracking

4. DTX - Sales User (Nhân viên kinh doanh)
   - Create/edit own Sale Orders
   - Create PAKD (readonly after approval)
   - View own commission
   - Limited subscription access
```

### 2. User Configuration

**Đường dẫn**: `Settings > Users & Companies > Users`

**Cấu hình cho mỗi user:**

```
User tab:
- Name: Nguyễn Văn A
- Email: nguyenvana@dtx.com
- Login: nguyenvana

Access Rights tab:
- Sales: Sales User / Sales Manager
- Inventory: User / Manager
- Manufacturing: User / Manager (nếu cần)
- Accounting: Invoicing / Billing (ít nhất)

DTX Groups:
- Chọn 1 trong 4 groups DTX ở trên
```

**Khuyến nghị phân quyền:**

| Vị trí | Odoo Sales | Odoo Inventory | DTX Group |
|--------|------------|----------------|-----------|
| CEO | Manager | Manager | DTX - CEO |
| Sales Director | Manager | Manager | DTX - Sales Director |
| Accountant | Invoicing | User | DTX - Chief Accountant |
| Sales Staff | User | User | DTX - Sales User |
| Warehouse Staff | User | Manager | - |

---

## PHẦN IX: MASTER DATA - PAYMENT TERMS

### 1. Payment Terms Configuration

**Đường dẫn**: `Accounting > Configuration > Payment Terms`

**Các điều khoản đề xuất:**

```
1. Immediate Payment (Thanh toán ngay)
   Terms: Due on receipt

2. Net 7 days
   Terms: 7 Days

3. Net 15 days
   Terms: 15 Days

4. Net 30 days (Phổ biến nhất)
   Terms: 30 Days

5. Net 45 days
   Terms: 45 Days

6. Net 60 days
   Terms: 60 Days

7. 50% Deposit, 50% on Delivery
   Terms:
   - 50% Due on receipt
   - 50% Due on delivery

8. 30% Deposit, 70% on Delivery
   Terms:
   - 30% Due on receipt
   - 70% Due on delivery
```

### 2. Default Payment Terms

**Cấu hình mặc định:**

- **Vendors**: Net 30 days (cho phép thanh toán chậm)
- **Customers**: Net 15 days (thu tiền nhanh hơn)
- **Subscription**: Immediate Payment (trả trước)

---

## PHẦN X: DTX-SPECIFIC CONFIGURATIONS

### 1. Apply DTX Standards (Chuẩn hóa hàng loạt)

**Đường dẫn**: `Inventory > Configuration > DTX - Công cụ > Apply DTX Standards`

**Wizard để áp dụng chuẩn cho nhiều products:**

```
Step 1: Chọn Product Type DTX
- ☐ Serial Device
- ☐ Component
- ☐ Kiosk
- ☐ Service
- ☐ Subscription

Step 2: Chọn products cần áp dụng (filter by category)

Step 3: Click "Apply Standards"
```

**Wizard sẽ tự động:**
- Set tracking = By Unique Serial (cho serial devices & kiosk)
- Set costing method = Average Cost
- Set DTX product type
- Configure routes (Buy, MTO, Manufacture)

### 2. BOM Template Configuration (Cho Kiosk)

**Đường dẫn**: `Inventory > Configuration > DTX - Công cụ > BOM Templates`

**Tạo BOM Template:**

```
BOM Template Name: Kiosk Standard KS-001
Finished Product: Kiosk KS-001
Subcontractor: (để trống nếu tự sản xuất)

Components:
- Màn hình 19" ASUS x 1
- Mini PC Intel i5 x 1
- Máy in nhiệt 80mm x 1
- RAM DDR4 8GB x 2
- SSD 256GB x 1
- Nguồn 12V 10A x 1
- Vỏ Kiosk thép x 1
```

**Generate BOM từ Template:**

```
Click "Generate BOM" button
→ Tạo real mrp.bom từ template
→ Có thể update BOM khi thay đổi components
```

### 3. Subscription Product Setup

**Đường dẫn**: `Inventory > Products > Products > Subscription Type`

**Cấu hình cho từng subscription product:**

```
Product: DiHub License - 10 devices

DTX Standards Tab:
- Product Type DTX: subscription
- Base Price (per device/month): 500,000 VND
- Default Duration (months): 12

Sales Tab:
- Sales Price: 60,000,000 VND (500k x 10 devices x 12 months)
- UoM: Month(s)
```

**Sale Order Line fields (khi bán):**

```
- Number of Devices: 10
- Number of Months: 12
- Quantity (auto): 120 (= 10 x 12)
- Start Date: 2026-01-15
- End Date: 2027-01-14
- Deployment Date: 2026-01-20 (optional)
```

---

## PHẦN XI: DATA MIGRATION & VALIDATION

### 1. Kiểm Tra Dữ Liệu Cũ

**Nếu bạn có dữ liệu cũ trên Odoo 16**, cần kiểm tra:

✅ **Products:**
```sql
SELECT id, name, tracking, type, categ_id
FROM product_template
WHERE type = 'product' AND tracking != 'serial'
-- Danh sách devices chưa set tracking = serial
```

✅ **Serial Numbers:**
```sql
SELECT COUNT(*) FROM stock_lot
-- Kiểm tra có bao nhiêu serial đã tạo
```

✅ **Unreconciled Invoices:**
```sql
SELECT name, partner_id, amount_residual
FROM account_move
WHERE move_type = 'out_invoice'
  AND state = 'posted'
  AND amount_residual > 0
-- Danh sách hóa đơn chưa thanh toán
```

### 2. Recompute Computed Fields (Nếu cần)

**Sau khi install modules, chạy recompute:**

```python
# Script: /scripts/recompute_all_dtx_fields.py

import odoo

env = odoo.api.Environment(...)

# Recompute product DTX fields
products = env['product.template'].search([])
products._compute_dtx_product_type()
products._compute_requires_serial()

# Recompute serial lifecycle state
serials = env['stock.lot'].search([])
serials._compute_lifecycle_state()
serials._compute_vendor_invoice_state()

# Recompute sale order financials
orders = env['sale.order'].search([('state', '!=', 'cancel')])
orders._compute_contract_financials()

env.cr.commit()
```

**Hoặc dùng Odoo UI:**

```
Settings > Technical > Scheduled Actions
> Create manual action to trigger compute
```

### 3. Validation Checklist

**Sau khi cấu hình xong, kiểm tra:**

- [ ] Tất cả Serial Devices có `tracking = serial`
- [ ] Tất cả Kiosk có `tracking = serial`
- [ ] Tất cả Products có Category phù hợp
- [ ] Tất cả Storable Products có Costing Method
- [ ] VAT taxes đầy đủ (0%, 5%, 8%, 10%)
- [ ] Payment Terms đã tạo
- [ ] Vendors có đầy đủ thông tin (Tax ID, Address)
- [ ] Customers có phân loại rõ ràng
- [ ] Locations cấu trúc hợp lý
- [ ] Users có đúng permissions
- [ ] BOM Templates tạo cho các Kiosk
- [ ] Subscription products có đầy đủ thông tin

---

## PHẦN XII: TROUBLESHOOTING

### 1. Lỗi Thường Gặp

#### A. "Serial number already exists"

**Nguyên nhân**: Serial đã được tạo trong hệ thống

**Giải pháp**:
```
1. Check existing serial: Inventory > Serial Numbers > Search
2. Nếu là serial cũ → Reuse
3. Nếu bị trùng → Đổi serial number mới
```

#### B. "Cannot change tracking on product with stock"

**Nguyên nhân**: Đã có stock moves với product này

**Giải pháp**:
```
1. Xuất hết tồn kho (Inventory Adjustment → Qty = 0)
2. Đổi tracking
3. Nhập lại với serial mới
```

#### C. "No tax found for VAT X%"

**Nguyên nhân**: PAKD module không tìm thấy tax rate

**Giải pháp**:
```
Accounting > Configuration > Taxes
> Tạo tax với đúng % rate
> Đảm bảo Tax Type = Sales
```

#### D. "Computed field not updating"

**Nguyên nhân**: Stored computed field chưa recompute

**Giải pháp**:
```python
# Force recompute
record.invalidate_cache(['field_name'])
record._compute_field_name()
env.cr.commit()
```

### 2. Performance Issues

**Nếu hệ thống chậm với nhiều dữ liệu:**

✅ **Index important fields**:
```sql
CREATE INDEX idx_stock_lot_name ON stock_lot(name);
CREATE INDEX idx_sale_order_contract_no ON sale_order(x_contract_no);
```

✅ **Archive old records**:
```
Archive các Sale Orders > 2 năm
Archive các Products không dùng
```

✅ **Vacuum database**:
```bash
docker exec dtx_postgres vacuumdb -U odoo -d dtxco_2024 --analyze
```

---

## PHẦN XIII: BEST PRACTICES

### 1. Naming Conventions

**Products:**
```
Format: [Category] [Brand] [Model] [Spec]
Examples:
- Màn hình ASUS VT190 19" Cảm ứng
- Mini PC Intel NUC i5-10210U 8GB
- Kiosk DTX Standard KS-001
- DiHub License - 10 devices - 12 months
```

**Serial Numbers:**
```
Format: [Product Code]-[Sequential Number]
Examples:
- ASUS-VT190-001
- ASUS-VT190-002
- KIOSK-001
- MINIPC-001
```

**Vendors:**
```
Format: [Tên công ty chính thức]
Examples:
- Công ty TNHH ABC Technology
- Công ty CP XYZ Distribution
```

### 2. Data Entry Workflow

**Quy trình nhập liệu chuẩn:**

```
1. Vendors → 2. Products → 3. BOM → 4. Purchase → 5. Receive → 6. Sales → 7. Delivery
```

**Chi tiết từng bước:**

1. **Tạo Vendors** → Đầy đủ thông tin thuế, địa chỉ
2. **Tạo Products** → Set category, tracking, costing
3. **Tạo BOM** (nếu Kiosk) → BOM Template hoặc real BOM
4. **Purchase Order** → Mua hàng từ vendors
5. **Receive** → Nhập kho, gán serial numbers
6. **Sales Order** → Tạo quotation, PAKD, apply
7. **Delivery** → Xuất kho, serial chuyển sang "delivered"

### 3. Regular Maintenance

**Hàng tháng:**
- [ ] Review AR Aging report
- [ ] Check expired subscriptions
- [ ] Archive old quotations
- [ ] Backup database

**Hàng quý:**
- [ ] Review product categories
- [ ] Clean up unused products
- [ ] Update vendor information
- [ ] Review user permissions

**Hàng năm:**
- [ ] Archive old sale orders (>2 years)
- [ ] Review and update BOM templates
- [ ] Audit inventory valuation
- [ ] Review tax configuration

---

## PHẦN XIV: QUICK REFERENCE

### 1. Module Dependencies

```
dtx_product_standards (v1.3.0)
  ↓ requires
  product, stock, purchase, sale, mrp

dtx_serial_ext (v2.5.0)
  ↓ requires
  stock, product, purchase, sale, account

dtx_sales_pakd_contract (v1.8.1)
  ↓ requires
  sale, sale_management, sale_stock, stock, purchase, purchase_stock, account, product
  ↓ requires
  dtx_product_standards (for subscription)
```

### 2. Key Reports

| Report | Location | Purpose |
|--------|----------|---------|
| Contract List | Sales > Contracts > Contract List | Profit/Loss analysis |
| AR Aging | Sales > Contracts > AR Aging | Receivables aging |
| Subscription Dashboard | Sales > Subscriptions > Dashboard | Active/expiring subscriptions |
| Device Serials | Inventory > Serial Numbers | Serial lifecycle tracking |

### 3. Import/Export Templates

**Sẽ bổ sung sau:**
- Product import template (CSV/Excel)
- Vendor import template
- Customer import template
- Initial inventory template

---

## KẾT LUẬN

Tài liệu này cung cấp hướng dẫn đầy đủ để chuẩn hóa Master Data khi triển khai DTX modules trên production environment.

**Thứ tự ưu tiên:**
1. ✅ Phần I-II: Settings & Categories (Bắt buộc)
2. ✅ Phần III-V: UoM, Contacts, Products (Bắt buộc)
3. ✅ Phần VI-IX: Locations, Taxes, Users, Payment Terms (Bắt buộc)
4. ✅ Phần X: DTX-specific (Khuyến nghị)
5. ✅ Phần XI-XIV: Migration, Troubleshooting, Best Practices (Tham khảo)

**Liên hệ hỗ trợ:**
- Technical documentation: `/PRODUCTION_DOCS/`
- Module-specific docs: Each module's `__manifest__.py`

---

**Phiên bản**: 1.0
**Ngày tạo**: 2026-01-15
**Tác giả**: DTX Implementation Team
**Module versions**: dtx_product_standards v1.3.0, dtx_serial_ext v2.5.0, dtx_sales_pakd_contract v1.8.1
