# DANH SÁCH FILES CẦN DỌN DẸP

**Tạo**: 2026-01-09
**Mục đích**: Cleanup trước khi deploy production

---

## FILES CẦN XÓA (RÁC - KHÔNG CẦN CHO PRODUCTION)

### 1. Test Scripts trong /odoo-dev/
```bash
rm -f odoo-dev/test_*.py
rm -f odoo-dev/check_*.py
rm -f odoo-dev/debug_*.py
rm -f odoo-dev/force_*.py
rm -f odoo-dev/recompute_*.py
rm -f odoo-dev/verify_*.py
rm -f odoo-dev/find_*.py
rm -f odoo-dev/fix_*.py
```

**Files cụ thể**:
- `test_advance_payment.py`
- `test_advance_simple.py`
- `test_commission.py`
- `test_customer_invoice_state.py`
- `check_component_moves.py`
- `check_kiosk_production.py`
- `check_so155_serials.py`
- `check_specific_serials.py`
- `debug_compute.py`
- `force_compute_direct.py`
- `force_recompute_with_flush.py`
- `recompute_serials.py`
- `verify_all_features.py`
- `find_consumed_components.py`
- `fix_lifecycle_state.py`

### 2. Session Summaries (Cũ)
```bash
rm -f SESSION_SUMMARY_*.md
rm -f ROOT_CAUSE_FINAL.md
rm -f FINAL_FIX_SUMMARY.md
```

### 3. Temporary Docs (Đã consolidate vào PRODUCTION_DOCS)
```bash
rm -f odoo-dev/IMPLEMENTATION_SUMMARY.md
rm -f odoo-dev/SERIAL_TRACKING_DIAGRAM.txt
# (Giữ SERIAL_TRACKING_EXPLAINED.md - đã copy sang PRODUCTION_DOCS)
```

### 4. Test/UAT Specific Docs
```bash
rm -f odoo-dev/addons/dtx_sales_pakd_contract/TESTING_COMPLETE_SUMMARY.md
rm -f odoo-dev/addons/dtx_sales_pakd_contract/UAT_*.md
# (Giữ MANUAL_UAT_TEST_CASES.md - có thể cần cho regression testing)
```

### 5. Formula Analysis Docs (Đã fix xong)
```bash
rm -f PAKD_*.md
rm -f SESSION_2026_01_04_PAKD_FORMULA_FIX.md
```

### 6. Setup Guides (Đã consolidate)
- Giữ `MACBOOK_SETUP.md`, `WINDOWS_SETUP.md`, `QUICK_START.md` - vẫn hữu ích
- Xóa `README_HANDOFF.md` - đã cũ

### 7. Subcontracting Workarounds (Không dùng nữa)
```bash
rm -f SUBCONTRACTING_*.md
```

### 8. Test Data Summary
```bash
rm -f TEST_DATA_SUMMARY.md
rm -f KIOSK_PRODUCTION_TEST_FLOW.md
```

### 9. Migration Guides (Không dùng)
```bash
rm -f ODOO_18_MIGRATION_GUIDE.md
```

---

## FILES GIỮ LẠI (CẦN THIẾT)

### Root Level
- ✅ `README.md` - Main project README
- ✅ `MACBOOK_SETUP.md` - Dev setup for macOS
- ✅ `WINDOWS_SETUP.md` - Dev setup for Windows
- ✅ `QUICK_START.md` - Quick start guide
- ✅ `PUSH_TO_GITHUB.md` - Git workflow
- ✅ `/docs/` - Original documentation structure
- ✅ `/backups/` - Backup files + restore instructions
- ✅ **`/PRODUCTION_DOCS/`** - ⭐ NEW: Production documentation (TẬP TRUNG)

### Module Documentation
- ✅ `odoo-dev/addons/dtx_serial_ext/README.md`
- ✅ `odoo-dev/addons/dtx_serial_ext/INSTALLATION.md`
- ✅ `odoo-dev/addons/dtx_serial_ext/docs/` - Module docs
- ✅ `odoo-dev/addons/dtx_product_standards/README.md`
- ✅ `odoo-dev/addons/dtx_sales_pakd_contract/README.md`
- ✅ `odoo-dev/addons/dtx_sales_pakd_contract/docs/MANUAL_UAT_TEST_CASES.md`
- ✅ `odoo-dev/addons/dtx_sales_pakd_contract/docs/COMMISSION_TRACKING.md`

### Utility Scripts (GIỮ - có thể cần trong production)
- ✅ `odoo-dev/upgrade_module.py` - Upgrade modules
- ✅ `odoo-dev/upgrade_sales_pakd.py` - Upgrade PAKD module

---

## SCRIPT TỰ ĐỘNG DỌN DẸP

