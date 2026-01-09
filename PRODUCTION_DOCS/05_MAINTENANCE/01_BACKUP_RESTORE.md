# 🔄 Database Restore Instructions - Chi Tiết

**Database**: odoo_db_2026_01_04_pakd_v1.3.0.sql.gz
**Date Created**: 2026-01-04 Evening
**Module Version**: dtx_sales_pakd_contract v16.0.1.3.0
**Size**: 1.7 MB (compressed), 15 MB (uncompressed)

---

## 🎯 Quick Start (MacBook M1)

### Option 1: Sử dụng script (KHUYÊN DÙNG)

```bash
cd ~/dtx_project/backups
./restore-db.sh odoo_db_2026_01_04_pakd_v1.3.0.sql.gz
```

**Xong!** Script sẽ tự động làm tất cả.

### Option 2: Manual commands (Step by step)

Làm theo section **"Manual Restore"** bên dưới.

---

## 📋 Database Credentials

### PostgreSQL Database:
- **Host**: localhost (inside docker network: `db`)
- **Port**: 5432 (default PostgreSQL port)
- **Database Name**: `odoo`
- **Username**: `odoo`
- **Password**: `odoo`

### Odoo Admin User:
- **URL**: http://localhost:8069
- **Username**: `admin`
- **Email**: admin@example.com (nếu có)
- **Password**: `admin`

### Docker Container Names:
- **PostgreSQL**: `dtx_postgres`
- **Odoo**: `dtx_odoo16`

---

## 🛠️ Manual Restore (Step by Step)

### Step 1: Stop Odoo

```bash
cd ~/dtx_project/odoo-dev
docker-compose stop odoo
```

**Verify stopped**:
```bash
docker-compose ps
# odoo should show "Exit 0"
```

---

### Step 2: Drop existing database

```bash
docker-compose exec db dropdb -U odoo odoo --if-exists
```

**Command breakdown**:
- `docker-compose exec db` - Chạy command trong container `db`
- `dropdb` - PostgreSQL command để xóa database
- `-U odoo` - User name = `odoo`
- `odoo` - Database name = `odoo`
- `--if-exists` - Không báo lỗi nếu database không tồn tại

**Expected output**:
```
(No output = success)
```

---

### Step 3: Create new empty database

```bash
docker-compose exec db createdb -U odoo odoo
```

**Command breakdown**:
- `createdb` - PostgreSQL command để tạo database
- `-U odoo` - User name = `odoo`
- `odoo` - Database name = `odoo`

**Expected output**:
```
(No output = success)
```

---

### Step 4: Restore from backup

```bash
cd ~/dtx_project/backups
gunzip -c odoo_db_2026_01_04_pakd_v1.3.0.sql.gz | \
  docker-compose -f ../odoo-dev/docker-compose.yml exec -T db psql -U odoo -d odoo
```

**Command breakdown**:
- `gunzip -c` - Decompress file và output ra stdout (không tạo file mới)
- `|` - Pipe output sang command tiếp theo
- `docker-compose -f ../odoo-dev/docker-compose.yml` - Chỉ định docker-compose file
- `exec -T db` - Chạy command trong container `db` (no TTY)
- `psql` - PostgreSQL client
- `-U odoo` - User name = `odoo`
- `-d odoo` - Database name = `odoo`

**Expected output**:
```
DROP SCHEMA
DROP SCHEMA
CREATE SCHEMA
CREATE SCHEMA
...
CREATE TRIGGER
CREATE TRIGGER
(Many lines of SQL commands)
```

**Duration**: ~30-60 seconds

**If you see errors**: Các lỗi kiểu "DROP TABLE IF EXISTS" là bình thường (vì table chưa tồn tại).

---

### Step 5: Start Odoo

```bash
cd ~/dtx_project/odoo-dev
docker-compose start odoo
```

**Expected output**:
```
Starting dtx_odoo16 ... done
```

---

### Step 6: Wait for Odoo to start

```bash
docker-compose logs odoo --tail=50 -f
```

