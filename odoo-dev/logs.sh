#!/bin/bash
# View Odoo logs

echo "📋 Viewing Odoo logs (Ctrl+C to exit)..."
echo ""

docker-compose logs -f --tail=100 odoo
