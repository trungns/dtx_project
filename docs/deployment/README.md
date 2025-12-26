# Deployment Guide

Documentation for installing and deploying DTX Odoo modules.

## 🚀 Available Guides

### [Installation Guide](installation-guide.md)
**Audience:** System administrators, IT staff
**Time:** 30 minutes
**Content:**
- Module structure overview
- Step-by-step installation
- Configuration steps
- 10 detailed test scenarios
- Troubleshooting guide

**Read this to:** Install and validate DTX modules on Odoo 16.

---

### [Production Deployment](production-deployment.md) *(Coming Soon)*
**Audience:** DevOps, system administrators
**Time:** TBD
**Content:**
- Production environment setup
- Security hardening
- Performance tuning
- Backup and recovery
- Monitoring

**Read this to:** Deploy DTX system to production environment.

---

## 🎯 Deployment Paths

### Development → Staging → Production

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Development │───▶│   Staging   │───▶│ Production  │
│  (Docker)   │    │ (Test Data) │    │ (Live Data) │
└─────────────┘    └─────────────┘    └─────────────┘
```

### Quick Reference

| Environment | Guide | Purpose |
|-------------|-------|---------|
| Development | [Dev Environment](../developer-guide/development-environment.md) | Code & test |
| Staging | [Installation Guide](installation-guide.md) | Integration test |
| Production | [Production Deployment](production-deployment.md) | Live system |

---

## 📋 Pre-Installation Checklist

Before installing on any environment:

### System Requirements
- [ ] Odoo 16 Community Edition installed
- [ ] PostgreSQL 13+ running
- [ ] Python 3.10+ available
- [ ] Sufficient disk space (500MB+ free)
- [ ] Network access (if downloading dependencies)

### Odoo Requirements
- [ ] Standard `stock` module installed
- [ ] Standard `product` module installed
- [ ] Admin access to Odoo
- [ ] Database created and accessible

### Pre-Installation Tasks
- [ ] Backup existing database
- [ ] Review module dependencies
- [ ] Plan downtime window (if production)
- [ ] Notify users (if production)

---

## 🔧 Installation Process

### Quick Installation (Development)

```bash
# 1. Copy module
cp -r dtx_serial_ext /path/to/odoo/addons/

# 2. Restart Odoo
sudo systemctl restart odoo

# 3. In Odoo UI
Apps → Update Apps List → Search "DTX Serial" → Install
```

See [Installation Guide](installation-guide.md) for detailed steps.

---

### Production Installation

See [Production Deployment Guide](production-deployment.md) *(coming soon)*

Key steps:
1. Test on staging first
2. Backup production database
3. Schedule maintenance window
4. Deploy module
5. Run validation tests
6. Monitor post-deployment

---

## 🧪 Testing & Validation

### Test Scenarios

All environments should pass these tests before go-live:

1. ✅ Module installs without errors
2. ✅ Menu items appear correctly
3. ✅ Create product with serial tracking
4. ✅ Create serial with dual serials
5. ✅ Search works on both serials
6. ✅ Vendor invoice state auto-updates
7. ✅ Lifecycle state updates on stock moves
8. ✅ Warranty active calculates correctly
9. ✅ Filters and groups work
10. ✅ Mobile UI displays properly

See [Installation Guide - Testing](installation-guide.md#testing-guide) for detailed test procedures.

---

## 🔄 Upgrade Process

### Upgrading Existing Installation

```bash
# 1. Backup database
pg_dump odoo_db > backup_$(date +%Y%m%d).sql

