# DTX Serial Extension - Production Deployment Guide

**Version:** 2.1.1
**Target:** Odoo 16 Production Environment
**Status:** Ready for Production

---

## ⚠️ PRE-DEPLOYMENT CHECKLIST

### 1. Backup Requirements

**CRITICAL: Backup TRƯỚC KHI bắt đầu!**

```bash
# 1. Backup PostgreSQL Database
pg_dump -U odoo_user -h localhost production_db > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. Backup Odoo Filestore (attachments, images)
tar -czf filestore_backup_$(date +%Y%m%d_%H%M%S).tar.gz /path/to/odoo/filestore/

# 3. Backup current addons (if customized)
tar -czf addons_backup_$(date +%Y%m%d_%H%M%S).tar.gz /path/to/odoo/addons/
```

**Verify backups:**
```bash
# Test database backup
psql -U odoo_user -d test_restore < backup_YYYYMMDD_HHMMSS.sql

# Check filestore backup
tar -tzf filestore_backup_YYYYMMDD_HHMMSS.tar.gz | head -10
```

### 2. Environment Check

- [ ] Odoo version: **16.0** (check: Apps > About Odoo)
- [ ] Required modules installed:
  - [ ] `stock` (Inventory)
  - [ ] `product` (Product)
  - [ ] `purchase` (Purchase)
  - [ ] `sale` (Sales)
  - [ ] `account` (Accounting)
- [ ] Database has free space (check: `SELECT pg_size_pretty(pg_database_size('your_db'));`)
- [ ] User has admin rights
- [ ] Scheduled downtime window (recommended: 30-60 minutes)

### 3. Test Environment Validation

**STRONGLY RECOMMENDED:** Test in staging/test environment first!

- [ ] Clone production DB to test environment
- [ ] Install module on test environment
- [ ] Verify all features work
- [ ] Check existing data not affected
- [ ] Performance test with real data volume

---

## 📦 DEPLOYMENT STEPS

### PHASE 1: Pre-Installation Setup (15 minutes)

#### Step 1.1: Announce Maintenance

**Email/Notify users:**
```
Subject: Scheduled Maintenance - Odoo Upgrade

Thời gian: [DATE] [TIME] - [TIME] (30-60 phút)
Nội dung: Cài đặt module quản lý serial number nâng cao
Ảnh hưởng: Hệ thống Odoo tạm ngưng sử dụng
Action: Lưu công việc trước thời gian bảo trì
```

#### Step 1.2: Prepare Rollback Plan

**Document current state:**
```bash
# 1. Note current module versions
# In Odoo: Apps > Installed > Export list

# 2. Create rollback script
cat > rollback.sh << 'EOF'
#!/bin/bash
# Rollback script
echo "Rolling back to backup..."
psql -U odoo_user -d production_db < backup_YYYYMMDD_HHMMSS.sql
sudo systemctl restart odoo
echo "Rollback complete"
EOF

chmod +x rollback.sh
```

#### Step 1.3: Stop Odoo Service

```bash
# Stop Odoo gracefully
sudo systemctl stop odoo

# Verify stopped
sudo systemctl status odoo
# Should show: "inactive (dead)"

# Check no Odoo processes running
ps aux | grep odoo
```

---

### PHASE 2: Module Installation (10 minutes)

#### Step 2.1: Upload Module Files

```bash
# 1. Copy module to addons directory
sudo cp -r /path/to/dtx_serial_ext /opt/odoo/addons/custom/

# 2. Set correct ownership
sudo chown -R odoo:odoo /opt/odoo/addons/custom/dtx_serial_ext

# 3. Set correct permissions
sudo chmod -R 755 /opt/odoo/addons/custom/dtx_serial_ext

# 4. Verify structure
ls -la /opt/odoo/addons/custom/dtx_serial_ext/
# Should show: __init__.py, __manifest__.py, models/, views/, etc.
```

#### Step 2.2: Update Odoo Config (if needed)

