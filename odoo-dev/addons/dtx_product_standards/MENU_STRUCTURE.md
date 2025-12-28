# DTX Product Standards - Menu Structure

## 📋 Cấu trúc Menu sau khi reorganize (v1.2.0)

### **INVENTORY APP**

```
INVENTORY
├─ Products
│   └─ Products (Odoo standard + DTX enhancements)
│       ├─ Form view có thêm:
│       │   ├─ Field "Loại sản phẩm DTX"
│       │   └─ Tab "DTX – Kiểm tra nhanh"
│       │
│       └─ Filter sẵn có:
│           ├─ Thiết bị Serial
│           ├─ Linh kiện
│           ├─ Kiosk
│           └─ Dịch vụ
│
├─ Configuration
│   ├─ Product Categories
│   ├─ Settings
│   └─ DTX - Công cụ ← NEW!
│       ├─ Mẫu BOM Kiosk
│       └─ Áp dụng chuẩn DTX (wizard)
```

### **MANUFACTURING APP**

```
MANUFACTURING
├─ Operations
│   └─ Manufacturing Orders
│
├─ Products
│   └─ Bills of Materials
│       → BOM được tạo tự động từ "Mẫu BOM Kiosk"
│
└─ Configuration
    └─ Settings
```

---

## 🎯 Workflow chính

### **1. Tạo sản phẩm**
```
Inventory > Products > Products > Create
→ Điền thông tin
→ Chọn "Loại sản phẩm DTX"
→ Save
```

### **2. Xem sản phẩm theo loại**
```
Inventory > Products > Products
→ Click filter:
   - "Thiết bị Serial" (mặc định)
   - "Linh kiện"
   - "Kiosk"
   - "Dịch vụ"
```

### **3. Tạo BOM Template (Simplified workflow)**
```
Inventory > Configuration > DTX - Công cụ > Mẫu BOM Kiosk
→ Create
→ Chọn sản phẩm Kiosk
→ Chọn đối tác gia công (nếu có)
→ Thêm components (linh kiện)
→ Save
→ Click "Tạo BOM"
```

### **4. Áp dụng chuẩn DTX hàng loạt**
```
Cách 1 - Từ menu:
  Inventory > Configuration > DTX - Công cụ > Áp dụng chuẩn DTX
  → Chọn tùy chọn
  → Áp dụng

Cách 2 - Từ danh sách sản phẩm:
  Inventory > Products > Products
  → Chọn sản phẩm (checkbox)
  → Action > Áp dụng chuẩn DTX
```

### **5. Xem BOM thực tế (Advanced)**
```
Manufacturing > Products > Bills of Materials
→ Tìm BOM đã được tạo từ Template
→ Check type = Subcontracting
→ Check subcontractor
```

---

## ✅ Lợi ích của cấu trúc mới

### **Trước đây (v1.1.0):**
- ❌ 2 menu Products (confusing)
- ❌ Menu "DTX – Chuẩn hóa dữ liệu" ở top-level
- ❌ User không biết dùng menu nào

### **Bây giờ (v1.2.0):**
- ✅ 1 menu Products duy nhất
- ✅ DTX features integrated vào Products standard
- ✅ "DTX - Công cụ" ở Configuration (đúng chỗ)
- ✅ Workflow rõ ràng, không duplicate

---

## 🔧 Technical Details

### **Menus đã xóa:**
- `menu_dtx_product_standards` (DTX – Chuẩn hóa dữ liệu)
- `menu_product_dtx` (Sản phẩm DTX)
- `action_product_template_dtx` (Action riêng cho Products DTX)

### **Menus mới:**
- `menu_dtx_tools` (DTX - Công cụ) - parent: stock.menu_stock_config_settings
- `menu_dtx_bom_template` (Mẫu BOM Kiosk) - parent: menu_dtx_tools
- `menu_apply_dtx_standards` (Áp dụng chuẩn DTX) - parent: menu_dtx_tools

### **Views giữ nguyên:**
- Product form view: Có field `x_dtx_type` và tab "DTX – Kiểm tra nhanh"
- Product tree view: Có column `x_dtx_type`
- Product search view: Có filters "Thiết bị Serial", "Linh kiện", "Kiosk", "Dịch vụ"

---

## 📝 Migration Notes

### **Nếu upgrade từ v1.1.0:**

1. **Menu cũ sẽ biến mất:**
   - "Inventory > DTX – Chuẩn hóa dữ liệu" → REMOVED
   - User phải dùng "Inventory > Products > Products" để xem sản phẩm

2. **Data KHÔNG bị mất:**
   - Sản phẩm đã tạo: Giữ nguyên
   - BOM Templates: Giữ nguyên
   - Field `x_dtx_type`: Giữ nguyên

3. **Bookmarks/Favorites:**
   - Nếu user đã bookmark "Sản phẩm DTX" → Bookmark sẽ broken
   - Hướng dẫn user tạo bookmark mới cho "Products" với filter

4. **Training:**
   - Hướng dẫn user workflow mới
   - Nhấn mạnh: Chỉ còn 1 menu Products duy nhất

---

## 💡 Tips & Best Practices

### **Tìm sản phẩm nhanh:**
```
1. Lưu filter làm Favorite:
   Inventory > Products > Products
   → Click filter "Thiết bị Serial"
   → "Save current search" → Đặt tên "DTX - Thiết bị Serial"
   → Next time: Click "Favorites" > "DTX - Thiết bị Serial"

2. Dùng Group By:
   → Group By > Loại sản phẩm DTX
   → Xem sản phẩm theo nhóm
```

### **Tạo BOM nhanh:**
```
1. Tạo Template một lần
2. Mỗi khi cần BOM mới → Duplicate Template
3. Sửa tên + components → Click "Tạo BOM"
```

---

**Last Updated:** 2025-12-28
**Version:** 1.2.0
