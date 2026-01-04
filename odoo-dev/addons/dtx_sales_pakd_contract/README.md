# DTX Sales PAKD Contract

## Tổng quan

Module **DTX Sales PAKD Contract** tích hợp quản lý **Phương Án Kinh Doanh (PAKD)** và **Hợp đồng** vào Sales Order của Odoo 16 Community.

### Mục tiêu
- Tận dụng tối đa `sale.order` / `sale.order.line` của Odoo (không tạo hệ báo giá mới)
- Cho phép tạo **nhiều PAKD** cho 1 báo giá để so sánh giá nhập/giá bán/lợi nhuận
- Apply PAKD tốt nhất vào Sales Order để tạo hợp đồng
- Quản lý file scan hợp đồng đã ký
- Phân quyền theo role: CEO, Sales Director, Chief Accountant, Sales User

## Tính năng chính

### 1. Extend Sale Order với các field hợp đồng
- **Khách hàng cuối (End User)**: `x_end_customer_id`
- **Đại lý/Đối tác giới thiệu**: `x_agent_id`
- **Số hợp đồng**: `x_contract_no`
- **Ngày ký HĐ**: `x_signed_date`
- **Ngày hết hạn HĐ**: `x_contract_end_date`
- **File scan hợp đồng**: `x_contract_scan_attachment_ids` (upload PDF/JPG)

### 2. PAKD (Phương Án Kinh Doanh)
- Model riêng: `dtx.pakd` + `dtx.pakd.line`
- **Nhiều PAKD** cho 1 Sale Order
- Mỗi PAKD line gồm:
  - Đơn giá báo giá (`sale_unit_price`)
  - Đơn giá nhập (`purchase_unit_price`)
  - Đơn giá HĐ (`contract_unit_price`)
  - VAT % (`vat_percent`) - tự động map sang `account.tax`
- Computed totals: Tổng nhập, tổng HĐ, lợi nhuận, tỷ lệ lãi

### 3. Auto map VAT% → account.tax
- Nhập `vat_percent` (0/5/8/10...) → hệ thống tìm `account.tax` tương ứng
- Fallback: Nếu không tìm thấy, cho phép chọn thủ công

### 4. Apply PAKD vào Sale Order
- Wizard `dtx.pakd.apply.wizard`
- Options:
  - **Thay thế toàn bộ dòng**: Xóa dòng cũ, tạo mới từ PAKD
  - **Nguồn giá**: Ưu tiên contract_unit_price hoặc chỉ dùng sale_unit_price
- Log message vào chatter của SO và PAKD

### 5. Security & Permissions
- **CEO / Sales Director / Chief Accountant**: Full access tất cả
- **Sales User**: Chỉ xem/sửa own Sales Order và own PAKD
- **Account User**: Read-only tất cả

## Cài đặt

### 1. Chuẩn bị

Đảm bảo đã cài các module phụ thuộc:
- `sale`
- `sale_management`
- `account`
- `product`

### 2. Install module

```bash
# Restart Odoo
docker-compose restart odoo

# Install module
docker-compose exec odoo odoo -i dtx_sales_pakd_contract -d your_database --stop-after-init

# Restart again
docker-compose restart odoo
```

### 3. Cấu hình VAT tax (quan trọng!)

Để auto-mapping VAT% hoạt động, cần tạo các tax chuẩn:

**Menu**: Accounting → Configuration → Taxes

Tạo các tax sau (nếu chưa có):

| Tên | Type | Computation | Amount | Scope |
|-----|------|-------------|--------|-------|
| VAT 0% | Sales | Percentage | 0% | Sale |
| VAT 5% | Sales | Percentage | 5% | Sale |
| VAT 8% | Sales | Percentage | 8% | Sale |
| VAT 10% | Sales | Percentage | 10% | Sale |

**Note**: Module sẽ tự động search tax theo `amount` percent khi user nhập `vat_percent`.

### 4. Cấu hình User Groups

**Menu**: Settings → Users → Users

Gán users vào các group phù hợp:
- **DTX CEO**: Full access
- **DTX Sales Director**: Full access
- **DTX Chief Accountant**: Full access
- **DTX Sales User**: Own records only
- **DTX Sales UI (Simplified)**: Ẩn field không dùng (campaign/medium/source)

## Quy trình sử dụng

### Workflow: Quotation → PAKD → Contract

