# Quick Start Guide - Install Helpdesk Module

## ✅ Status: Ready to Install

OCA Helpdesk modules have been downloaded and are ready to install via Odoo UI.

---

## 📦 Step 1: Update Apps List

1. **Login to Odoo**: http://localhost:8069
2. **Go to Apps** menu (top menu)
3. **Click**: Apps → Update Apps List
4. **Confirm** the update dialog
5. **Wait** for the update to complete (~30 seconds)

---

## 🔍 Step 2: Search & Install Core Helpdesk

1. In **Apps** screen, remove "Apps" filter (click X on search bar)
2. **Search**: `helpdesk`
3. Find module: **Helpdesk Management** (`helpdesk_mgmt`)
   - Description: "Manage helpdesk tickets"
   - Author: Odoo Community Association (OCA)
4. **Click Install** button
5. **Wait** for installation (~1 minute)

---

## 🔗 Step 3: Install Sale Order Integration

After core module installed:

1. **Search**: `helpdesk sale`
2. Find module: **Helpdesk Management - Sale** (`helpdesk_mgmt_sale`)
   - Description: "Link helpdesk tickets to sale orders"
3. **Click Install**
4. **Wait** for installation

---

## ⏱️ Step 4: Install SLA Management (Optional but Recommended)

1. **Search**: `helpdesk sla`
2. Find module: **Helpdesk Management SLA** (`helpdesk_mgmt_sla`)
   - Description: "Service Level Agreement management"
3. **Click Install**
4. **Wait** for installation

---

## ⚙️ Step 5: Initial Configuration

After installation, you'll see new menu: **Helpdesk**

### Create Support Team

1. **Menu**: Helpdesk → Configuration → Teams
2. **Click**: Create
3. **Fill in**:
   - Name: `DTX Support Team`
   - Alias (email): `support@dtx.com` (optional)
4. **Save**

### Configure Stages

Default stages are already created:
- New
- In Progress
- Solved
- Closed

You can customize via: Helpdesk → Configuration → Stages

---

## 🎫 Step 6: Create First Test Ticket

1. **Menu**: Helpdesk → Tickets
2. **Click**: Create
3. **Fill in**:
   - Subject: `Test ticket - Camera issue`
   - Team: `DTX Support Team`
   - Partner: (Select any customer, e.g., VNPAY)
   - Priority: High
   - Description: `Testing helpdesk module installation`
4. **Save**

### Link to Sale Order

1. In the ticket form, you should see a **Sale Order** field
2. Select a sale order (e.g., S00164)
3. **Save**
4. **Verify**: Go to Sale Order → should see related tickets

---

## 📊 Step 7: Verify Installation

### Check Menu Items

You should now see:
- **Helpdesk** (top menu)
  - Tickets
  - Dashboard
  - Reporting
  - Configuration
    - Teams
    - Stages
    - Categories (if installed)
    - SLA Policies (if SLA module installed)

### Check Sale Order Form

1. Open any Sale Order (e.g., S00164)
2. You should see a **Tickets** tab or smart button
3. Can view tickets linked to this SO

---

## 🔧 Optional Modules to Consider

After basic installation works:

1. **helpdesk_mgmt_rating** - Customer satisfaction ratings
2. **helpdesk_mgmt_timesheet** - Track time spent on tickets
3. **helpdesk_mgmt_project** - Link tickets to project tasks
4. **helpdesk_type** - Categorize tickets by type

Install these later if needed.

---

## 🎯 Next Steps

After installation complete:

1. **Review**: [MANUAL_UAT_TEST_CASES.md - Section 7](MANUAL_UAT_TEST_CASES.md#7-bảo-trì--support)
2. **Run Test Case 21**: Activate Maintenance
3. **Run Test Case 22**: Customer Support Request
4. **Configure**:
   - Email gateway (to create tickets from emails)
   - SLA policies (response/resolution times)
   - Customer portal access
5. **Train support team** on using the module

---

## 📚 Documentation

### OCA Helpdesk Docs
- GitHub: https://github.com/OCA/helpdesk
- Module README: `/Users/trungns/dtx_project/odoo-dev/addons/helpdesk/helpdesk_mgmt/README.rst`

### Odoo Official Helpdesk Guide
- https://www.odoo.com/documentation/16.0/applications/services/helpdesk.html
- (Note: This is for Enterprise edition, but concepts are similar)

---

## ❓ Troubleshooting

### Module not showing in Apps list

**Solution**:
1. Make sure you clicked "Update Apps List"
2. Remove all search filters (click X on search bar)
3. Try searching just "helpdesk" without quotes

### Installation fails

**Check logs**:
```bash
docker logs dtx_odoo16 --tail 100
```

**Common issues**:
- Missing Python dependencies → restart Docker container
- Database lock → wait and try again
- Permission issues → check module folder permissions

### Sale Order field not showing in ticket

**Solution**:
1. Make sure `helpdesk_mgmt_sale` module is installed (not just helpdesk_mgmt)
2. Refresh browser (Ctrl+Shift+R)
3. Check if field is hidden in form view → Developer mode → Edit Form View

---

## ✅ Success Criteria

You'll know installation is successful when:

- [x] Helpdesk menu appears in top menu
- [x] Can create tickets
- [x] Can link tickets to Sale Orders
- [x] Sale Orders show ticket count/smart button
- [x] Can configure teams and stages
- [x] (Optional) Can set SLA policies

---

**Created**: 2026-01-15
**Last Updated**: 2026-01-15
**Status**: **READY TO INSTALL**
