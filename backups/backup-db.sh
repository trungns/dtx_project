#!/bin/bash
# Database Backup Script for MacBook M1
# Usage: ./backup-db.sh [description]

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}==================================================${NC}"
echo -e "${GREEN}  DTX Odoo Database Backup Script${NC}"
echo -e "${GREEN}==================================================${NC}"
echo ""

# Get description from argument or use default
DESCRIPTION="${1:-backup}"
DATE=$(date +%Y_%m_%d_%H%M)
BACKUP_NAME="odoo_db_${DATE}_${DESCRIPTION}"
SQL_FILE="${BACKUP_NAME}.sql"
GZ_FILE="${BACKUP_NAME}.sql.gz"

echo -e "${YELLOW}Creating backup: $GZ_FILE${NC}"
echo ""

echo -e "${GREEN}Step 1: Dumping database...${NC}"
cd ../odoo-dev
docker-compose exec -T db pg_dump -U odoo -d odoo --clean --if-exists > "../backups/${SQL_FILE}"
echo -e "${GREEN}✓ Database dumped${NC}"
echo ""

echo -e "${GREEN}Step 2: Compressing backup...${NC}"
cd ../backups
gzip -9 "$SQL_FILE"
echo -e "${GREEN}✓ Backup compressed${NC}"
echo ""

# Get file size
FILE_SIZE=$(ls -lh "$GZ_FILE" | awk '{print $5}')

echo -e "${GREEN}==================================================${NC}"
echo -e "${GREEN}  ✅ BACKUP COMPLETE!${NC}"
echo -e "${GREEN}==================================================${NC}"
echo ""
echo -e "${YELLOW}Backup file: ${GREEN}$GZ_FILE${NC}"
echo -e "${YELLOW}File size: ${GREEN}$FILE_SIZE${NC}"
echo ""
echo -e "${YELLOW}To restore this backup:${NC}"
echo -e "  ${GREEN}./restore-db.sh $GZ_FILE${NC}"
echo ""
