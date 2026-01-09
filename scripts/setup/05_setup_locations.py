#!/usr/bin/env python3
"""
Setup Stock Locations (Kho components, finished, maintenance, subcontractors)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.odoo_client import OdooClient


def setup_locations(client, skip_existing=True):
    """Setup stock locations"""

    print("=" * 80)
    print("SETUP STOCK LOCATIONS")
    print("=" * 80)
    print()

    # Get WH/Stock (default location)
    stock_location = client.search(
        'stock.location',
        [('name', '=', 'Stock'), ('usage', '=', 'internal')],
        limit=1
    )

    if not stock_location:
        print("❌ Default Stock location not found!")
        print("   Please check your Odoo installation")
        return 0, 0

    stock_location_id = stock_location[0]['id']
    print(f"✅ Found default Stock location (ID: {stock_location_id})")
    print()

    # Locations to create
    locations = [
        {
            'name': 'Components',
            'complete_name': 'WH/Stock/Components',
            'location_id': stock_location_id,
            'usage': 'internal',
            'company_id': stock_location[0].get('company_id')[0] if stock_location[0].get('company_id') else False,
        },
        {
            'name': 'Finished Products',
            'complete_name': 'WH/Stock/Finished Products',
            'location_id': stock_location_id,
            'usage': 'internal',
            'company_id': stock_location[0].get('company_id')[0] if stock_location[0].get('company_id') else False,
        },
        {
            'name': 'Maintenance',
            'complete_name': 'WH/Maintenance',
            'location_id': False,  # Top level
            'usage': 'internal',
            'company_id': stock_location[0].get('company_id')[0] if stock_location[0].get('company_id') else False,
        },
    ]

    created_count = 0
    skipped_count = 0

    for loc_data in locations:
        name = loc_data['name']
        complete_name = loc_data['complete_name']

        # Check if exists by complete_name
        domain = [('complete_name', '=', complete_name)]

        loc_id, created = client.get_or_create(
            'stock.location',
            domain,
            loc_data,
            skip_existing=skip_existing
        )

        if created:
            print(f"✅ Created: {complete_name}")
            created_count += 1
        else:
            print(f"⏭️  Skipped: {complete_name} (already exists)")
            skipped_count += 1

    print()
    print("=" * 80)
    print(f"SUMMARY: {created_count} created, {skipped_count} skipped")
    print("=" * 80)
    print()

    print("💡 TIP: Để tạo locations cho đối tác gia công:")
    print("   1. Vào Inventory > Configuration > Locations")
    print("   2. Tìm 'Partner Locations'")
    print("   3. Create location mới với Usage = 'External'")
    print("   4. Gắn partner vào location")
    print()

    return created_count, skipped_count


if __name__ == '__main__':
    client = OdooClient()
    client.connect()

    skip_existing = client.config.getboolean('setup', 'skip_existing', fallback=True)

    setup_locations(client, skip_existing=skip_existing)

    print("✅ Stock locations setup completed!")
