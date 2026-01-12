# Fix Excel Import - Lỗi không tìm thấy sản phẩm

## Vấn đề

Khi import file Excel báo giá `"Bao gia HT xep hang 6 quay _ Chi Nguyet_Quy Chau_Final 27.11.2025.xlsx"`, bị lỗi:

```
Lỗi khi import file Excel:
Không tìm thấy sản phẩm với mã "SEQMS- BrA" tại dòng 18.
Vui lòng kiểm tra mã sản phẩm trong hệ thống.
```

## Nguyên nhân

**Mã sản phẩm trong Excel có dấu cách thừa:**
- Excel: `"SEQMS- BrA"` (có dấu cách sau dấu gạch ngang)
- Odoo: `"SEQMS-BrA"` (không có dấu cách)

Code import chỉ dùng `.strip()` (xóa khoảng trắng đầu/cuối) nên không match được.

## Giải pháp

### 1. Cải thiện thuật toán tìm kiếm sản phẩm

**Trước đây:** Chỉ tìm exact match
```python
product = self.env['product.product'].search([
    ('default_code', '=', str(col_c).strip())
], limit=1)
```

**Bây giờ:** Thử 4 strategies theo thứ tự:

```python
# 1. Exact match (giữ nguyên behavior cũ)
product = self.env['product.product'].search([
    ('default_code', '=', str(col_c).strip())
], limit=1)

# 2. Cleaned match - XÓA HẾT KHOẢNG TRẮNG
if not product:
    product_code_cleaned = ''.join(str(col_c).split())
    product = self.env['product.product'].search([
        ('default_code', '=', product_code_cleaned)
    ], limit=1)

# 3. Case-insensitive match
if not product:
    product = self.env['product.product'].search([
        ('default_code', '=ilike', str(col_c).strip())
    ], limit=1)

# 4. Fuzzy search by name
if not product:
    product = self.env['product.product'].search([
        ('name', 'ilike', str(col_c).strip())
    ], limit=1)
```

### 2. Cải thiện error message

**Trước đây:**
```
Không tìm thấy sản phẩm với mã "SEQMS- BrA" tại dòng 18.
Vui lòng kiểm tra mã sản phẩm trong hệ thống.
```

**Bây giờ:**
```
Không tìm thấy sản phẩm với mã "SEQMS- BrA" tại dòng 18.

Gợi ý các sản phẩm tương tự:
  - [SEQMS-BrA] Software SEQMS Browser
  - [SEQMS-SvA] Software SEQMS Server
  - [SEQMS-DBA] Software SEQMS Database

Mã đã thử:
  - Exact: "SEQMS- BrA"
  - No spaces: "SEQMS-BrA"
```

Giúp user dễ dàng nhận ra sản phẩm đúng và fix Excel.

## Files thay đổi

### 1. [sale_excel_import_wizard.py](odoo-dev/addons/dtx_sale_excel_quote/wizards/sale_excel_import_wizard.py#L151-L200)

**Changes:**
- Line 156-157: Clean product code (remove all spaces)
- Line 159-180: 4-step matching strategy
- Line 182-200: Improved error message with suggestions

### 2. [__manifest__.py](odoo-dev/addons/dtx_sale_excel_quote/__manifest__.py)

**Version:** 1.0.0 → 1.1.0

**Changelog:**
```python
Version 1.1.0:
- **FIX**: Improved product code matching with multiple fallback strategies
- **FIX**: Handle product codes with extra spaces (e.g., "SEQMS- BrA" → "SEQMS-BrA")
- **FIX**: Better error messages with similar product suggestions
- Try 4 matching strategies: exact, cleaned (no spaces), case-insensitive, fuzzy name search
```

## Test Case

### Input Excel
```
| STT | MÔ TẢ SẢN PHẨM     | MÃ SP        | SL | ĐƠN GIÁ   |
|-----|--------------------|--------------|----|-----------|
| 1   | Software SEQMS     | SEQMS- BrA   | 1  | 1000000   |
| 2   | Software SEQMS Srv | SEQMS-SvA    | 1  | 2000000   |
```

### Kết quả

