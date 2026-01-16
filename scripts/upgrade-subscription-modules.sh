#!/bin/bash
# Upgrade script for DTX Subscription modules
# Version: 1.0
# Date: 2026-01-14

set -e  # Exit on error

echo "======================================"
echo "DTX Subscription Module Upgrade"
echo "======================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Change to project directory
cd /Users/trungns/dtx_project

echo -e "${YELLOW}Step 1: Backup current database${NC}"
./scripts/backup-db.sh dtx_odoo16
echo -e "${GREEN}✓ Database backed up${NC}"
echo ""

echo -e "${YELLOW}Step 2: Stop Odoo container${NC}"
docker-compose stop odoo
echo -e "${GREEN}✓ Odoo stopped${NC}"
echo ""

echo -e "${YELLOW}Step 3: Upgrade modules${NC}"
echo "Upgrading: dtx_product_standards (v1.2.0 → v1.3.0)"
echo "Upgrading: dtx_sales_pakd_contract (v1.5.0 → v1.6.0)"
echo ""

docker-compose run --rm odoo odoo \
    -u dtx_product_standards,dtx_sales_pakd_contract \
    -d dtx_odoo16 \
    --stop-after-init

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Modules upgraded successfully${NC}"
else
    echo -e "${RED}✗ Upgrade failed! Check logs above.${NC}"
    exit 1
fi
echo ""

echo -e "${YELLOW}Step 4: Start Odoo${NC}"
docker-compose up -d odoo
echo -e "${GREEN}✓ Odoo started${NC}"
echo ""

echo -e "${YELLOW}Step 5: Wait for Odoo to be ready (30 seconds)${NC}"
sleep 30
echo -e "${GREEN}✓ Odoo should be ready${NC}"
echo ""

echo "======================================"
echo -e "${GREEN}Upgrade completed!${NC}"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Check logs: docker-compose logs -f odoo"
echo "2. Login to Odoo: http://localhost:8069"
echo "3. Run test cases (see TESTING.md)"
echo ""
echo "Modules upgraded:"
echo "  - dtx_product_standards: v1.3.0"
echo "  - dtx_sales_pakd_contract: v1.6.0"
echo ""
