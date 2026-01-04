#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DTX Data Setup Script
=====================
Script để tạo Product Categories, Products, và Vendors chuẩn cho DTX

Usage:
    docker-compose exec odoo python3 /mnt/extra-addons/../scripts/setup_dtx_data.py

Requirements:
    - Odoo 16 running with dtx_product_standards module installed
    - Database: dtx_dev
"""

import xmlrpc.client

# ============================================
# CONFIGURATION
# ============================================
ODOO_URL = 'http://localhost:8069'
DB_NAME = 'dtx_dev'
USERNAME = 'admin@dtxco.vn'
PASSWORD = 'admin'

# ============================================
# CONNECT TO ODOO
# ============================================
print("=" * 60)
print("DTX Data Setup Script")
print("=" * 60)
print(f"\nConnecting to Odoo at {ODOO_URL}...")

common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
uid = common.authenticate(DB_NAME, USERNAME, PASSWORD, {})

if not uid:
    print("❌ Authentication failed! Check username/password.")
    exit(1)

print(f"✅ Connected successfully! User ID: {uid}")

models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

# ============================================
# HELPER FUNCTIONS
# ============================================
def create_or_update(model, domain, values, context=None):
    """Create record if not exists, otherwise update"""
    context = context or {}
    existing = models.execute_kw(
        DB_NAME, uid, PASSWORD,
        model, 'search', [domain],
        {'limit': 1}
    )

    if existing:
        models.execute_kw(
            DB_NAME, uid, PASSWORD,
            model, 'write', [existing, values],
            {'context': context}
        )
        print(f"  ✓ Updated: {values.get('name', 'Record')}")
        return existing[0]
    else:
        record_id = models.execute_kw(
            DB_NAME, uid, PASSWORD,
            model, 'create', [values],
            {'context': context}
        )
        print(f"  ✅ Created: {values.get('name', 'Record')}")
        return record_id

# ============================================
# STEP 1: CREATE PRODUCT CATEGORIES
# ============================================
print("\n" + "=" * 60)
print("STEP 1: Creating Product Categories")
print("=" * 60)

categories = [
    {
        'name': 'Linh kiện DTX',
        'property_cost_method': 'average',
        'property_valuation': 'real_time',
    },
    {
        'name': 'Thành phẩm DTX',
        'property_cost_method': 'average',
        'property_valuation': 'real_time',
    },
    {
        'name': 'Dịch vụ gia công',
        'property_cost_method': 'standard',
        'property_valuation': 'manual_periodic',
    },
    {
        'name': 'License phần mềm',
        'property_cost_method': 'standard',
        'property_valuation': 'manual_periodic',
    },
]

for cat_data in categories:
    create_or_update(
        'product.category',
        [('name', '=', cat_data['name'])],
        cat_data
    )

# ============================================
# STEP 2: CREATE VENDORS
# ============================================
print("\n" + "=" * 60)
print("STEP 2: Creating Vendors")
print("=" * 60)

vendors = [
    {
        'name': 'LGMEC',
        'is_company': True,
        'supplier_rank': 1,
        'phone': '0909123456',
        'email': 'lgmec@example.com',
        'street': 'Khu Công nghiệp Tân Bình',
        'city': 'TP.HCM',
        'country_id': models.execute_kw(
            DB_NAME, uid, PASSWORD,
            'res.country', 'search',
            [[('code', '=', 'VN')]],
            {'limit': 1}
        )[0] if models.execute_kw(
            DB_NAME, uid, PASSWORD,
            'res.country', 'search',
            [[('code', '=', 'VN')]],
            {'limit': 1}
        ) else False,
        'comment': 'Đối tác gia công lắp ráp Kiosk',
    },
    {
        'name': 'Công ty TNHH Touch Display Việt Nam',
        'is_company': True,
        'supplier_rank': 1,
        'phone': '0281234567',
        'email': 'touchvn@example.com',
        'street': 'Quận 7',
        'city': 'TP.HCM',
        'comment': 'Nhà cung cấp màn hình cảm ứng',
    },
    {
        'name': 'Công ty CP Thiết bị In Hà Nội',
        'is_company': True,
        'supplier_rank': 1,
        'phone': '0241234567',
        'email': 'printhn@example.com',
        'street': 'Cầu Giấy',
        'city': 'Hà Nội',
        'comment': 'Nhà cung cấp máy in nhiệt',
    },
    {
        'name': 'Công ty TNHH PC Components VN',
        'is_company': True,
        'supplier_rank': 1,
        'phone': '0283456789',
        'email': 'pcvn@example.com',
        'street': 'Quận 1',
        'city': 'TP.HCM',
        'comment': 'Nhà cung cấp Mini PC',
    },
    {
        'name': 'Công ty TNHH Camera & Security',
        'is_company': True,
        'supplier_rank': 1,
        'phone': '0909876543',
        'email': 'camsec@example.com',
        'street': 'Quận Tân Bình',
        'city': 'TP.HCM',
        'comment': 'Nhà cung cấp Camera IP',
    },
    {
        'name': 'Công ty TNHH NFC Technology',
        'is_company': True,
        'supplier_rank': 1,
        'phone': '0243456789',
        'email': 'nfctech@example.com',
        'street': 'Hoàn Kiếm',
        'city': 'Hà Nội',
        'comment': 'Nhà cung cấp đầu đọc CCCD',
    },
]

for vendor_data in vendors:
    create_or_update(
        'res.partner',
        [('name', '=', vendor_data['name'])],
        vendor_data
    )

# ============================================
# STEP 3: CREATE STANDARD PRODUCTS
# ============================================
print("\n" + "=" * 60)
print("STEP 3: Creating Standard Products")
print("=" * 60)

# Get category IDs
cat_linh_kien = models.execute_kw(
    DB_NAME, uid, PASSWORD,
    'product.category', 'search',
    [[('name', '=', 'Linh kiện DTX')]],
    {'limit': 1}
)[0]

cat_thanh_pham = models.execute_kw(
    DB_NAME, uid, PASSWORD,
    'product.category', 'search',
    [[('name', '=', 'Thành phẩm DTX')]],
    {'limit': 1}
)[0]

cat_dich_vu = models.execute_kw(
    DB_NAME, uid, PASSWORD,
    'product.category', 'search',
    [[('name', '=', 'Dịch vụ gia công')]],
    {'limit': 1}
)[0]

# 3.1. Linh kiện có Serial
print("\n3.1. Creating components with serial tracking...")
components = [
    {
        'name': 'Touch Screen 15.6"',
        'type': 'product',
        'categ_id': cat_linh_kien,
        'tracking': 'serial',
        'x_dtx_type': 'device_serialized',
        'purchase_ok': True,
        'sale_ok': True,
        'list_price': 3000000,
        'standard_price': 2500000,
    },
    {
        'name': 'Thermal Printer 80mm',
        'type': 'product',
        'categ_id': cat_linh_kien,
        'tracking': 'serial',
        'x_dtx_type': 'device_serialized',
        'purchase_ok': True,
        'sale_ok': True,
        'list_price': 2000000,
        'standard_price': 1800000,
    },
    {
        'name': 'Mini PC Intel i5',
        'type': 'product',
        'categ_id': cat_linh_kien,
        'tracking': 'serial',
        'x_dtx_type': 'device_serialized',
        'purchase_ok': True,
        'sale_ok': True,
        'list_price': 6000000,
        'standard_price': 4500000,
    },
    {
        'name': 'Camera IP 2MP',
        'type': 'product',
        'categ_id': cat_linh_kien,
        'tracking': 'serial',
        'x_dtx_type': 'device_serialized',
        'purchase_ok': True,
        'sale_ok': True,
        'list_price': 1500000,
        'standard_price': 1200000,
    },
    {
        'name': 'CCCD Reader NFC',
        'type': 'product',
        'categ_id': cat_linh_kien,
        'tracking': 'serial',
        'x_dtx_type': 'device_serialized',
        'purchase_ok': True,
        'sale_ok': True,
        'list_price': 1000000,
        'standard_price': 800000,
    },
]

for product_data in components:
    create_or_update(
        'product.template',
        [('name', '=', product_data['name'])],
        product_data
    )

# 3.2. Thành phẩm Kiosk
print("\n3.2. Creating finished products (Kiosk)...")
kiosk_products = [
    {
        'name': 'Kiosk lấy số DTX-A17',
        'type': 'product',
        'categ_id': cat_thanh_pham,
        'tracking': 'serial',
        'x_dtx_type': 'finished_kiosk',
        'purchase_ok': True,  # Important for subcontracting!
        'sale_ok': True,
        'list_price': 30000000,
        'standard_price': 0,
    },
]

for product_data in kiosk_products:
    create_or_update(
        'product.template',
        [('name', '=', product_data['name'])],
        product_data
    )

# 3.3. Dịch vụ gia công
print("\n3.3. Creating services...")
services = [
    {
        'name': 'Dịch vụ gia công lắp ráp Kiosk',
        'type': 'service',
        'categ_id': cat_dich_vu,
        'x_dtx_type': 'service',
        'purchase_ok': True,
        'sale_ok': False,
        'standard_price': 5000000,
    },
]

for product_data in services:
    create_or_update(
        'product.template',
        [('name', '=', product_data['name'])],
        product_data
    )

# ============================================
# SUMMARY
# ============================================
print("\n" + "=" * 60)
print("✅ SETUP COMPLETED SUCCESSFULLY!")
print("=" * 60)
print("\nSummary:")
print("  ✓ 4 Product Categories created")
print("  ✓ 6 Vendors created:")
print("    - LGMEC (gia công)")
print("    - Touch Display VN (màn hình)")
print("    - Thiết bị In HN (máy in)")
print("    - PC Components VN (Mini PC)")
print("    - Camera & Security (camera)")
print("    - NFC Technology (CCCD reader)")
print("  ✓ 5 Components (with serial) created")
print("  ✓ 1 Kiosk product created")
print("  ✓ 1 Service created")
print("\nNext steps:")
print("  1. Login to Odoo: http://localhost:8069")
print("  2. Go to: Inventory > Products > Products")
print("  3. Verify all products are created")
print("  4. Create BOM Template: Inventory > Configuration > DTX - Công cụ > Mẫu BOM Kiosk")
print("\n" + "=" * 60)
