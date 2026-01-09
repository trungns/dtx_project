# Chi tiết 3 đường tracking Serial Numbers

## Tổng quan vấn đề

Khi bán hàng trong Odoo, cần tracking được **serial number nào được bán cho đơn hàng nào**. Tuy nhiên, có nhiều tình huống khác nhau:

1. **Bán sản phẩm đơn lẻ** (ví dụ: bán 1 cái TV)
2. **Bán kit/combo** (ví dụ: bán 1 bộ gồm TV + Speaker)
3. **Bán sản phẩm sản xuất từ BoM** (ví dụ: bán KIOSK được lắp ráp từ nhiều linh kiện)

Mỗi tình huống cần một cách tracking khác nhau → **3 Paths**

---

## PATH 1: Direct SO Line - Bán sản phẩm đơn lẻ

### Khi nào dùng?
Khi bán **sản phẩm đơn lẻ** có serial, sản phẩm được ghi trực tiếp vào dòng Sale Order.

### Ví dụ thực tế: Bán TV1
```
Sale Order S00155 có dòng:
- [UA98DU9000] Samsung TV x 1
```

### Luồng dữ liệu:
```
1. Sale Order S00155
   └─ Sale Order Line: Samsung TV x 1
      └─ Stock Move: Samsung TV (sale_line_id = SO line trên)
         └─ Stock Move Line: Serial = TV1
```

### Cách tracking:
```python
# Tìm serial TV1
serial = TV1

# Path 1: Đi từ serial → move → sale_line_id → sale_order
serial.move_lines.move_id.sale_line_id.order_id
# Kết quả: S00155 ✅
```

### Đặc điểm:
- ✅ Đơn giản nhất
- ✅ Mối quan hệ trực tiếp: Serial → Move → SO Line → SO
- ✅ Field `sale_line_id` được populate tự động bởi Odoo

### Kết quả:
```
TV1 → S00155 (Direct)
```

---

## PATH 2: Via Picking Sale ID - Bán Kit/Combo

### Khi nào dùng?
Khi bán **kit hoặc combo** (product type = 'consu' + BoM type = 'kit'), các components được **deliver cùng lúc** trong cùng một picking.

### Ví dụ giả định: Bán COMBO-01 (TV + Speaker)
```
Sale Order S00200 có dòng:
- COMBO-01 (TV + Speaker kit) x 1

BoM của COMBO-01:
- Samsung TV x 1
- Speaker X2 x 1
```

### Luồng dữ liệu:
```
1. Sale Order S00200
   └─ Sale Order Line: COMBO-01 x 1
      └─ Stock Picking WH/OUT/00100 (sale_id = S00200)
         ├─ Stock Move Line: TV serial = TV-KIT-001 (❌ KHÔNG có sale_line_id)
         └─ Stock Move Line: Speaker serial = SPK-KIT-001 (❌ KHÔNG có sale_line_id)
```

### Vấn đề:
```
TV-KIT-001.move_id.sale_line_id = False ❌
→ Path 1 không work!
```

**Tại sao?** Vì trong kit, components không phải là dòng Sale Order độc lập. Chỉ có COMBO-01 là dòng SO, còn TV và Speaker là components tự động unbundle khi deliver.

### Cách tracking:
```python
# Tìm serial TV-KIT-001
serial = TV-KIT-001

# Path 1 thất bại vì không có sale_line_id
serial.move_lines.move_id.sale_line_id  # = False ❌

# Path 2: Đi qua picking
serial.move_lines.picking_id.sale_id
# Kết quả: S00200 ✅
```

### Đặc điểm:
- ✅ Dùng cho kit/combo
- ✅ Components được deliver cùng lúc trong cùng picking
- ✅ Picking có field `sale_id` trỏ về Sale Order
- ⚠️ Components không có `sale_line_id` riêng

### Kết quả:
```
TV-KIT-001 → S00200 (Via Picking)
SPK-KIT-001 → S00200 (Via Picking)
```

---

## PATH 3: Via Production Order - Sản xuất/Lắp ráp

### Khi nào dùng?
Khi bán **sản phẩm được sản xuất** (manufactured product) từ BoM, các components được **consumed trong quá trình sản xuất**, KHÔNG được deliver trực tiếp.

### Ví dụ thực tế: Bán KIOSK10

#### Bước 1: Cấu trúc BoM
```
Product: KIOSK10 [DTX-A17]
BoM Type: Subcontracting (hoặc Manufacture)

Components (consumed):
- Touchscreen 17" x 1
- Mini PC x 1
- Máy in nhiệt x 1
```

#### Bước 2: Sale Order
```
Sale Order: S00155
Dòng SO: KIOSK10 x 1
```

#### Bước 3: Production Order (Sản xuất)
```
Production Order: WH/SBC/00004
Product to produce: KIOSK10
Qty: 1
Serial: KIOSK10

Components consumed (raw materials):
- Touchscreen10 (serial)
- MiniPC10 (serial)
- MáyIn1 (serial)
```

