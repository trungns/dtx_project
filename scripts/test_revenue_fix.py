#!/usr/bin/env python3
"""
Test script for revenue actual calculation fix (v1.8.0)
Run inside Odoo container: odoo shell -d dtx_dev < /mnt/extra-addons/../scripts/test_revenue_fix.py
"""

# Test SO S00164
print("\n" + "="*60)
print("TESTING REVENUE FIX - v1.8.0")
print("="*60)

so_s00164 = env['sale.order'].search([('name', '=', 'S00164')], limit=1)
if so_s00164:
    print(f"\n=== SO S00164 ===")
    print(f"Name: {so_s00164.name}")
    print(f"Partner: {so_s00164.partner_id.name}")
    print(f"State: {so_s00164.state}")
    print(f"\n--- Financial Data ---")
    print(f"Revenue Expected: {so_s00164.x_revenue_expected:,.2f}")
    print(f"Revenue Actual: {so_s00164.x_revenue_actual:,.2f}")
    print(f"Total Cost: {so_s00164.x_total_cost:,.2f}")
    print(f"Profit: {so_s00164.x_profit:,.2f}")
    print(f"Profit Margin: {so_s00164.x_profit_margin:.2f}%")

    print(f"\n--- Invoices ---")
    for inv in so_s00164.invoice_ids:
        print(f"  Invoice: {inv.name}")
        print(f"    Type: {inv.move_type}")
        print(f"    State: {inv.state}")
        print(f"    Payment State: {inv.payment_state}")
        print(f"    Amount Untaxed: {inv.amount_untaxed:,.2f}")
        print(f"    Amount Residual: {inv.amount_residual:,.2f}")

    print(f"\n--- Paid Invoices (used for revenue actual) ---")
    paid_invoices = so_s00164.invoice_ids.filtered(
        lambda inv: inv.move_type == 'out_invoice' and
                    inv.state == 'posted' and
                    inv.payment_state == 'paid'
    )
    if paid_invoices:
        for inv in paid_invoices:
            print(f"  ✅ {inv.name}: {inv.amount_untaxed:,.2f}")
        print(f"  Total Paid: {sum(paid_invoices.mapped('amount_untaxed')):,.2f}")
    else:
        print("  ❌ No paid invoices found")

    print(f"\n--- Contract Costs ---")
    if so_s00164.contract_cost_ids:
        for cost in so_s00164.contract_cost_ids:
            print(f"  {cost.product_id.name}")
            print(f"    Total Sale: {cost.total_sale:,.2f}")
            print(f"    Total Purchase: {cost.total_purchase:,.2f}")
    else:
        print("  (No contract costs)")
else:
    print("SO S00164 not found")

# Test SO S00165
so_s00165 = env['sale.order'].search([('name', '=', 'S00165')], limit=1)
if so_s00165:
    print(f"\n\n=== SO S00165 ===")
    print(f"Name: {so_s00165.name}")
    print(f"Partner: {so_s00165.partner_id.name}")
    print(f"State: {so_s00165.state}")
    print(f"\n--- Financial Data ---")
    print(f"Revenue Expected: {so_s00165.x_revenue_expected:,.2f}")
    print(f"Revenue Actual: {so_s00165.x_revenue_actual:,.2f}")
    print(f"Total Cost: {so_s00165.x_total_cost:,.2f}")
    print(f"Profit: {so_s00165.x_profit:,.2f}")

    print(f"\n--- Paid Invoices ---")
    paid_invoices = so_s00165.invoice_ids.filtered(
        lambda inv: inv.move_type == 'out_invoice' and
                    inv.state == 'posted' and
                    inv.payment_state == 'paid'
    )
    if paid_invoices:
        for inv in paid_invoices:
            print(f"  ✅ {inv.name}: {inv.amount_untaxed:,.2f}")
        print(f"  Total Paid: {sum(paid_invoices.mapped('amount_untaxed')):,.2f}")
    else:
        print("  ❌ No paid invoices found")
else:
    print("SO S00165 not found")

print("\n" + "="*60)
print("TEST COMPLETED")
print("="*60)
print("\nExpected Result:")
print("- If invoices have payment_state == 'paid':")
print("  → Revenue Actual should = sum of paid invoice amounts")
print("- If no paid invoices:")
print("  → Revenue Actual should = 0")
print("\n")