**Only if custom addons path not configured:**

```bash
sudo nano /etc/odoo/odoo.conf
```

Add/verify:
```ini
[options]
addons_path = /opt/odoo/addons,/opt/odoo/addons/custom
```

#### Step 2.3: Start Odoo Service

```bash
# Start Odoo
sudo systemctl start odoo

# Monitor logs for errors
sudo tail -f /var/log/odoo/odoo-server.log

# Look for:
# - "odoo.modules.loading: Module dtx_serial_ext loaded"
# - NO errors or warnings about dtx_serial_ext
```

**If errors appear:**
```bash
# Stop service
sudo systemctl stop odoo

# Check Python syntax
python3 -m py_compile /opt/odoo/addons/custom/dtx_serial_ext/models/*.py

# Fix errors, then restart
sudo systemctl start odoo
```

---

### PHASE 3: Module Activation (10 minutes)

#### Step 3.1: Login to Odoo

1. Access Odoo URL: `https://your-odoo-domain.com`
2. Login as **Administrator**
3. Verify login successful

#### Step 3.2: Update Apps List

1. Go to: **Apps** (📦 icon in top menu)
2. Click: **Update Apps List** (⟳ icon)
3. In popup, click: **Update**
4. Wait for confirmation: "Apps updated successfully"

#### Step 3.3: Install DTX Serial Extension

1. **Remove "Apps" filter:**
   - Click on search box filter icon
   - Uncheck "Apps" filter
   - Should now show all modules

2. **Search for module:**
   - Search: "DTX Serial"
   - Should find: "DTX Serial Extension"

3. **Install:**
   - Click: **Install** button
   - Wait for installation (may take 30-60 seconds)
   - Watch for: "Module installed successfully"

4. **Verify installation:**
   - Check: Apps > Installed
   - Find: "DTX Serial Extension"
   - Status: "Installed" ✅
   - Version: "2.1.1"

**If installation fails:**
```bash
# Check logs
sudo tail -100 /var/log/odoo/odoo-server.log | grep -i error

# Common issues:
# - Missing dependencies → Install required modules first
# - Permission errors → Check file ownership
# - Syntax errors → Check Python files
```

---

### PHASE 4: Product Configuration (20 minutes)

#### Step 4.1: Configure Product Categories

**For all products you want to track by serial:**

1. **Navigate:**
   - Inventory > Configuration > Product Categories

2. **Select/Create Category:**
   - Example: "Electronic Devices" or "DTX Equipment"

3. **Configure Costing Method:**
   - **Costing Method:** AVCO (Average Cost)
   - **Inventory Valuation:** Automated
   - **Save**

**Why AVCO?**
- ✅ Accurate cost tracking for each serial
- ✅ Handles price fluctuations
- ✅ Required for proper inventory accounting

#### Step 4.2: Configure Products for Serial Tracking

**For EACH product to track:**

1. **Open Product:**
   - Inventory > Products > Products
   - Find your product (e.g., "DTX Queue Display Device")

2. **Configure Inventory Tab:**

   **Product Type:**
   - ✅ Select: **Storable Product**

   **Tracking:**
   - ✅ Select: **By Unique Serial Number**
   - ⚠️ WARNING: Cannot change after transactions exist!

   **Routes:**
   - ✅ Check: Buy
   - ✅ Check: Make To Order (if applicable)

3. **Configure General Information Tab:**

   **Product Category:**
   - Select: Category configured in Step 4.1
   - (e.g., "Electronic Devices")

4. **Save Product**

**Repeat for all products requiring serial tracking.**

#### Step 4.3: Test Product Configuration

**Quick test:**

1. **Create test Purchase Order:**
   - Purchase > Orders > Create
   - Add product with serial tracking
   - Confirm Order

2. **Validate Receipt:**
   - Click: Receipt (WH/IN/XXXXX)
   - Click: Validate

