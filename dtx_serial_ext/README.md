# DTX Serial Extension

Extended serial/lot tracking for DTX device lifecycle management.

**Version:** 2.1.0 | **Odoo:** 16.0 | **License:** LGPL-3

---

## 🎯 Quick Overview

This module extends Odoo 16's `stock.lot` model with:
- ✅ Dual serial number tracking (supplier + DTX internal)
- ✅ Device lifecycle state management (6 states with auto-update)
- ✅ **Vendor invoice tracking - FULLY AUTOMATIC** (v2.1.0+)
- ✅ Purchase/Sales order automatic linking
- ✅ Warranty period management
- ✅ Mobile-friendly UI with enhanced search and filters

---

## 📚 Documentation

### Essential Guides
- **[INSTALLATION.md](INSTALLATION.md)** - How to install and setup this module
- **[docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)** - Common issues and solutions
- **[docs/testing/HOW_TO_TEST.md](docs/testing/HOW_TO_TEST.md)** - Testing workflows
- **[docs/upgrade/UPGRADE_TO_V2.1.md](docs/upgrade/UPGRADE_TO_V2.1.md)** - Upgrade from v2.0.x to v2.1.0

### Related Documentation
Full project documentation: [`/docs/`](../docs/)

---

## ✨ Key Features

### 1. Dual Serial Number Tracking
- **Supplier Serial** (`stock.lot.name`): Primary key, from manufacturer
- **DTX Internal Serial** (`dtx_serial_internal`): Optional customer-facing ID
- Both searchable across the system

### 2. Automatic Lifecycle State Tracking

States automatically update based on stock moves:

| State | When It Happens | Color |
|-------|----------------|-------|
| **In Stock** | Received from supplier/production | 🟢 Green |
| **Allocated** | Reserved for project (manual) | 🔵 Blue |
| **Delivered** | Shipped to customer | ⚪ Default |
| **Installed** | Deployed at site (manual) | 🟢 Green |
| **Maintenance** | Moved to maintenance location | 🟡 Yellow |
| **Scrapped** | Moved to scrap location | 🔴 Red |

### 3. 🎉 **NEW in v2.1.0: Fully Automatic Vendor Invoice Tracking**

**No more manual updates!** Vendor invoice state now automatically computes:

```
Receipt Validated → Bill Posted → State INSTANT "linked" ✨
Bill Cancelled → State AUTO "missing"
```

**States:**
- **Invoice Missing** 🔴 - No bill posted yet (normal flow)
- **Invoice Linked** 🟢 - Bill exists and posted
- **Invoice Replaced** 🟡 - Manual override for corrections

### 4. Automatic Purchase/Sales Order Linking

**Computed via stock moves:**
- Purchase Orders → Shows all POs that supplied this serial
- Vendor Bills → Auto-displays bills from linked POs
- Sales Orders → Shows all SOs that delivered this serial
- Customer Invoices → Auto-displays invoices from linked SOs

### 5. Warranty Management
- Start/end dates with active indicator
- Visual active/inactive status
- Searchable by warranty status

---

## 🚀 Quick Start

### Installation

```bash
# 1. Copy module to addons
cp -r dtx_serial_ext /path/to/odoo/addons/

# 2. Restart Odoo
docker-compose restart web  # or your restart method

# 3. Update apps list & install
# In Odoo UI: Apps > Update Apps List > Search "DTX Serial" > Install
```

See [INSTALLATION.md](INSTALLATION.md) for detailed instructions.

### Basic Usage

**1. Setup Product:**
- Product Type: Storable
- Tracking: By Unique Serial Number

**2. Receive Devices:**
- Create PO → Validate Receipt → Assign Serial
- Lifecycle state: "In Stock" ✅
- Vendor invoice state: "Invoice Missing" (normal)

**3. Post Vendor Bill:**
- Create Bill from PO → Post
- Vendor invoice state: **AUTO "Invoice Linked"** ✨ (v2.1.0+)

**4. Deliver to Customer:**
- Create SO → Deliver → Assign Serial
- Lifecycle state: **AUTO "Delivered"** ✅

---

## 🔧 Technical Details

### Models Extended

**`stock.lot` (Serial/Lot Numbers):**
- New fields: dtx_serial_internal, lifecycle_state, customer_id, vendor_invoice_state, etc.
- Computed fields: purchase_order_ids, vendor_bill_ids, sale_order_ids, customer_invoice_ids
- Enhanced search: Both serials searchable

**`stock.move.line` (Stock Moves):**
- Override `_action_done()`: Auto-update lifecycle state based on location types
- Logging for debugging

### Automatic Behaviors

| Trigger | Action | Auto-Update |
|---------|--------|-------------|
| Receipt from supplier | → Internal location | lifecycle_state = 'stock' |
| Delivery to customer | → Customer location | lifecycle_state = 'delivered' |
| Move to scrap | → Scrap location | lifecycle_state = 'scrapped' |
| Move to maintenance | → "maintenance" location | lifecycle_state = 'maintenance' |
| **Bill posted** (v2.1.0) | vendor_bill_ids updated | vendor_invoice_state = 'linked' ✨ |
| **Bill cancelled** (v2.1.0) | vendor_bill_ids cleared | vendor_invoice_state = 'missing' |

### Views

**Tree View:** Color-coded badges for quick status overview
**Form View:** Mobile-friendly sections with Purchase/Sales tracking
**Search:** Filters by state, customer, PO, SO, warranty

**Menu:** Inventory > Products > Device Serials

---

## 📋 What's New in v2.1.0

🎉 **MAJOR: Vendor Invoice State is now FULLY AUTOMATIC!**

**Before (v2.0.x):**
- ❌ State only checked when validating receipt
- ❌ Bill posted after receipt → State stuck "missing"
- ❌ Required manual update or Python script

**Now (v2.1.0):**
- ✅ State auto-computes from `vendor_bill_ids`
- ✅ Bill posted → State INSTANT "linked"
- ✅ Bill cancelled → State AUTO "missing"
- ✅ NO manual intervention needed!

See [docs/upgrade/UPGRADE_TO_V2.1.md](docs/upgrade/UPGRADE_TO_V2.1.md) for upgrade instructions.

---

## 🛠 Troubleshooting

**Issue:** Vendor invoice state not updating
**Solution:** See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

**Issue:** Lifecycle state not changing
**Solution:** Check location types (internal/customer/scrap), see logs

**Need Help?**
- Check [docs/testing/HOW_TO_TEST.md](docs/testing/HOW_TO_TEST.md)
- Review logs: `docker-compose logs -f web | grep "DTX Serial"`
- Contact DTX development team

---

## 📦 Dependencies

- `stock` - Odoo standard
- `product` - Odoo standard
- `purchase` - For PO/vendor bill tracking
- `sale` - For SO/customer invoice tracking
- `account` - For invoice/bill tracking

**Compatible with:** Odoo 16.0 Community/Enterprise

---

## 📄 License

LGPL-3

## 👥 Author

DTX - Smart Queue Management Systems

---

## 🔗 Links

- Module repository: (internal)
- Full documentation: [`../docs/`](../docs/)
- Report issues: Contact DTX dev team

---

**Built for DTX Smart Queue Management Systems**
