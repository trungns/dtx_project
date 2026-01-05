#!/bin/bash
# Database Restore Script for MacBook M1
# Usage: ./restore-db.sh [backup_file.sql.gz]

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}==================================================${NC}"
echo -e "${GREEN}  DTX Odoo Database Restore Script${NC}"
echo -e "${GREEN}==================================================${NC}"
echo ""

# Check if backup file is provided
if [ -z "$1" ]; then
    echo -e "${YELLOW}Available backups:${NC}"
    ls -lh *.sql.gz 2>/dev/null || echo "No backups found"
    echo ""
    echo -e "${RED}Usage: ./restore-db.sh <backup_file.sql.gz>${NC}"
    echo -e "${YELLOW}Example: ./restore-db.sh odoo_db_2026_01_04_pakd_v1.3.0.sql.gz${NC}"
    exit 1
fi

BACKUP_FILE="$1"

# Check if file exists
if [ ! -f "$BACKUP_FILE" ]; then
    echo -e "${RED}Error: Backup file not found: $BACKUP_FILE${NC}"
    exit 1
fi

echo -e "${YELLOW}Backup file: $BACKUP_FILE${NC}"
echo -e "${YELLOW}File size: $(ls -lh $BACKUP_FILE | awk '{print $5}')${NC}"
echo ""

# Confirm
read -p "This will replace the current database. Continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Restore cancelled.${NC}"
    exit 0
fi

echo ""
echo -e "${GREEN}Step 1: Stopping Odoo...${NC}"
cd ../odoo-dev
docker-compose stop odoo
echo -e "${GREEN}✓ Odoo stopped${NC}"
echo ""

echo -e "${GREEN}Step 2: Dropping existing database...${NC}"
docker-compose exec -T db dropdb -U odoo odoo --if-exists 2>/dev/null || true
echo -e "${GREEN}✓ Database dropped${NC}"
echo ""

echo -e "${GREEN}Step 3: Creating new database...${NC}"
docker-compose exec -T db createdb -U odoo odoo
echo -e "${GREEN}✓ Database created${NC}"
echo ""

echo -e "${GREEN}Step 4: Restoring from backup...${NC}"
echo -e "${YELLOW}This may take 30-60 seconds...${NC}"
cd ../backups
gunzip -c "$BACKUP_FILE" | docker-compose -f ../odoo-dev/docker-compose.yml exec -T db psql -U odoo -d odoo
echo -e "${GREEN}✓ Database restored${NC}"
echo ""

echo -e "${GREEN}Step 5: Starting Odoo...${NC}"
cd ../odoo-dev
docker-compose start odoo
echo ""

echo -e "${GREEN}Step 6: Waiting for Odoo to start...${NC}"
sleep 5
echo -e "${GREEN}✓ Odoo started${NC}"
echo ""

echo -e "${GREEN}==================================================${NC}"
echo -e "${GREEN}  ✅ RESTORE COMPLETE!${NC}"
echo -e "${GREEN}==================================================${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo -e "  1. Open: ${GREEN}http://localhost:8069${NC}"
echo -e "  2. Login: ${GREEN}admin / admin${NC}"
echo -e "  3. Verify module: ${GREEN}dtx_sales_pakd_contract v1.3.0${NC}"
echo -e "  4. Create test data: Follow ${GREEN}MANUAL_UAT_GUIDE.md${NC}"
echo ""
echo -e "${YELLOW}Check Odoo logs:${NC}"
echo -e "  ${GREEN}docker-compose logs odoo --tail=50${NC}"
echo ""
