# Chi phí cho Khách hàng / Người giới thiệu (Commission Tracking)

## Tổng quan

Module đã được mở rộng để theo dõi các khoản chi phí (hoa hồng) phải trả cho khách hàng và người giới thiệu, và tính toán **Lãi ròng** (Net Profit) sau khi trừ đi các khoản chi phí này.

## Các trường dữ liệu mới

### 1. Hoa hồng / Chi phí cho KH (`x_customer_commission`)
- **Kiểu**: Monetary
- **Mục đích**: Lưu trữ số tiền hoa hồng hoặc chi phí khác phải trả cho khách hàng
- **Ví dụ**: Chiết khấu thanh toán sớm, chi phí hỗ trợ kỹ thuật, etc.
- **Nhập liệu**: Thủ công trong tab "Hợp đồng" của Sale Order

### 2. Hoa hồng người giới thiệu (`x_referrer_commission`)
- **Kiểu**: Monetary
- **Mục đích**: Lưu trữ số tiền hoa hồng cho người giới thiệu/đại lý
- **Ví dụ**: 5% doanh thu cho đại lý, 10M VND cho người giới thiệu
- **Nhập liệu**: Thủ công trong tab "Hợp đồng" của Sale Order

### 3. Tổng hoa hồng (`x_total_commission`)
- **Kiểu**: Monetary (Computed, Stored)
- **Công thức**: `x_customer_commission + x_referrer_commission`
- **Mục đích**: Tổng tất cả các khoản hoa hồng phải chi
- **Tự động tính**: Cập nhật tự động khi thay đổi hoa hồng KH hoặc người GT

### 4. Lãi ròng (`x_net_profit`)
- **Kiểu**: Monetary (Computed, Stored)
- **Công thức**: `x_profit - x_total_commission`
- **Mục đích**: Lợi nhuận thực sự sau khi trừ tất cả chi phí
- **Tự động tính**: Cập nhật khi thay đổi lãi hoặc hoa hồng
- **Màu sắc**:
  - 🔴 Đỏ nếu âm (lỗ)
  - 🟢 Xanh nếu dương (lãi)

### 5. Lãi ròng (%) (`x_net_profit_margin`)
- **Kiểu**: Float (Computed, Stored)
- **Công thức**: `(x_net_profit / x_revenue_actual) * 100`
- **Mục đích**: Tỷ lệ % lợi nhuận ròng so với doanh thu
- **Tự động tính**: Cập nhật khi thay đổi lãi ròng hoặc doanh thu
- **Màu sắc**:
  - 🔴 Đỏ nếu âm (tỷ lệ lỗ)
  - 🟢 Xanh nếu dương (tỷ lệ lãi)

## Công thức tính toán

```
Tổng hoa hồng = Hoa hồng KH + Hoa hồng người GT
Lãi ròng = Lãi - Tổng hoa hồng
Lãi ròng (%) = (Lãi ròng / Doanh thu thực tế) × 100
```

### Ví dụ tính toán

**Ví dụ 1: Không có hoa hồng**
- Doanh thu: 100M
- Chi phí: 60M
- Lãi: 40M
- Hoa hồng KH: 0M
- Hoa hồng người GT: 0M
- → **Tổng hoa hồng: 0M**
- → **Lãi ròng: 40M - 0M = 40M**
- → **Lãi ròng (%): (40M / 100M) × 100 = 40%**

**Ví dụ 2: Có hoa hồng KH**
- Doanh thu: 100M
- Chi phí: 60M
- Lãi: 40M
- Hoa hồng KH: 10M
- Hoa hồng người GT: 0M
- → **Tổng hoa hồng: 10M**
- → **Lãi ròng: 40M - 10M = 30M**
- → **Lãi ròng (%): (30M / 100M) × 100 = 30%**

**Ví dụ 3: Có cả hai loại hoa hồng**
- Doanh thu: 100M
- Chi phí: 60M
- Lãi: 40M
- Hoa hồng KH: 10M
- Hoa hồng người GT: 5M
- → **Tổng hoa hồng: 15M**
- → **Lãi ròng: 40M - 15M = 25M**
- → **Lãi ròng (%): (25M / 100M) × 100 = 25%**

**Ví dụ 4: Hoa hồng > Lãi (Trường hợp LỖ)**
- Doanh thu: 100M
- Chi phí: 60M
- Lãi: 40M
- Hoa hồng KH: 30M
- Hoa hồng người GT: 20M
- → **Tổng hoa hồng: 50M**
- → **Lãi ròng: 40M - 50M = -10M** ❌ (LỖ 10M!)
- → **Lãi ròng (%): (-10M / 100M) × 100 = -10%**

## Giao diện người dùng

### 1. Contract List (Danh sách hợp đồng)

Các cột mới được thêm vào:

| Tên cột | Mô tả | Hiển thị mặc định | Màu sắc |
|---------|-------|-------------------|---------|
| **HH cho KH** | Hoa hồng khách hàng | ❌ Ẩn | - |
| **HH người GT** | Hoa hồng người giới thiệu | ❌ Ẩn | - |
| **Tổng HH** | Tổng hoa hồng | ✅ Hiện | - |
| **Lãi ròng** | Lợi nhuận sau hoa hồng | ✅ Hiện | 🔴 Đỏ nếu < 0<br>🟢 Xanh nếu > 0 |
| **Lãi ròng (%)** | Tỷ lệ lợi nhuận ròng | ✅ Hiện | 🔴 Đỏ nếu < 0<br>🟢 Xanh nếu > 0 |