3. **Assign Serial:**
   - Should see: "Lot/Serial Number" field
   - Enter test serial: "TEST-001"
   - Confirm

4. **Verify Serial Created:**
   - Inventory > Products > **Device Serials** (NEW MENU!)
   - Find: "TEST-001"
   - Check fields visible:
     - ✅ Lifecycle State
     - ✅ Purchase Orders
     - ✅ Vendor Invoice State
     - ✅ Vendor Bills (if bill exists)

**If serial menu not visible:**
```
Settings > Technical > Sequences & Identifiers > Menu Items
Search: "Device Serials"
Check: "parent_id" = "Inventory Control"
```

---

### PHASE 5: Existing Data Migration (If Applicable)

#### Scenario A: No Existing Serials

✅ **Skip to Phase 6** - You're starting fresh!

#### Scenario B: Existing Serials (Migration Needed)

**Check existing serials:**
```python
# Settings > Technical > Python Code
existing_lots = env['stock.lot'].search([])
print(f"Found {len(existing_lots)} existing serial numbers")

# Sample first 5
for lot in existing_lots[:5]:
    print(f"- {lot.name}: {lot.product_id.name}")
```

**If serials exist, run migration:**

```python
# This will populate new fields with default values
all_lots = env['stock.lot'].search([])

count = 0
for lot in all_lots:
    # Set lifecycle state based on current location
    if lot.product_qty > 0:
        lot.lifecycle_state = 'stock'
    else:
        lot.lifecycle_state = 'delivered'

    count += 1
    if count % 100 == 0:
        print(f"Processed {count} serials...")
        env.cr.commit()  # Commit every 100 records

env.cr.commit()
print(f"Migration complete: {count} serials updated")
```

**Verify migration:**
```python
# Check distribution
states = env['stock.lot'].read_group(
    [],
    ['lifecycle_state'],
    ['lifecycle_state']
)
for state in states:
    print(f"{state['lifecycle_state']}: {state['lifecycle_state_count']} serials")
```

---

### PHASE 6: User Access Configuration (5 minutes)

#### Step 6.1: Configure User Groups

**Inventory Manager:**
- Can view/edit all serial fields
- Can change lifecycle states manually
- Can override vendor invoice state

**Warehouse User:**
- Can view serial information
- Can assign serials during receipt
- Cannot change lifecycle states manually

**Configuration:**

1. **Settings > Users & Companies > Users**

2. **For each user, set:**
   - **Inventory:** Inventory Manager (for managers)
   - **Inventory:** Inventory User (for warehouse staff)

3. **Test access:**
   - Login as each user type
   - Verify can access "Device Serials" menu
   - Verify permissions correct

---

### PHASE 7: Testing & Validation (15 minutes)

#### Test Case 1: Purchase Order Flow

**Complete end-to-end test:**

1. **Create PO:**
   - Purchase > Orders > Create
   - Vendor: (select vendor)
   - Product: (serial tracked product)
   - Quantity: 1
   - Confirm Order

2. **Validate Receipt:**
   - Click: Receipt (WH/IN/XXXXX)
   - Validate
   - Assign Serial: "PROD-TEST-001"
   - Confirm

3. **Verify Serial:**
   - Inventory > Device Serials
   - Find: "PROD-TEST-001"
   - **Expected values:**
     - ✅ Lifecycle State: "In Stock" (green badge)
     - ✅ Purchase Orders: Shows PO number
     - ✅ Vendor Invoice State: "Invoice Missing" (red badge)
     - ✅ Vendor Bills: Empty

4. **Create & Post Vendor Bill:**
   - Purchase > Orders > Open PO
   - Click: "Create Bill"
   - Enter: Invoice date, reference
   - Click: "Confirm" (Post)

5. **Verify Auto-Update:**
   - **Refresh serial page** (F5)
   - **Expected values:**
     - ✅ Vendor Bills: Shows bill number
     - ✅ Vendor Invoice State: **"Invoice Linked"** (green) ✨

