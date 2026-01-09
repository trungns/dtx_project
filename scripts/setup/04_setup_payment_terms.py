#!/usr/bin/env python3
"""
Setup Payment Terms (15, 30, 60 days, Immediate)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.odoo_client import OdooClient


def setup_payment_terms(client, skip_existing=True):
    """Setup standard payment terms"""

    print("=" * 80)
    print("SETUP PAYMENT TERMS")
    print("=" * 80)
    print()

    payment_terms = [
        {
            'name': 'Immediate Payment',
            'note': 'Thanh toán ngay',
            'line_ids': [(0, 0, {
                'value': 'balance',
                'days': 0,
            })],
        },
        {
            'name': '15 Days',
            'note': 'Net 15 Days',
            'line_ids': [(0, 0, {
                'value': 'balance',
                'days': 15,
            })],
        },
        {
            'name': '30 Days',
            'note': 'Net 30 Days',
            'line_ids': [(0, 0, {
                'value': 'balance',
                'days': 30,
            })],
        },
        {
            'name': '60 Days',
            'note': 'Net 60 Days',
            'line_ids': [(0, 0, {
                'value': 'balance',
                'days': 60,
            })],
        },
    ]

    created_count = 0
    skipped_count = 0

    for term_data in payment_terms:
        name = term_data['name']

        # Check if exists
        domain = [('name', '=', name)]

        term_id, created = client.get_or_create(
            'account.payment.term',
            domain,
            term_data,
            skip_existing=skip_existing
        )

        if created:
            note = term_data.get('note', '')
            print(f"✅ Created: {name} ({note})")
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

    setup_payment_terms(client, skip_existing=skip_existing)

    print("✅ Payment terms setup completed!")
