#!/usr/bin/env python3
"""
Upgrade dtx_sales_pakd_contract module
"""

import xmlrpc.client

url = 'http://localhost:8069'
db = 'dtx_dev'
username = 'admin'
password = 'admin'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

print("Upgrading module dtx_sales_pakd_contract...")

# Find the module
module_ids = models.execute_kw(db, uid, password, 'ir.module.module', 'search',
                               [[('name', '=', 'dtx_sales_pakd_contract')]])

if not module_ids:
    print("❌ Module not found!")
    exit(1)

# Upgrade the module
models.execute_kw(db, uid, password, 'ir.module.module', 'button_immediate_upgrade',
                 [module_ids])

print("✅ Module upgraded successfully!")
print("\nNow recomputing sale orders...")

# Recompute all sale orders
so_ids = models.execute_kw(db, uid, password, 'sale.order', 'search', [[]])
print(f"Found {len(so_ids)} sale orders")

# Force recompute by writing empty dict
models.execute_kw(db, uid, password, 'sale.order', 'write', [so_ids, {}])

print("✅ Recompute completed!")