```bash
#!/bin/bash
# cleanup.sh - Tự động xóa files rác

cd /Users/trungns/dtx_project

# Test scripts
rm -f odoo-dev/test_*.py
rm -f odoo-dev/check_*.py
rm -f odoo-dev/debug_*.py
rm -f odoo-dev/force_*.py
rm -f odoo-dev/recompute_*.py
rm -f odoo-dev/verify_*.py
rm -f odoo-dev/find_*.py
rm -f odoo-dev/fix_*.py

# Session summaries
rm -f SESSION_SUMMARY_*.md
rm -f ROOT_CAUSE_FINAL.md
rm -f FINAL_FIX_SUMMARY.md
rm -f FIX_ACCOUNTING_ACCOUNTS.md
rm -f README_HANDOFF.md

# PAKD docs
rm -f PAKD_*.md
rm -f SESSION_2026_01_04_PAKD_FORMULA_FIX.md

# Subcontracting
rm -f SUBCONTRACTING_*.md

# Test data
rm -f TEST_DATA_SUMMARY.md
rm -f KIOSK_PRODUCTION_TEST_FLOW.md

# Migration
rm -f ODOO_18_MIGRATION_GUIDE.md

# Temporary implementation docs
rm -f odoo-dev/IMPLEMENTATION_SUMMARY.md
rm -f odoo-dev/SERIAL_TRACKING_DIAGRAM.txt

# UAT docs (keep manual test cases)
rm -f odoo-dev/addons/dtx_sales_pakd_contract/TESTING_COMPLETE_SUMMARY.md
rm -f odoo-dev/addons/dtx_sales_pakd_contract/UAT_AR_AGING.md
rm -f odoo-dev/addons/dtx_sales_pakd_contract/UAT_CONTRACT_COST_TRACKING.md
rm -f odoo-dev/addons/dtx_sales_pakd_contract/UAT_EXCEL_PAKD_FORMULAS.md

echo "✅ Cleanup completed!"
echo "Remaining important files:"
echo "- /PRODUCTION_DOCS/ (NEW - Main documentation)"
echo "- /docs/ (Original docs)"
echo "- /backups/ (Backup files)"
echo "- Module READMEs"
echo "- Setup guides (MACBOOK_SETUP, WINDOWS_SETUP, QUICK_START)"
```

**Chạy script**:
```bash
chmod +x cleanup.sh
./cleanup.sh
```

---

## CẤU TRÚC SAU KHI CLEANUP

```
dtx_project/
├── README.md ✅
├── MACBOOK_SETUP.md ✅
├── WINDOWS_SETUP.md ✅
├── QUICK_START.md ✅
├── PUSH_TO_GITHUB.md ✅
│
├── PRODUCTION_DOCS/ ⭐ NEW - DOCUMENTATION TẬP TRUNG
│   ├── README.md
│   ├── 01_INSTALLATION/
│   ├── 02_CONFIGURATION/
│   ├── 03_USER_GUIDES/
│   ├── 04_TECHNICAL/
│   └── 05_MAINTENANCE/
│
├── docs/ (Original structure - giữ lại nếu cần)
│
├── backups/ ✅
│   ├── README.md
│   ├── RESTORE_INSTRUCTIONS.md
│   └── *.zip
│
├── odoo-dev/
│   ├── docker-compose.yml
│   ├── config/
│   ├── addons/
│   │   ├── dtx_serial_ext/
│   │   │   ├── README.md ✅
│   │   │   └── docs/
│   │   ├── dtx_product_standards/
│   │   │   └── README.md ✅
│   │   └── dtx_sales_pakd_contract/
│   │       ├── README.md ✅
│   │       └── docs/
│   │           ├── MANUAL_UAT_TEST_CASES.md ✅
│   │           └── COMMISSION_TRACKING.md ✅
│   ├── upgrade_module.py ✅
│   └── upgrade_sales_pakd.py ✅
│
└── [Test scripts đã xóa] ❌
```

---

## LƯU Ý QUAN TRỌNG

1. **Backup trước khi xóa**:
```bash
tar -czf dtx_project_before_cleanup_$(date +%Y%m%d).tar.gz dtx_project/
```

2. **Kiểm tra git status**:
```bash
cd dtx_project
git status
# Không commit files test vào production branch
```

3. **Files trong .gitignore**:
```
# Test scripts
test_*.py
check_*.py
debug_*.py
force_*.py
verify_*.py
fix_*.py
recompute_*.py
find_*.py

# Session summaries
SESSION_SUMMARY_*.md

# Temporary docs
*_SUMMARY.md
*_FIX*.md
```

---

**Cleanup List - DTX Odoo 16**
**Date**: 2026-01-09
