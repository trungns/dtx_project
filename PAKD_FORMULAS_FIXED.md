# ✅ PAKD Formulas đã được sửa theo Excel Template

**Ngày**: 2026-01-04
**Version mới**: 16.0.1.3.0
**Trạng thái**: ✅ Đã upgrade thành công

---

## 📊 Tóm tắt thay đổi

Đã phân tích hình Excel bạn gửi và **sửa tất cả công thức PAKD** để khớp chính xác với file Excel template.

### Vấn đề chính đã sửa:

1. ❌ **Trước**: Thu thuế tính trên `tổng tiền HĐ chưa VAT`
   ✅ **Sau**: Thu thuế tính trên `chênh lệch giá` (đúng như Excel)

2. ❌ **Trước**: Không có field "Tổng gối thêm"
   ✅ **Sau**: Đã thêm field mới `cushion_amount = chênh lệch giá - thu thuế`

3. ❌ **Trước**: Hoa hồng nhập tay
   ✅ **Sau**: Hoa hồng tự tính theo % (từ `tổng tiền HĐ chưa VAT`)

4. ❌ **Trước**: Tổng chi phí cho khách nhập tay
   ✅ **Sau**: Tự tính = `Tổng gối thêm + Hoa hồng`

5. ❌ **Trước**: Label không khớp Excel
   ✅ **Sau**: Đánh số 1-9 đúng như Excel

---

## 🆕 Field mới trong PAKD

### 1. **Tổng gối thêm** (`cushion_amount`)
- **Loại**: Tự động tính (stored)
- **Công thức**: `= Chênh lệch giá - Thu thuế`
- **Ý nghĩa**: Số tiền còn lại sau khi trừ thuế từ chênh lệch giá
- **Hiển thị**: Row 6 trong tab "Tổng kết"

### 2. **Tỷ lệ hoa hồng %** (`referral_commission_percent`)
- **Loại**: Nhập tay
- **Mặc định**: 0%
- **Ví dụ**: Nhập 3 (tức 3%)
- **Hiển thị**: Row 7 bên cạnh field "Hoa hồng"

---

## 📐 Công thức mới (khớp Excel)

### Tab "Tổng kết" → Section "Phần chi phí cho khách hàng/người giới thiệu"

| Row | Label | Công thức | Input? |
|-----|-------|-----------|--------|
| 1 | Tổng tiền nhập (chi phí đầu vào) | `= SUM(purchase_total)` | Tự động |
| 2 | Tổng tiền bán (chi phí thứ vỡ) | `= SUM(sale_total)` | Tự động |
| 3 | Tổng tiền HĐ (bao gồm chi phí ghi nêu cả) | `= SUM(contract_total_incl_vat)` | Tự động |
| 4 | **Chênh lệch giá** | `= Row 2 - Row 1` | Tự động |
| 5 | **Thu thuế X%** | `= Row 4 × X%` | **Nhập X%** |
| 6 | **Tổng gối thêm** | `= Row 4 - Row 5` | Tự động ✨ |
| 7 | **Hoa hồng Y%** | `= Row 3a × Y%` | **Nhập Y%** ✨ |
| 8 | **Tổng chi phí cho khách** | `= Row 6 + Row 7` | Tự động ✨ |
| 9 | **Lợi nhuận** | `= Row 4 - Row 5 - Row 7` | Tự động |

✨ = Field mới hoặc công thức đã sửa

---

## ✅ Ví dụ với UAT Quỳ Châu (197.5M)

### Giả sử:
- **Tổng tiền nhập** (Row 1): 156,000,000 VND
- **Tổng tiền bán** (Row 2): 156,000,000 VND
- **Tổng tiền HĐ có VAT** (Row 3): 197,500,000 VND
- **Tổng tiền HĐ chưa VAT** (Row 3a): 179,545,455 VND
- **Chênh lệch giá** (Row 4): 156M - 156M = 0 *(hoặc có thể khác nếu giá bán ≠ giá nhập)*

