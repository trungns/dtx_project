# Database Backups

## Current Backup

**File**: `odoo_db_2026_01_04_pakd_v1.3.0.sql.gz`
**Date**: 2026-01-04 Evening
**Size**: 1.7 MB (compressed from 15 MB)
**Module Version**: dtx_sales_pakd_contract v16.0.1.3.0

### What's Included:
- ✅ All Odoo base modules
- ✅ dtx_sales_pakd_contract v1.3.0 (PAKD formulas fixed)
- ✅ dtx_vendorbill_alert module
- ✅ Admin user (admin/admin)
- ✅ Default company configuration
- ✅ Sample taxes (VAT 0%, 10%)
- ✅ AR Aging configuration
- ⚠️ No test data yet (no products, partners, or PAKDs created)

### Why This Backup?
This backup was created right after:
1. Module upgrade to v1.3.0
2. PAKD formula fixes
3. Database schema updated (added cushion_amount, referral_commission_percent fields)
4. Ready for UAT testing

---

## How to Restore on MacBook M1

### Quick Restore (Recommended)

```bash
# 1. Stop Odoo
cd ~/dtx_project/odoo-dev
docker-compose stop odoo

# 2. Drop and recreate database
docker-compose exec db dropdb -U odoo odoo --if-exists
docker-compose exec db createdb -U odoo odoo

# 3. Restore from backup
cd ~/dtx_project/backups
gunzip -c odoo_db_2026_01_04_pakd_v1.3.0.sql.gz | \
  docker-compose -f ../odoo-dev/docker-compose.yml exec -T db psql -U odoo -d odoo

# 4. Start Odoo
cd ../odoo-dev
docker-compose start odoo

# 5. Verify
# Open http://localhost:8069
# Login: admin / admin
```

### Using Restore Script (Easier)

```bash
cd ~/dtx_project/backups
./restore-db.sh odoo_db_2026_01_04_pakd_v1.3.0.sql.gz
```

---

## Backup Contents Details

### Modules Installed:
```
base, web, sale, sale_management, account, product
dtx_sales_pakd_contract (v16.0.1.3.0)
dtx_vendorbill_alert
```

### Database Schema:
- **dtx_pakd** table with new fields:
  - cushion_amount (numeric) ✨ NEW
  - referral_commission_percent (float) ✨ NEW
- **dtx_pakd_line** table
- **sale_order** with AR aging fields (x_ar_*)
- **dtx_ar_aging_summary** SQL view
- **dtx_ar_aging_config** table

### Master Data:
- Admin user: admin / admin
- Default company
- Default taxes: VAT 0%, VAT 10%
- AR Aging buckets: 7/15/30/60/90 days

### What's NOT Included:
- ❌ No products created yet
- ❌ No partners created yet
- ❌ No quotations/PAKDs created yet
- ❌ No invoices

**Why?** This is a clean base for testing. You'll create test data following MANUAL_UAT_GUIDE.md

---

## Create New Backup

### Manual Backup:
```bash
cd ~/dtx_project/odoo-dev

# Backup to SQL
docker-compose exec -T db pg_dump -U odoo -d odoo --clean --if-exists \
  > ../backups/odoo_db_$(date +%Y_%m_%d).sql

# Compress
cd ../backups
gzip -9 odoo_db_$(date +%Y_%m_%d).sql
```

### Using Backup Script:
```bash
cd ~/dtx_project/backups
./backup-db.sh
```

---

## Backup Strategy

### When to Backup:
1. ✅ After major module upgrades
2. ✅ Before testing destructive operations
3. ✅ After creating important test data
4. ✅ Before database migrations
5. ✅ End of day (if you made significant changes)

### Naming Convention:
```
odoo_db_YYYY_MM_DD_description.sql.gz

Examples:
- odoo_db_2026_01_04_pakd_v1.3.0.sql.gz
- odoo_db_2026_01_05_with_test_data.sql.gz
- odoo_db_2026_01_06_before_upgrade.sql.gz
```

---

## Troubleshooting

### Error: "database odoo already exists"
```bash
docker-compose exec db dropdb -U odoo odoo --if-exists
docker-compose exec db createdb -U odoo odoo
```

### Error: "Permission denied"
```bash
# Make restore script executable
chmod +x restore-db.sh backup-db.sh
```

### Error: "gunzip: command not found" (on Windows)
```bash
# Use Git Bash or WSL
# Or decompress manually:
gunzip odoo_db_2026_01_04_pakd_v1.3.0.sql.gz
# Then use psql directly
```

### Restore takes too long
This is normal - 15MB SQL takes ~30-60 seconds to restore.
Watch progress: `docker-compose logs -f db`

---

## Best Practices

1. **Always stop Odoo before restore**
   ```bash
   docker-compose stop odoo
   ```

2. **Verify backup after creation**
   ```bash
   gunzip -t odoo_db_2026_01_04_pakd_v1.3.0.sql.gz
   # If no error = backup is valid
   ```

3. **Keep multiple backups**
   - Don't overwrite old backups
   - Keep at least 3 recent backups
   - Delete old backups after 1 month

4. **Test restore periodically**
   - Restore to a test database
   - Verify data integrity

5. **Document what's in each backup**
   - Add description to filename
   - Update this README

---

## File Sizes

| Backup | Uncompressed | Compressed | Ratio |
|--------|--------------|------------|-------|
| Base (empty) | ~8 MB | ~800 KB | 10:1 |
| With modules | ~15 MB | ~1.7 MB | 9:1 |
| With test data | ~20 MB | ~2.5 MB | 8:1 |

**Tip**: gzip compression saves ~90% of space!

---

## Next Steps After Restore

1. **Verify Odoo is running**
   ```bash
   docker-compose ps
   docker-compose logs odoo --tail=50
   ```

2. **Login and check**
   - URL: http://localhost:8069
   - Login: admin / admin
   - Check Apps → Installed → dtx_sales_pakd_contract v1.3.0

3. **Create test data**
   - Follow: MANUAL_UAT_GUIDE.md STEP 1
   - Or run: `setup_uat_quy_chau_data.py`

4. **Test PAKD formulas**
   - Follow: MANUAL_UAT_GUIDE.md STEP 2-10

---

## Backup History

| Date | File | Size | Description |
|------|------|------|-------------|
| 2026-01-04 | odoo_db_2026_01_04_pakd_v1.3.0.sql.gz | 1.7 MB | After PAKD v1.3.0 upgrade, formulas fixed |

---

**Created**: 2026-01-04
**Platform**: Windows Desktop → MacBook M1
**Status**: ✅ Ready for restore