```
┌─────────────────────────────────────────────────────────────┐
│ 1. TẠO QUOTATION (Báo giá)                                  │
│    - Tạo sale.order mới                                     │
│    - Nhập khách hàng, sản phẩm, giá sơ bộ                   │
│    - State: draft/sent                                      │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. TẠO PAKD (Phương án kinh doanh)                          │
│    - Click "Tạo PAKD mới" trên SO                           │
│    - Hệ thống tạo PAKD với lines từ SO lines                │
│    - Chỉnh sửa:                                             │
│      + purchase_unit_price (giá nhập)                       │
│      + contract_unit_price (giá HĐ chốt)                    │
│      + vat_percent (VAT %)                                  │
│    - Xem totals: lợi nhuận, margin                          │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. SO SÁNH NHIỀU PAKD (nếu cần)                             │
│    - Tạo thêm PAKD 2, PAKD 3... với giá khác nhau           │
│    - Compare profit/margin                                  │
│    - Chọn PAKD tốt nhất                                     │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. APPLY PAKD VÀO SO                                        │
│    - Mở PAKD đã chọn                                        │
│    - Click "Apply vào Báo giá"                              │
│    - Wizard: chọn replace lines + price source              │
│    - Confirm → SO lines được cập nhật                       │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. CONFIRM TẠO HỢP ĐỒNG                                     │
│    - Click "Confirm" trên SO (dùng core Odoo)               │
│    - State: sale (= Hợp đồng)                               │
│    - Nhập thông tin HĐ:                                     │
│      + Số hợp đồng (x_contract_no)                          │
│      + Ngày ký (x_signed_date)                              │
│      + Ngày hết hạn (x_contract_end_date)                   │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. UPLOAD FILE SCAN HỢP ĐỒNG                                │
│    - Tab "Hợp đồng" trên SO                                 │
│    - Upload PDF/JPG scan hợp đồng đã ký                     │
│    - Lưu                                                    │
└─────────────────────────────────────────────────────────────┘
```

## UAT Test Case: "Kim Sơn 7 quầy"

### Chuẩn bị test data

**1. Tạo Partners**:
- Customer: **Kim Sơn Co., Ltd** (is_company=True)
- End User: **Siêu thị Kim Sơn** (is_company=False)

**2. Tạo Products** (nếu chưa có):
- **Kiosk Model A** (Kiosk hoàn chỉnh)
  - Type: Consumable hoặc Storable
  - Sale Price: 50,000,000 VND
  - Cost: 35,000,000 VND
  - Taxes: VAT 10%

### Test Scenario

#### Step 1: Tạo Quotation

1. Menu: **Sales → Orders → Quotations → Create**
2. Điền thông tin:
   - Customer: Kim Sơn Co., Ltd
   - End User: Siêu thị Kim Sơn
   - Agent: (để trống hoặc chọn nếu có)
3. Add product line:
   - Product: Kiosk Model A
   - Qty: 7
   - Unit Price: 50,000,000 (auto-fill)
   - Tax: VAT 10%
4. **Save** (chưa Confirm)

**Expected**:
- Quotation created với state = draft
- Total: 385,000,000 VND (7 x 50M + VAT 10%)

---

#### Step 2: Tạo PAKD 1 (Phương án giá cao)

1. Mở quotation vừa tạo
2. Tab **"Phương án kinh doanh (PAKD)"**
3. Click **"Tạo PAKD mới"**
4. Hệ thống tạo PAKD với 1 line từ SO line
5. Edit PAKD line:
   - Đơn giá báo giá: 50,000,000 (auto-fill)
   - **Đơn giá nhập**: 35,000,000
   - **Đơn giá HĐ**: 50,000,000 (giữ nguyên)
   - **VAT %**: 10 (auto map to VAT 10% tax)
6. **Save**

**Expected**:
- PAKD name: PAKD-2026-0001
- Totals:
  - Tổng giá nhập: 245,000,000 (7 x 35M)
  - Tổng giá HĐ (chưa VAT): 350,000,000 (7 x 50M)
  - Tổng VAT: 35,000,000
  - Tổng giá HĐ (có VAT): 385,000,000
  - **Lợi nhuận**: 105,000,000 (350M - 245M)
  - **Margin**: 30% (105M / 350M)

---

#### Step 3: Tạo PAKD 2 (Phương án giá thấp hơn)

1. Quay lại quotation
2. Click **"Tạo PAKD mới"** lần nữa
3. Edit PAKD 2 line:
   - Đơn giá nhập: 35,000,000
   - Đơn giá HĐ: **45,000,000** (giảm giá)
   - VAT %: 10
4. **Save**

**Expected**:
- PAKD name: PAKD-2026-0002
- Totals:
  - Tổng giá HĐ (chưa VAT): 315,000,000 (7 x 45M)
  - **Lợi nhuận**: 70,000,000 (315M - 245M)
  - **Margin**: 22.22%

---

#### Step 4: So sánh và Apply PAKD

1. Mở tab **"PAKD liên quan"** trên quotation
2. Xem 2 PAKD:
   - PAKD-2026-0001: Margin 30%
   - PAKD-2026-0002: Margin 22.22%
3. Quyết định chọn **PAKD 1** (margin cao hơn)
4. Mở PAKD-2026-0001
5. Click **"Apply vào Báo giá"**
6. Wizard:
   - Thay thế toàn bộ dòng: ✅ Tick
   - Nguồn giá: **Ưu tiên đơn giá HĐ**
7. Click **"Apply"**

**Expected**:
- SO lines updated:
  - Kiosk Model A x7, Unit Price = 50,000,000, Tax = VAT 10%
- Chatter message: "✅ Đã apply PAKD PAKD-2026-0001"
- Total không đổi: 385,000,000

