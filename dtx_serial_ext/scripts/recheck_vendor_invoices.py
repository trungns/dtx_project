#!/usr/bin/env python3
"""
Script to manually recheck vendor invoice state for serials
Run this in Odoo shell or via Technical > Python Code

Usage scenarios:
1. Bill was created AFTER receipt was validated
2. Bulk update multiple serials from same PO
3. Fix serials stuck in 'missing' state
"""

# ==========================================
# Option 1: Recheck ALL serials with missing state
# ==========================================
def recheck_all_missing_invoices(env):
    """
    Find all serials with 'missing' state and recheck if bills exist
    """
    print("=== Rechecking all serials with missing vendor invoice state ===")

    # Find all serials with missing state
    lots = env['stock.lot'].search([
        ('vendor_invoice_state', '=', 'missing'),
        ('purchase_order_ids', '!=', False),  # Only those linked to PO
    ])

    print(f"Found {len(lots)} serials with missing invoice state")

    updated_count = 0
    for lot in lots:
        # Check each linked PO for bills
        for po in lot.purchase_order_ids:
            # Search for posted vendor bills
            bills = env['account.move'].search([
                ('move_type', '=', 'in_invoice'),
                ('invoice_origin', '=', po.name),
                ('state', '=', 'posted'),
            ], limit=1, order='invoice_date desc')

            if bills:
                bill = bills[0]
                lot.write({
                    'vendor_invoice_state': 'linked',
                    'vendor_invoice_note': f'Bill {bill.name} dated {bill.invoice_date} - Auto-linked via recheck script',
                })

                lot.message_post(
                    body=f"Vendor invoice {bill.name} dated {bill.invoice_date} detected via recheck script",
                    subject="Vendor Invoice State Updated (Manual Recheck)",
                )

                print(f"✓ Updated lot {lot.name}: linked to bill {bill.name}")
                updated_count += 1
                break  # Only link to first bill found

    print(f"\n=== Summary: Updated {updated_count} / {len(lots)} serials ===")
    return updated_count


# ==========================================
# Option 2: Recheck specific PO
# ==========================================
def recheck_po_invoices(env, po_name):
    """
    Recheck all serials from a specific Purchase Order

    Args:
        po_name: PO reference like 'P00007'
    """
    print(f"=== Rechecking serials from PO {po_name} ===")

    # Find the PO
    po = env['purchase.order'].search([('name', '=', po_name)], limit=1)
    if not po:
        print(f"ERROR: Purchase Order {po_name} not found")
        return 0

    # Find all serials linked to this PO
    lots = env['stock.lot'].search([
        ('purchase_order_ids', 'in', [po.id]),
    ])

    print(f"Found {len(lots)} serials from PO {po_name}")

    # Check if bills exist for this PO
    bills = env['account.move'].search([
        ('move_type', '=', 'in_invoice'),
        ('invoice_origin', '=', po.name),
        ('state', '=', 'posted'),
    ], order='invoice_date desc')

    if not bills:
        print(f"WARNING: No posted vendor bills found for PO {po_name}")
        print(f"Current serials state:")
        for lot in lots:
            print(f"  - {lot.name}: {lot.vendor_invoice_state}")
        return 0

    print(f"Found {len(bills)} posted bill(s) for PO {po_name}:")
    for bill in bills:
        print(f"  - {bill.name} dated {bill.invoice_date} (state: {bill.state})")

    # Update serials that are still in 'missing' state
    bill = bills[0]  # Use most recent bill
    updated_count = 0

    for lot in lots:
        if lot.vendor_invoice_state == 'missing':
            lot.write({
                'vendor_invoice_state': 'linked',
                'vendor_invoice_note': f'Bill {bill.name} dated {bill.invoice_date} - Linked via recheck script for PO {po_name}',
            })

            lot.message_post(
                body=f"Vendor invoice {bill.name} dated {bill.invoice_date} linked via recheck script",
                subject="Vendor Invoice State Updated",
            )

            print(f"✓ Updated lot {lot.name}: missing → linked")
            updated_count += 1
        else:
            print(f"  Skip lot {lot.name}: already in state '{lot.vendor_invoice_state}'")

    print(f"\n=== Summary: Updated {updated_count} / {len(lots)} serials ===")
    return updated_count


# ==========================================
# Option 3: Recheck specific serial
# ==========================================
def recheck_serial_invoice(env, serial_name):
    """
    Recheck vendor invoice for a specific serial number

    Args:
        serial_name: Serial number like 'SN001' or supplier serial
    """
    print(f"=== Rechecking serial {serial_name} ===")

    # Find the serial
    lot = env['stock.lot'].search([('name', '=', serial_name)], limit=1)
    if not lot:
        print(f"ERROR: Serial {serial_name} not found")
        return False

    print(f"Serial: {lot.name}")
    print(f"Current state: {lot.vendor_invoice_state}")
    print(f"Linked POs: {lot.purchase_order_ids.mapped('name')}")

    if not lot.purchase_order_ids:
        print("WARNING: No purchase orders linked to this serial")
        return False

    # Check each linked PO for bills
    for po in lot.purchase_order_ids:
        print(f"\nChecking PO {po.name}...")

        bills = env['account.move'].search([
            ('move_type', '=', 'in_invoice'),
            ('invoice_origin', '=', po.name),
            ('state', '=', 'posted'),
        ], order='invoice_date desc')

        if bills:
            bill = bills[0]
            print(f"  Found bill: {bill.name} dated {bill.invoice_date}")

            if lot.vendor_invoice_state == 'missing':
                lot.write({
                    'vendor_invoice_state': 'linked',
                    'vendor_invoice_note': f'Bill {bill.name} dated {bill.invoice_date} - Linked via recheck script',
                })

                lot.message_post(
                    body=f"Vendor invoice {bill.name} dated {bill.invoice_date} linked via recheck script",
                    subject="Vendor Invoice State Updated",
                )

                print(f"✓ Updated serial state: missing → linked")
                return True
            else:
                print(f"  Serial already in state '{lot.vendor_invoice_state}'")
                return False
        else:
            print(f"  No posted bills found for PO {po.name}")

    print("\nNo bills found for any linked PO")
    return False


# ==========================================
# USAGE EXAMPLES
# ==========================================
"""
# In Odoo shell (docker-compose exec web odoo shell -d dtx_dev):

# Import the functions (copy paste vào shell)
from pathlib import Path
exec(Path('/mnt/extra-addons/dtx_serial_ext/scripts/recheck_vendor_invoices.py').read_text())

# Option 1: Recheck ALL missing invoices
recheck_all_missing_invoices(env)

# Option 2: Recheck specific PO (VD: P00007)
recheck_po_invoices(env, 'P00007')

# Option 3: Recheck specific serial
recheck_serial_invoice(env, 'SN001')


# Or in Settings > Technical > Python Code (Developer Mode):
# Copy paste function bạn cần vào và gọi với env
"""

if __name__ == '__main__':
    print("This script should be run inside Odoo shell")
    print("See USAGE EXAMPLES in the script for instructions")
