#!/bin/bash
# Upgrade DTX module script

MODULE_NAME=${1:-dtx_serial_ext}
DB_NAME=${2:-dtx_dev}

echo "🔄 Upgrading module: $MODULE_NAME"
echo "   Database: $DB_NAME"
echo ""

docker exec dtx_odoo16 odoo \
    --addons-path=/mnt/extra-addons,/usr/lib/python3/dist-packages/odoo/addons \
    -d $DB_NAME \
    -u $MODULE_NAME \
    --stop-after-init

echo ""
echo "♻️  Restarting Odoo..."
docker-compose restart odoo

echo ""
echo "✅ Module upgraded successfully!"
echo "   Refresh your browser: http://localhost:8069"
