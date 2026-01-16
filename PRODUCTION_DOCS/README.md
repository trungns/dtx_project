# DTX ODOO 16 - TÀI LIỆU PRODUCTION

**Phiên bản**: 2.1.0
**Ngày cập nhật**: 2026-01-13
**Môi trường**: Odoo 16.0 Community Edition

---

## 📋 MỤC LỤC DOCUMENTATION

### 01. [CÀI ĐẶT](01_INSTALLATION/)
Hướng dẫn cài đặt và deployment hệ thống lên production

- **[01_INSTALLATION_GUIDE.md](01_INSTALLATION/01_INSTALLATION_GUIDE.md)** - Hướng dẫn cài đặt Odoo 16 trên server
- **[02_MODULE_INSTALLATION.md](01_INSTALLATION/02_MODULE_INSTALLATION.md)** - Cài đặt các module DTX
- **[03_DATABASE_RESTORE.md](01_INSTALLATION/03_DATABASE_RESTORE.md)** - Khôi phục database từ backup
- **[WINDOWS_PRODUCTION_DEPLOYMENT.md](01_INSTALLATION/WINDOWS_PRODUCTION_DEPLOYMENT.md)** - **[MỚI]** Deployment đầy đủ lên Windows Server

### 02. [CẤU HÌNH](02_CONFIGURATION/)
Cấu hình ban đầu và chuẩn hóa dữ liệu

- **[00_MASTER_DATA_CHECKLIST.md](02_CONFIGURATION/00_MASTER_DATA_CHECKLIST.md)** - **[⭐ QUAN TRỌNG]** Checklist chuẩn hóa toàn bộ Master Data
- **[01_PRODUCT_STANDARDS.md](02_CONFIGURATION/01_PRODUCT_STANDARDS.md)** - Chuẩn hóa sản phẩm (5 loại DTX)
- **[02_VAT_CONFIGURATION.md](02_CONFIGURATION/02_VAT_CONFIGURATION.md)** - Cấu hình VAT & Thuế
- **[03_USER_PERMISSIONS.md](02_CONFIGURATION/03_USER_PERMISSIONS.md)** - Phân quyền người dùng
- **[04_INITIAL_DATA.md](02_CONFIGURATION/04_INITIAL_DATA.md)** - Nhập master data ban đầu
- **[05_SUBSCRIPTION_PRODUCTS.md](02_CONFIGURATION/05_SUBSCRIPTION_PRODUCTS.md)** - Cấu hình sản phẩm Subscription

### 03. [HƯỚNG DẪN SỬ DỤNG](03_USER_GUIDES/)
Hướng dẫn sử dụng cho từng bộ phận

- **[01_SALES_WORKFLOW.md](03_USER_GUIDES/01_SALES_WORKFLOW.md)** - Quy trình bán hàng (Quotation → SO → Invoice)
- **[02_PAKD_MANAGEMENT.md](03_USER_GUIDES/02_PAKD_MANAGEMENT.md)** - Quản lý Phương án kinh doanh
- **[03_INVENTORY_SERIAL_TRACKING.md](03_USER_GUIDES/03_INVENTORY_SERIAL_TRACKING.md)** - Quản lý Serial Numbers
- **[04_CONTRACT_COST_TRACKING.md](03_USER_GUIDES/04_CONTRACT_COST_TRACKING.md)** - Theo dõi chi phí hợp đồng
- **[05_AR_MANAGEMENT.md](03_USER_GUIDES/05_AR_MANAGEMENT.md)** - Quản lý công nợ khách hàng
- **[06_COMMISSION_TRACKING.md](03_USER_GUIDES/06_COMMISSION_TRACKING.md)** - Theo dõi hoa hồng KH/Người GT

### 04. [TÀI LIỆU KỸ THUẬT](04_TECHNICAL/)
Tài liệu kỹ thuật cho developers và admins

