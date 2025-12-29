# 🚀 Odoo 18 Migration Guide - DTX Project

## 📋 Overview

This guide documents the migration of DTX custom modules from Odoo 16 to Odoo 18.

**Migration Type:** Clean installation (no data migration)
**Estimated Time:** 2-5 days
**Current Status:** ✅ Test environment ready

---

## 🔍 Research Summary

### Odoo 18 Key Breaking Changes

Based on official documentation ([ORM Changelog](https://www.odoo.com/documentation/18.0/developer/reference/backend/orm/changelog.html)), here are the critical changes affecting our modules:

#### 1. **Deprecated Methods**
- ❌ `name_get()` → Use `display_name` field instead
- ❌ `fields_get_keys()` → Deprecated
- ❌ `get_xml_id()` → Deprecated
- ❌ `_mapped_cache()` → Removed

#### 2. **Method Signature Changes**
- ⚠️ `search()`, `search_count()`, `_search()`: argument `args` renamed to `domain`
- ⚠️ `_read_group()`: New signature
- ✅ NEW: `search_fetch()` and `fetch()` methods (better performance)

#### 3. **Removed Features**
- ❌ `limit` attribute of One2many and Many2many fields
- ❌ `column_format` and `deprecated` attributes of Field
- ❌ `_sequence` attribute of Model

#### 4. **View Changes (Minor)**
- ⚠️ Odoo 18.2: "Mobile" field removed from Contacts model
- ⚠️ Possible `attrs` syntax updates (need testing)

**Sources:**
- [Odoo 18 Release Notes](https://www.odoo.com/odoo-18-release-notes)
- [ORM API Changelog](https://www.odoo.com/documentation/18.0/developer/reference/backend/orm/changelog.html)
- [Migration Guide from Odoo 16 to 18](https://dev.to/webbycrownsolutions/odoo-16-modules-to-odoo-18-migration-guide-3048)

---

## 🧪 Test Environment Setup

### Architecture

```
┌─────────────────────────────────────────────────────┐
│  Odoo 16 (Production)      Odoo 18 (Test)          │
│  ─────────────────────     ──────────────────       │
│  Port: 8069                Port: 8018               │
│  DB: dtx_dev               DB: dtx_dev_v18          │
│  Addons: /addons           Addons: /addons-v18     │
│  Postgres: 5432            Postgres: 5433           │
└─────────────────────────────────────────────────────┘
```

### Docker Setup

**Files:**
- `docker-compose.yml` → Odoo 16 (unchanged)
- `docker-compose-v18.yml` → Odoo 18 (NEW)

**Start Odoo 18:**
```bash
cd /Users/trungns/dtx_project/odoo-dev
docker-compose -f docker-compose-v18.yml up -d
```

**Access:**
- Odoo 18: http://localhost:8018
- Odoo 16: http://localhost:8069 (still running)

**Stop Odoo 18:**
```bash
docker-compose -f docker-compose-v18.yml down
```

---

## 📦 Module Updates

### Version Changes

| Module | Odoo 16 Version | Odoo 18 Version |
|--------|----------------|-----------------|
| dtx_serial_ext | 16.0.2.2.0 | 18.0.2.2.0 |
| dtx_product_standards | 16.0.1.2.0 | 18.0.1.2.0 |

**Changes Made:**
- ✅ Updated `__manifest__.py` versions
- ✅ Copied to `/addons-v18` for isolated testing
- ⏳ Code changes pending (after testing)

---

## 🧐 Impact Analysis

### dtx_serial_ext (v2.2.0 → v18.0.2.2.0)

**Files to Review:**
- `models/stock_lot.py` - Many2one fields, computed fields
- `models/account_move.py` - Hook methods
- `models/stock_move_line.py` - Stock move logic
- `views/stock_lot_views.xml` - View definitions

**Potential Issues:**
1. ⚠️ `search()` calls with `args` parameter → Change to `domain`
2. ⚠️ Any `name_get()` overrides → Use `display_name` compute
3. ✅ Many2one/Many2many fields → Should be compatible
4. ✅ Computed fields with `@api.depends` → Should work
5. ✅ XML views with `attrs` → Need testing

**Risk Level:** 🟡 **Low-Medium**

---

### dtx_product_standards (v1.2.0 → v18.0.1.2.0)

**Files to Review:**
- `models/product_template.py` - Selection fields, computed fields
- `models/dtx_bom_template.py` - BOM template logic
- `wizards/*.py` - Wizard models
- `views/*.xml` - All view files

**Potential Issues:**
1. ⚠️ Selection field definitions → Should be compatible
2. ⚠️ Wizard (`TransientModel`) → Need testing
3. ⚠️ BOM generation logic → Check mrp module changes
4. ✅ View inheritance with XPath → Should work
5. ⚠️ Menu structure → Need verification

**Risk Level:** 🟡 **Low-Medium**

---

## ✅ Testing Checklist

### Phase 1: Installation Testing
- [ ] Create database `dtx_dev_v18` on Odoo 18
- [ ] Install `dtx_serial_ext` module
- [ ] Install `dtx_product_standards` module
- [ ] Check for installation errors
- [ ] Verify menu structure

### Phase 2: dtx_serial_ext Testing
- [ ] Create product with serial tracking
- [ ] Create serial numbers
- [ ] Test computed fields (vendor_invoice_state, etc.)
- [ ] Test Many2many relationships (PO, SO, Bills)
- [ ] Test replacement invoice functionality
- [ ] Test stock move tracking
- [ ] Verify view rendering

### Phase 3: dtx_product_standards Testing
- [ ] Create products with DTX types
- [ ] Test checklist tab (computed fields)
- [ ] Test "Áp dụng chuẩn DTX" wizard
- [ ] Create BOM Template
- [ ] Add components to BOM
- [ ] Generate mrp.bom from template
- [ ] Test subcontracting setup
- [ ] Verify all menus work

### Phase 4: Integration Testing
- [ ] Run `setup_dtx_data.py` script
- [ ] Test full subcontracting workflow:
  - Create PO for components
  - Receive components with serials
  - Create subcontracting PO
  - Deliver components to subcontractor
  - Receive finished Kiosks
  - Verify serial tracking
- [ ] Test vendor bill linking
- [ ] Test replacement invoice flow

### Phase 5: Performance & Compatibility
- [ ] Check query performance
- [ ] Verify no deprecated warnings in logs
- [ ] Test with multiple users (if applicable)
- [ ] Export/Import data (if needed)

---

## 📝 Expected Code Changes

### Change 1: search() domain parameter

**Before (Odoo 16):**
```python
records = self.env['product.template'].search([('x_dtx_type', '=', 'device_serialized')])
```

**After (Odoo 18):**
```python
# Same syntax works! 'args' was just parameter name in method definition
records = self.env['product.template'].search([('x_dtx_type', '=', 'device_serialized')])
```

**Impact:** ✅ None (we don't use `args` keyword explicitly)

---

### Change 2: name_get() deprecation

**Check if we override `name_get()`:**
```bash
grep -r "def name_get" addons-v18/
```

**If found:** Replace with `display_name` computed field

---

### Change 3: XML attrs syntax (if needed)

**Before:**
```xml
<field name="x_dtx_type" attrs="{'invisible': [('type', '!=', 'product')]}"/>
```

**After (modern Odoo):**
```xml
<field name="x_dtx_type" invisible="type != 'product'"/>
```

**Impact:** ⏳ Need to verify in testing

---

## 🎯 Migration Timeline

### Day 1: Setup & Initial Testing (4-6 hours)
- ✅ Setup Docker Compose for Odoo 18
- ✅ Update __manifest__.py versions
- ⏳ Create database on Odoo 18
- ⏳ Install modules
- ⏳ Check for immediate errors

### Day 2: Code Fixes & Testing (4-6 hours)
- ⏳ Fix any installation errors
- ⏳ Update deprecated method calls
- ⏳ Test all computed fields
- ⏳ Test all wizards
- ⏳ Fix XML view issues (if any)

### Day 3: Integration Testing (4-6 hours)
- ⏳ Run full subcontracting workflow
- ⏳ Test serial tracking end-to-end
- ⏳ Test BOM template generation
- ⏳ Verify all features work

### Day 4-5: Bug Fixes & Polish (if needed)
- ⏳ Fix edge cases
- ⏳ Performance optimization
- ⏳ Documentation updates

---

## 🚧 Known Risks

### High Risk
- ❌ None identified (modules are relatively simple)

### Medium Risk
- ⚠️ BOM generation logic may need updates if `mrp` module changed
- ⚠️ Wizard behavior changes (TransientModel)
- ⚠️ Menu structure changes in Odoo 18

### Low Risk
- ✅ Computed fields should work (same syntax)
- ✅ Many2one/Many2many relationships compatible
- ✅ View inheritance (XPath) should work

---

## 📊 Decision Matrix

### Should we migrate to Odoo 18?

| Factor | Odoo 16 | Odoo 18 | Winner |
|--------|---------|---------|--------|
| Long-term support | Until 2027 | Until 2029+ | 18 |
| Stability | ✅ Very stable | ⚠️ New (may have bugs) | 16 |
| Features | Sufficient | More features | 18 |
| Migration effort | N/A | 2-5 days | 16 |
| Community support | ✅ Mature | 🌱 Growing | 16 |

**Recommendation:**

**If you need:**
- ✅ **Production stability NOW** → Stay on Odoo 16
- ✅ **Future-proof solution** → Migrate to Odoo 18
- ✅ **Latest features** → Migrate to Odoo 18

**Suggested approach:**
1. Test thoroughly on Odoo 18 (1-2 weeks)
2. Keep Odoo 16 in production
3. Switch to Odoo 18 when confident (after finding/fixing all issues)

---

## 🔗 Resources

### Official Documentation
- [Odoo 18 Release Notes](https://www.odoo.com/odoo-18-release-notes)
- [Odoo 18 Developer Documentation](https://www.odoo.com/documentation/18.0/)
- [ORM API Changelog](https://www.odoo.com/documentation/18.0/developer/reference/backend/orm/changelog.html)

### Community Resources
- [Odoo 16 to 18 Migration Guide](https://dev.to/webbycrownsolutions/odoo-16-modules-to-odoo-18-migration-guide-3048)
- [Odoo Community Forum](https://www.odoo.com/forum)

---

## 📞 Support

**If you encounter issues:**
1. Check Odoo 18 logs: `docker-compose -f docker-compose-v18.yml logs -f odoo-v18`
2. Search Odoo forums
3. Check GitHub issues: https://github.com/odoo/odoo/issues
4. Document issues in this guide for future reference

---

**Last Updated:** 2025-12-29
**Status:** ✅ Test environment ready, awaiting testing
**Next Step:** Create database and install modules on Odoo 18

---

Generated with [Claude Code](https://claude.com/claude-code)
