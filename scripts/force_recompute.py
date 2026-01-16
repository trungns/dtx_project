#!/usr/bin/env python3
"""
Force recompute revenue for S00165 and S00166
Run: docker exec dtx_odoo16 odoo shell -d dtx_dev < /tmp/force_recompute.py
"""

print("\n" + "="*60)
print("FORCE RECOMPUTE REVENUE - S00165, S00166")
print("="*60)

# Find SO S00165 and S00166
for so_name in ['S00165', 'S00166']:
    so = env['sale.order'].search([('name', '=', so_name)], limit=1)

    if so:
        print(f"\n=== {so_name} ===")
        print(f"Before: Revenue Actual = {so.x_revenue_actual:,.2f}")

        # Force recompute by invalidating cache and calling compute
        so.invalidate_cache(['x_revenue_actual', 'x_profit', 'x_profit_margin'])
        so._compute_contract_financials()

        print(f"After: Revenue Actual = {so.x_revenue_actual:,.2f}")

        # Show paid invoices
        paid = so.invoice_ids.filtered(
            lambda i: i.move_type == 'out_invoice' and
                      i.state == 'posted' and
                      i.payment_state == 'paid'
        )
        if paid:
            print(f"Paid invoices: {len(paid)}")
            total = sum(paid.mapped('amount_untaxed'))
            print(f"Expected: {total:,.2f}")
            print(f"Match: {'✅' if abs(so.x_revenue_actual - total) < 0.01 else '❌'}")
    else:
        print(f"{so_name} not found")

# Commit changes
env.cr.commit()
print("\n✅ Changes committed. Check Contract List!")
print("="*60 + "\n")
