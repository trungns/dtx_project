#!/bin/bash
# Recompute all serial lifecycle states
# Usage: ./scripts/recompute_serials.sh

echo "🔄 Recomputing lifecycle states for all serial numbers..."

docker exec dtx_odoo16 odoo shell -d dtx_dev --no-http <<EOF
# Get all serial numbers
serials = env['stock.lot'].search([])
print(f"Found {len(serials)} serial numbers")

# Recompute each
success = 0
consumed = 0
for serial in serials:
    try:
        # Check if consumed (no quants)
        quants = env['stock.quant'].search([
            ('lot_id', '=', serial.id),
            ('quantity', '>', 0)
        ])

        old_state = serial.x_lifecycle_state

        # Trigger recompute
        serial._compute_x_lifecycle_state()

        if not quants:
            consumed += 1
            if old_state != serial.x_lifecycle_state:
                print(f"  📦 {serial.name}: {old_state} → {serial.x_lifecycle_state} (consumed)")
        elif old_state != serial.x_lifecycle_state:
            print(f"  📦 {serial.name}: {old_state} → {serial.x_lifecycle_state}")

        success += 1
    except Exception as e:
        print(f"  ❌ Error with {serial.name}: {e}")

print(f"\n✅ Complete: {success} serials recomputed")
print(f"   - Consumed (no quants): {consumed}")

# Commit changes
env.cr.commit()
print("💾 Changes saved")
EOF

echo "✅ Done! All serial lifecycle states have been recomputed."