6. **Check Logs (optional):**
   ```bash
   sudo tail -50 /var/log/odoo/odoo-server.log | grep "DTX Serial"
   # Should see: "Vendor bill XXX posted for PO YYY, triggering serial recompute"
   ```

#### Test Case 2: Sales Order Flow

1. **Create SO:**
   - Sales > Orders > Create
   - Customer: (select customer)
   - Product: "PROD-TEST-001"
   - Confirm Sale Order

2. **Deliver:**
   - Click: Delivery (WH/OUT/XXXXX)
   - Click: Validate
   - Select Serial: "PROD-TEST-001"
   - Confirm

3. **Verify Serial:**
   - Inventory > Device Serials > "PROD-TEST-001"
   - **Expected:**
     - ✅ Lifecycle State: "Delivered" (auto-updated!)
     - ✅ Sale Orders: Shows SO number
     - ✅ Customer: Shows customer name

#### Test Case 3: Manual State Override

1. **Open Serial:**
   - Inventory > Device Serials > "PROD-TEST-001"

2. **Change Vendor Invoice State:**
   - Click: Vendor Invoice State dropdown
   - Select: "Invoice Replaced"
   - Add note: "Testing manual override"
   - Save

3. **Verify:**
   - State = "Invoice Replaced" (yellow)
   - Note saved
   - **Even if bill posted/cancelled, state stays "replaced"** ✅

---

### PHASE 8: Cleanup & Documentation (10 minutes)

#### Step 8.1: Remove Test Data

```python
# Settings > Technical > Python Code

# Delete test serials
test_lots = env['stock.lot'].search([('name', 'like', 'TEST%')])
print(f"Found {len(test_lots)} test serials")

# CAREFUL: Verify these are test data!
for lot in test_lots:
    print(f"- {lot.name}")

# If confirmed, delete
# test_lots.unlink()
```

#### Step 8.2: Document Configuration

**Create internal documentation:**

```markdown
# DTX Serial Extension - Production Setup

## Installation Date
- Installed: [DATE]
- Version: 2.1.1
- Installed by: [NAME]

## Configured Products
- Product 1: [Name] - Serial Tracking: ✅
- Product 2: [Name] - Serial Tracking: ✅
- ...

## User Training
- Warehouse Team: [DATE] - Completed ✅
- Purchase Team: [DATE] - Pending ⏳
- Management: [DATE] - Scheduled 📅

## Known Issues
- None

## Support Contacts
- Technical: [EMAIL/PHONE]
- Administrator: [EMAIL/PHONE]
```

#### Step 8.3: Enable Production Mode

```bash
# Disable dev mode if enabled
# Settings > Deactivate Developer Mode
```

---

## 📊 POST-DEPLOYMENT MONITORING

### Day 1: Intensive Monitoring

**Check every hour:**

1. **System logs:**
   ```bash
   sudo tail -100 /var/log/odoo/odoo-server.log | grep -i "error\|warning"
   ```

2. **Serial creation:**
   - Verify new serials created correctly
   - Check lifecycle states accurate
   - Verify vendor invoice state updates

3. **User feedback:**
   - Contact warehouse team
   - Ask about any issues

### Week 1: Daily Checks

**Daily checklist:**

- [ ] New serials created without errors
- [ ] Lifecycle states transitioning correctly
- [ ] Vendor invoice states updating when bills posted
- [ ] No error logs related to dtx_serial_ext
- [ ] Users report no issues

### Month 1: Weekly Reviews

**Weekly tasks:**

- Review serial data quality
- Check for serials stuck in wrong states
- Verify vendor invoice tracking working
- Collect user feedback
- Plan improvements if needed

---

## 🐛 TROUBLESHOOTING

### Issue 1: Module Won't Install

**Symptoms:**
- "Module not found" error
- Installation fails

**Solutions:**