**Wait for this line**:
```
odoo.modules.registry: Registry loaded in X.XXXs
odoo.http: HTTP service (werkzeug) running on http://0.0.0.0:8069
```

**Press Ctrl+C** to stop watching logs.

---

### Step 7: Verify restore

Open browser:
```
http://localhost:8069
```

**Login**:
- Username: `admin`
- Password: `admin`

**Check**:
1. Apps menu → Installed
2. Find: `DTX Sales PAKD Contract`
3. Version should be: `16.0.1.3.0`

---

## ✅ Verification Checklist

After restore, verify these:

### 1. Database Connection
```bash
docker-compose exec db psql -U odoo -d odoo -c "SELECT version();"
```

**Expected**: PostgreSQL version info

### 2. Check Tables
```bash
docker-compose exec db psql -U odoo -d odoo -c "\dt" | grep dtx_pakd
```

**Expected**:
```
 public | dtx_pakd              | table | odoo
 public | dtx_pakd_line         | table | odoo
```

### 3. Check New Columns
```bash
docker-compose exec db psql -U odoo -d odoo -c "\d dtx_pakd" | grep cushion
```

**Expected**:
```
 cushion_amount              | numeric          |
 referral_commission_percent | double precision |
```

### 4. Login to Odoo
- URL: http://localhost:8069
- User: admin
- Pass: admin

### 5. Check Module Version
Navigate: Apps → Installed → Search "dtx_sales"

**Expected**: `DTX Sales PAKD Contract (16.0.1.3.0)`

---

## 🐛 Troubleshooting

### Problem 1: "database odoo already exists"

**Solution**:
```bash
docker-compose exec db dropdb -U odoo odoo --force
docker-compose exec db createdb -U odoo odoo
```

---

### Problem 2: "role odoo does not exist"

**Solution**:
```bash
# Create user
docker-compose exec db psql -U postgres -c "CREATE USER odoo WITH PASSWORD 'odoo' CREATEDB;"

# Create database
docker-compose exec db createdb -U odoo odoo
```

---

### Problem 3: "gunzip: command not found"

**Solution** (on Windows):
```bash
# Use Git Bash or WSL
# Or decompress manually:
gunzip odoo_db_2026_01_04_pakd_v1.3.0.sql.gz

# Then restore:
docker-compose exec -T db psql -U odoo -d odoo < odoo_db_2026_01_04_pakd_v1.3.0.sql
```

---

### Problem 4: Restore hangs / takes too long

**Check progress**:
```bash
# In another terminal:
docker-compose exec db psql -U odoo -d odoo -c "SELECT count(*) FROM ir_module_module;"
```

If number is increasing → restore is working.

**Normal duration**: 30-60 seconds for 15MB SQL file.

---

### Problem 5: "Cannot connect to database"

**Check database is running**:
```bash
docker-compose ps db
```

**Restart database**:
```bash
docker-compose restart db
```

**Check logs**:
```bash
docker-compose logs db --tail=100
```

---

### Problem 6: Odoo shows "Database not found"

**Fix**:
1. Restart Odoo:
```bash
docker-compose restart odoo
```

2. Clear browser cache: Ctrl+Shift+R

3. Or use incognito window

---

### Problem 7: Login fails with "Invalid credentials"

**Reset admin password**:
```bash
docker-compose exec db psql -U odoo -d odoo -c \
  "UPDATE res_users SET password='admin' WHERE login='admin';"
```

Then login with: admin / admin

---

## 📊 What's in This Backup?

### Modules Installed:
```sql
-- Check installed modules
docker-compose exec db psql -U odoo -d odoo -c \
  "SELECT name, state, latest_version FROM ir_module_module WHERE state='installed' AND name LIKE 'dtx%';"
```

**Expected**:
- dtx_sales_pakd_contract | installed | 16.0.1.3.0
- dtx_vendorbill_alert | installed | 1.0.0

### Database Size:
```bash
docker-compose exec db psql -U odoo -d odoo -c \
  "SELECT pg_size_pretty(pg_database_size('odoo'));"
```