### Nếu Chênh lệch giá = 41,500,000 VND (ước tính từ Excel):

Nhập vào PAKD:
- **Thu thuế %**: Nhập `17` (%)
- **Hoa hồng %**: Nhập `3` (%)

Hệ thống tự tính:
- **Row 5: Thu thuế** = 41,500,000 × 17% = **7,055,000 VND** ✅ (khớp Excel!)
- **Row 6: Tổng gối thêm** = 41,500,000 - 7,055,000 = **34,445,000 VND**
- **Row 7: Hoa hồng** = 179,545,455 × 3% = **5,386,364 VND**
- **Row 8: Tổng chi phí cho khách** = 34,445,000 + 5,386,364 = **39,831,364 VND**
- **Row 9: Lợi nhuận** = 41,500,000 - 7,055,000 - 5,386,364 = **29,058,636 VND**
- **Tỷ lệ lãi** = 29,058,636 / 179,545,455 = **16.19%**

---

## 🔄 Breaking Changes (Quan trọng!)

⚠️ **CHÚ Ý**: Nếu có PAKD cũ, các field sau sẽ **thay đổi từ nhập tay → tự tính**:

1. **`referral_commission`** (Hoa hồng người giới thiệu):
   - Trước: Nhập tay
   - Sau: Tự tính theo %
   - ➡️ Giá trị cũ sẽ bị ghi đè!

2. **`customer_support_cost`** (Tổng chi phí cho khách):
   - Trước: Nhập tay
   - Sau: Tự tính = gối thêm + hoa hồng
   - ➡️ Giá trị cũ sẽ bị ghi đè!

### Giải pháp:
- Hiện tại chưa có PAKD nào trong database → Không bị ảnh hưởng ✅
- Nếu sau này cần nhập manual: có thể mở rộng thêm field riêng

---

## 🎯 Hướng dẫn sử dụng mới

### Bước 1: Tạo Quotation (như cũ)
- Tạo báo giá với 9 dòng
- Tổng = 197,500,000 VND

### Bước 2: Tạo PAKD từ Quotation
- Click nút **"Tạo PAKD"**
- Hệ thống tạo PAKD với 9 dòng

### Bước 3: Nhập giá Purchase (như cũ)
- Trong PAKD lines, nhập `purchase_unit_price` cho từng dòng

### Bước 4: Nhập tỷ lệ % (MỚI!)

Chuyển sang tab **"Tổng kết"**, section **"Phần chi phí cho khách hàng/người giới thiệu"**:

#### **Row 5: Thu thuế**
- Nhập **"Tỷ lệ thu thuế (%)"**: Ví dụ `17`
- Hệ thống tự tính số tiền = `Chênh lệch giá × 17%`

#### **Row 7: Hoa hồng**
- Nhập **"Tỷ lệ hoa hồng (%)"**: Ví dụ `3`
- Hệ thống tự tính số tiền = `Tổng tiền HĐ chưa VAT × 3%`

### Bước 5: Kiểm tra kết quả
- **Row 6: Tổng gối thêm** tự tính = Row 4 - Row 5 ✅
- **Row 8: Tổng chi phí cho khách** tự tính = Row 6 + Row 7 ✅
- **Row 9: Lợi nhuận** tự tính = Row 4 - Row 5 - Row 7 ✅

### Bước 6: Apply vào Quotation và Confirm (như cũ)

---

## 📁 Files đã thay đổi

1. **[models/dtx_pakd.py](odoo-dev/addons/dtx_sales_pakd_contract/models/dtx_pakd.py)**
   - Thêm field: `cushion_amount`, `referral_commission_percent`
   - Sửa công thức: `_compute_business_costs()`

2. **[views/dtx_pakd_views.xml](odoo-dev/addons/dtx_sales_pakd_contract/views/dtx_pakd_views.xml)**
   - Tab "Tổng kết" được cấu trúc lại
   - Label đánh số 1-9 khớp Excel

