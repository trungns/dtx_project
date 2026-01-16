#!/usr/bin/env python3
"""
Script to force recompute subscription status for all subscription lines
Run inside Odoo container: odoo shell -d odoo16 < /mnt/extra-addons/../scripts/recompute_subscription_status.py
"""

# Find all subscription lines
subscription_lines = env['sale.order.line'].search([
    ('x_is_subscription', '=', True),
])

print(f"Found {len(subscription_lines)} subscription lines")

# Force recompute
subscription_lines._compute_subscription_status()

# Also recompute SO-level fields
sale_orders = subscription_lines.mapped('order_id')
sale_orders._compute_has_subscription_lines()
sale_orders._compute_renewal_count()
sale_orders._compute_subscription_status_summary()

print(f"Recomputed {len(sale_orders)} sale orders")

# Show S00164 status
so_s00164 = env['sale.order'].search([('name', '=', 'S00164')], limit=1)
if so_s00164:
    print(f"\n=== SO S00164 Status ===")
    print(f"Has subscription lines: {so_s00164.x_has_subscription_lines}")
    print(f"Subscription status summary: {so_s00164.x_subscription_status_summary}")
    print(f"Renewal count: {so_s00164.x_renewal_count}")

    for line in so_s00164.order_line.filtered('x_is_subscription'):
        print(f"\n--- Subscription Line: {line.product_id.name} ---")
        print(f"Device count: {line.x_device_count}")
        print(f"Months: {line.x_months}")
        print(f"Start: {line.x_subscription_start}")
        print(f"End: {line.x_subscription_end}")
        print(f"Deployment: {line.x_deployment_date}")
        print(f"Status: {line.x_subscription_status}")
        print(f"Days to expiry: {line.x_days_to_expiry}")
else:
    print("SO S00164 not found")

env.cr.commit()
print("\n✅ Done! Changes committed.")
