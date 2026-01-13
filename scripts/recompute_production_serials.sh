#!/bin/bash
# Recompute lifecycle states for serials in production location
# This fixes components stuck in production after MO completion
# Usage: ./scripts/recompute_production_serials.sh

echo "🔄 Recomputing lifecycle states for serials in production location..."

docker exec dtx_odoo16 odoo shell -d dtx_dev --no-http <<'EOF'
import logging
_logger = logging.getLogger(__name__)

# Get all serials with quants in production location
production_locations = env['stock.location'].search([('usage', '=', 'production')])
_logger.info(f"Found {len(production_locations)} production locations")

quants = env['stock.quant'].search([
    ('location_id', 'in', production_locations.ids),
    ('quantity', '>', 0),
])

serial_ids = quants.mapped('lot_id').ids
print(f"\nFound {len(serial_ids)} serials in production locations\n")

# Recompute each
updated = 0
for serial in env['stock.lot'].browse(serial_ids):
    old_state = serial.x_lifecycle_state

    # Trigger recompute
    serial._compute_x_lifecycle_state()

    if old_state != serial.x_lifecycle_state:
        updated += 1
        print(f"  ✅ {serial.name}: {old_state} → {serial.x_lifecycle_state}")

print(f"\n✅ Complete:")
print(f"   - Total serials in production: {len(serial_ids)}")
print(f"   - Updated: {updated}")

# Commit changes
env.cr.commit()
print("💾 Changes saved")
EOF

echo "✅ Done!"