- **[01_MODULE_DTX_SERIAL_EXT.md](04_TECHNICAL/01_MODULE_DTX_SERIAL_EXT.md)** - Module Serial Extension
- **[02_MODULE_DTX_PRODUCT_STANDARDS.md](04_TECHNICAL/02_MODULE_DTX_PRODUCT_STANDARDS.md)** - Module Product Standards
- **[03_MODULE_DTX_SALES_PAKD_CONTRACT.md](04_TECHNICAL/03_MODULE_DTX_SALES_PAKD_CONTRACT.md)** - Module Sales PAKD Contract
- **[04_SERIAL_TRACKING_3_PATHS.md](04_TECHNICAL/04_SERIAL_TRACKING_3_PATHS.md)** - Chi tiết 3 đường tracking serial
- **[05_DATABASE_SCHEMA.md](04_TECHNICAL/05_DATABASE_SCHEMA.md)** - Database schema và custom fields
- **[COMMISSION_TRACKING.md](04_TECHNICAL/COMMISSION_TRACKING.md)** - Hệ thống theo dõi hoa hồng

### 05. [BẢO TRÌ](05_MAINTENANCE/)
Hướng dẫn bảo trì và troubleshooting

- **[01_BACKUP_RESTORE.md](05_MAINTENANCE/01_BACKUP_RESTORE.md)** - Backup và restore database
- **[02_MODULE_UPGRADE.md](05_MAINTENANCE/02_MODULE_UPGRADE.md)** - Nâng cấp module
- **[03_TROUBLESHOOTING.md](05_MAINTENANCE/03_TROUBLESHOOTING.md)** - Xử lý sự cố thường gặp
- **[04_PERFORMANCE_OPTIMIZATION.md](05_MAINTENANCE/04_PERFORMANCE_OPTIMIZATION.md)** - Tối ưu hiệu năng

---

## 🚀 QUICK START

### Cho Admin/IT

1. **Cài đặt hệ thống**: Đọc [01_INSTALLATION/](01_INSTALLATION/)
2. **⭐ Chuẩn hóa Master Data**: Đọc [02_CONFIGURATION/00_MASTER_DATA_CHECKLIST.md](02_CONFIGURATION/00_MASTER_DATA_CHECKLIST.md) - **BẮT BUỘC**
3. **Cấu hình ban đầu**: Đọc [02_CONFIGURATION/](02_CONFIGURATION/)
4. **Backup database**: Đọc [05_MAINTENANCE/01_BACKUP_RESTORE.md](05_MAINTENANCE/01_BACKUP_RESTORE.md)

### Cho Nhân viên Kinh doanh

1. **Quy trình bán hàng**: Đọc [03_USER_GUIDES/01_SALES_WORKFLOW.md](03_USER_GUIDES/01_SALES_WORKFLOW.md)
2. **Tạo và quản lý PAKD**: Đọc [03_USER_GUIDES/02_PAKD_MANAGEMENT.md](03_USER_GUIDES/02_PAKD_MANAGEMENT.md)
3. **Theo dõi hoa hồng**: Đọc [03_USER_GUIDES/06_COMMISSION_TRACKING.md](03_USER_GUIDES/06_COMMISSION_TRACKING.md)

### Cho Nhân viên Kho

1. **Quản lý Serial**: Đọc [03_USER_GUIDES/03_INVENTORY_SERIAL_TRACKING.md](03_USER_GUIDES/03_INVENTORY_SERIAL_TRACKING.md)
2. **Nhập xuất kho**: Đọc Odoo standard inventory documentation

### Cho Kế toán

1. **Quản lý công nợ**: Đọc [03_USER_GUIDES/05_AR_MANAGEMENT.md](03_USER_GUIDES/05_AR_MANAGEMENT.md)
2. **Theo dõi chi phí**: Đọc [03_USER_GUIDES/04_CONTRACT_COST_TRACKING.md](03_USER_GUIDES/04_CONTRACT_COST_TRACKING.md)

---

## 📦 MODULES OVERVIEW

### 1. dtx_serial_ext (v2.5.0)
**Chức năng**: Quản lý Serial Numbers nâng cao

**Tính năng chính**:
- ✅ Dual serial tracking (Supplier + DTX Internal)
- ✅ Lifecycle state tự động (Stock → Delivered → Installed)
- ✅ Component state inheritance (linh kiện thừa hưởng trạng thái từ thành phẩm)
- ✅ Sale order auto-linking (linh kiện tự động link với SO của thành phẩm)
- ✅ **[MỚI]** MISA external invoice number tracking
- ✅ Vendor invoice state tự động
- ✅ Customer invoice state tự động
- ✅ Serial tracking qua 3 đường (Direct, Picking, Production)
- ✅ Warranty management