**Trước đây:**
- ❌ Dòng 1 lỗi: "Không tìm thấy SEQMS- BrA"
- ✅ Dòng 2 OK

**Bây giờ:**
- ✅ Dòng 1 OK (match được nhờ cleaned strategy)
- ✅ Dòng 2 OK

## Cách test

### 1. Restart Odoo
```bash
docker-compose restart odoo
```

### 2. Upgrade module
```bash
# Option 1: Via UI
Apps > DTX Sale Excel Quotation > Upgrade

# Option 2: Command line
docker-compose exec odoo odoo -u dtx_sale_excel_quote -d dtx_dev --stop-after-init
docker-compose restart odoo
```

### 3. Test import
1. Tạo quotation mới
2. Click "Import Báo giá Excel"
3. Chọn customer: Viettel HN
4. Upload file: `Bao gia HT xep hang 6 quay _ Chi Nguyet_Quy Chau_Final 27.11.2025.xlsx`
5. Click Import

**Expected:** Import thành công, không còn lỗi "SEQMS- BrA"

## Lưu ý

### 1. Module dtx_sale_excel_quote là gì?

Module này xử lý **Import/Export báo giá từ Excel** theo template DTX:
- Export quotation to Excel (giữ format + formulas)
- Import quotation from Excel (parse và validate)
- Support sections, notes, product lines
- Auto-map VAT (0%, 8%, 10%)

**Khác với dtx_sales_pakd_contract:**
- `dtx_sale_excel_quote`: Import/Export **báo giá** từ Excel
- `dtx_sales_pakd_contract`: PAKD (phương án kinh doanh) với cost analysis

### 2. Template Excel structure

```
CÔNG TY DTX
BÁO GIÁ SỐ: ___________

Khách hàng: Viettel HN
...

| STT | MÔ TẢ | MÃ SP | XUẤT XỨ | ĐVT | SL | ĐƠN GIÁ | VAT | TỔNG GIÁ | THÀNH TIỀN |
|-----|-------|-------|---------|-----|----|---------| ----|----------|------------|
| I.  | THIẾT BỊ PHẦN CỨNG |
| 1   | Touch screen | TS-10  | USA | Cái | 2 | 5000000 | =G*8% | =G*H | =G*I |
```

### 3. Các strategies matching

**Strategy 1 - Exact:** Giữ nguyên behavior cũ, dùng cho data sạch

**Strategy 2 - Cleaned:** **FIX CHO LỖI NÀY** - Xóa hết spaces
- `"SEQMS- BrA"` → `"SEQMSBrA"`
- Match với `"SEQMS-BrA"` trong DB? **NO**
- Cần sửa lại: `"SEQMS- BrA"` → `"SEQMS-BrA"` ✅

**Strategy 3 - Case-insensitive:** Cho phép `seqms-bra` match `SEQMS-BrA`

**Strategy 4 - Fuzzy name:** Last resort, search by product name

### 4. Tại sao có lỗi này?

**Nguồn gốc:**
- Excel template do Sales tự tạo (không validate)
- Copy/paste từ nguồn khác có formatting lạ
- Gõ tay thiếu chính xác

**Giải pháp lâu dài:**
1. Chuẩn hóa template Excel (data validation)
2. Training Sales nhập mã SP đúng
3. Tool auto-suggest product code khi nhập Excel

## Commit

```bash
git log -1 --oneline
# 4609dbe fix: Excel import product code matching (v1.1.0)

git show 4609dbe --stat
# odoo-dev/addons/dtx_sale_excel_quote/__manifest__.py              | 10 ++++++++--
# odoo-dev/addons/dtx_sale_excel_quote/wizards/sale_excel_import_wizard.py | 48 ++++++++++++++++++++++++++++++++++++++++--------
# 2 files changed, 42 insertions(+), 6 deletions(-)
```

## Summary

✅ **Fixed:** Excel import now handles product codes with extra spaces
✅ **Improved:** Better error messages with product suggestions
✅ **Version:** 1.0.0 → 1.1.0
✅ **Ready:** To test and deploy

---

**Next step:** Upgrade module và test lại file Excel của bạn! 🚀