#### Bước 4: Delivery
```
Stock Picking: WH/OUT/00017 (sale_id = S00155)
Move Line: KIOSK10 serial (✅ có sale_line_id)
```

### Luồng dữ liệu đầy đủ:

```
1. Components được consume trong production:
   Touchscreen10 → Production WH/SBC/00004 (consumed)
   MiniPC10 → Production WH/SBC/00004 (consumed)
   MáyIn1 → Production WH/SBC/00004 (consumed)

2. Production tạo ra finished product:
   Production WH/SBC/00004 → KIOSK10 serial

3. Finished product được deliver:
   KIOSK10 serial → WH/OUT/00017 (sale_id = S00155)
```

### Vấn đề:
```
# MiniPC10 không được deliver trực tiếp!
MiniPC10.move_lines → Chỉ có moves từ:
  - WH/IN/00021 (Receipt - nhập hàng)
  - WH/RES/00002 (Resupply - chuyển kho)
  - WH/SBC/00004 (Production - consumed) ← Đây!

MiniPC10.move_lines.move_id.sale_line_id = False ❌
MiniPC10.move_lines.picking_id.sale_id = False ❌
→ Path 1 và Path 2 đều không work!
```

**Tại sao?** Vì MiniPC10 không được **deliver** ra khỏi kho. Nó được **consumed** (tiêu thụ) trong quá trình sản xuất KIOSK10. Khi KIOSK10 được giao cho khách hàng, MiniPC10 đã nằm bên trong KIOSK10 rồi!

### Cách tracking (Path 3):

```python
# Bước 1: Tìm serial MiniPC10
serial = MiniPC10

# Bước 2: Tìm production order đã consume serial này
move_lines = serial.move_lines  # 3 moves
consumed_move = move_lines.filtered(lambda m: m.raw_material_production_id)
# → Move WH/SBC/00004 với raw_material_production_id = Production WH/SBC/00004

production = consumed_move.raw_material_production_id
# → Production Order: WH/SBC/00004

# Bước 3: Tìm finished product serial từ production
finished_serial = production.lot_producing_id
# → KIOSK10 serial

# Bước 4: Tìm sale order của finished product
# Dùng Path 1 hoặc Path 2 cho finished product
finished_serial.move_lines.picking_id.sale_id
# → S00155 ✅
```

### Code implementation:
```python
def _compute_sale_orders(self):
    for lot in self:
        sale_orders = self.env['sale.order']

        # ... Path 1 & 2 ...

        # Path 3: Via production order
        move_lines = self.env['stock.move.line'].search([('lot_id', '=', lot.id)])

        # Tìm moves có raw_material_production_id (consumed in production)
        consumed_moves = move_lines.mapped('move_id').filtered(
            lambda m: m.raw_material_production_id
        )

        for move in consumed_moves:
            production = move.raw_material_production_id
            finished_lot = production.lot_producing_id  # Serial của sản phẩm hoàn thiện

            if finished_lot:
                # Tìm sale orders của finished product
                finished_move_lines = self.env['stock.move.line'].search([
                    ('lot_id', '=', finished_lot.id)
                ])

                # Path 3a: Finished product có sale_line_id
                if 'sale_line_id' in self.env['stock.move']._fields:
                    finished_so_lines = finished_move_lines.mapped('move_id.sale_line_id')
                    sale_orders |= finished_so_lines.mapped('order_id')

                # Path 3b: Finished product qua picking
                if 'sale_id' in self.env['stock.picking']._fields:
                    finished_pickings = finished_move_lines.mapped('picking_id')
                    sale_orders |= finished_pickings.mapped('sale_id')

        lot.sale_order_ids = sale_orders
```

### Đặc điểm:
- ✅ Dùng cho sản phẩm manufactured/subcontracting
- ✅ Components bị consumed, KHÔNG được deliver
- ✅ Tracking qua production chain
- ✅ Hỗ trợ multi-level BoM (recursive)
- ⚠️ Phức tạp hơn Path 1 & 2

### Kết quả:
```
MiniPC10 → Production WH/SBC/00004 → KIOSK10 → S00155
Touchscreen10 → Production WH/SBC/00004 → KIOSK10 → S00155
MáyIn1 → Production WH/SBC/00004 → KIOSK10 → S00155
```

---

## So sánh 3 Paths

| Tiêu chí | Path 1 | Path 2 | Path 3 |
|----------|--------|--------|--------|
| **Tình huống** | Bán đơn lẻ | Kit/Combo | Sản xuất/Lắp ráp |
| **Components** | Không có | Deliver cùng | Consumed |
| **sale_line_id** | ✅ Có | ❌ Không | ❌ Không |
| **picking.sale_id** | ✅ Có | ✅ Có | ❌ Không (component) |
| **Production** | Không | Không | ✅ Có |
| **Độ phức tạp** | Thấp | Trung bình | Cao |

