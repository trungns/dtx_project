# 🍎 DTX Project - MacBook Air M1 Setup Guide

## 📋 **Tổng quan**

Hướng dẫn setup DTX Odoo 16 project trên **MacBook Air M1** (Apple Silicon)

**Repository:** https://github.com/trungns/dtx_project

---

## ⚡ **QUICK START - 5 phút**

### **Bước 1: Cài đặt Prerequisites**

```bash
# 1. Install Homebrew (nếu chưa có)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Install Git
brew install git

# 3. Install Docker Desktop for Mac (Apple Silicon)
# Download from: https://www.docker.com/products/docker-desktop
# Hoặc dùng Homebrew:
brew install --cask docker

# 4. Mở Docker Desktop app và đợi Docker chạy
open -a Docker
```

---

### **Bước 2: Clone Repository**

```bash
# Tạo thư mục làm việc
mkdir -p ~/Projects
cd ~/Projects

# Clone repository
git clone https://github.com/trungns/dtx_project.git
cd dtx_project
```

---

### **Bước 3: Khởi động Odoo**

```bash
cd odoo-dev

# Pull Docker images (lần đầu sẽ mất 5-10 phút)
docker-compose pull

# Khởi động containers
docker-compose up -d

# Xem logs (optional)
docker-compose logs -f odoo
# Nhấn Ctrl+C để thoát logs
```

---

### **Bước 4: Truy cập Odoo**

```bash
# Mở browser
open http://localhost:8069

# Login:
#   Database: dtx_dev
#   Email: admin
#   Password: admin
```

---

### **Bước 5: Setup Data chuẩn (Tự động)**

```bash
# Chạy script tạo categories, products, vendors
cd ~/Projects/dtx_project/odoo-dev

docker-compose exec odoo python3 /mnt/extra-addons/../scripts/setup_dtx_data.py
```

**Script sẽ tạo:**
- ✅ 4 Product Categories (Linh kiện, Thành phẩm, Dịch vụ, License)
- ✅ 2 Vendors (LGMEC, Nhà cung cấp Linh kiện A)
- ✅ 5 Components (Touch Screen, Printer, Mini PC, Camera, CCCD reader)
- ✅ 1 Kiosk product (DTX-A17)
- ✅ 1 Service (Dịch vụ gia công)

---

## 🎯 **WORKFLOW THƯỜNG DÙNG**

### **1. Khởi động Odoo**
```bash
cd ~/Projects/dtx_project/odoo-dev
docker-compose up -d
```

### **2. Dừng Odoo**
```bash
docker-compose down
```

### **3. Xem logs**
```bash
docker-compose logs -f odoo
```

### **4. Restart Odoo**
```bash
docker-compose restart odoo
```

### **5. Upgrade module sau khi sửa code**
```bash
# Tạo file upgrade script cho Mac
cat > upgrade-module.sh << 'EOF'
#!/bin/bash
MODULE_NAME=$1

if [ -z "$MODULE_NAME" ]; then
    echo "Usage: ./upgrade-module.sh <module_name>"
    exit 1
fi

echo "=========================================="
echo "  Upgrading Odoo Module: $MODULE_NAME"
echo "=========================================="

docker-compose exec odoo odoo -u $MODULE_NAME -d dtx_dev --stop-after-init
docker-compose restart odoo

echo "✅ Module $MODULE_NAME upgraded successfully!"
EOF

chmod +x upgrade-module.sh

# Sử dụng:
./upgrade-module.sh dtx_product_standards
```

### **6. Commit code lên GitHub**
```bash
cd ~/Projects/dtx_project

git status
git add .
git commit -m "feat: Your commit message"
git push origin main
```

---

## 🔧 **ODOO MODULE DEVELOPMENT**