**User Guide**: [03_USER_GUIDES/03_INVENTORY_SERIAL_TRACKING.md](03_USER_GUIDES/03_INVENTORY_SERIAL_TRACKING.md)
**Technical Doc**: [04_TECHNICAL/01_MODULE_DTX_SERIAL_EXT.md](04_TECHNICAL/01_MODULE_DTX_SERIAL_EXT.md)

---

### 2. dtx_product_standards (v1.1.0)
**Chức năng**: Chuẩn hóa danh mục sản phẩm

**Tính năng chính**:
- ✅ 4 loại sản phẩm DTX (Device Serial, Component, Kiosk, Service)
- ✅ Checklist kiểm tra cấu hình sản phẩm
- ✅ Wizard áp dụng chuẩn hàng loạt
- ✅ BOM Template cho Kiosk manufacturing
- ✅ Subcontracting support

**User Guide**: [02_CONFIGURATION/01_PRODUCT_STANDARDS.md](02_CONFIGURATION/01_PRODUCT_STANDARDS.md)
**Technical Doc**: [04_TECHNICAL/02_MODULE_DTX_PRODUCT_STANDARDS.md](04_TECHNICAL/02_MODULE_DTX_PRODUCT_STANDARDS.md)

---

### 3. dtx_sales_pakd_contract (v1.5.0)
**Chức năng**: Quản lý PAKD và Hợp đồng

**Tính năng chính**:
- ✅ PAKD (Phương án kinh doanh) - so sánh nhiều phương án
- ✅ Apply PAKD vào Sale Order với wizard
- ✅ **[MỚI]** Contract Cost Profit Analysis (phân tích lợi nhuận theo từng dòng)
- ✅ Auto-populate purchase price from PO (tự động lấy giá mua)
- ✅ Line-by-line profit & margin calculation
- ✅ Color coding for quick profit assessment
- ✅ AR (Accounts Receivable) tracking
- ✅ Lifecycle State (7 trạng thái từ quotation → paid)
- ✅ Commission Tracking (hoa hồng KH/Người giới thiệu)
- ✅ Advance Payment Tracking (tạm ứng)
- ✅ Net Profit Calculation (lãi ròng sau hoa hồng)

**User Guides**:
- [03_USER_GUIDES/01_SALES_WORKFLOW.md](03_USER_GUIDES/01_SALES_WORKFLOW.md)
- [03_USER_GUIDES/02_PAKD_MANAGEMENT.md](03_USER_GUIDES/02_PAKD_MANAGEMENT.md)
- [03_USER_GUIDES/04_CONTRACT_COST_TRACKING.md](03_USER_GUIDES/04_CONTRACT_COST_TRACKING.md)
- [03_USER_GUIDES/05_AR_MANAGEMENT.md](03_USER_GUIDES/05_AR_MANAGEMENT.md)
- [03_USER_GUIDES/06_COMMISSION_TRACKING.md](03_USER_GUIDES/06_COMMISSION_TRACKING.md)

**Technical Doc**: [04_TECHNICAL/03_MODULE_DTX_SALES_PAKD_CONTRACT.md](04_TECHNICAL/03_MODULE_DTX_SALES_PAKD_CONTRACT.md)

---

## 🏢 HỆ THỐNG QUẢN LÝ HÀNG ĐỢI THÔNG MINH

DTX Odoo 16 được thiết kế cho công ty DTX - chuyên cung cấp giải pháp hàng đợi thông minh (Queue Management System) bao gồm:

### Sản phẩm chính
- **Kiosk tự phục vụ** (Self-service Kiosk)
- **Màn hình LED** (LED Display)
- **Thiết bị xếp hàng** (Queue Management Hardware)

### Quy trình kinh doanh
```
Quotation → PAKD (so sánh giá) → Confirm SO → Mua linh kiện
→ Lắp ráp (nội bộ hoặc thuê ngoài) → Triển khai tại site
→ Nghiệm thu → Invoice → Thu tiền → Bảo trì
```