---

## Ví dụ tổng hợp: Sale Order S00155

### Sản phẩm được bán:
1. **KIOSK10** x 1 (manufactured product)
2. **TV1** x 1 (simple product)
3. **LED10** x 1 (simple product)
4. **Speaker0** x 1 (simple product)

### Tracking results:

#### Path 1 (Direct):
```
✅ TV1 → S00155
   TV1.move_lines.move_id.sale_line_id.order_id = S00155

✅ LED10 → S00155
   LED10.move_lines.move_id.sale_line_id.order_id = S00155

✅ Speaker0 → S00155
   Speaker0.move_lines.move_id.sale_line_id.order_id = S00155

✅ KIOSK10 → S00155
   KIOSK10.move_lines.move_id.sale_line_id.order_id = S00155
```

#### Path 3 (Production Chain):
```
✅ MiniPC10 → S00155
   MiniPC10 → Production WH/SBC/00004 → KIOSK10 → S00155

✅ Touchscreen10 → S00155
   Touchscreen10 → Production WH/SBC/00004 → KIOSK10 → S00155

✅ MáyIn1 → S00155
   MáyIn1 → Production WH/SBC/00004 → KIOSK10 → S00155
```

### Kết quả cuối:
**7 serials được tracking về S00155:**
1. KIOSK10 (Path 1 - sản phẩm chính)
2. MiniPC10 (Path 3 - component của KIOSK10)
3. Touchscreen10 (Path 3 - component của KIOSK10)
4. MáyIn1 (Path 3 - component của KIOSK10)
5. TV1 (Path 1 - sản phẩm đơn)
6. LED10 (Path 1 - sản phẩm đơn)
7. Speaker0 (Path 1 - sản phẩm đơn)

---

## Tại sao cần Path 3?

### Trước khi có Path 3:
```
KIOSK10 → S00155 ✅ (tracking được)
MiniPC10 → ❌ (KHÔNG tracking được)
Touchscreen10 → ❌ (KHÔNG tracking được)
```

**Vấn đề:** Không biết serial nào của MiniPC và Touchscreen đã được bán cho khách hàng nào!

### Sau khi có Path 3:
```
KIOSK10 → S00155 ✅
MiniPC10 → S00155 ✅ (via production chain)
Touchscreen10 → S00155 ✅ (via production chain)
```

**Lợi ích:**
1. ✅ **Full traceability**: Biết chính xác serial nào được bán cho đơn hàng nào
2. ✅ **Warranty tracking**: Biết warranty của component nào thuộc về khách hàng nào
3. ✅ **Quality control**: Nếu có lỗi, tìm được tất cả đơn hàng có component bị lỗi
4. ✅ **Invoice matching**: Biết serial nào đã invoice cho khách hàng nào

---

## Câu hỏi thường gặp

### Q1: Path 2 và Path 3 khác nhau thế nào?

**Path 2 (Kit):**
- Components được **deliver** cùng lúc trong cùng picking
- Components VẪN TỒN TẠI dưới dạng items riêng lẻ khi đến tay khách
- Ví dụ: Bán combo gồm TV + Speaker, khách nhận được 2 thứ riêng biệt

**Path 3 (Production):**
- Components bị **consumed** trong quá trình sản xuất
- Components KHÔNG TỒN TẠI riêng lẻ nữa, đã trở thành PART của finished product
- Ví dụ: Bán KIOSK, khách chỉ nhận được KIOSK (MiniPC và Touchscreen đã nằm bên trong)

### Q2: Nếu có multi-level BoM thì sao?

Ví dụ:
```
KIOSK (Level 3)
├─ Assembly A (Level 2)
│  ├─ Component X (Level 1)
│  └─ Component Y (Level 1)
└─ Assembly B (Level 2)
   └─ Component Z (Level 1)
```

Path 3 sẽ tracking **recursively**:
- Component X → Assembly A → KIOSK → Sale Order
- Component Y → Assembly A → KIOSK → Sale Order
- Component Z → Assembly B → KIOSK → Sale Order

### Q3: Nếu component không có serial thì sao?

Path 3 chỉ tracking được serial numbers. Nếu component không có serial (tracked by lot or none), thì:
- ❌ Không tracking được cụ thể unit nào
- ✅ Nhưng vẫn biết product type nào được dùng trong production

---

## Kết luận

**Path 3** là innovation quan trọng nhất trong implementation này vì:

1. ✅ **Giải quyết vấn đề thực tế**: Tracking components trong sản phẩm manufactured
2. ✅ **Full traceability**: Không để sót serial nào
3. ✅ **Production chain aware**: Hiểu được manufacturing workflow của Odoo
4. ✅ **Scalable**: Support multi-level BoM

Với 3 paths kết hợp, giờ bạn có thể tracking **100% serials** trong mọi tình huống bán hàng!
