# Windows Setup Guide - DTX Odoo 16 Project

Hướng dẫn cài đặt và phát triển trên Windows với VSCode.

---

## Bước 1: Tạo Repository trên GitHub

**Chú ý:** Bạn cần tạo repository trước khi clone về máy Windows.

### Cách 1: Tạo từ Web (Khuyến nghị)

1. Truy cập: https://github.com/new
2. Điền thông tin:
   - **Repository name:** `dtx_project`
   - **Description:** `DTX Odoo 16 - Queue Management System`
   - **Visibility:** Private (hoặc Public tùy bạn)
   - **⚠️ KHÔNG CHỌN:** "Add a README file", "Add .gitignore", "Choose a license"
     (Vì project đã có sẵn các file này)
3. Click **"Create repository"**

### Cách 2: Tạo từ Command Line (trên Mac hiện tại)

Nếu bạn đã cài GitHub CLI (`gh`):

```bash
cd /Users/trungns/dtx_project
gh repo create trungns/dtx_project --private --source=. --push
```

---

## Bước 2: Push Code lên GitHub (trên Mac hiện tại)

Sau khi tạo repository xong, chạy lệnh sau trên Mac:

```bash
cd /Users/trungns/dtx_project
git push -u origin main
```

**Kết quả mong đợi:**
```
Enumerating objects: 120, done.
Counting objects: 100% (120/120), done.
Delta compression using up to 8 threads
Compressing objects: 100% (98/98), done.
Writing objects: 100% (120/120), 215.34 KiB | 7.16 MiB/s, done.
Total 120 (delta 15), reused 0 (delta 0), pack-reused 0
remote: Resolving deltas: 100% (15/15), done.
To https://github.com/trungns/dtx_project.git
 * [new branch]      main -> main
Branch 'main' set up to track remote branch 'main' from 'origin'.
```

---

## Bước 3: Cài đặt môi trường Windows

### 3.1. Cài đặt Git cho Windows

1. Download: https://git-scm.com/download/win
2. Cài đặt với cấu hình mặc định
3. **Quan trọng:** Chọn "Checkout as-is, commit Unix-style line endings" (LF)

### 3.2. Cài đặt Docker Desktop for Windows

1. Download: https://www.docker.com/products/docker-desktop/
2. Cài đặt và khởi động Docker Desktop
3. Yêu cầu:
   - Windows 10/11 64-bit (Home, Pro, hoặc Enterprise)
   - WSL 2 backend (sẽ tự động cài đặt)
   - 8GB RAM minimum

**Kiểm tra cài đặt:**
```powershell
docker --version
docker-compose --version
```

### 3.3. Cài đặt VSCode

1. Download: https://code.visualstudio.com/
2. Cài đặt với cấu hình mặc định

---

## Bước 4: Clone Project về Windows

### 4.1. Chọn thư mục làm việc

