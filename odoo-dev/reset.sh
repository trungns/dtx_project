#!/bin/bash
# Reset entire development environment

echo "⚠️  WARNING: This will DELETE all data and reset everything!"
echo ""
read -p "Are you sure? (type 'yes' to confirm): " confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ Cancelled"
    exit 0
fi

echo ""
echo "🗑️  Stopping and removing containers..."
docker-compose down -v

echo ""
echo "🧹 Cleaning up..."
rm -rf data/

echo ""
echo "✅ Reset complete!"
echo ""
echo "To start fresh:"
echo "   ./start.sh"
echo "   Then create new database at http://localhost:8069"
