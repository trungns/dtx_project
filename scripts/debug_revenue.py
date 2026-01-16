#!/usr/bin/env python3
"""
Debug revenue calculation for S00165/S00166
"""

print("\n" + "="*80)
print("DEBUGGING REVENUE CALCULATION - S00165, S00166")
print("="*80)

for so_name in ['S00165', 'S00166']:
    so = env['sale.order'].search([('name', '=', so_name)], limit=1)

    if so:
        print(f"\n{'='*80}")
        print(f"SO: {so.name}")
        print(f"Partner: {so.partner_id.name}")
        print(f"State: {so.state}")
        print(f"{'='*80}")

        print(f"\n--- FINANCIAL FIELDS ---")
        print(f"Revenue Expected: {so.x_revenue_expected:,.2f}")
        print(f"Revenue Actual: {so.x_revenue_actual:,.2f}")
        print(f"Total Cost: {so.x_total_cost:,.2f}")
        print(f"Profit: {so.x_profit:,.2f}")

        print(f"\n--- ALL INVOICES ---")
        if so.invoice_ids:
            for inv in so.invoice_ids:
                print(f"\nInvoice: {inv.name}")
                print(f"  Move Type: {inv.move_type}")
                print(f"  State: {inv.state}")
                print(f"  Payment State: {inv.payment_state}")
                print(f"  Amount Untaxed: {inv.amount_untaxed:,.2f}")
                print(f"  Amount Residual: {inv.amount_residual:,.2f}")

                # Check if this invoice should be counted
                is_customer_invoice = inv.move_type == 'out_invoice'
                is_posted = inv.state == 'posted'
                is_paid = inv.payment_state == 'paid'

                print(f"  Should count?")
                print(f"    - Customer invoice (out_invoice)? {is_customer_invoice}")
                print(f"    - Posted? {is_posted}")
                print(f"    - Paid? {is_paid}")
                print(f"    - RESULT: {'✅ YES' if (is_customer_invoice and is_posted and is_paid) else '❌ NO'}")
        else:
            print("  No invoices found!")

        print(f"\n--- PAID INVOICES CALCULATION ---")
        paid_invoices = so.invoice_ids.filtered(
            lambda inv: inv.move_type == 'out_invoice' and
                        inv.state == 'posted' and
                        inv.payment_state == 'paid'
        )

        if paid_invoices:
            print(f"Found {len(paid_invoices)} paid invoice(s):")
            total = 0
            for inv in paid_invoices:
                print(f"  {inv.name}: {inv.amount_untaxed:,.2f}")
                total += inv.amount_untaxed
            print(f"\nExpected Revenue Actual: {total:,.2f}")
            print(f"Actual Revenue Actual: {so.x_revenue_actual:,.2f}")
            print(f"Match? {'✅ YES' if abs(so.x_revenue_actual - total) < 0.01 else '❌ NO - MISMATCH!'}")
        else:
            print("No paid invoices found!")
            print(f"Expected Revenue Actual: 0.00")
            print(f"Actual Revenue Actual: {so.x_revenue_actual:,.2f}")
            print(f"Match? {'✅ YES' if so.x_revenue_actual == 0 else '❌ NO - Should be 0!'}")

        print(f"\n--- CONTRACT COSTS ---")
        if so.contract_cost_ids:
            for cost in so.contract_cost_ids:
                print(f"  {cost.product_id.name}")
                print(f"    Total Sale: {cost.total_sale:,.2f}")
                print(f"    Total Purchase: {cost.total_purchase:,.2f}")
        else:
            print("  No contract costs")
    else:
        print(f"\n{so_name} not found")

print("\n" + "="*80)
print("DEBUG COMPLETED")
print("="*80 + "\n")