### **Structure hiện tại:**
```
dtx_project/
├── README.md
├── WINDOWS_SETUP.md
├── MACBOOK_SETUP.md ← File này
├── odoo-dev/
│   ├── docker-compose.yml
│   ├── config/odoo.conf
│   ├── scripts/
│   │   └── setup_dtx_data.py ← Script tạo data
│   └── addons/
│       ├── dtx_serial_ext/ (v2.2.0)
│       └── dtx_product_standards/ (v1.2.0) ← Mới nhất
│           ├── __manifest__.py
│           ├── models/
│           │   ├── product_template.py
│           │   └── dtx_bom_template.py
│           ├── views/
│           │   ├── product_template_views.xml
│           │   └── dtx_bom_template_views.xml
│           ├── wizards/
│           │   ├── apply_dtx_standards_wizard.py
│           │   └── bom_generate_wizard.py
│           ├── README.md
│           └── MENU_STRUCTURE.md ← Menu documentation
```

---

## 📱 **VSCode trên MacBook**

### **Cài đặt VSCode:**
```bash
brew install --cask visual-studio-code
```

### **Extensions khuyến nghị:**
```bash
# Open VSCode
code ~/Projects/dtx_project

# Install extensions:
code --install-extension ms-python.python
code --install-extension redhat.vscode-xml
code --install-extension ms-azuretools.vscode-docker
```

### **VSCode Settings (JSON):**
```json
{
    "files.associations": {
        "*.xml": "xml"
    },
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "[xml]": {
        "editor.defaultFormatter": "redhat.vscode-xml"
    },
    "[python]": {
        "editor.tabSize": 4,
        "editor.insertSpaces": true
    }
}
```

---

## 🐳 **Docker Tips cho Mac M1**

### **1. Docker Desktop Settings:**
```
Settings > Resources:
  CPUs: 4 (hoặc 6 nếu MacBook có 8 cores)
  Memory: 4 GB (hoặc 6 GB nếu có 16 GB RAM)
  Swap: 1 GB
```

### **2. Performance:**
- ✅ Dùng **Apple Silicon** mode (native ARM)
- ✅ Enable **VirtioFS** (faster file sharing)
- ❌ Tắt "Use Rosetta for x86/amd64 emulation" (không cần)

### **3. Disk Space:**
```bash
# Xem Docker disk usage
docker system df

# Cleanup nếu cần
docker system prune -a
```

---

## 🌐 **PORT CONFLICTS**

### **Nếu port 8069 đã được dùng:**

**1. Tìm process đang dùng port:**
```bash
lsof -i :8069
```

**2. Kill process:**
```bash
kill -9 <PID>
```

**3. Hoặc đổi port Odoo:**
```bash
# Edit docker-compose.yml
code odoo-dev/docker-compose.yml

# Đổi:
#   ports:
#     - "8070:8069"  # Dùng port 8070 thay vì 8069

# Restart:
docker-compose down
docker-compose up -d
```

---

## 🔄 **SYNC GIỮA WINDOWS & MAC**

### **Workflow đề xuất:**

```
┌─────────────────────────────────────────────────┐
│ WINDOWS PC (tại nhà)                            │
├─────────────────────────────────────────────────┤
│ 1. Code trên VSCode                             │
│ 2. Test trên Docker                             │
│ 3. Commit + Push to GitHub                      │
└─────────────────────────────────────────────────┘
                    ↓ git push
┌─────────────────────────────────────────────────┐
│ GITHUB (github.com/trungns/dtx_project)         │
└─────────────────────────────────────────────────┘
                    ↓ git pull
┌─────────────────────────────────────────────────┐
│ MACBOOK AIR M1 (công ty)                        │
├─────────────────────────────────────────────────┤
│ 1. Pull latest code                             │
│ 2. Continue coding                              │
│ 3. Commit + Push to GitHub                      │
└─────────────────────────────────────────────────┘
```

### **Commands:**

**Trên Windows (cuối ngày):**
```powershell
cd D:\trungns\dtx_project
git add .
git commit -m "work: End of day commit"
git push origin main
```

**Trên MacBook (sáng hôm sau):**
```bash
cd ~/Projects/dtx_project
git pull origin main
docker-compose restart odoo
```

---

## 📝 **TERMINAL SETUP (Optional nhưng recommended)**

### **Install Oh My Zsh:**
```bash
# Install Oh My Zsh
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

# Install Powerlevel10k theme (đẹp!)
git clone --depth=1 https://github.com/romkatv/powerlevel10k.git ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/themes/powerlevel10k

# Edit ~/.zshrc
code ~/.zshrc

# Change theme:
ZSH_THEME="powerlevel10k/powerlevel10k"

# Add aliases:
alias dtx="cd ~/Projects/dtx_project/odoo-dev"
alias dup="docker-compose up -d"
alias ddown="docker-compose down"
alias dlogs="docker-compose logs -f odoo"
alias drestart="docker-compose restart odoo"

# Reload:
source ~/.zshrc
```