Khuyến nghị: `C:\Projects\` hoặc `D:\Projects\`

```powershell
# Mở PowerShell hoặc Git Bash
cd C:\Projects
```

### 4.2. Clone repository

```bash
git clone https://github.com/trungns/dtx_project.git
cd dtx_project
```

**Kết quả:**
```
dtx_project/
├── odoo-dev/
│   ├── addons/
│   │   ├── dtx_serial_ext/
│   │   └── dtx_product_standards/
│   ├── config/
│   ├── docker-compose.yml
│   └── start.sh
├── docs/
├── .gitignore
└── README.md
```

---

## Bước 5: Cài đặt VSCode Extensions

Mở VSCode và cài đặt các extension sau:

### 5.1. Extension bắt buộc

1. **Python** (Microsoft) - `ms-python.python`
2. **Pylance** (Microsoft) - `ms-python.vscode-pylance`
3. **XML** (Red Hat) - `redhat.vscode-xml`
4. **Docker** (Microsoft) - `ms-azuretools.vscode-docker`

### 5.2. Extension khuyến nghị

5. **Odoo Snippets** - `jigar-patel.odoosnippets`
6. **GitLens** - `eamodio.gitlens`
7. **Better Comments** - `aaron-bond.better-comments`
8. **Indent Rainbow** - `oderwat.indent-rainbow`

### 5.3. Cách cài nhanh

Mở Command Palette (`Ctrl+Shift+P`), gõ:
```
ext install ms-python.python redhat.vscode-xml ms-azuretools.vscode-docker
```

---

## Bước 6: Cấu hình VSCode cho Odoo

### 6.1. Mở project

```
File > Open Folder > Chọn C:\Projects\dtx_project
```

### 6.2. Tạo workspace settings

VSCode sẽ tự nhận `.vscode/settings.json` trong project. Nếu chưa có, tạo file:

**File:** `C:\Projects\dtx_project\.vscode\settings.json`
```json
{
    "python.defaultInterpreterPath": "/usr/bin/python3",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": true,
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true
    },
    "files.watcherExclude": {
        "**/odoo-dev/postgres-data/**": true,
        "**/odoo-dev/filestore/**": true
    },
    "[python]": {
        "editor.tabSize": 4,
        "editor.insertSpaces": true
    },
    "[xml]": {
        "editor.tabSize": 4,
        "editor.insertSpaces": true
    }
}
```

---

## Bước 7: Khởi động Odoo trên Windows

### 7.1. Mở Terminal trong VSCode

`Ctrl+` ` (phím backtick) hoặc `Terminal > New Terminal`

### 7.2. Chuyển vào thư mục odoo-dev

```powershell
cd odoo-dev
```

### 7.3. Khởi động Docker Compose

```powershell
docker-compose up -d
```

**Lần đầu sẽ mất 5-10 phút để download images:**
```
[+] Running 2/2
 ✔ Container odoo-dev-db-1   Started
 ✔ Container odoo-dev-web-1  Started
```

### 7.4. Kiểm tra logs

```powershell
docker-compose logs -f web
```

**Chờ đến khi thấy:**
```
odoo.modules.loading: Modules loaded.
INFO ? odoo.service.server: HTTP service (werkzeug) running on 0.0.0.0:8069
```

Nhấn `Ctrl+C` để thoát logs (container vẫn chạy).

### 7.5. Truy cập Odoo

Mở browser: **http://localhost:8069**

**Thông tin đăng nhập:**
- Database: `dtx_dev`
- Email: `admin`
- Password: `admin`

---

## Bước 8: Cài đặt Modules

### 8.1. Cài module qua UI

1. Vào **Apps** menu
2. Click **Update Apps List** (góc trên bên phải)
3. Xác nhận "Update"
4. Tìm "DTX" trong search box
5. Cài đặt:
   - **DTX Serial Extension** (dtx_serial_ext)
   - **DTX Product Standards** (dtx_product_standards)

### 8.2. Cài module qua command line (nhanh hơn)

```powershell
docker-compose exec web odoo -d dtx_dev -i dtx_serial_ext,dtx_product_standards --stop-after-init
docker-compose restart web
```

---

## Bước 9: Workflow phát triển trên Windows

### 9.1. Sửa code

Mở VSCode, chỉnh sửa file trong:
```
dtx_project\odoo-dev\addons\dtx_serial_ext\
dtx_project\odoo-dev\addons\dtx_product_standards\
```

### 9.2. Upgrade module sau khi sửa code

**Cách 1: Dùng script (khuyến nghị)**
```powershell
cd odoo-dev
.\upgrade-module.ps1 dtx_serial_ext
```

**Chú ý:** Nếu file `upgrade-module.ps1` chưa có, tạo file mới:

**File:** `odoo-dev\upgrade-module.ps1`
```powershell
param(
    [Parameter(Mandatory=$true)]
    [string]$ModuleName
)

Write-Host "Upgrading module: $ModuleName" -ForegroundColor Green
docker-compose exec web odoo -d dtx_dev -u $ModuleName --stop-after-init
docker-compose restart web
Write-Host "Module $ModuleName upgraded!" -ForegroundColor Green
```

