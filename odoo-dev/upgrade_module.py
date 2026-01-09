#!/usr/bin/env python3
"""
Upgrade dtx_serial_ext module
"""

import xmlrpc.client

url = 'http://localhost:8069'
db = 'dtx_dev'
username = 'admin'
password = 'admin'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

print("Upgrading module dtx_serial_ext...")

# Find the module
module_ids = models.execute_kw(db, uid, password, 'ir.module.module', 'search',
                               [[('name', '=', 'dtx_serial_ext')]])

if not module_ids:
    print("❌ Module not found!")
    exit(1)

# Upgrade the module
models.execute_kw(db, uid, password, 'ir.module.module', 'button_immediate_upgrade',
                 [module_ids])

print("✅ Module upgraded successfully!")
print("\nNow recomputing serial numbers...")

# Recompute all serials
lot_ids = models.execute_kw(db, uid, password, 'stock.lot', 'search', [[]])
print(f"Found {len(lot_ids)} serials")

# Force recompute by writing empty dict
models.execute_kw(db, uid, password, 'stock.lot', 'write', [lot_ids, {}])

print("✅ Recompute completed!")
