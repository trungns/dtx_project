#!/bin/bash
# Quick start script for DTX Odoo Development

echo "🚀 Starting DTX Odoo Development Environment..."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running!"
    echo "   Please start Docker Desktop first."
    exit 1
fi

# Start containers
docker-compose up -d

echo ""
echo "⏳ Waiting for Odoo to be ready..."
sleep 5

# Check if containers are running
if docker-compose ps | grep -q "Up"; then
    echo ""
    echo "✅ Odoo is starting..."
    echo ""
    echo "📊 Container status:"
    docker-compose ps
    echo ""
    echo "🌐 Open Odoo at: http://localhost:8069"
    echo ""
    echo "📝 Useful commands:"
    echo "   View logs:    docker-compose logs -f odoo"
    echo "   Stop:         docker-compose stop"
    echo "   Restart:      docker-compose restart odoo"
    echo ""
    echo "📖 Read README.md for full documentation"
else
    echo "❌ Failed to start containers"
    echo "   Check logs: docker-compose logs"
fi
