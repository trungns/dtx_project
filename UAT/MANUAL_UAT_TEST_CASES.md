# MANUAL UAT TEST CASES - DTX SALES PAKD CONTRACT

**Module**: dtx_sales_pakd_contract
**Version**: 1.3.0
**Odoo Version**: 16.0
**Author**: DTX
**Last Updated**: 2026-01-05

---

## MỤC LỤC

1. [Tổng quan quy trình](#1-tổng-quan-quy-trình)
2. [Chuẩn bị Master Data](#2-chuẩn-bị-master-data)
3. [PAKD & Quotation](#3-pakd--quotation)
4. [Mua hàng & Resupply](#4-mua-hàng--resupply)
5. [Triển khai & Nghiệm thu](#5-triển-khai--nghiệm-thu)
6. [Hóa đơn & Thanh toán](#6-hóa-đơn--thanh-toán)
7. [Bảo trì & Support](#7-bảo-trì--support)
8. [Báo cáo & Phân tích](#8-báo-cáo--phân-tích)

---

## 1. TỔNG QUAN QUY TRÌNH

### 1.1. Sơ đồ quy trình End-to-End

```
[Quotation] → [PAKD] → [Confirm SO] → [Mua linh kiện] → [Resupply cho đối tác]
    → [Nhận thành phẩm] → [Triển khai] → [Nghiệm thu] → [Xuất Invoice]
    → [Thu tiền] → [Bảo trì]
```

### 1.2. Các giai đoạn chính

| Giai đoạn | Mô tả | Module Odoo |
|-----------|-------|-------------|
| 1. Pre-Sales | Lập báo giá, PAKD, tính giá | Sales, PAKD |
| 2. Sales | Confirm SO, ký hợp đồng | Sales |
| 3. Procurement | Mua linh kiện, resupply đối tác | Purchase, Inventory |
| 4. Production | Đối tác lắp ráp, nhận thành phẩm | Inventory (Subcontracting) |
| 5. Deployment | Triển khai tại site, nghiệm thu | Project (optional) |
| 6. Invoicing | Xuất hóa đơn sau nghiệm thu | Accounting |
| 7. Collection | Thu tiền, quản lý công nợ | Accounting, AR |
| 8. Maintenance | Bảo trì, hỗ trợ sau bán | Helpdesk (optional) |

---

## 2. CHUẨN BỊ MASTER DATA

### 2.1. Tạo Customer (Khách hàng)

**Menu**: Contacts → Create

**Test Data - Customer 1**:
- **Name**: CÔNG TY CP VNPAY
- **Type**: Company
- **Customer**: ✓
- **Email**: contact@vnpay.vn
- **Phone**: 024-1234-5678
- **Address**:
  - Street: 285 Đội Cấn, Ba Đình
  - City: Hà Nội
  - Country: Vietnam
- **Payment Terms**: 30 Days
- **Tags**: VIP Customer

**Test Data - End Customer** (nếu bán qua đại lý):
- **Name**: NGÂN HÀNG TMCP QUỐC TẾ VIB
- **Type**: Company
- **Email**: info@vib.com.vn
- **Phone**: 024-9999-8888

**Expected Result**:
- ✅ Customer được tạo thành công
- ✅ Có thể search trong Sales Order

---

### 2.2. Tạo Vendor (Nhà cung cấp)

**Menu**: Contacts → Create

**Test Data - Vendor 1: NCC Linh kiện**:
- **Name**: ABC Technology Distributor
- **Type**: Company
- **Vendor**: ✓
- **Email**: sales@abc-tech.com
- **Phone**: 028-7777-6666
- **Payment Terms**: 15 Days
- **Tags**: Component Supplier

**Test Data - Vendor 2: Đối tác sản xuất/Gia công**:
- **Name**: XYZ Manufacturing Vietnam
- **Type**: Company
- **Vendor**: ✓
- **Email**: production@xyz-mfg.vn
- **Phone**: 028-5555-4444
- **Tags**: Subcontractor
- **Notes**: "Đối tác lắp ráp Kiosk"

**Expected Result**:
- ✅ Vendor xuất hiện trong Purchase Order
- ✅ Có thể phân biệt NCC linh kiện vs đối tác gia công

---

### 2.3. Tạo Products (Sản phẩm)

#### 2.3.1. Linh kiện (Components)

**Menu**: Inventory → Products → Products → Create

**Product 1: Raspberry Pi**
- **Name**: Raspberry Pi 4 Model B - 8GB RAM
- **Product Type**: Storable Product
- **Sales Price**: 2,500,000 VND
- **Cost**: 1,800,000 VND
- **Unit of Measure**: Unit
- **Can be Sold**: ✓
- **Can be Purchased**: ✓
- **Customer Taxes**: VAT 10%
- **Vendor Taxes**: VAT 10%
- **Internal Reference**: RPI-4B-8G

**Product 2: Màn hình cảm ứng**
- **Name**: Industrial Touchscreen 15.6" - 1920x1080
- **Sales Price**: 4,500,000 VND
- **Cost**: 3,200,000 VND
- **Internal Reference**: SCREEN-156-FHD

**Product 3: Camera**
- **Name**: Camera Module 5MP - Auto Focus
- **Sales Price**: 800,000 VND
- **Cost**: 550,000 VND
- **Internal Reference**: CAM-5MP-AF

**Product 4: Vỏ Kiosk**
- **Name**: Kiosk Enclosure - Stainless Steel - Black
- **Sales Price**: 3,000,000 VND
- **Cost**: 2,100,000 VND
- **Internal Reference**: ENCL-SS-BLK

**Product 5: Card mạng/Phụ kiện**
- **Name**: Network & Accessories Kit
- **Sales Price**: 500,000 VND
- **Cost**: 350,000 VND
- **Internal Reference**: NET-ACC-KIT

#### 2.3.2. Thành phẩm (Finished Product)

**Product: Kiosk hoàn chỉnh**
- **Name**: Self-service Kiosk - Complete System
- **Product Type**: Storable Product
- **Sales Price**: 25,000,000 VND (giá list ban đầu)
- **Cost**: 0 (sẽ tính từ linh kiện + gia công)
- **Unit of Measure**: Unit
- **Can be Sold**: ✓
- **Can be Purchased**: ✗
- **Customer Taxes**: VAT 10%
- **Internal Reference**: KIOSK-COMPLETE-001
- **Description for Quotations**:
  ```
  Self-service Kiosk System bao gồm:
  - Raspberry Pi 4B 8GB
  - Màn hình cảm ứng 15.6" Full HD
  - Camera 5MP tự động lấy nét
  - Vỏ thép không gỉ màu đen
  - Bộ phụ kiện mạng & cáp
  - Bảo hành 12 tháng
  - Hỗ trợ cài đặt tại site
  ```

#### 2.3.3. Dịch vụ (Services)

**Service 1: Gia công lắp ráp**
- **Name**: Kiosk Assembly Service
- **Product Type**: Service
- **Sales Price**: 0
- **Cost**: 1,500,000 VND/unit
- **Can be Purchased**: ✓
- **Internal Reference**: SVC-ASSEMBLY

**Service 2: Triển khai**
- **Name**: On-site Installation & Configuration
- **Product Type**: Service
- **Sales Price**: 3,000,000 VND
- **Cost**: 0 (internal cost, tính trong nhân công)
- **Can be Sold**: ✓
- **Internal Reference**: SVC-INSTALL

**Service 3: Bảo trì**
- **Name**: 12-Month Maintenance Contract
- **Product Type**: Service
- **Sales Price**: 5,000,000 VND
- **Cost**: 0
- **Can be Sold**: ✓
- **Internal Reference**: SVC-MAINT-12M

**Expected Result**:
- ✅ Tất cả products có thể search được
- ✅ Cost & Price được set đúng
- ✅ VAT được áp dụng đúng

---

### 2.4. Cấu hình VAT (Taxes)

**Menu**: Accounting → Configuration → Taxes → Create

**Tax: VAT 10%**
- **Name**: VAT 10%
- **Tax Type**: Sales / Purchase
- **Tax Computation**: Percentage of Price
- **Amount**: 10%
- **Tax Scope**: Services and goods

**Tax: VAT 8%** (nếu cần)
- **Name**: VAT 8%
- **Amount**: 8%

**Tax: VAT 0%** (xuất khẩu)
- **Name**: VAT 0% (Export)
- **Amount**: 0%

**Expected Result**:
- ✅ Taxes xuất hiện trong dropdown khi tạo PAKD/SO
- ✅ PAKD tự động map VAT% → account.tax

---

### 2.5. Cấu hình Inventory Locations (Locations)

**Menu**: Inventory → Configuration → Locations

**Location 1: Kho DTX**
- **Name**: WH/Stock
- **Type**: Internal Location
- *(Đã có sẵn)*

**Location 2: Đối tác gia công**
- **Name**: Subcontractor - XYZ Manufacturing
- **Parent Location**: Partner Locations
- **Type**: External Location
- **Partner**: XYZ Manufacturing Vietnam

**Expected Result**:
- ✅ Có thể track hàng tại đối tác
- ✅ Resupply transfer có destination đúng

---

## 3. PAKD & QUOTATION

### 3.1. Tạo Quotation mới

**Menu**: Sales → Orders → Quotations → Create

**Test Case 01: Tạo Quotation cho dự án VNPAY Kiosk**

**Input Data**:
- **Customer**: CÔNG TY CP VNPAY
- **Expiration**: +30 days
- **Payment Terms**: 30 Days
- **Salesperson**: (user hiện tại)
- **Tags**: Kiosk Project

**Custom Fields** (nếu có):
- **End Customer** (x_end_customer_id): NGÂN HÀNG TMCP QUỐC TẾ VIB
- **Agent** (x_agent_id): (để trống nếu không có đại lý)

**Order Lines** (thêm sơ bộ):
- Product: Self-service Kiosk - Complete System
- Quantity: 10
- Unit Price: 25,000,000
- Tax: VAT 10%

**Actions**:
1. Click **Save**
2. Kiểm tra SO number (ví dụ: S00001, hoặc QT00001)
3. Click **Send by Email** (optional) → Preview quotation PDF
4. **Chưa confirm**, giữ ở trạng thái Quotation

**Expected Result**:
- ✅ Quotation được tạo thành công (state = draft/sent)
- ✅ Tổng tiền: 10 × 25,000,000 = 250,000,000 VND
- ✅ Tổng có VAT: 275,000,000 VND
- ✅ Smart button "PAKD" = 0 (chưa có PAKD nào)

---

### 3.2. Tạo PAKD từ Quotation

**Menu**: Mở quotation S00001 → Click button **Create PAKD**

**Test Case 02: Tạo PAKD Option 1 - Giá thấp**

**Actions**:
1. Click **Create PAKD** button trên SO
2. Hệ thống tạo PAKD mới và copy lines từ SO
3. PAKD auto-fill:
   - Sale Order: S00001
   - Customer: VNPAY
   - End Customer: VIB
   - Owner: User hiện tại
   - State: Draft

**Chỉnh sửa PAKD Lines**:

Vào tab **Chi tiết sản phẩm**, xóa dòng cũ và thêm mới theo cấu trúc:

**Section 1: Phần mềm/License**
- *(Add Section)* → Display Type = Section, Name = "A. PHẦN MỀM / LICENSE"

| Sản phẩm | Qty | ĐV | Dự toán | Giá List | Discount% | Giá nhập | Giá bán | Giá HĐ | VAT% |
|----------|-----|----|---------| ---------|-----------|----------|---------|--------|------|
| (Để trống - không có item software trong case này) | | | | | | | | | |

**Section 2: Phần cứng/Hardware**
- *(Add Section)* → Display Type = Section, Name = "B. PHẦN CỨNG / HARDWARE"

| Sản phẩm | Qty | ĐV | Dự toán (excl VAT) | Giá List NCC | Discount% | Giá nhập | Giá bán | Giá HĐ | VAT% |
|----------|-----|----|--------------------|--------------|-----------|----------|---------|--------|------|
| Raspberry Pi 4B 8GB | 10 | Unit | 2,500,000 | 2,200,000 | 15% | 1,870,000 | 2,500,000 | 2,400,000 | 10 |
| Industrial Touchscreen 15.6" | 10 | Unit | 4,500,000 | 4,000,000 | 20% | 3,200,000 | 4,500,000 | 4,300,000 | 10 |
| Camera 5MP | 10 | Unit | 800,000 | 700,000 | 15% | 595,000 | 800,000 | 750,000 | 10 |
| Kiosk Enclosure SS Black | 10 | Unit | 3,000,000 | 2,800,000 | 20% | 2,240,000 | 3,000,000 | 2,900,000 | 10 |
| Network & Accessories Kit | 10 | Unit | 500,000 | 450,000 | 10% | 405,000 | 500,000 | 480,000 | 10 |

**Section 3: Triển khai/Deployment**
- *(Add Section)* → Display Type = Section, Name = "C. TRIỂN KHAI / DEPLOYMENT"

| Sản phẩm | Qty | ĐV | Dự toán | Giá List | Discount% | Giá nhập | Giá bán | Giá HĐ | VAT% |
|----------|-----|----|---------| ---------|-----------|----------|---------|--------|------|
| On-site Installation & Config | 10 | Unit | 3,000,000 | 0 | 0 | 0 | 3,000,000 | 2,800,000 | 10 |
| 12-Month Maintenance | 10 | Unit | 5,000,000 | 0 | 0 | 0 | 5,000,000 | 4,500,000 | 10 |

**Lưu ý khi nhập**:
- **Giá nhập** (purchase_unit_price): Tự động tính từ Giá List × (1 - Discount%), hoặc nhập thủ công
- **Giá bán** (sale_unit_price): Giá muốn bán cho KH (chưa có chiết khấu)
- **Giá HĐ** (contract_unit_price): Giá cuối cùng trong hợp đồng (đã có chiết khấu). Nếu = 0, hệ thống dùng Giá bán

**Vào tab "Tổng kết"**, điền các field:

**Chi phí cho khách hàng/người giới thiệu**:
- **% Thu thuế** (tax_withheld_percent): 0% (không có)
- **% Hoa hồng** (referral_commission_percent): 5%

**Kiểm tra các tổng tự động**:
- **1. Tổng tiền nhập** (total_purchase): ≈ 81,100,000 VND (linh kiện) + 0 (dịch vụ)
- **2. Tổng tiền bán** (total_sale): ≈ 138,000,000 VND
- **3a. Tổng HĐ chưa VAT** (total_contract_untaxed): ≈ 132,300,000 VND
- **3b. Tổng VAT**: ≈ 13,230,000 VND
- **3. Tổng HĐ có VAT**: ≈ 145,530,000 VND
- **4. Chênh lệch giá** (price_diff): 3a - 2 ≈ -5,700,000 VND
- **7. Hoa hồng** (referral_commission): 2 × 5% = 6,900,000 VND
- **9. Lợi nhuận** (expected_profit): 2 - 1 - 7 ≈ 50,000,000 VND
- **Tỷ lệ lãi %** (expected_margin_percent): 9 / 3a × 100 ≈ 37.8%

**Actions**:
1. Click **Save**
2. Click **Trình duyệt** (Submit)
3. State chuyển sang **Submitted**

**Expected Result**:
- ✅ PAKD được tạo với name như "PAKD/2026/001"
- ✅ Các công thức tính đúng như Excel template
- ✅ State = Submitted

---

### 3.3. Phê duyệt PAKD

**Role**: Sales Director hoặc CEO

**Test Case 03: Approve PAKD**

**Actions**:
1. Login bằng user có quyền Approve (Sales Director/CEO)
2. Vào menu: Sales → PAKD → Filter "Đã trình"
3. Mở PAKD/2026/001
4. Review tab "Chi tiết sản phẩm" và "Tổng kết"
5. Click **Phê duyệt** (Approve)
6. State → **Approved**

**Test Case 04: Reject PAKD** (Optional)
- Click **Từ chối** (Reject) → State = Rejected
- Lý do: "Giá bán thấp quá, không đạt margin 40%"
- Sales phải điều chỉnh và submit lại

**Expected Result**:
- ✅ PAKD state = Approved
- ✅ Button "Apply vào Báo giá" sáng lên

---

### 3.4. Apply PAKD vào Quotation

**Test Case 05: Apply PAKD approved vào SO**

**Actions**:
1. Mở PAKD/2026/001 (đã approved)
2. Click button **Apply vào Báo giá**
3. Popup wizard hiện ra:
   - **Quotation**: S00001 (auto-fill)
   - **Thay thế toàn bộ dòng hiện tại**: ✓ (checked)
   - **Nguồn giá**: Ưu tiên đơn giá HĐ (contract_unit_price)
   - **Warning**: "Sẽ xóa 1 dòng hiện tại trong đơn hàng"
4. Click **Apply**

**Expected Result**:
- ✅ Wizard đóng lại, quay về SO S00001
- ✅ SO Lines được cập nhật từ PAKD:
  - 10 dòng sản phẩm/dịch vụ (không có section/note)
  - Unit Price = contract_unit_price (hoặc sale_unit_price nếu contract = 0)
  - Tax = 10%
- ✅ SO Total (Untaxed) ≈ 132,300,000 VND
- ✅ SO Total (Tax incl) ≈ 145,530,000 VND
- ✅ Message log trên SO: "✅ Đã apply PAKD PAKD/2026/001"
- ✅ Message log trên PAKD: "✅ Đã apply vào S00001"

---

### 3.5. Confirm Quotation

**Test Case 06: Confirm Sales Order**

**Precondition**:
- PAKD đã apply vào quotation
- Customer đồng ý giá

**Actions**:
1. Mở quotation S00001
2. Kiểm tra lại Order Lines, Total
3. Click **Confirm**
4. State chuyển sang **Sales Order**
5. SO name có thể thay đổi (ví dụ: S00001 → SO001)

**Điền thêm thông tin hợp đồng** (Custom fields):
- **Số hợp đồng** (x_contract_no): HĐ/2026/VNPAY/001
- **Ngày ký HĐ** (x_signed_date): 2026-01-05
- **Ngày hết hạn HĐ** (x_contract_end_date): 2027-01-05
- Upload **File scan hợp đồng** (x_contract_scan_attachment_ids): PDF hợp đồng đã ký

**Expected Result**:
- ✅ SO state = Sale
- ✅ Smart buttons xuất hiện:
  - **Delivery**: 1 (WH/OUT/00001 auto-created, waiting)
  - **PAKD**: 1
  - **Costs**: 0 (chưa import)
  - **Invoices**: 0 (chưa tạo invoice)
- ✅ Delivery Status: Waiting (chưa giao hàng)
- ✅ Invoice Status: To Invoice (chưa invoice)

---

### 3.6. Import Chi phí từ PAKD vào Contract Cost

**Test Case 07: Import Planned Costs**

**Actions**:
1. Mở SO001
2. Click button **Import PAKD Costs**
3. Popup confirm: "Sẽ import chi phí từ PAKD/2026/001. Tiếp tục?"
4. Click **OK**
5. Hệ thống tạo contract costs từ PAKD lines

**Expected Result**:
- ✅ Smart Button **Costs** = 10 (hoặc 5 nếu chỉ tính linh kiện, không tính service)
- ✅ Click vào **Costs**, kiểm tra list:
  - Raspberry Pi: Planned = Actual = 1,870,000
  - Touchscreen: Planned = Actual = 3,200,000
  - Camera: Planned = Actual = 595,000
  - Enclosure: Planned = Actual = 2,240,000
  - Network Kit: Planned = Actual = 405,000
  - Cost Type = "planned"
- ✅ Total Planned Cost ≈ 81,100,000 VND
- ✅ Message log: "✅ Đã import 5 dòng chi phí từ PAKD PAKD/2026/001"

---

## 4. MUA HÀNG & RESUPPLY

### 4.1. Tạo Purchase Order mua linh kiện

**Test Case 08: Tạo PO mua linh kiện từ NCC**

**Menu**: Purchase → Orders → Create

**Input Data**:
- **Vendor**: ABC Technology Distributor
- **Order Deadline**: +15 days
- **Payment Terms**: 15 Days
- **Notes**: "Linh kiện cho dự án VNPAY Kiosk - SO001"

**Order Lines** (nhập theo PAKD):

| Product | Qty | Unit Price | Taxes |
|---------|-----|------------|-------|
| Raspberry Pi 4B 8GB | 10 | 1,870,000 | VAT 10% |
| Industrial Touchscreen 15.6" | 10 | 3,200,000 | VAT 10% |
| Camera 5MP | 10 | 595,000 | VAT 10% |
| Kiosk Enclosure SS Black | 10 | 2,240,000 | VAT 10% |
| Network & Accessories Kit | 10 | 405,000 | VAT 10% |

**Actions**:
1. Click **Save**
2. PO Number: PO00001
3. Kiểm tra Total: ≈ 81,100,000 + VAT = 89,210,000 VND
4. Click **Confirm Order**
5. State → **Purchase Order**

**Expected Result**:
- ✅ PO state = Purchase Order
- ✅ Smart Button **Receipt**: 1 (WH/IN/00001 waiting)
- ✅ Billed Status: Nothing to Bill (chưa nhận hàng)

---

### 4.2. Nhận linh kiện vào kho

**Test Case 09: Receipt linh kiện từ NCC**

**Actions**:
1. Mở PO00001
2. Click Smart Button **Receipt** → Mở WH/IN/00001
3. Kiểm tra **Operations** tab:
   - From: Vendors
   - To: WH/Stock
   - Products: 5 loại linh kiện, mỗi loại qty = 10
4. Click **Check Availability** (nếu cần)
5. **Detailed Operations** tab:
   - Từng dòng: Demand = 10, Reserved = 0 → Done = 10
6. Click **Validate**
7. Popup "All quantities processed?" → Click **Apply**

**Expected Result**:
- ✅ Receipt state = Done
- ✅ PO Receipt Status = Fully Received
- ✅ Kiểm tra tồn kho (Inventory → Products):
  - Raspberry Pi: On Hand = 10
  - Touchscreen: On Hand = 10
  - Camera: On Hand = 10
  - Enclosure: On Hand = 10
  - Network Kit: On Hand = 10

**Test Case 10: Partial Receipt** (Optional)
- Validate WH/IN/00001 với Done = 5 (thay vì 10)
- → Tạo backorder WH/IN/00002 cho 5 cái còn lại
- PO Receipt Status = Partially Received

---

### 4.3. Resupply linh kiện cho đối tác sản xuất

**Context**:
- DTX đã nhận đủ linh kiện vào kho
- Bây giờ cần chuyển linh kiện cho XYZ Manufacturing để lắp ráp

**Option A: Sử dụng Subcontracting Module** (khuyến nghị nếu có Odoo Manufacturing)

#### A1. Cấu hình Bill of Materials (BoM)

**Menu**: Manufacturing → Configuration → Bills of Materials → Create

**BoM Data**:
- **Product**: Self-service Kiosk - Complete System
- **BoM Type**: Subcontracting
- **Subcontractor**: XYZ Manufacturing Vietnam
- **Quantity**: 1 unit
- **Components**:
  - Raspberry Pi 4B 8GB: 1
  - Industrial Touchscreen 15.6": 1
  - Camera 5MP: 1
  - Kiosk Enclosure SS Black: 1
  - Network & Accessories Kit: 1

**Actions**: Save

#### A2. Tạo Purchase Order cho Subcontractor

**Menu**: Purchase → Orders → Create

**Input**:
- **Vendor**: XYZ Manufacturing Vietnam
- **Order Lines**:
  - Product: Self-service Kiosk - Complete System
  - Qty: 10
  - Unit Price: 1,500,000 (chi phí gia công)
  - Taxes: VAT 10%
- Odoo tự động phát hiện BoM type = Subcontracting
- Tạo **Resupply picking** tự động

**Actions**:
1. Confirm PO → PO00002
2. Smart Button **Resupply**: 1

#### A3. Chuyển linh kiện cho Subcontractor

**Actions**:
1. Click Smart Button **Resupply** trên PO00002
2. Mở Resupply picking (RESUPPLY/00001)
3. Kiểm tra:
   - From: WH/Stock
   - To: Subcontractor - XYZ Manufacturing
   - Products: 5 loại × 10 = 50 items
4. Click **Check Availability**
5. Click **Validate**

**Expected Result**:
- ✅ Resupply Done
- ✅ Tồn kho tại WH/Stock giảm xuống 0
- ✅ Tồn kho tại Subcontractor = 10 (từng loại)

---

**Option B: Không dùng Subcontracting** (đơn giản hơn)

#### B1. Tạo Internal Transfer chuyển linh kiện

**Menu**: Inventory → Operations → Transfers → Create

**Input**:
- **Operation Type**: Internal Transfers
- **Contact**: XYZ Manufacturing Vietnam
- **Source Location**: WH/Stock
- **Destination Location**: Partner Locations/Subcontractor - XYZ Manufacturing
- **Scheduled Date**: Hôm nay
- **Source Document**: "Resupply for SO001 - VNPAY Kiosk"
- **Products**:
  - Raspberry Pi: 10
  - Touchscreen: 10
  - Camera: 10
  - Enclosure: 10
  - Network Kit: 10

**Actions**:
1. Click **Save** → INT/00001
2. Click **Check Availability**
3. Click **Validate**

**Expected Result**:
- ✅ Transfer Done
- ✅ On Hand tại WH/Stock = 0
- ✅ Có thể track location tại đối tác (nếu cấu hình)

#### B2. Tạo PO cho dịch vụ gia công

**Menu**: Purchase → Orders → Create

**Input**:
- **Vendor**: XYZ Manufacturing Vietnam
- **Order Lines**:
  - Product: Kiosk Assembly Service (service type)
  - Qty: 10
  - Unit Price: 1,500,000 VND
  - Taxes: VAT 10%

**Actions**: Confirm → PO00002

**Expected Result**:
- ✅ PO for service created
- ✅ Total: 15,000,000 + VAT = 16,500,000 VND

---

### 4.4. Nhận thành phẩm từ đối tác

**Test Case 11: Receipt thành phẩm Kiosk**

**Option A: Với Subcontracting**
- Mở PO00002 (Subcontracting PO)
- Click **Receive Products**
- Validate Receipt
- Thành phẩm "Self-service Kiosk" tự động vào kho WH/Stock

**Option B: Không dùng Subcontracting**

**Menu**: Inventory → Operations → Receipts → Create

**Input**:
- **Operation Type**: Receipts
- **Contact**: XYZ Manufacturing Vietnam
- **Source Document**: "Thành phẩm từ XYZ - SO001"
- **Product**:
  - Self-service Kiosk - Complete System: 10 units
- **Source Location**: Partner Locations/XYZ Manufacturing
- **Destination**: WH/Stock

**Actions**:
1. Click **Validate**
2. Receipt Done → WH/IN/00002

**Expected Result**:
- ✅ Receipt Done
- ✅ On Hand: Self-service Kiosk = 10 units
- ✅ Linh kiện đã hết (đã chuyển cho đối tác)

---

### 4.5. Cập nhật chi phí thực tế vào Contract Cost

**Test Case 12: Update Actual Cost from PO**

**Scenario**:
- Giá nhập thực tế khác với PAKD dự kiến
- Ví dụ: Raspberry Pi thực tế mua 1,900,000 (dự kiến 1,870,000)

**Actions**:
1. Mở SO001
2. Click Smart Button **Costs**
3. Tìm dòng "Raspberry Pi"
4. Edit:
   - Actual Unit Cost: 1,900,000 (từ 1,870,000)
   - Save
5. Kiểm tra:
   - Cost Variance = (1,900,000 - 1,870,000) × 10 = 300,000 VND
   - Variance % ≈ 1.6%

**Thêm chi phí gia công**:
1. Vẫn trong Costs list, click **Create**
2. Input:
   - Product: Kiosk Assembly Service
   - Name: "Chi phí gia công lắp ráp 10 cây Kiosk"
   - Qty: 10
   - UoM: Unit
   - Planned Unit Cost: 1,500,000
   - Actual Unit Cost: 1,500,000
   - Cost Type: additional
3. Save

**Expected Result**:
- ✅ Total Cost = Linh kiện (81,400,000) + Gia công (15,000,000) = 96,400,000 VND
- ✅ Profit = Revenue - Cost (tính sau khi có invoice)

---

## 5. TRIỂN KHAI & NGHIỆM THU

### 5.1. Xuất kho giao hàng cho deployment

**Test Case 13: Delivery cho dự án triển khai**

**Context**:
- Thành phẩm Kiosk đã có trong kho
- Bây giờ giao cho team triển khai hoặc ship đến site khách hàng

**Actions**:
1. Mở SO001
2. Click Smart Button **Delivery** → Mở WH/OUT/00001
3. Kiểm tra:
   - State: Waiting Availability (chờ hàng có sẵn)
   - Product: Self-service Kiosk - Complete System × 10
   - From: WH/Stock
   - To: Customers (hoặc location cụ thể nếu set)
4. Click **Check Availability**
5. Reserved = 10 (đủ hàng)
6. Click **Validate**

**Partial Delivery** (nếu giao từng đợt):
- Đợt 1: Done = 5 → Create Backorder
- Đợt 2: Done = 5 (WH/OUT/00002)

**Expected Result**:
- ✅ Delivery Done
- ✅ SO Delivery Status = Fully Delivered
- ✅ On Hand Kiosk = 0 (đã giao hết)

---

### 5.2. Triển khai tại site khách hàng

**Test Case 14: Lắp đặt & cấu hình tại site**

**Option 1: Không dùng Project module**

**Tracking thủ công**:
1. Tạo Internal Note trên SO001:
   - "2026-01-10: Team kỹ thuật đã triển khai 5 cây tại VNPAY HN Office"
   - "2026-01-12: Triển khai 5 cây còn lại tại VNPAY HCM Office"
2. Update field custom (nếu có):
   - x_deployment_status: In Progress / Completed
   - x_deployment_date: 2026-01-12

**Option 2: Dùng Project module** (khuyến nghị)

**Menu**: Project → Create Project

**Project Data**:
- **Name**: Triển khai Kiosk - VNPAY
- **Customer**: CÔNG TY CP VNPAY
- **Sale Order**: SO001

**Tasks**:
1. **Task 1**: Giao hàng & setup phần cứng
   - Assigned to: Kỹ thuật viên A
   - Deadline: 2026-01-10
   - Status: Done
2. **Task 2**: Cài đặt phần mềm & kết nối
   - Assigned to: Dev Team
   - Status: Done
3. **Task 3**: Training cho user
   - Assigned to: Support Team
   - Status: Done
4. **Task 4**: Nghiệm thu chính thức
   - Assigned to: Project Manager
   - Status: In Progress

**Expected Result**:
- ✅ Project tracking đầy đủ
- ✅ Link Project ↔ SO

---

### 5.3. Nghiệm thu (Acceptance)

**Test Case 15: Khách hàng nghiệm thu & ký biên bản**

**Quy trình nghiệm thu**:
1. **Tạo Biên bản nghiệm thu** (tài liệu ngoài Odoo):
   - Template Word/PDF
   - Checklist:
     - [ ] 10 cây Kiosk hoạt động bình thường
     - [ ] Phần mềm chạy đúng chức năng
     - [ ] Kết nối mạng ổn định
     - [ ] Đã training cho user
   - Ký: Đại diện VNPAY + Đại diện DTX
   - Ngày: 2026-01-15

2. **Upload biên bản vào Odoo**:
   - Mở SO001
   - Tab **Attachments** hoặc Chatter
   - Upload file: "Bien_ban_nghiem_thu_VNPAY_20260115.pdf"

3. **Update trạng thái nghiệm thu** (field custom nếu có):
   - x_acceptance_status: Accepted
   - x_acceptance_date: 2026-01-15

4. **Ghi chú vào Chatter**:
   - Message: "✅ Nghiệm thu hoàn tất ngày 15/01/2026. Biên bản đã ký kèm theo."

**Expected Result**:
- ✅ Biên bản nghiệm thu được lưu trữ
- ✅ Trạng thái nghiệm thu = Accepted
- ✅ **Bây giờ mới được xuất Invoice**

---

## 6. HÓA ĐƠN & THANH TOÁN

### 6.1. Tạo Invoice sau nghiệm thu

**Test Case 16: Create Invoice**

**Precondition**:
- SO001 đã Delivery = Fully Delivered
- Đã nghiệm thu xong (Acceptance Done)

**Actions**:
1. Mở SO001
2. Click button **Create Invoice**
3. Chọn **Regular Invoice**
4. Click **Create and View Invoice**

**Invoice Data**:
- **Customer**: CÔNG TY CP VNPAY
- **Invoice Date**: 2026-01-15 (ngày nghiệm thu)
- **Due Date**: 2026-02-14 (30 days)
- **Payment Reference**: HĐ/2026/VNPAY/001
- **Invoice Lines**: Auto-copy từ SO
  - 10 sản phẩm/dịch vụ
  - Đúng giá HĐ đã apply từ PAKD
- **Subtotal**: ≈ 132,300,000 VND
- **Tax (VAT 10%)**: ≈ 13,230,000 VND
- **Total**: ≈ 145,530,000 VND

**Actions**:
1. Kiểm tra lại Invoice lines & Total
2. Click **Confirm** → Invoice state = Posted
3. Invoice Number: INV/2026/00001

**Expected Result**:
- ✅ Invoice state = Posted
- ✅ Payment Status = Not Paid
- ✅ Amount Due = 145,530,000 VND
- ✅ SO Invoice Status = Fully Invoiced
- ✅ Smart Button **Invoices** = 1

---

### 6.2. Thanh toán đợt 1 (Partial Payment)

**Test Case 17: Register Partial Payment**

**Scenario**: Khách thanh toán 50% trước

**Actions**:
1. Mở Invoice INV/2026/00001
2. Click button **Register Payment**
3. Popup Payment:
   - **Journal**: Bank (hoặc Cash)
   - **Payment Method**: Manual / Bank Transfer
   - **Amount**: 72,765,000 VND (50% của 145,530,000)
   - **Payment Date**: 2026-01-20
   - **Memo**: "Thanh toán đợt 1 - 50% giá trị HĐ VNPAY"
4. Click **Create Payment**

**Expected Result**:
- ✅ Payment được tạo (BNK1/2026/0001)
- ✅ Invoice Payment Status = Partial
- ✅ Amount Due = 72,765,000 VND (còn 50%)
- ✅ Kiểm tra SO001:
  - x_revenue_actual = 66,150,000 VND (50% untaxed amount)
  - x_payment_date = 2026-01-20
  - x_ar_residual_total = 72,765,000 VND
  - x_ar_status = "ok" (chưa quá hạn)

---

### 6.3. Thanh toán đợt 2 (Final Payment)

**Test Case 18: Final Payment**

**Scenario**: Khách thanh toán 50% còn lại

**Actions**:
1. Mở Invoice INV/2026/00001
2. Click **Register Payment**
3. Amount: 72,765,000 VND (auto-fill residual)
4. Payment Date: 2026-02-10
5. Memo: "Thanh toán đợt 2 - Hoàn tất HĐ VNPAY"
6. Click **Create Payment**

**Expected Result**:
- ✅ Invoice Payment Status = Paid
- ✅ Amount Due = 0
- ✅ Kiểm tra SO001:
  - x_revenue_actual = 132,300,000 VND (full untaxed)
  - x_ar_residual_total = 0
  - x_ar_status = "ok"
  - x_payment_date = 2026-02-10

---

### 6.4. Tính lợi nhuận thực tế

**Test Case 19: Profit Analysis**

**Menu**: Sales → Contract Management → Contract List

**Hoặc**: Mở SO001, kiểm tra fields

**Kiểm tra**:
- **Revenue Expected** (x_revenue_expected): 132,300,000 VND (SO untaxed)
- **Revenue Actual** (x_revenue_actual): 132,300,000 VND (invoice paid)
- **Total Cost** (x_total_cost): 96,400,000 VND (từ Contract Costs)
- **Profit** (x_profit): 132,300,000 - 96,400,000 = **35,900,000 VND**
- **Profit Margin %** (x_profit_margin): 35,900,000 / 132,300,000 × 100 ≈ **27.1%**

**So sánh với PAKD dự kiến**:
- PAKD Expected Profit: 50,000,000 VND
- PAKD Expected Margin: 37.8%
- **Variance**: -14,100,000 VND (lợi nhuận giảm do chi phí tăng)

**Expected Result**:
- ✅ Contract List hiển thị đầy đủ financial data
- ✅ Profit & Margin tính chính xác
- ✅ Có thể so sánh với PAKD

---

### 6.5. Trường hợp khách trễ hạn thanh toán

**Test Case 20: Overdue Payment Tracking**

**Scenario**: Khách hàng trễ hạn thanh toán đợt 2

**Actions để test**:
1. Mở Invoice INV/2026/00001 (đã thanh toán 50%)
2. Click **Reset to Draft**
3. Sửa Due Date = 2026-01-25 (quá khứ, để test overdue)
4. Confirm lại Invoice
5. Không register payment cho 50% còn lại

**Kiểm tra AR Status**:
1. Mở SO001
2. Kiểm tra fields:
   - **x_ar_residual_total**: 72,765,000 VND
   - **x_ar_max_days_overdue**: >0 (số ngày quá hạn tính từ 25/01)
   - **x_ar_status**: "overdue"

**Xem AR Aging Report**:
- Menu: Sales → Reporting → AR Aging
- Filter: Customer = VNPAY
- Kiểm tra bucket phân loại:
  - 0-7 days: 0
  - 8-15 days: 0
  - 16-30 days: 72,765,000 VND (ví dụ)
  - ...

**Expected Result**:
- ✅ Hệ thống track đúng công nợ quá hạn
- ✅ AR Status = overdue
- ✅ AR Aging bucket đúng

---

## 7. BẢO TRÌ & SUPPORT

### 7.1. Tạo Maintenance Contract

**Test Case 21: Activate Maintenance**

**Context**:
- Hợp đồng bảo trì 12 tháng đã bán trong SO001
- Bắt đầu sau nghiệm thu

**Option 1: Tracking thủ công**

**Tạo thông tin bảo trì trên SO**:
1. Mở SO001
2. Tab **Internal Notes**:
   ```
   BẢO TRÌ 12 THÁNG
   - Bắt đầu: 2026-01-15
   - Kết thúc: 2027-01-15
   - Nội dung:
     * Hỗ trợ technical 24/7
     * Bảo hành phần cứng
     * Update phần mềm miễn phí
   - Liên hệ: support@dtx.com / 1900-xxx-xxx
   ```

**Option 2: Dùng Helpdesk/FSM module**

**Menu**: Helpdesk → Configuration → Teams → Create

**Team Data**:
- **Name**: Kiosk Support Team
- **Email**: kiosk-support@dtx.com

**Tạo SLA Policy**:
- Response Time: 4 hours
- Resolution Time: 24 hours

**Link SO với Helpdesk**:
- Khi khách gửi ticket, gắn tag "SO001 - VNPAY"

**Expected Result**:
- ✅ Bảo trì được tracking
- ✅ Ticket support có link với SO

---

### 7.2. Xử lý Support Ticket

**Test Case 22: Customer Support Request**

**Scenario**: Khách báo 1 cây Kiosk bị lỗi camera

**Option 1: Tracking bằng Chatter**

**Actions**:
1. Mở SO001
2. Chatter → Log note:
   ```
   🔧 TICKET #001 - 2026-02-20
   Khách hàng: VNPAY - Chi nhánh HCM
   Vấn đề: Camera kiosk số 5 không hoạt động
   Action: Gửi kỹ thuật viên thay camera
   Status: In Progress
   ```
3. Update sau khi xử lý:
   ```
   ✅ RESOLVED - 2026-02-21
   Đã thay camera mới (warranty)
   Kiosk hoạt động bình thường
   ```

**Option 2: Dùng Helpdesk module**

**Menu**: Helpdesk → Tickets → Create

**Ticket Data**:
- **Subject**: Camera không hoạt động - Kiosk #5 VNPAY HCM
- **Customer**: VNPAY
- **Team**: Kiosk Support Team
- **Priority**: High
- **Description**: "Camera tại kiosk số 5 (serial: KSK-005) không bật được. Khách hàng cần hỗ trợ gấp."
- **Related Sale Order**: SO001
- **SLA Deadline**: Auto-calculated (24h)

**Actions**:
1. Assign ticket cho kỹ thuật viên
2. Kỹ thuật viên update ticket:
   - "Đã kiểm tra, camera bị lỗi hardware"
   - "Thay camera mới từ kho warranty"
3. Ticket Status → Solved
4. Close ticket

**Tracking chi phí warranty** (optional):
- Vào SO001 → Costs → Create
- Product: Camera 5MP
- Name: "Thay camera warranty - Ticket #001"
- Qty: 1
- Actual Cost: 595,000 VND
- Cost Type: additional
- → Profit giảm

**Expected Result**:
- ✅ Support request được xử lý đúng SLA
- ✅ Chi phí warranty được tracking
- ✅ Customer satisfaction

---

### 7.3. Gia hạn bảo trì (Renewal)

**Test Case 23: Maintenance Renewal**

**Scenario**: Hết 12 tháng, khách muốn gia hạn

**Actions**:
1. Tạo Quotation mới:
   - Customer: VNPAY
   - Product: 12-Month Maintenance Contract
   - Qty: 10 (10 cây kiosk)
   - Unit Price: 5,000,000
   - Reference: "Gia hạn bảo trì cho SO001"
2. Confirm → SO002
3. Create Invoice → Customer thanh toán

**Expected Result**:
- ✅ Recurring revenue
- ✅ Customer retention

---

## 8. BÁO CÁO & PHÂN TÍCH

### 8.1. Contract List - Tổng hợp hợp đồng

**Test Case 24: View Contract Financial Summary**

**Menu**: Sales → Contract Management → Contract List

**Kiểm tra dữ liệu**:

| SO | Customer | Revenue Expected | Revenue Actual | Total Cost | Profit | Margin % | AR Status |
|----|----------|------------------|----------------|------------|--------|----------|-----------|
| SO001 | VNPAY | 132,300,000 | 132,300,000 | 96,400,000 | 35,900,000 | 27.1% | ok |
| SO002 | VIB | ... | ... | ... | ... | ... | ... |

**Filters & Group By**:
- Group by: Salesperson
- Filter: Profit Margin > 25%
- Filter: AR Status = overdue

**Expected Result**:
- ✅ List view hiển thị đầy đủ financial metrics
- ✅ Có thể sort/filter/group
- ✅ Performance tốt với nhiều records

---

### 8.2. AR Aging Report

**Test Case 25: Accounts Receivable Aging**

**Menu**: Sales → Reporting → AR Aging
**Hoặc**: Sales → Contract Management → AR Aging

**Report Data**:

| Customer | SO | Invoice | Total | 0-7 days | 8-15 days | 16-30 days | 31-60 days | 61-90 days | >90 days |
|----------|----|---------| ------|----------|-----------|------------|------------|------------|----------|
| VNPAY | SO001 | INV/001 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| VIB | SO002 | INV/002 | 50M | 0 | 0 | 50M | 0 | 0 | 0 |

**Filter & Actions**:
- Filter: Only Overdue
- Group by: Customer
- Export to Excel

**Expected Result**:
- ✅ Aging bucket classification chính xác
- ✅ SQL view performance tốt (10K+ invoices)
- ✅ Có thể export

---

### 8.3. PAKD vs Actual Comparison

**Test Case 26: Compare PAKD Forecast vs Actual**

**Manual Analysis** (trong Excel hoặc custom report):

| Metric | PAKD Forecast | Actual | Variance | Variance % |
|--------|---------------|--------|----------|------------|
| Revenue (untaxed) | 132,300,000 | 132,300,000 | 0 | 0% |
| Cost - Components | 81,100,000 | 81,400,000 | +300,000 | +0.4% |
| Cost - Assembly | 0 | 15,000,000 | +15,000,000 | - |
| Total Cost | 81,100,000 | 96,400,000 | +15,300,000 | +18.9% |
| Profit | 50,000,000 | 35,900,000 | -14,100,000 | -28.2% |
| Margin % | 37.8% | 27.1% | -10.7 pp | - |

**Insights**:
- ❌ Lợi nhuận thực tế thấp hơn dự kiến 28.2%
- ⚠️ Nguyên nhân: Không tính chi phí gia công trong PAKD ban đầu
- ✅ Lesson learned: PAKD cần include ALL costs (assembly, shipping, etc.)

**Expected Result**:
- ✅ Có thể so sánh forecast vs actual
- ✅ Identify variance drivers
- ✅ Improve PAKD accuracy cho dự án sau

---

### 8.4. Sales Performance by Salesperson

**Menu**: Sales → Reporting → Sales Analysis

**Report**:
- **Group by**: Salesperson
- **Measures**:
  - Count (số SO)
  - Untaxed Amount (doanh thu)
  - Profit (nếu có custom)
- **Filters**:
  - Date: This Year
  - State: Sale (confirmed)

**Expected Result**:
- ✅ Ranking sales team
- ✅ KPI tracking

---

## 9. EDGE CASES & ERROR HANDLING

### 9.1. PAKD apply vào SO đã có delivery

**Test Case 27: Cannot apply PAKD to confirmed SO**

**Scenario**: SO đã confirm, đã delivery một phần

**Actions**:
1. Confirm SO (state = sale)
2. Validate một phần delivery
3. Thử apply PAKD mới

**Expected Result**:
- ⚠️ Warning: "SO đã confirm, apply PAKD có thể ảnh hưởng"
- ✅ Admin có thể force apply
- ❌ Sales User không được apply (nếu có security rule)

---

### 9.2. UOM mismatch

**Test Case 28: Product UOM mismatch between PAKD and SO**

**Scenario**:
- PAKD: Product A - UOM = Unit
- Product A master data: UOM = Dozen

**Actions**:
- Tạo PAKD line với UOM = Unit
- Apply vào SO

**Expected Result**:
- ✅ Apply wizard tự động convert UOM
- Hoặc: ⚠️