**Expected**: ~15-20 MB

### Table Count:
```bash
docker-compose exec db psql -U odoo -d odoo -c \
  "SELECT count(*) FROM information_schema.tables WHERE table_schema='public';"
```

**Expected**: 200+ tables

---

## 🔐 Security Notes

### Passwords in Backup:
⚠️ **WARNING**: This backup contains:
- Admin password hash (admin/admin)
- Database connection info
- User emails and names

**Best Practice**:
- Do NOT commit sensitive backups to public repos
- Change admin password after restore
- Use environment variables for production

### Change Admin Password:
```python
# In Odoo shell:
docker-compose exec odoo odoo shell -d odoo

# Then:
env['res.users'].browse(2).write({'password': 'new_password'})
```

---

## 📝 Backup File Structure

```
odoo_db_2026_01_04_pakd_v1.3.0.sql.gz
│
└── Compressed SQL file contains:
    ├── DROP commands (clean existing objects)
    ├── CREATE SCHEMA (public, information_schema)
    ├── CREATE TABLE (all Odoo tables)
    ├── COPY (data for each table)
    ├── CREATE INDEX (all indexes)
    ├── CREATE CONSTRAINT (foreign keys, etc)
    └── CREATE TRIGGER (all triggers)
```

---

## 🎓 Advanced Commands

### View Backup Contents (without restoring):
```bash
gunzip -c odoo_db_2026_01_04_pakd_v1.3.0.sql.gz | less
```

Press `q` to quit.

### Extract Specific Table:
```bash
gunzip -c odoo_db_2026_01_04_pakd_v1.3.0.sql.gz | \
  grep -A 100 "COPY public.dtx_pakd" | head -110
```

### Check Backup Integrity:
```bash
gunzip -t odoo_db_2026_01_04_pakd_v1.3.0.sql.gz
echo $?  # Should print 0 (success)
```

### Restore Only Specific Tables:
```bash
# Not recommended - use full restore instead
# But if needed:
gunzip -c backup.sql.gz | \
  grep -A 1000 "COPY public.dtx_pakd " | \
  docker-compose exec -T db psql -U odoo -d odoo
```

---

## 🔄 Create New Backup

### Using Script:
```bash
./backup-db.sh "after_uat_test"
# Creates: odoo_db_2026_01_05_HHMM_after_uat_test.sql.gz
```

### Manual:
```bash
# Backup
docker-compose exec -T db pg_dump -U odoo -d odoo --clean --if-exists \
  > odoo_db_$(date +%Y_%m_%d).sql

# Compress
gzip -9 odoo_db_$(date +%Y_%m_%d).sql
```

---

## 📞 Quick Reference

| What | Command |
|------|---------|
| Stop Odoo | `docker-compose stop odoo` |
| Start Odoo | `docker-compose start odoo` |
| Restart Odoo | `docker-compose restart odoo` |
| Odoo Logs | `docker-compose logs odoo -f` |
| DB Logs | `docker-compose logs db -f` |
| Container Status | `docker-compose ps` |
| Connect to DB | `docker-compose exec db psql -U odoo -d odoo` |
| List Databases | `docker-compose exec db psql -U odoo -c "\l"` |
| List Tables | `docker-compose exec db psql -U odoo -d odoo -c "\dt"` |
| Check Module | Apps → Installed → Search "dtx_sales" |
| Reset Password | See "Problem 7" above |

---

## ✅ Next Steps After Restore

1. **Verify login**: http://localhost:8069 (admin/admin)
2. **Check module version**: Apps → dtx_sales_pakd_contract → Should be v1.3.0
3. **Read session summary**: `SESSION_2026_01_04_PAKD_FORMULA_FIX.md`
4. **Create test data**: Follow `MANUAL_UAT_GUIDE.md` STEP 1
5. **Test PAKD formulas**: Follow STEP 2-10

---

**Created**: 2026-01-04
**Platform**: Windows → MacBook M1
**Status**: ✅ Tested and working