---

## 🐛 **TROUBLESHOOTING**

### **1. Docker Desktop không khởi động được**

**Kiểm tra:**
```bash
# Check Docker version
docker --version

# Check Docker status
docker ps
```

**Fix:**
- Restart Docker Desktop app
- Check System Requirements: macOS 11+ (Big Sur trở lên)
- Enable "Use Rosetta for x86/amd64 emulation" trong Settings (nếu cần)

---

### **2. Container bị crash**

**Kiểm tra logs:**
```bash
docker-compose logs odoo
docker-compose logs db
```

**Fix:**
```bash
# Remove containers và recreate
docker-compose down -v
docker-compose up -d
```

---

### **3. Module không upgrade được**

**Fix:**
```bash
# Clear cache
docker-compose exec odoo find /mnt/extra-addons -type d -name __pycache__ -exec rm -rf {} +

# Restart
docker-compose restart odoo

# Upgrade lại
./upgrade-module.sh dtx_product_standards
```

---

### **4. Git conflicts khi pull**

**Fix:**
```bash
# Stash local changes
git stash

# Pull from GitHub
git pull origin main

# Apply stashed changes
git stash pop

# Resolve conflicts nếu có
code <conflicted-file>

# After resolving:
git add .
git commit -m "fix: Merge conflicts"
```

---

## ✅ **CHECKLIST - SAU KHI SETUP**

```
☑ Docker Desktop đã cài và chạy
☑ Repository đã clone về ~/Projects/dtx_project
☑ Containers đã chạy (docker-compose up -d)
☑ Truy cập được Odoo tại http://localhost:8069
☑ Login thành công (admin/admin)
☑ Module dtx_product_standards đã installed
☑ Data đã được setup (chạy setup_dtx_data.py)
☑ VSCode đã cài và mở project
☑ Git config đã setup (user.name, user.email)
☑ Alias đã add vào ~/.zshrc
☑ Đã test commit + push to GitHub
```

---

## 📚 **DOCUMENTATION LINKS**

- **Main README:** [README.md](README.md)
- **Windows Setup:** [WINDOWS_SETUP.md](WINDOWS_SETUP.md)
- **Menu Structure:** [odoo-dev/addons/dtx_product_standards/MENU_STRUCTURE.md](odoo-dev/addons/dtx_product_standards/MENU_STRUCTURE.md)
- **Module READMEs:**
  - [dtx_serial_ext/README.md](odoo-dev/addons/dtx_serial_ext/README.md)
  - [dtx_product_standards/README.md](odoo-dev/addons/dtx_product_standards/README.md)

---

## 🔗 **USEFUL COMMANDS**

```bash
# Navigate to project
cd ~/Projects/dtx_project/odoo-dev

# Start Odoo
docker-compose up -d

# Stop Odoo
docker-compose down

# Restart Odoo
docker-compose restart odoo

# View logs
docker-compose logs -f odoo

# Upgrade module
./upgrade-module.sh dtx_product_standards

# Setup data
docker-compose exec odoo python3 /mnt/extra-addons/../scripts/setup_dtx_data.py

# Access Odoo shell (Python)
docker-compose exec odoo odoo shell -d dtx_dev

# Access PostgreSQL
docker-compose exec db psql -U odoo dtx_dev

# Git workflow
git pull origin main
git status
git add .
git commit -m "feat: Your message"
git push origin main
```

---

## 🎓 **LEARNING RESOURCES**

- **Odoo Documentation:** https://www.odoo.com/documentation/16.0/
- **Docker for Mac:** https://docs.docker.com/desktop/mac/install/
- **Git Basics:** https://git-scm.com/book/en/v2
- **VSCode Python:** https://code.visualstudio.com/docs/python/python-tutorial

---

**Last Updated:** 2025-12-28
**MacBook Model:** MacBook Air M1
**macOS:** Compatible with macOS 11+ (Big Sur and later)