# 2. Update module files
cp -r dtx_serial_ext_new/* /path/to/odoo/addons/dtx_serial_ext/

# 3. Restart Odoo
sudo systemctl restart odoo

# 4. Upgrade module in UI
Apps → Search module → Upgrade
```

---

## 🗂️ Configuration

### Post-Installation Configuration

#### 1. Product Category Setup
```
Inventory → Configuration → Product Categories
- Name: DTX Devices
- Costing Method: Average Cost (AVCO)
- Inventory Valuation: Automated
```

#### 2. Product Setup
```
Inventory → Products → Products
For each device:
- Product Type: Storable Product
- Tracking: By Unique Serial Number
- Category: DTX Devices
```

#### 3. Warehouse Locations (Optional)
```
Inventory → Configuration → Locations
Create: WH/Stock/Maintenance
- Location Type: Internal Location
```

See [Installation Guide - Configuration](installation-guide.md#post-installation-configuration) for details.

---

## 🔐 Security Considerations

### Access Rights
- Default: Uses standard Odoo stock security
- Users: Inventory/User (read, write, create)
- Managers: Inventory/Manager (read, write, create, delete)

### Custom Security (If Needed)
```xml
<!-- Add custom security groups in security/ir.model.access.csv -->
```

---

## 📊 Deployment Checklist

### Before Deployment
- [ ] Module tested on development
- [ ] Module tested on staging
- [ ] All test scenarios passed
- [ ] Database backed up
- [ ] Users notified
- [ ] Rollback plan prepared

### During Deployment
- [ ] Copy module files
- [ ] Restart Odoo service
- [ ] Update apps list
- [ ] Install/upgrade module
- [ ] Verify no errors in logs

### After Deployment
- [ ] Run validation tests
- [ ] Check error logs
- [ ] Verify performance
- [ ] Train users (if needed)
- [ ] Monitor for 24 hours
- [ ] Document any issues

---

## 🆘 Troubleshooting

### Module Not Appearing
```bash
# Check module path
ls -la /path/to/odoo/addons/dtx_serial_ext/

# Check Odoo config
cat /etc/odoo/odoo.conf | grep addons_path

# Restart and update
sudo systemctl restart odoo
# Then: Apps → Update Apps List
```

### Installation Errors
```bash
# Check Odoo logs
tail -f /var/log/odoo/odoo-server.log

# Check PostgreSQL
sudo -u postgres psql -d odoo_db -c "SELECT * FROM ir_module_module WHERE name='dtx_serial_ext';"
```

### Permission Issues
```bash
# Fix file permissions
chown -R odoo:odoo /path/to/odoo/addons/dtx_serial_ext/
chmod -R 755 /path/to/odoo/addons/dtx_serial_ext/
```

See [Installation Guide - Troubleshooting](installation-guide.md#troubleshooting) for more.

---

## 📈 Monitoring Post-Deployment

### What to Monitor

| Metric | Tool | Alert If |
|--------|------|----------|
| Error logs | `tail -f odoo.log` | Any ERROR level |
| Database size | `pg_database_size()` | >80% capacity |
| Response time | Browser dev tools | >3 seconds |
| CPU usage | `top`, `htop` | >80% sustained |
| Memory usage | `free -h` | >90% |

### Health Check Queries

```sql
-- Check module status
SELECT name, state FROM ir_module_module WHERE name LIKE 'dtx_%';

-- Check serial records
SELECT COUNT(*) FROM stock_lot WHERE dtx_serial_internal IS NOT NULL;

-- Check for errors
SELECT * FROM ir_logging WHERE level='ERROR' AND create_date > NOW() - INTERVAL '1 hour';
```

---

## 📝 Rollback Plan

If deployment fails:

```bash
# 1. Stop Odoo
sudo systemctl stop odoo

# 2. Restore database backup
psql -U odoo -d odoo_db < backup_20251223.sql

# 3. Remove/revert module files
rm -rf /path/to/odoo/addons/dtx_serial_ext/

# 4. Start Odoo
sudo systemctl start odoo

# 5. Verify system operational
```

---

## 🎓 Training Materials

### For End Users
- [User Guide](../user-guide/)
- [Quick Start](../user-guide/quick-start.md)
- [Module Manual](../user-guide/dtx-serial-extension.md)

### For Administrators
- This guide
- [Installation Guide](installation-guide.md)
- [Developer Guide](../developer-guide/)

---

## 📅 Deployment Timeline

### Recommended Schedule

**Week 1-2: Development**
- Module development
- Unit testing
- Code review

**Week 3: Staging**
- Deploy to staging
- Integration testing
- User acceptance testing (UAT)

**Week 4: Production**
- Final testing on staging
- Production deployment
- User training
- Go-live support

---

## 🔗 Related Documentation

- [Development Environment](../developer-guide/development-environment.md)
- [API Reference](../developer-guide/api-reference.md)
- [System Architecture](../architecture/)
- [User Guide](../user-guide/)

---

**Last Updated:** 2025-12-23
**Next Review:** After production deployment
