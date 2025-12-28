# ⚡ DTX PROJECT - QUICK START GUIDE

## 🚀 **TRÊN MACBOOK M1 (Công ty)**

### **1. Setup lần đầu (5 phút)**
```bash
# Clone repo
git clone https://github.com/trungns/dtx_project.git
cd dtx_project/odoo-dev

# Start Odoo
docker-compose up -d

# Auto-create data
docker-compose exec odoo python3 /mnt/extra-addons/../scripts/setup_dtx_data.py

# Open Odoo
open http://localhost:8069
# Login: admin / admin
```

### **2. Làm việc hàng ngày**
```bash
# Start Odoo
cd ~/Projects/dtx_project/odoo-dev
docker-compose up -d

# Pull code mới nhất (nếu đã code ở nhà)
git pull origin main
docker-compose restart odoo

# ... Code code code ...

# Commit & Push (cuối ngày)
git add .
git commit -m "work: Your changes"
git push origin main
```

---

## 💻 **TRÊN WINDOWS (Nhà)**

### **1. Làm việc hàng ngày**
```powershell
# Start Odoo
cd D:\trungns\dtx_project\odoo-dev
docker-compose up -d

# Pull code mới nhất (nếu đã code ở công ty)
git pull origin main
docker-compose restart odoo

# ... Code code code ...

# Upgrade module sau khi sửa code
.\upgrade-module.ps1 dtx_product_standards

# Commit & Push (cuối ngày)
git add .
git commit -m "work: Your changes"
git push origin main
```

---

## 📋 **COMMON TASKS**

### **Xem logs**
```bash
docker-compose logs -f odoo
```

### **Restart Odoo**
```bash
docker-compose restart odoo
```

### **Stop Odoo**
```bash
docker-compose down
```

### **Upgrade module**
```bash
# Mac:
./upgrade-module.sh dtx_product_standards

# Windows:
.\upgrade-module.ps1 dtx_product_standards
```

### **Access Odoo shell**
```bash
docker-compose exec odoo odoo shell -d dtx_dev
```

---

## 🎯 **MENU LOCATIONS (v1.2.0)**

```
📁 INVENTORY
  ├─ 📦 Products
  │   └─ Products ← Tất cả sản phẩm ở đây
  │
  └─ ⚙️ Configuration
      └─ 🔧 DTX - Công cụ
          ├─ Mẫu BOM Kiosk
          └─ Áp dụng chuẩn DTX

📁 MANUFACTURING
  └─ 📦 Products
      └─ Bills of Materials ← BOM thực tế
```

---

## 🔧 **WORKFLOW CHÍNH**

### **1. Tạo sản phẩm**
```
Inventory > Products > Products > Create
→ Loại sản phẩm DTX: [Chọn loại]
→ Save
```

### **2. Tạo BOM Template**
```
Inventory > Configuration > DTX - Công cụ > Mẫu BOM Kiosk
→ Create
→ Chọn Kiosk + Đối tác gia công + Components
→ Click "Tạo BOM"
```

### **3. Subcontracting (Gia công)**
```
Purchase > Orders > Create
→ Vendor: LGMEC
→ Product: Kiosk DTX-A17, Qty: 3
→ Confirm
→ Delivery: Assign serial linh kiện → Validate
→ Receipt: Assign serial Kiosk → Validate
```

---

## 📚 **FULL DOCS**

- **MacBook Setup:** [MACBOOK_SETUP.md](MACBOOK_SETUP.md)
- **Windows Setup:** [WINDOWS_SETUP.md](WINDOWS_SETUP.md)
- **Session Summary:** [SESSION_SUMMARY_2025-12-28.md](SESSION_SUMMARY_2025-12-28.md)
- **Menu Structure:** [odoo-dev/addons/dtx_product_standards/MENU_STRUCTURE.md](odoo-dev/addons/dtx_product_standards/MENU_STRUCTURE.md)

---

## 🆘 **TROUBLESHOOTING**

### **Port 8069 đã được dùng**
```bash
# Mac:
lsof -i :8069
kill -9 <PID>

# Windows:
netstat -ano | findstr :8069
taskkill /PID <PID> /F
```

### **Module không upgrade**
```bash
# Clear cache
docker-compose exec odoo find /mnt/extra-addons -type d -name __pycache__ -exec rm -rf {} +
docker-compose restart odoo
```

### **Git conflict**
```bash
git stash
git pull origin main
git stash pop
# Resolve conflicts → git add . → git commit
```

---

**Last Updated:** 2025-12-28
**Version:** dtx_product_standards v1.2.0
**Repo:** https://github.com/trungns/dtx_project