**Cách 2: Command thủ công**
```powershell
docker-compose exec web odoo -d dtx_dev -u dtx_serial_ext --stop-after-init
docker-compose restart web
```

### 9.3. Xem logs

```powershell
# Xem logs real-time
docker-compose logs -f web

# Xem 100 dòng cuối
docker-compose logs --tail=100 web
```

### 9.4. Dừng và khởi động lại

```powershell
# Dừng containers
docker-compose down

# Khởi động lại
docker-compose up -d

# Khởi động lại nhanh (không tắt DB)
docker-compose restart web
```

---

## Bước 10: Git Workflow trên Windows

### 10.1. Kiểm tra thay đổi

```bash
git status
git diff
```

### 10.2. Commit changes

```bash
# Stage files
git add odoo-dev/addons/dtx_serial_ext/
git add odoo-dev/addons/dtx_product_standards/

# Commit
git commit -m "feat: Add new feature XYZ"

# Push to GitHub
git push origin main
```

### 10.3. Pull updates (nếu code từ Mac)

```bash
git pull origin main
```

---

## Chú ý quan trọng cho Windows

### ⚠️ Line Endings (LF vs CRLF)

**Vấn đề:** Windows dùng CRLF (`\r\n`), Linux/Mac dùng LF (`\n`).

**Giải pháp:** Git đã được cấu hình tự động (trong `.gitattributes`).

Nếu gặp lỗi, chạy:
```bash
git config core.autocrlf false
```

### ⚠️ Path Separators

- **Windows:** `C:\Projects\dtx_project\`
- **Linux/Mac:** `/Users/trungns/dtx_project/`
- **Docker:** `/mnt/extra-addons/` (luôn dùng `/`)

**Trong code Python/XML:** LUÔN dùng `/` hoặc `os.path.join()`.

### ⚠️ File Permissions

Không cần `chmod +x` trên Windows. Docker sẽ tự xử lý.

### ⚠️ Performance

WSL 2 backend nhanh hơn Hyper-V. Đảm bảo Docker Desktop dùng WSL 2:
```
Settings > General > Use the WSL 2 based engine
```

---

## Troubleshooting

### Lỗi: "Cannot connect to the Docker daemon"

**Giải pháp:**
1. Mở Docker Desktop
2. Chờ Docker khởi động hoàn toàn (icon whale không còn nhấp nháy)

### Lỗi: "Port 8069 already in use"

**Giải pháp:**
```powershell
# Tìm process đang dùng port 8069
netstat -ano | findstr :8069

# Kill process (thay <PID> bằng process ID)
taskkill /PID <PID> /F
```

### Lỗi: Module không upgrade

**Giải pháp:**
```powershell
# Hard restart
docker-compose down
docker-compose up -d

# Xóa cache Python
docker-compose exec web find /mnt/extra-addons -type d -name __pycache__ -exec rm -rf {} +
docker-compose restart web
```

### Lỗi: "Database dtx_dev does not exist"

**Giải pháp:**
```powershell
# Tạo database mới
docker-compose exec web odoo -d dtx_dev -i base --stop-after-init
docker-compose restart web
```

---

## Tài liệu tham khảo

- **Project README:** [GITHUB_README.md](GITHUB_README.md)
- **User Guide:** [docs/user-guide/](docs/user-guide/)
- **Developer Guide:** [docs/developer-guide/](docs/developer-guide/)
- **dtx_serial_ext:** [odoo-dev/addons/dtx_serial_ext/README.md](odoo-dev/addons/dtx_serial_ext/README.md)
- **dtx_product_standards:** [odoo-dev/addons/dtx_product_standards/README.md](odoo-dev/addons/dtx_product_standards/README.md)

---

## Liên hệ

- **GitHub Issues:** https://github.com/trungns/dtx_project/issues
- **Email:** trungns@dtx.com

---

**Chúc phát triển thành công trên Windows! 🚀**
