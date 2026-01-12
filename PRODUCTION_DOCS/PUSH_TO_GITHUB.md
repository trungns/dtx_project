# Hướng dẫn Push Code lên GitHub

Code đã được commit xong trên Mac. Giờ cần push lên GitHub để dùng trên Windows.

---

## Bước 1: Tạo Repository trên GitHub (QUAN TRỌNG!)

### Cách A: Qua Web (Dễ nhất - Khuyến nghị)

1. Mở trình duyệt, truy cập: **https://github.com/new**

2. Điền thông tin:
   ```
   Repository name: dtx_project
   Description: DTX Odoo 16 - Queue Management System
   Visibility: Private (hoặc Public tùy bạn)
   ```

3. **⚠️ QUAN TRỌNG - KHÔNG CHỌN:**
   - ❌ Add a README file
   - ❌ Add .gitignore
   - ❌ Choose a license

   **Lý do:** Project đã có sẵn tất cả các file này!

4. Click nút **"Create repository"** màu xanh lá

5. **GHI CHÚ URL hiển thị:**
   ```
   https://github.com/trungns/dtx_project.git
   ```

6. **ĐÓNG TRANG ĐÓ LẠI** - Không làm theo hướng dẫn trên trang đó!

### Cách B: Qua GitHub CLI (Nếu đã cài `gh`)

```bash
cd /Users/trungns/dtx_project
gh repo create trungns/dtx_project --private --source=. --push
```

Nếu dùng cách này, **XONG RỒI** - không cần làm Bước 2!

---

## Bước 2: Push Code lên GitHub (trên Mac này)

Sau khi tạo repository xong ở Bước 1, chạy lệnh:

```bash
cd /Users/trungns/dtx_project
git push -u origin main
```

### Kết quả mong đợi:

```
Enumerating objects: 122, done.
Counting objects: 100% (122/122), done.
Delta compression using up to 8 threads
Compressing objects: 100% (100/100), done.
Writing objects: 100% (122/122), 220.45 KiB | 8.16 MiB/s, done.
Total 122 (delta 17), reused 0 (delta 0), pack-reused 0
remote: Resolving deltas: 100% (17/17), done.
To https://github.com/trungns/dtx_project.git
 * [new branch]      main -> main
Branch 'main' set up to track remote branch 'main' from 'origin'.
```

### Nếu gặp lỗi authentication:

**Lỗi:** `remote: Support for password authentication was removed`

**Giải pháp:**

1. Tạo Personal Access Token (PAT):
   - Truy cập: https://github.com/settings/tokens
   - Click **"Generate new token"** > **"Generate new token (classic)"**
   - Chọn scopes: `repo` (full control of private repositories)
   - Click **"Generate token"**
   - **SAO CHÉP TOKEN NGAY** (chỉ hiện 1 lần!)

2. Push lại và dùng token làm password:
   ```bash
   git push -u origin main
   Username: trungns
   Password: <paste-your-token-here>
   ```

3. Hoặc dùng SSH (khuyến nghị cho lâu dài):
   - Xem hướng dẫn: https://docs.github.com/en/authentication/connecting-to-github-with-ssh

---

## Bước 3: Kiểm tra trên GitHub

1. Mở browser: **https://github.com/trungns/dtx_project**

2. Kiểm tra có đủ file:
   ```
   ✓ odoo-dev/
   ✓ docs/
   ✓ .gitignore
   ✓ GITHUB_README.md
   ✓ WINDOWS_SETUP.md
   ✓ README.md
   ```

3. Click vào `GITHUB_README.md` - đây là file README chính cho GitHub

---

## Bước 4: Clone về máy Windows

**Trên máy Windows:**

1. Cài đặt Git cho Windows (nếu chưa có):
   - Download: https://git-scm.com/download/win

2. Mở PowerShell hoặc Git Bash:
   ```powershell
   cd C:\Projects
   git clone https://github.com/trungns/dtx_project.git
   cd dtx_project
   ```

3. Đọc hướng dẫn setup Windows:
   - Mở file `WINDOWS_SETUP.md` và làm theo từng bước

---

## Tóm tắt

**Trên Mac (hiện tại):**
1. ✅ Code đã commit xong (2 commits)
2. ✅ Git repository đã sẵn sàng
3. ✅ Windows setup guide đã tạo
4. ⏳ Cần: Tạo repo trên GitHub + Push

**Để hoàn thành:**
1. Tạo repository: https://github.com/new
2. Chạy: `git push -u origin main`
3. Clone về Windows: `git clone https://github.com/trungns/dtx_project.git`

**Files hướng dẫn:**
- `WINDOWS_SETUP.md` - Hướng dẫn đầy đủ cho Windows
- `GITHUB_README.md` - README chính cho GitHub
- `odoo-dev/upgrade-module.ps1` - Script upgrade module trên Windows

---

## Commits đã tạo

```
commit a68d9d6 (HEAD -> main)
Author: Trung Nguyen
Date:   Thu Dec 26 2025

    docs: Add Windows setup guide and PowerShell upgrade script

commit 90258c3
Author: Trung Nguyen
Date:   Thu Dec 26 2025

    feat: Initial commit - DTX Odoo 16 modules

    - dtx_serial_ext v2.2.0: Serial tracking with vendor invoice management
    - dtx_product_standards v1.1.0: Product standardization & BOM templates
    - Full documentation in docs/
    - Docker-based development environment
    - Production deployment guides
```

---

**Sẵn sàng push lên GitHub! 🚀**