3. **[__manifest__.py](odoo-dev/addons/dtx_sales_pakd_contract/__manifest__.py)**
   - Version: 16.0.1.1.0 → **16.0.1.3.0**

---

## ✅ Trạng thái Upgrade

```
✅ Module đã upgrade thành công
✅ Database đã thêm 2 column mới:
   - dtx_pakd.cushion_amount (numeric)
   - dtx_pakd.referral_commission_percent (float)
✅ Odoo đang chạy trên port 8069
```

---

## 🧪 Next Steps - Test ngay!

### 1. Tạo Quotation mới
Làm theo [MANUAL_UAT_GUIDE.md](odoo-dev/addons/dtx_sales_pakd_contract/MANUAL_UAT_GUIDE.md) STEP 2:
- Customer: Viettel Hà Nội
- End Customer: UBND Quỳ Châu
- 9 dòng sản phẩm
- **Kiểm tra**: Tổng = 197,500,000 VND ✅

### 2. Tạo PAKD
- Click **"Tạo PAKD"**
- **Kiểm tra**: PAKD có 9 dòng ✅

### 3. Nhập Purchase prices
Trong PAKD lines, nhập giá nhập cho các sản phẩm:
- DTX-A17: 22,000,000
- DTX-LEDw: 3,100,000
- UA98DU9000: 45,000,000
- X2-2.1: 2,000,000
- SV-INSTALL: 18,000,000

### 4. Nhập % trong tab "Tổng kết"
- **Thu thuế %**: Nhập `17`
- **Hoa hồng %**: Nhập `3`

### 5. Verify công thức
**Kiểm tra Row 5 (Thu thuế)**:
- Nếu Chênh lệch giá = 41,500,000
- Thu thuế = 41,500,000 × 17% = 7,055,000 ✅

**Kiểm tra Row 6 (Tổng gối thêm)**:
- = 41,500,000 - 7,055,000 = 34,445,000 ✅

**Kiểm tra Row 7 (Hoa hồng)**:
- Tổng tiền HĐ chưa VAT ≈ 179,545,455
- Hoa hồng = 179,545,455 × 3% ≈ 5,386,364 ✅

**Kiểm tra Row 8 (Tổng chi phí cho khách)**:
- = 34,445,000 + 5,386,364 ≈ 39,831,364 ✅

**Kiểm tra Row 9 (Lợi nhuận)**:
- = 41,500,000 - 7,055,000 - 5,386,364 ≈ 29,058,636 ✅

### 6. So sánh với Excel
- Đối chiếu từng row với Excel screenshot bạn gửi
- Nếu khớp → ✅ Success!
- Nếu không khớp → Báo cho tôi biết giá trị nào sai

---

## 🐛 Troubleshooting

### Vấn đề: Không thấy field "Tổng gối thêm"
**Nguyên nhân**: Browser cache
**Giải pháp**: Shift + F5 để hard refresh, hoặc Ctrl + Shift + R

### Vấn đề: Công thức vẫn sai
**Nguyên nhân**: PAKD cũ chưa recompute
**Giải pháp**:
1. Mở PAKD
2. Click Edit
3. Thay đổi bất kỳ field nào (ví dụ: tax_withheld_percent)
4. Save
5. Hệ thống sẽ tự tính lại

### Vấn đề: Lỗi khi tạo PAKD (uom_id)
**Trạng thái**: Đang điều tra
**Workaround**: Đảm bảo quotation có đầy đủ 9 dòng với product_uom hợp lệ

---

## 📞 Support

Nếu gặp vấn đề:
1. Check log: `docker-compose logs odoo --tail=50`
2. Gửi screenshot lỗi
3. Hoặc gửi giá trị cụ thể trong PAKD để so sánh

---

**Status**: ✅ Sẵn sàng test với data thực!
**Odoo URL**: http://localhost:8069
**Login**: admin / admin