1. **Check module files:**
   ```bash
   ls -la /opt/odoo/addons/custom/dtx_serial_ext/
   # Must have: __init__.py, __manifest__.py
   ```

2. **Check permissions:**
   ```bash
   sudo chown -R odoo:odoo /opt/odoo/addons/custom/dtx_serial_ext
   ```

3. **Check addons_path:**
   ```bash
   grep addons_path /etc/odoo/odoo.conf
   # Must include: /opt/odoo/addons/custom
   ```

4. **Update apps list again:**
   - Apps > Update Apps List

### Issue 2: Vendor Invoice State Not Updating

**Symptoms:**
- Bill posted, but state still "missing"

**Solutions:**

1. **Check logs:**
   ```bash
   sudo tail -100 /var/log/odoo/odoo-server.log | grep "DTX Serial"
   # Look for: "Vendor bill XXX posted for PO YYY"
   ```

2. **Manual trigger:**
   ```python
   lot = env['stock.lot'].search([('name', '=', 'SERIAL_NAME')])
   lot._compute_vendor_invoice_state()
   print(f"State: {lot.vendor_invoice_state}")
   ```

3. **Verify bill properly linked:**
   - Check bill's "Source Document" field = PO number
   - Check PO linked to serial

### Issue 3: Lifecycle State Not Changing

**Symptoms:**
- Deliver product, but state still "stock"

**Check logs:**
```bash
sudo tail -100 /var/log/odoo/odoo-server.log | grep "DTX Serial.*Lot.*->"
# Should see: "Lot ABC123 -> DELIVERED"
```

**Verify locations:**
- Source location usage = "internal"
- Dest location usage = "customer"

**Manual fix:**
```python
lot = env['stock.lot'].search([('name', '=', 'SERIAL_NAME')])
lot.lifecycle_state = 'delivered'
```

---

## 🔄 ROLLBACK PROCEDURE

**If critical issues arise:**

### Step 1: Stop Odoo

```bash
sudo systemctl stop odoo
```

### Step 2: Restore Database

```bash
# Drop current database
sudo -u postgres psql -c "DROP DATABASE production_db;"

# Restore from backup
sudo -u postgres psql -c "CREATE DATABASE production_db OWNER odoo_user;"
psql -U odoo_user -d production_db < backup_YYYYMMDD_HHMMSS.sql
```

### Step 3: Remove Module Files

```bash
sudo rm -rf /opt/odoo/addons/custom/dtx_serial_ext
```

### Step 4: Restart Odoo

```bash
sudo systemctl start odoo
```

### Step 5: Verify System

- Login as admin
- Check data intact
- Verify no errors

---

## 📞 SUPPORT

**Issues during deployment:**

1. **Check documentation:**
   - [TROUBLESHOOTING.md](../TROUBLESHOOTING.md)
   - [HOW_TO_TEST.md](testing/HOW_TO_TEST.md)

2. **Check logs:**
   ```bash
   sudo tail -200 /var/log/odoo/odoo-server.log
   ```

3. **Contact support:**
   - Email: [SUPPORT_EMAIL]
   - Phone: [SUPPORT_PHONE]
   - Include:
     - Error message (full text)
     - Steps to reproduce
     - Log excerpts
     - Screenshot if applicable

---

## ✅ DEPLOYMENT SUCCESS CRITERIA

**Deployment is successful when:**

- [x] Module installed without errors
- [x] All required products configured for serial tracking
- [x] Test PO → Receipt → Bill flow works
- [x] Vendor invoice state auto-updates when bills posted
- [x] Test SO → Delivery flow works
- [x] Lifecycle states transition correctly
- [x] Users can access Device Serials menu
- [x] No errors in logs related to dtx_serial_ext
- [x] Backup created and verified
- [x] Rollback procedure tested (in staging)
- [x] Users trained and comfortable with new features

---

**DTX Serial Extension v2.1.1 - Production Deployment Guide**
**Last Updated:** 2025-12-25
