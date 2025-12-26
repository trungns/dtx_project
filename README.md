# DTX Odoo 16 - Queue Management System

Hệ thống quản lý hàng đợi thông minh cho DTX trên nền tảng Odoo 16 Community.

## 📦 Modules

### 1. **dtx_serial_ext** (v2.2.0)
Serial number tracking với quản lý vendor invoice tự động.

**Tính năng:**
- ✅ Lifecycle state tracking (In Stock, Delivered, Installed, etc.)
- ✅ Automatic vendor invoice state (Missing/Linked/Replaced)
- ✅ Replacement invoice support cho edge cases
- ✅ Many2many relationships đến PO/SO/Bills
- ✅ Auto-update khi bill posted/cancelled

**Location:** `/odoo-dev/addons/dtx_serial_ext/`

### 2. **dtx_product_standards** (v1.1.0)
Chuẩn hóa danh mục sản phẩm & BOM template cho Kiosk.

**Tính năng:**
- ✅ 4 loại sản phẩm DTX (Device Serial, Component, Kiosk, Service)
- ✅ Checklist tab kiểm tra cấu hình
- ✅ Wizard áp dụng chuẩn hàng loạt
- ✅ BOM Template cho Kiosk manufacturing (Excel-style)
- ✅ Subcontracting support (basic)

**Location:** `/odoo-dev/addons/dtx_product_standards/`

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Git
- 8GB RAM minimum

### Setup (macOS/Linux)
```bash
# Clone repository
git clone https://github.com/trungns/dtx_project.git
cd dtx_project/odoo-dev

# Start Odoo
./start.sh

# Access Odoo
# URL: http://localhost:8069
# Database: dtx_dev
# User: admin / Password: admin
```

### Setup (Windows)
```powershell
# Clone repository
git clone https://github.com/trungns/dtx_project.git
cd dtx_project\odoo-dev

# Start Odoo
docker-compose up -d

# Access Odoo
# URL: http://localhost:8069
# Database: dtx_dev
# User: admin / Password: admin
```

## 📚 Documentation

- **[START HERE](docs/START_HERE.md)** - Bắt đầu từ đây
- **[Architecture](docs/architecture/)** - Kiến trúc hệ thống
- **[User Guide](docs/user-guide/)** - Hướng dẫn sử dụng
- **[Developer Guide](docs/developer-guide/)** - Hướng dẫn phát triển
- **[Deployment](docs/deployment/)** - Hướng dẫn deploy production

## 🔧 Development

### Install Modules
```bash
# In Odoo UI: Apps > Update Apps List
# Search "DTX" > Install modules

# Or via command line:
docker-compose exec web odoo -d dtx_dev -i dtx_serial_ext,dtx_product_standards --stop-after-init
```

### Upgrade Modules
```bash
./upgrade-module.sh dtx_serial_ext
./upgrade-module.sh dtx_product_standards
```

### View Logs
```bash
./logs.sh
# Or: docker-compose logs -f web
```

## 📂 Project Structure

```
dtx_project/
├── docs/                           # Documentation
│   ├── START_HERE.md              # Bắt đầu từ đây
│   ├── architecture/              # System architecture
│   ├── user-guide/                # User documentation
│   ├── developer-guide/           # Developer docs
│   └── deployment/                # Deployment guides
│
├── odoo-dev/                      # Development environment
│   ├── docker-compose.yml         # Docker setup
│   ├── config/odoo.conf          # Odoo configuration
│   ├── addons/                    # Custom addons
│   │   ├── dtx_serial_ext/       # Serial tracking module
│   │   └── dtx_product_standards/ # Product standards module
│   └── scripts/                   # Helper scripts
│
└── dtx_serial_ext/                # Standalone module (for production)
    └── [same as odoo-dev/addons/dtx_serial_ext]
```

## 🛠️ Tech Stack

- **Odoo:** 16.0 Community
- **Python:** 3.10
- **PostgreSQL:** 15
- **Docker:** Latest
- **OS:** Ubuntu 22.04 (in Docker)

## 🎯 Modules Overview

### dtx_serial_ext
Track từng serial number với lifecycle state và vendor invoice state tự động.

**Use cases:**
- Quản lý Touch screen, Mini PC, Máy in theo serial
- Tự động link vendor bill khi nhập kho
- Track lifecycle: Stock → Delivered → Installed
- Support replacement invoice cho edge cases

### dtx_product_standards
Chuẩn hóa dữ liệu sản phẩm, giảm sai sót, chuẩn bị cho manufacturing.

**Use cases:**
- Phân loại 4 loại sản phẩm DTX
- Check cấu hình sản phẩm (Serial tracking, AVCO, BOM)
- Áp dụng chuẩn hàng loạt qua wizard
- Tạo BOM cho Kiosk manufacturing

## 📝 Version History

### Current Versions
- **dtx_serial_ext:** 2.2.0 (2025-12-25)
- **dtx_product_standards:** 1.1.0 (2025-12-25)

See [CHANGELOG](docs/CHANGELOG.md) for detailed version history.

## 🤝 Contributing

Development workflow:
1. Create feature branch from `main`
2. Make changes in `/odoo-dev/addons/`
3. Test locally
4. Commit with clear message
5. Create Pull Request

## 📞 Support

- **Documentation:** [docs/](docs/)
- **Issues:** [GitHub Issues](https://github.com/trungns/dtx_project/issues)
- **Email:** trungns@dtx.com

## 📄 License

LGPL-3 - See individual modules for details.

---

**DTX Project**
Built with Odoo 16 Community | Generated with [Claude Code](https://claude.com/claude-code)