**Cách sử dụng**:
- Mở menu **Sales → Hợp đồng**
- Các cột được sắp xếp sau cột "Lãi (%)" và trước cột "Hợp đồng số"
- Click vào icon cột để show/hide các cột chi tiết (HH cho KH, HH người GT)

### 2. Sale Order Form (Form Sale Order)

Trong tab **"Hợp đồng"**, có section mới:

**Section: "Chi phí cho KH/Người giới thiệu"**
- Hoa hồng/Chi phí cho KH
- Hoa hồng người giới thiệu
- Tổng hoa hồng (readonly, tự động tính)

**Section: "Lãi ròng (sau khi trừ hoa hồng)"**
- Lãi ròng (readonly, tự động tính)
  - 🔴 Đỏ nếu âm
  - 🟢 Xanh nếu dương
- Lãi ròng (%) (readonly, tự động tính)
  - 🔴 Đỏ nếu âm
  - 🟢 Xanh nếu dương

**Cách sử dụng**:
1. Mở Sale Order
2. Vào tab **"Hợp đồng"**
3. Cuộn xuống phần "Chi phí cho KH/Người giới thiệu"
4. Nhập số tiền hoa hồng cho KH (nếu có)
5. Nhập số tiền hoa hồng cho người giới thiệu (nếu có)
6. Hệ thống tự động tính **Tổng hoa hồng** và **Lãi ròng**

## Luồng nghiệp vụ

### Kịch bản 1: Hợp đồng có hoa hồng cho người giới thiệu

1. Sales tạo quotation, confirm thành Sale Order
2. Sau khi có số hợp đồng, vào tab "Hợp đồng"
3. Nhập:
   - Hoa hồng người GT: 5,000,000 VND
4. Hệ thống tự động:
   - Tổng hoa hồng = 5,000,000
   - Lãi ròng = Lãi - 5,000,000
   - Cập nhật % lãi ròng
5. Xem kết quả trong Contract List

### Kịch bản 2: Hợp đồng có nhiều loại chi phí

1. Nhập:
   - Hoa hồng cho KH: 3,000,000 VND (chiết khấu thanh toán sớm)
   - Hoa hồng người GT: 2,000,000 VND
2. Hệ thống tự động:
   - Tổng hoa hồng = 5,000,000
   - Lãi ròng = Lãi - 5,000,000
3. Nếu Lãi ròng < 0 → Hiển thị màu đỏ (cảnh báo lỗ)

### Kịch bản 3: Kiểm tra lãi ròng trong Contract List

1. Mở menu **Sales → Hợp đồng**
2. Xem cột "Lãi ròng" và "Lãi ròng (%)"
3. Các hợp đồng có lãi ròng âm sẽ hiển thị màu đỏ
4. Click vào record để xem chi tiết hoa hồng

## Technical Implementation

### Model Changes (`sale_order.py`)

```python
# Compute methods
@api.depends('x_customer_commission', 'x_referrer_commission')
def _compute_total_commission(self):
    for order in self:
        order.x_total_commission = (order.x_customer_commission or 0.0) + (order.x_referrer_commission or 0.0)

@api.depends('x_profit', 'x_total_commission', 'x_revenue_actual')
def _compute_net_profit(self):
    for order in self:
        order.x_net_profit = order.x_profit - order.x_total_commission
        if order.x_revenue_actual:
            order.x_net_profit_margin = (order.x_net_profit / order.x_revenue_actual) * 100
        else:
            order.x_net_profit_margin = 0.0
```

### View Changes

**Contract List (`contract_list_views.xml`)**:
- Added 5 new columns with sum/avg aggregation
- Added color decorations for net profit

**Sale Order Form (`sale_order_views.xml`)**:
- Added commission section in Contract tab
- Added net profit section with color decorations

## Testing

Test script: `test_commission.py`

**Test cases**:
1. ✅ Customer commission only
2. ✅ Customer + Referrer commission
3. ✅ Commission > Profit (negative net profit)
4. ✅ Reset to zero

Run test:
```bash
python3 test_commission.py
```

## FAQ

**Q: Tại sao lãi ròng hiển thị màu đỏ?**
A: Vì tổng hoa hồng lớn hơn lãi → Sau khi trừ hoa hồng thì bị lỗ.

**Q: Lãi ròng khác gì với lãi thường?**
A:
- **Lãi** = Doanh thu - Chi phí (chưa trừ hoa hồng)
- **Lãi ròng** = Lãi - Hoa hồng (đã trừ hoa hồng)

**Q: Tôi có thể nhập hoa hồng âm không?**
A: Có, nhưng không khuyến khích. Nếu cần điều chỉnh, hãy sửa chi phí hợp đồng.

**Q: Khi nào nên nhập hoa hồng?**
A:
- Sau khi ký hợp đồng
- Khi có thỏa thuận hoa hồng với người giới thiệu
- Khi có chi phí đặc biệt cho khách hàng (chiết khấu, hỗ trợ, etc.)

**Q: Lãi ròng có được tính vào báo cáo tài chính không?**
A: Hiện tại chỉ dùng cho theo dõi nội bộ. Để tính toán chính xác, cần liên kết với module Accounting.

## Version History

- **v1.0.0** (2026-01-08): Initial implementation
  - Added commission tracking fields
  - Added net profit calculation
  - Added UI in Contract List and Sale Order form
  - Added test script
