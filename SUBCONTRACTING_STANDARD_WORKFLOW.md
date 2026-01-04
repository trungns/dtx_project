# Quy trình Subcontracting Chuẩn của Odoo 16

## Tóm tắt
Odoo 16 đã có **sẵn** tính năng Resupply cho subcontracting trong module `mrp_subcontracting`.
**KHÔNG CẦN** tạo custom module để tự động hóa việc này.

## Workflow Chuẩn

### Bước 1: Cấu hình sản phẩm thành phẩm
Ví dụ: DTX-A17 Kiosk

1. Vào sản phẩm DTX-A17 Kiosk
2. Tab **Purchase**
3. ✅ Tick **"Resupply Subcontractor on Order"**

**Ý nghĩa**: Khi tạo PO cho sản phẩm này, Odoo sẽ tự động hiện nút "Resupply" để gửi components.

### Bước 2: Tạo Subcontracting BOM
1. Menu: Manufacturing → Products → Bills of Materials
2. Create BOM:
   - Product: DTX-A17 Kiosk
   - BOM Type: **Subcontracting**
   - Subcontractors: Chọn LGMEC
   - Components: Touch screen, Printer, Mini PC, Camera, CCCD Reader

### Bước 3: Tạo Purchase Order
1. Menu: Purchase → Orders → Purchase Orders → Create
2. Vendor: LGMEC
3. Add product: DTX-A17 Kiosk (qty: 3)
4. **Confirm Order**

→ Lúc này PO sẽ có **nút "Resupply"** ở góc trên

### Bước 4: Gửi components cho subcontractor
1. Click nút **"Resupply"** trên PO
2. Odoo tự động tạo **Delivery Order** với:
   - Destination: Partner/Vendors (LGMEC location)
   - Components: Touch x3, Printer x3, Mini PC x3, Camera x3, CCCD Reader x3
3. Assign serial numbers cho từng component
4. **Validate** delivery → Components đã gửi cho LGMEC

### Bước 5: Nhận thành phẩm
1. Quay lại PO, click nút **"Receipt"**
2. Nhận 3 Kiosk từ LGMEC
3. Assign serial numbers cho 3 Kiosk
4. **Validate** receipt

## Lưu ý quan trọng

### ✅ ĐÚNG: Dùng tính năng có sẵn của Odoo
- Tick "Resupply Subcontractor on Order" trên sản phẩm
- Odoo tự động tạo nút "Resupply"
- Click nút để tạo picking

### ❌ SAI: Tạo custom module
- ~~Tự động tạo Resupply picking khi confirm PO~~
- ~~Bypass workflow chuẩn của Odoo~~
- ~~Tạo duplicate logic không cần thiết~~

## Tại sao không cần custom module?

1. **Odoo đã có sẵn**: Module `mrp_subcontracting` đã handle toàn bộ workflow
2. **Linh hoạt hơn**: Người dùng quyết định khi nào gửi components (click nút Resupply)
3. **Chuẩn hóa**: Follow best practice của Odoo, dễ maintain
4. **Tránh lỗi**: Custom logic có thể tạo duplicate pickings hoặc sai flow

## Kết luận

Module `dtx_subcontracting_auto` đã được **XÓA** vì không cần thiết.
Workflow chuẩn của Odoo đã đủ và tốt hơn.
