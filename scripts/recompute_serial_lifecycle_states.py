#!/usr/bin/env python3
"""
Recompute lifecycle states for all serial numbers

This script manually triggers recomputation of x_lifecycle_state for all
serial numbers, especially those consumed in production.

Usage:
    docker exec dtx_odoo16 python3 /mnt/extra-addons/../scripts/recompute_serial_lifecycle_states.py

Or via Odoo shell:
    docker exec dtx_odoo16 odoo shell -d dtx_dev --no-http
    >>> exec(open('/mnt/extra-addons/../scripts/recompute_serial_lifecycle_states.py').read())
"""

import xmlrpc.client
import os

# Odoo connection details
url = os.getenv('ODOO_URL', 'http://localhost:8069')
db = os.getenv('ODOO_DB', 'dtx_dev')
username = os.getenv('ODOO_USER', 'admin')
password = os.getenv('ODOO_PASSWORD', 'admin')

print(f"Connecting to Odoo at {url}...")

# Authenticate
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})

if not uid:
    print("❌ Authentication failed!")
    exit(1)

print(f"✅ Authenticated as user ID: {uid}")

# Get models proxy
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

print("\n📊 Fetching all serial numbers...")

# Get all serial numbers
serial_ids = models.execute_kw(
    db, uid, password,
    'stock.lot', 'search',
    [[]]
)

print(f"Found {len(serial_ids)} serial numbers")

print("\n🔄 Recomputing lifecycle states...")

success_count = 0
error_count = 0
consumed_count = 0

for serial_id in serial_ids:
    try:
        # Get serial info
        serial = models.execute_kw(
            db, uid, password,
            'stock.lot', 'read',
            [[serial_id]],
            {'fields': ['name', 'x_lifecycle_state']}
        )[0]

        # Check if has quants
        quant_ids = models.execute_kw(
            db, uid, password,
            'stock.quant', 'search',
            [[('lot_id', '=', serial_id), ('quantity', '>', 0)]]
        )

        old_state = serial.get('x_lifecycle_state', 'N/A')

        # Trigger recompute by writing empty dict (triggers computed fields)
        models.execute_kw(
            db, uid, password,
            'stock.lot', 'write',
            [[serial_id], {}]
        )

        # Get new state
        serial_new = models.execute_kw(
            db, uid, password,
            'stock.lot', 'read',
            [[serial_id]],
            {'fields': ['name', 'x_lifecycle_state']}
        )[0]

        new_state = serial_new.get('x_lifecycle_state', 'N/A')

        if not quant_ids:
            consumed_count += 1
            if old_state != new_state:
                print(f"  📦 {serial['name']}: {old_state} → {new_state} (consumed)")
        elif old_state != new_state:
            print(f"  📦 {serial['name']}: {old_state} → {new_state}")

        success_count += 1

    except Exception as e:
        print(f"  ❌ Error with serial {serial_id}: {str(e)}")
        error_count += 1

print(f"\n✅ Recompute complete!")
print(f"   - Total: {len(serial_ids)}")
print(f"   - Success: {success_count}")
print(f"   - Consumed (no quants): {consumed_count}")
print(f"   - Errors: {error_count}")

print("\n💡 Tip: Consumed serials should now inherit state from finished products")
