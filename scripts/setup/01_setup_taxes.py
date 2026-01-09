#!/usr/bin/env python3
"""
Setup VAT Taxes (0%, 5%, 8%, 10%)

Mục đích:
- PAKD auto-map VAT% → account.tax
- Chuẩn hóa thuế cho sale/purchase
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.odoo_client import OdooClient


def setup_taxes(client, skip_existing=True):
    """Setup standard VAT taxes"""

    print("=" * 80)
    print("SETUP TAXES (VAT)")
    print("=" * 80)
    print()

    taxes = [
        {
            'name': 'VAT 0%',
            'amount': 0.0,
            'amount_type': 'percent',
            'type_tax_use': 'sale',
            'description': 'VAT 0%',
        },
        {
            'name': 'VAT 5%',
            'amount': 5.0,
            'amount_type': 'percent',
            'type_tax_use': 'sale',
            'description': 'VAT 5%',
        },
        {
            'name': 'VAT 8%',
            'amount': 8.0,
            'amount_type': 'percent',
            'type_tax_use': 'sale',
            'description': 'VAT 8%',
        },
        {
            'name': 'VAT 10%',
            'amount': 10.0,
            'amount_type': 'percent',
            'type_tax_use': 'sale',
            'description': 'VAT 10%',
        },
    ]

    created_count = 0
    skipped_count = 0

    for tax_data in taxes:
        name = tax_data['name']
        amount = tax_data['amount']

        # Check if exists
        domain = [('name', '=', name), ('amount', '=', amount)]

        tax_id, created = client.get_or_create(
            'account.tax',
            domain,
            tax_data,
            skip_existing=skip_existing
        )

        if created:
            print(f"✅ Created: {name} ({amount}%)")
            created_count += 1
        else:
            print(f"⏭️  Skipped: {name} (already exists)")
            skipped_count += 1

    print()
    print("=" * 80)
    print(f"SUMMARY: {created_count} created, {skipped_count} skipped")
    print("=" * 80)
    print()

    return created_count, skipped_count


if __name__ == '__main__':
    client = OdooClient()
    client.connect()

    skip_existing = client.config.getboolean('setup', 'skip_existing', fallback=True)

    setup_taxes(client, skip_existing=skip_existing)

    print("✅ Tax setup completed!")
