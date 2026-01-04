#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick setup script for UAT Quỳ Châu test data
Run this to quickly create partners, products, and taxes needed for testing

Usage:
    docker-compose exec odoo python3 /mnt/extra-addons/dtx_sales_pakd_contract/scripts/setup_uat_quy_chau_data.py
"""

import odoorpc

# Connection
odoo = odoorpc.ODOO('localhost', port=8069)
odoo.login('odoo', 'admin', 'admin')

print("=" * 80)
print("UAT QUỲ CHÂU - Quick Setup Script")
print("=" * 80)

# Models
Partner = odoo.env['res.partner']
Product = odoo.env['product.product']
ProductTemplate = odoo.env['product.template']
Tax = odoo.env['account.tax']
Company = odoo.env['res.company']

company_id = odoo.env.company.id

# ==========================================
# 1. SETUP TAXES
# ==========================================
print("\n1. Setting up taxes...")

# VAT 0%
tax_0 = Tax.search([
    ('type_tax_use', '=', 'sale'),
    ('amount_type', '=', 'percent'),
    ('amount', '=', 0.0),
    ('company_id', '=', company_id)
])

if not tax_0:
    tax_0_id = Tax.create({
        'name': 'VAT 0%',
        'type_tax_use': 'sale',
        'amount_type': 'percent',
        'amount': 0.0,
        'company_id': company_id,
    })
    print(f"   ✓ Created VAT 0% (ID: {tax_0_id})")
else:
    tax_0_id = tax_0[0]
    print(f"   ✓ VAT 0% exists (ID: {tax_0_id})")

# VAT 10%
tax_10 = Tax.search([
    ('type_tax_use', '=', 'sale'),
    ('amount_type', '=', 'percent'),
    ('amount', '=', 10.0),
    ('company_id', '=', company_id)
])

if not tax_10:
    tax_10_id = Tax.create({
        'name': 'VAT 10%',
        'type_tax_use': 'sale',
        'amount_type': 'percent',
        'amount': 10.0,
        'company_id': company_id,
    })
    print(f"   ✓ Created VAT 10% (ID: {tax_10_id})")
else:
    tax_10_id = tax_10[0]
    print(f"   ✓ VAT 10% exists (ID: {tax_10_id})")

# ==========================================
# 2. SETUP PARTNERS
# ==========================================
print("\n2. Setting up partners...")

# Viettel HN
partner_viettel = Partner.search([('name', '=', 'Viettel Hà Nội')])
if not partner_viettel:
    partner_viettel_id = Partner.create({
        'name': 'Viettel Hà Nội',
        'company_type': 'company',
        'is_company': True,
        'street': '1 Giang Văn Minh',
        'city': 'Hà Nội',
        'phone': '0243.943.9999',
    })
    print(f"   ✓ Created Viettel Hà Nội (ID: {partner_viettel_id})")
else:
    partner_viettel_id = partner_viettel[0]
    print(f"   ✓ Viettel Hà Nội exists (ID: {partner_viettel_id})")

# UBND Quỳ Châu
partner_qc = Partner.search([('name', '=', 'UBND Quỳ Châu')])
if not partner_qc:
    partner_qc_id = Partner.create({
        'name': 'UBND Quỳ Châu',
        'company_type': 'company',
        'is_company': True,
        'street': 'Quỳ Châu',
        'city': 'Nghệ An',
    })
    print(f"   ✓ Created UBND Quỳ Châu (ID: {partner_qc_id})")
else:
    partner_qc_id = partner_qc[0]
    print(f"   ✓ UBND Quỳ Châu exists (ID: {partner_qc_id})")

# ==========================================
# 3. SETUP PRODUCTS
# ==========================================
print("\n3. Setting up products...")

products_data = [
    # (code, name, type, list_price, vat_tax_id)
    ('SEQMS-BrA', 'SEQMS-BrA License', 'service', 45628000, tax_0_id),
    ('SEQMS-Counter', 'SEQMS-Counter Module', 'service', 4000000, tax_0_id),
    ('DTX-A17', 'DTX-A17 LED Display', 'product', 34560000, tax_10_id),
    ('DTX-LEDw', 'DTX-LEDw LED Panel', 'product', 4320000, tax_10_id),
    ('UA98DU9000', 'Samsung TV UA98DU9000', 'product', 49680000, tax_10_id),
    ('X2-2.1', 'Speaker X2-2.1', 'product', 2592000, tax_10_id),
    ('SV-VC', 'Videoconference Service', 'service', 2160000, tax_10_id),
    ('SV-INSTALL', 'Installation Service', 'service', 1620000, tax_10_id),
    ('SV-TRAIN', 'Training Service', 'service', 3240000, tax_10_id),
]

created_products = {}

for code, name, prod_type, list_price, tax_id in products_data:
    # Check if product exists
    existing = ProductTemplate.search([('default_code', '=', code)])

    if not existing:
        tmpl_id = ProductTemplate.create({
            'name': name,
            'default_code': code,
            'type': prod_type,
            'list_price': list_price,
            'standard_price': list_price * 0.7,  # Default cost
            'sale_ok': True,
            'purchase_ok': True,
            'taxes_id': [(6, 0, [tax_id])],
        })

        # Get product variant
        tmpl = ProductTemplate.browse(tmpl_id)
        product_id = tmpl.product_variant_id.id

        created_products[code] = product_id
        vat_pct = 0 if tax_id == tax_0_id else 10
        print(f"   ✓ Created {code}: {name} (VAT {vat_pct}%)")
    else:
        tmpl = ProductTemplate.browse(existing[0])
        product_id = tmpl.product_variant_id.id
        created_products[code] = product_id
        print(f"   ✓ {code} exists (ID: {product_id})")

# ==========================================
# SUMMARY
# ==========================================
print("\n" + "=" * 80)
print("SETUP COMPLETE!")
print("=" * 80)
print(f"\nTaxes:")
print(f"  - VAT 0%: ID {tax_0_id}")
print(f"  - VAT 10%: ID {tax_10_id}")
print(f"\nPartners:")
print(f"  - Viettel Hà Nội: ID {partner_viettel_id}")
print(f"  - UBND Quỳ Châu: ID {partner_qc_id}")
print(f"\nProducts: {len(created_products)} items")
for code in created_products:
    print(f"  - {code}: ID {created_products[code]}")

print(f"\n✅ Ready for UAT testing!")
print(f"\nNext steps:")
print(f"  1. Go to http://localhost:8069")
print(f"  2. Navigate: Sales → Orders → Quotations → Create")
print(f"  3. Follow MANUAL_UAT_GUIDE.md from STEP 2")
print("=" * 80)