---

#### Step 5: Confirm tạo Hợp đồng

1. Click **"Confirm"** trên quotation
2. State: sale (= Sales Order = Hợp đồng)
3. Tab **"Hợp đồng"**:
   - Số hợp đồng: **HĐ-KS-2026-001**
   - Ngày ký: 03/01/2026
   - Ngày hết hạn: 03/01/2027
4. **Save**

**Expected**:
- State = sale
- Order name: SO001
- Contract fields filled

---

#### Step 6: Upload file scan

1. Chuẩn bị file PDF/JPG (fake contract scan)
2. Tab **"Hợp đồng"** → **"Upload file scan"**
3. Select file → Upload
4. **Save**

**Expected**:
- Smart button "File HĐ" hiện số lượng file
- Click button → xem attachment

---

### Test Permissions

**Test 1: Sales User own records**
1. Login as Sales User (not owner)
2. Menu: Sales → Orders → Quotations
3. **Expected**: Chỉ thấy quotations của mình (user_id = current user)

**Test 2: Sales Director full access**
1. Login as Sales Director
2. Menu: Sales → Orders → Quotations
3. **Expected**: Thấy tất cả quotations

**Test 3: PAKD access**
1. Login as Sales User
2. Menu: Sales → PAKD
3. **Expected**: Chỉ thấy PAKD của mình (owner_user_id = current user)

---

## Troubleshooting

### Issue 1: VAT không auto-map

**Nguyên nhân**: Chưa có tax với percent tương ứng

**Giải pháp**:
1. Menu: Accounting → Configuration → Taxes
2. Create tax mới:
   - Name: VAT X%
   - Tax Type: Sales
   - Tax Computation: Percentage of Price
   - Amount: X%
   - Tax Scope: Sale

### Issue 2: Apply PAKD bị lỗi "Missing Record"

**Nguyên nhân**: SO đã bị xóa hoặc PAKD bị orphan

**Giải pháp**:
- Kiểm tra `pakd.sale_order_id` còn tồn tại không
- Nếu SO bị xóa, PAKD cũng tự động xóa (ondelete='cascade')

### Issue 3: File scan không upload được

**Nguyên nhân**: User không có quyền attachment

**Giải pháp**:
- Kiểm tra user có quyền `base.group_user`
- Kiểm tra ir.rule cho `ir.attachment`

---

## API Reference

### Models

#### `sale.order` (inherited)
**New Fields**:
- `x_end_customer_id`: Many2one(res.partner)
- `x_agent_id`: Many2one(res.partner)
- `x_contract_no`: Char
- `x_signed_date`: Date
- `x_contract_end_date`: Date
- `x_contract_scan_attachment_ids`: Many2many(ir.attachment)
- `pakd_ids`: One2many(dtx.pakd)

**New Methods**:
- `action_view_pakd()`: View PAKDs for this SO
- `action_create_pakd()`: Create new PAKD from SO lines
- `action_view_contract_scans()`: View contract attachments

#### `dtx.pakd`
**Fields**:
- `name`: Char (PAKD-YYYY-NNNN)
- `sale_order_id`: Many2one(sale.order)
- `owner_user_id`: Many2one(res.users)
- `state`: Selection (draft/submitted/approved/rejected)
- `line_ids`: One2many(dtx.pakd.line)
- `total_purchase`: Monetary (computed)
- `total_contract_untaxed`: Monetary (computed)
- `expected_profit`: Monetary (computed)
- `expected_margin_percent`: Float (computed)

**Methods**:
- `action_submit()`: Submit for approval
- `action_approve()`: Approve PAKD
- `action_open_apply_wizard()`: Open apply wizard

#### `dtx.pakd.line`
**Fields**:
- `product_id`: Many2one(product.product)
- `qty`: Float
- `uom_id`: Many2one(uom.uom)
- `sale_unit_price`: Monetary
- `purchase_unit_price`: Monetary
- `contract_unit_price`: Monetary
- `vat_percent`: Float
- `tax_id`: Many2one(account.tax)
- Computed totals: purchase_total, contract_total_excl_vat, contract_tax_amount, line_profit, line_margin_percent

**Methods**:
- `_find_tax_by_percent(vat_percent)`: Find tax by percent

---

## Changelog

### Version 1.0.0 (2026-01-03)
**Initial Release**:
- ✅ Extend sale.order với contract fields
- ✅ Model dtx.pakd + dtx.pakd.line
- ✅ Multi-PAKD per quotation
- ✅ Auto VAT% → account.tax mapping
- ✅ Apply wizard với price override
- ✅ Security groups: CEO, Sales Director, Chief Accountant, Sales User
- ✅ Record rules phân quyền
- ✅ View inheritance (ẩn unused fields)
- ✅ Contract scan attachment upload
- ✅ Chatter integration
- ✅ Computed totals (profit, margin)

---

## License

LGPL-3

## Author

DTX Project Team

## Support

- GitHub: https://github.com/your-org/dtx-odoo-modules
- Email: support@dtx.com