### Đặc thù
- Sản phẩm có **Serial Number** cần tracking chi tiết
- Lắp ráp từ **nhiều linh kiện** (BoM)
- Có thể **gia công thuê ngoài** (Subcontracting)
- Cần theo dõi **chi phí hợp đồng** vs **PAKD dự kiến**
- Quản lý **công nợ khách hàng** (AR)
- Theo dõi **hoa hồng** cho KH và người giới thiệu

---

## ⚙️ HỆ THỐNG YÊU CẦU

### Server Requirements (Production)
- **OS**: Ubuntu 22.04 LTS (khuyến nghị) hoặc CentOS 8+
- **CPU**: 4 cores minimum, 8 cores khuyến nghị
- **RAM**: 8GB minimum, 16GB khuyến nghị
- **Disk**: 100GB SSD minimum
- **Database**: PostgreSQL 15

### Development Environment
- **Docker**: Latest version
- **Docker Compose**: v2.x
- **OS**: macOS, Linux, hoặc Windows với WSL2

---

## 🔐 BẢO MẬT & PHÂN QUYỀN

Hệ thống có 4 nhóm quyền chính:

1. **CEO / Sales Director / Chief Accountant**: Full access tất cả
2. **Sales User**: Chỉ xem/sửa own records
3. **Inventory Manager**: Quản lý kho và serial
4. **Account User**: Read-only tài chính

Chi tiết: [02_CONFIGURATION/03_USER_PERMISSIONS.md](02_CONFIGURATION/03_USER_PERMISSIONS.md)

---

## 📞 HỖ TRỢ

### Vấn đề kỹ thuật
1. Kiểm tra [05_MAINTENANCE/03_TROUBLESHOOTING.md](05_MAINTENANCE/03_TROUBLESHOOTING.md)
2. Xem logs: `docker-compose logs -f odoo`
3. Liên hệ DTX Dev Team

### Đào tạo sử dụng
- Đọc [03_USER_GUIDES/](03_USER_GUIDES/) theo vai trò công việc
- Request training session với Admin

### Yêu cầu tính năng mới
- Tạo ticket nội bộ hoặc liên hệ Product Owner

---

## 📝 CHANGELOG

### Version 2.1.0 (2026-01-13)
**Production Deployment & MISA Integration**

- ✅ **[MỚI]** Windows Production Deployment Guide đầy đủ
- ✅ **[MỚI]** MISA External Invoice Number Tracking (dtx_serial_ext v2.5.0)
- ✅ Contract Cost Profit Analysis (dtx_sales_pakd_contract v1.5.0)
- ✅ Component Sale Order Auto-linking (dtx_serial_ext v2.4.2)
- ✅ Component Lifecycle State Inheritance fix (dtx_serial_ext v2.4.1)
- ✅ Merge docs folder vào PRODUCTION_DOCS
- ✅ Detailed fix documentation in PRODUCTION_DOCS/fixes/

### Version 2.0.0 (2026-01-09)
**Consolidated Documentation Release**

- ✅ Tổ chức lại toàn bộ documentation theo cấu trúc chuẩn
- ✅ Tách riêng Installation, Configuration, User Guides, Technical, Maintenance
- ✅ Loại bỏ files rác và test scripts không cần thiết
- ✅ Cập nhật tài liệu Commission Tracking
- ✅ Cập nhật tài liệu Advance Payment
- ✅ Production-ready documentation cho deployment

### Version 1.4.0 (2026-01-08)
- ✅ Feature: Commission Tracking cho KH/Người giới thiệu
- ✅ Feature: Advance Payment Tracking
- ✅ Feature: Net Profit Calculation
- ✅ All modules upgraded và tested

### Version 1.3.0 (2026-01-05)
- ✅ Fixed PAKD formulas to match Excel template
- ✅ Feature: AR (Accounts Receivable) Tracking
- ✅ Feature: Lifecycle State (7 states)
- ✅ Feature: Serial Tracking via 3 Paths (Direct, Picking, Production)
- ✅ Feature: Customer Invoice State Tracking

---

**DTX Odoo 16 Production Documentation**
**Copyright © 2026 DTX - Smart Queue Management Systems**
**Built with Odoo 16 Community Edition**
