#!/usr/bin/env python3
"""
Verify DTX Setup

Kiểm tra tất cả cấu hình đã được setup đúng
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.odoo_client import OdooClient


def verify_taxes(client):
    """Verify taxes"""
    print("Checking Taxes...")

    expected_taxes = ['VAT 0%', 'VAT 5%', 'VAT 8%', 'VAT 10%']
    found = 0

    for tax_name in expected_taxes:
        result = client.search('account.tax', [('name', '=', tax_name)], limit=1)
        if result:
            found += 1

    status = "✅" if found == len(expected_taxes) else "❌"
    print(f"{status} Taxes: {found}/{len(expected_taxes)}")
    return found == len(expected_taxes)


def verify_categories(client):
    """Verify product categories"""
    print("Checking Product Categories...")

    expected_categories = [
        'DTX Products',
        'DTX Hardware',
        'DTX Components',
        'DTX Finished Products',
        'DTX Accessories',
        'DTX Services',
    ]
    found = 0

    for cat_name in expected_categories:
        result = client.search('product.category', [('name', '=', cat_name)], limit=1)
        if result:
            found += 1

    status = "✅" if found == len(expected_categories) else "❌"
    print(f"{status} Categories: {found}/{len(expected_categories)}")
    return found == len(expected_categories)


def verify_payment_terms(client):
    """Verify payment terms"""
    print("Checking Payment Terms...")

    expected_terms = ['Immediate Payment', '15 Days', '30 Days', '60 Days']
    found = 0

    for term_name in expected_terms:
        result = client.search('account.payment.term', [('name', '=', term_name)], limit=1)
        if result:
            found += 1

    status = "✅" if found == len(expected_terms) else "❌"
    print(f"{status} Payment Terms: {found}/{len(expected_terms)}")
    return found == len(expected_terms)


def verify_locations(client):
    """Verify stock locations"""
    print("Checking Stock Locations...")

    expected_locations = [
        'WH/Stock/Components',
        'WH/Stock/Finished Products',
        'WH/Maintenance',
    ]
    found = 0

    for loc_name in expected_locations:
        result = client.search('stock.location', [('complete_name', '=', loc_name)], limit=1)
        if result:
            found += 1

    status = "✅" if found == len(expected_locations) else "❌"
    print(f"{status} Locations: {found}/{len(expected_locations)}")
    return found == len(expected_locations)


def verify_dtx_modules(client):
    """Verify DTX modules installed"""
    print("Checking DTX Modules...")

    expected_modules = [
        'dtx_product_standards',
        'dtx_serial_ext',
        'dtx_sales_pakd_contract',
    ]
    found = 0

    for module_name in expected_modules:
        result = client.search('ir.module.module', [
            ('name', '=', module_name),
            ('state', '=', 'installed')
        ], limit=1)
        if result:
            found += 1
        else:
            print(f"  ⚠️  Module '{module_name}' not installed")

    status = "✅" if found == len(expected_modules) else "❌"
    print(f"{status} Modules: {found}/{len(expected_modules)}")
    return found == len(expected_modules)


def main():
    """Main verification"""
    print("=" * 80)
    print("DTX SETUP VERIFICATION")
    print("=" * 80)
    print()

    client = OdooClient()
    client.connect()

    results = []

    results.append(verify_taxes(client))
    results.append(verify_categories(client))
    results.append(verify_payment_terms(client))
    results.append(verify_locations(client))
    results.append(verify_dtx_modules(client))

    print()
    print("=" * 80)

    if all(results):
        print("✅ ALL CHECKS PASSED!")
        print("=" * 80)
        print()
        print("Your DTX Odoo 16 is ready to use! 🎉")
        print()
        print("Next steps:")
        print("1. Start creating products: Inventory > DTX - Chuẩn hóa dữ liệu")
        print("2. Create customers/vendors: Contacts")
        print("3. Start sales workflow: Sales > Quotations")
        print()
        return 0
    else:
        print("❌ SOME CHECKS FAILED")
        print("=" * 80)
        print()
        print("Please run setup scripts:")
        print("  python3 run_all_setup.py")
        print()
        return 1


if __name__ == '__main__':
    sys.exit(main())
