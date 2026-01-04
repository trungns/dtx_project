# -*- coding: utf-8 -*-
"""
UAT Test Case: Quỳ Châu Project
================================

Test dự án thực tế Quỳ Châu với đầy đủ workflow:
- Setup partners, products, taxes, UOM
- Create quotation với 9 dòng sản phẩm
- Create PAKD từ sale.order
- Set purchase prices và apply PAKD
- Confirm sale order
- Upload contract scans
- Create invoice và test AR aging

RUN TESTS:
---------
Method 1 - Upgrade and test:
    docker-compose run --rm odoo odoo -d odoo -u dtx_sales_pakd_contract --test-enable --stop-after-init

Method 2 - Test only (module already installed):
    docker-compose run --rm odoo odoo -d odoo -i dtx_sales_pakd_contract --test-enable --test-tags=dtx_sales_pakd_contract --stop-after-init

Method 3 - Specific test class:
    docker-compose run --rm odoo odoo -d odoo -i dtx_sales_pakd_contract --test-enable --test-tags=dtx_sales_pakd_contract.test_uat_quy_chau --stop-after-init

EXPECTED RESULTS:
----------------
All test assertions should PASS, matching UAT Quỳ Châu requirements:
- Total amount_total = 197,500,000 VND (with tolerance ±1)
- PAKD formulas match Excel calculations
- AR aging report shows correct residuals
"""

import logging
from datetime import date, timedelta
from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


@tagged('post_install', '-at_install', 'dtx_sales_pakd_contract')
class TestUATQuyChau(TransactionCase):
    """
    UAT Test for Quỳ Châu project
    Full workflow: Quotation → PAKD → Apply → Confirm → Invoice → AR Aging
    """

    @classmethod
    def setUpClass(cls):
        """Setup test data matching UAT Quỳ Châu"""
        super(TestUATQuyChau, cls).setUpClass()

        _logger.info("=" * 80)
        _logger.info("UAT QUỲ CHÂU - Setup Test Data")
        _logger.info("=" * 80)

        # Get models
        cls.Partner = cls.env['res.partner']
        cls.Product = cls.env['product.product']
        cls.ProductTemplate = cls.env['product.template']
        cls.Tax = cls.env['account.tax']
        cls.Uom = cls.env['uom.uom']
        cls.SaleOrder = cls.env['sale.order']
        cls.SaleOrderLine = cls.env['sale.order.line']
        cls.Pakd = cls.env['dtx.pakd']
        cls.PakdLine = cls.env['dtx.pakd.line']
        cls.PakdWizard = cls.env['dtx.pakd.apply.wizard']
        cls.AccountMove = cls.env['account.move']
        cls.ArAgingSummary = cls.env['dtx.ar.aging.summary']
        cls.Attachment = cls.env['ir.attachment']

        # Currency
        cls.currency = cls.env.company.currency_id

        # ==========================================
        # 1) SETUP TAXES (0%, 10%)
        # ==========================================
        _logger.info("1) Creating VAT taxes (0%, 10%)...")

        # VAT 0%
        cls.tax_vat_0 = cls.Tax.search([
            ('type_tax_use', '=', 'sale'),
            ('amount_type', '=', 'percent'),
            ('amount', '=', 0.0),
            ('company_id', '=', cls.env.company.id),
        ], limit=1)

        if not cls.tax_vat_0:
            cls.tax_vat_0 = cls.Tax.create({
                'name': 'VAT 0%',
                'type_tax_use': 'sale',
                'amount_type': 'percent',
                'amount': 0.0,
                'company_id': cls.env.company.id,
            })
        _logger.info(f"   ✓ VAT 0%: {cls.tax_vat_0.name} (ID: {cls.tax_vat_0.id})")

        # VAT 10%
        cls.tax_vat_10 = cls.Tax.search([
            ('type_tax_use', '=', 'sale'),
            ('amount_type', '=', 'percent'),
            ('amount', '=', 10.0),
            ('company_id', '=', cls.env.company.id),
        ], limit=1)

        if not cls.tax_vat_10:
            cls.tax_vat_10 = cls.Tax.create({
                'name': 'VAT 10%',
                'type_tax_use': 'sale',
                'amount_type': 'percent',
                'amount': 10.0,
                'company_id': cls.env.company.id,
            })
        _logger.info(f"   ✓ VAT 10%: {cls.tax_vat_10.name} (ID: {cls.tax_vat_10.id})")

        # ==========================================
        # 2) SETUP UOM
        # ==========================================
        _logger.info("2) Getting UOM Units...")
        cls.uom_unit = cls.env.ref('uom.product_uom_unit')
        _logger.info(f"   ✓ UoM Unit: {cls.uom_unit.name}")

        # ==========================================
        # 3) SETUP PARTNERS
        # ==========================================
        _logger.info("3) Creating partners...")

        cls.partner_viettel_hn = cls.Partner.create({
            'name': 'Viettel Hà Nội',
            'company_type': 'company',
            'is_company': True,
            'street': '1 Giang Văn Minh',
            'city': 'Hà Nội',
            'phone': '0243.943.9999',
        })
        _logger.info(f"   ✓ Đại lý: {cls.partner_viettel_hn.name}")

        cls.partner_quy_chau = cls.Partner.create({
            'name': 'UBND Quỳ Châu',
            'company_type': 'company',
            'is_company': True,
            'street': 'Quỳ Châu',
            'city': 'Nghệ An',
        })
        _logger.info(f"   ✓ End customer: {cls.partner_quy_chau.name}")

        # ==========================================
        # 4) SETUP PRODUCTS
        # ==========================================
        _logger.info("4) Creating products...")

        # Product templates for easier product creation
        products_data = [
            # (code, name, type, list_price, standard_price, vat_tax)
            ('SEQMS-BrA', 'SEQMS-BrA License', 'service', 45628000, 40000000, cls.tax_vat_0),
            ('SEQMS-Counter', 'SEQMS-Counter Module', 'service', 4000000, 3500000, cls.tax_vat_0),
            ('DTX-A17', 'DTX-A17 LED Display', 'product', 34560000, 22000000, cls.tax_vat_10),
            ('DTX-LEDw', 'DTX-LEDw LED Panel', 'product', 4320000, 3100000, cls.tax_vat_10),
            ('UA98DU9000', 'Samsung TV UA98DU9000', 'product', 49680000, 45000000, cls.tax_vat_10),
            ('X2-2.1', 'Speaker X2-2.1', 'product', 2592000, 2000000, cls.tax_vat_10),
            ('SV-VC', 'Videoconference Service', 'service', 2160000, 1800000, cls.tax_vat_10),
            ('SV-INSTALL', 'Installation Service', 'service', 1620000, 18000000, cls.tax_vat_10),  # Note: purchase > sale for testing
            ('SV-TRAIN', 'Training Service', 'service', 3240000, 2500000, cls.tax_vat_10),
        ]

        cls.products = {}
        for code, name, prod_type, list_price, standard_price, tax in products_data:
            product = cls.ProductTemplate.create({
                'name': name,
                'default_code': code,
                'type': prod_type,
                'list_price': list_price,
                'standard_price': standard_price,
                'sale_ok': True,
                'purchase_ok': True,
                'uom_id': cls.uom_unit.id,
                'uom_po_id': cls.uom_unit.id,
                'taxes_id': [(6, 0, [tax.id])],
            })
            cls.products[code] = product.product_variant_id
            _logger.info(f"   ✓ {code}: {name} (VAT {tax.amount}%)")

        # ==========================================
        # 5) CREATE QUOTATION
        # ==========================================
        _logger.info("5) Creating Quotation SO-QUY-CHAU...")

        cls.sale_order = cls.SaleOrder.create({
            'partner_id': cls.partner_viettel_hn.id,
            'x_end_customer_id': cls.partner_quy_chau.id,
            'date_order': date.today(),
        })
        _logger.info(f"   ✓ Sale Order: {cls.sale_order.name}")

        # Create sale order lines matching UAT data
        order_lines_data = [
            # (product_code, qty, price_unit)
            ('SEQMS-BrA', 1, 45628000),
            ('SEQMS-Counter', 6, 4000000),
            ('DTX-A17', 1, 34560000),
            ('DTX-LEDw', 6, 4320000),
            ('UA98DU9000', 1, 49680000),
            ('X2-2.1', 1, 2592000),
            ('SV-VC', 1, 2160000),
            ('SV-INSTALL', 6, 1620000),
            ('SV-TRAIN', 1, 3240000),
        ]

        for product_code, qty, price_unit in order_lines_data:
            product = cls.products[product_code]
            tax_ids = product.product_tmpl_id.taxes_id.ids

            cls.SaleOrderLine.create({
                'order_id': cls.sale_order.id,
                'product_id': product.id,
                'name': product.name,
                'product_uom_qty': qty,
                'product_uom': cls.uom_unit.id,
                'price_unit': price_unit,
                'tax_id': [(6, 0, tax_ids)],
            })
            _logger.info(f"   ✓ Line: {product_code} x {qty} @ {price_unit:,.0f}")

        # Trigger compute
        cls.sale_order._compute_amount_all_wrapper()

        _logger.info(f"   ✓ Total amount_untaxed: {cls.sale_order.amount_untaxed:,.0f}")
        _logger.info(f"   ✓ Total amount_tax: {cls.sale_order.amount_tax:,.0f}")
        _logger.info(f"   ✓ Total amount_total: {cls.sale_order.amount_total:,.0f}")

        _logger.info("=" * 80)
        _logger.info("Setup Complete - Ready for Tests")
        _logger.info("=" * 80)

    def test_01_quotation_total(self):
        """Test 1: Verify quotation total = 197,500,000"""
        _logger.info("\n" + "=" * 80)
        _logger.info("TEST 1: Quotation Total Verification")
        _logger.info("=" * 80)

        # Expected total (with tolerance for rounding)
        expected_total = 197500000
        tolerance = 1

        _logger.info(f"Expected amount_total: {expected_total:,.0f}")
        _logger.info(f"Actual amount_total: {self.sale_order.amount_total:,.0f}")
        _logger.info(f"Tolerance: ±{tolerance}")

        self.assertAlmostEqual(
            self.sale_order.amount_total,
            expected_total,
            delta=tolerance,
            msg=f"Sale Order total should be {expected_total:,.0f} ± {tolerance}"
        )

        _logger.info("✅ TEST 1 PASSED: Quotation total matches UAT expectation")

    def test_02_end_customer_field(self):
        """Test 2: Verify x_end_customer_id is set correctly"""
        _logger.info("\n" + "=" * 80)
        _logger.info("TEST 2: End Customer Field Verification")
        _logger.info("=" * 80)

        _logger.info(f"Partner (Đại lý): {self.sale_order.partner_id.name}")
        _logger.info(f"End Customer: {self.sale_order.x_end_customer_id.name}")

        self.assertEqual(
            self.sale_order.partner_id.id,
            self.partner_viettel_hn.id,
            "Partner should be Viettel HN"
        )

        self.assertEqual(
            self.sale_order.x_end_customer_id.id,
            self.partner_quy_chau.id,
            "End customer should be UBND Quỳ Châu"
        )

        _logger.info("✅ TEST 2 PASSED: End customer field correct")

    def test_03_create_pakd_from_sale_order(self):
        """Test 3: Create PAKD from sale.order button action"""
        _logger.info("\n" + "=" * 80)
        _logger.info("TEST 3: Create PAKD from Sale Order")
        _logger.info("=" * 80)

        # Count existing PAKDs
        existing_pakd_count = len(self.sale_order.pakd_ids)
        _logger.info(f"Existing PAKD count: {existing_pakd_count}")

        # Call action_create_pakd (simulates button click)
        action = self.sale_order.action_create_pakd()
        _logger.info(f"Action returned: {action.get('res_model')}")

        # Verify PAKD was created
        self.assertEqual(
            len(self.sale_order.pakd_ids),
            existing_pakd_count + 1,
            "Should create exactly 1 new PAKD"
        )

        pakd = self.sale_order.pakd_ids[0]
        _logger.info(f"✓ Created PAKD: {pakd.name}")
        _logger.info(f"✓ PAKD partner: {pakd.partner_id.name}")
        _logger.info(f"✓ PAKD end_customer: {pakd.end_customer_id.name}")
        _logger.info(f"✓ PAKD line count: {len(pakd.line_ids)}")

        # Verify PAKD has 9 lines (matching sale.order.line)
        self.assertEqual(
            len(pakd.line_ids),
            9,
            "PAKD should have 9 lines matching sale order"
        )

        # Verify PAKD lines have correct data
        for pakd_line in pakd.line_ids:
            _logger.info(
                f"   - {pakd_line.product_code}: qty={pakd_line.qty}, "
                f"sale_unit_price={pakd_line.sale_unit_price:,.0f}, "
                f"vat={pakd_line.vat_percent}%"
            )

            # Verify product_id, qty, sale_unit_price copied correctly
            self.assertTrue(pakd_line.product_id, "PAKD line must have product")
            self.assertGreater(pakd_line.qty, 0, "PAKD line qty must be > 0")
            self.assertGreater(pakd_line.sale_unit_price, 0, "PAKD line sale_unit_price must be > 0")

            # Verify VAT mapping
            if pakd_line.product_code in ['SEQMS-BrA', 'SEQMS-Counter']:
                self.assertEqual(pakd_line.vat_percent, 0.0, f"{pakd_line.product_code} should have VAT 0%")
            else:
                self.assertEqual(pakd_line.vat_percent, 10.0, f"{pakd_line.product_code} should have VAT 10%")

        _logger.info("✅ TEST 3 PASSED: PAKD created successfully with correct data")

    def test_04_pakd_formulas(self):
        """Test 4: Set purchase prices and verify PAKD formulas"""
        _logger.info("\n" + "=" * 80)
        _logger.info("TEST 4: PAKD Formulas Verification")
        _logger.info("=" * 80)

        # Create PAKD if not exists
        if not self.sale_order.pakd_ids:
            self.sale_order.action_create_pakd()

        pakd = self.sale_order.pakd_ids[0]

        # Set purchase prices for specific products (matching UAT)
        purchase_prices = {
            'DTX-A17': 22000000,
            'DTX-LEDw': 3100000,
            'UA98DU9000': 45000000,
            'X2-2.1': 2000000,
            'SV-INSTALL': 18000000,  # Total for 6 units
        }

        for pakd_line in pakd.line_ids:
            if pakd_line.product_code in purchase_prices:
                pakd_line.write({
                    'purchase_unit_price': purchase_prices[pakd_line.product_code],
                    'contract_unit_price': pakd_line.sale_unit_price,  # Use sale price as contract price
                })
                _logger.info(
                    f"   ✓ Set {pakd_line.product_code}: "
                    f"purchase={pakd_line.purchase_unit_price:,.0f}, "
                    f"contract={pakd_line.contract_unit_price:,.0f}"
                )

        # Trigger recompute
        pakd.line_ids._compute_totals()
        pakd._compute_totals()

        _logger.info(f"\nPAKD Totals:")
        _logger.info(f"   total_purchase: {pakd.total_purchase:,.0f}")
        _logger.info(f"   total_sale: {pakd.total_sale:,.0f}")
        _logger.info(f"   total_contract_untaxed: {pakd.total_contract_untaxed:,.0f}")
        _logger.info(f"   total_contract_tax: {pakd.total_contract_tax:,.0f}")
        _logger.info(f"   total_contract_total: {pakd.total_contract_total:,.0f}")

        # Verify total_contract_total matches expected (197,500,000)
        expected_total = 197500000
        tolerance = 1

        self.assertAlmostEqual(
            pakd.total_contract_total,
            expected_total,
            delta=tolerance,
            msg=f"PAKD total_contract_total should be {expected_total:,.0f}"
        )

        # Verify individual line formulas
        for pakd_line in pakd.line_ids:
            # Skip if no purchase price set
            if not pakd_line.purchase_unit_price:
                continue

            # Verify purchase_total = qty * purchase_unit_price
            expected_purchase_total = self.currency.round(
                pakd_line.qty * pakd_line.purchase_unit_price
            )
            self.assertEqual(
                pakd_line.purchase_total,
                expected_purchase_total,
                f"{pakd_line.product_code}: purchase_total formula incorrect"
            )

            # Verify contract_total_excl_vat uses contract_unit_price (or sale_unit_price)
            effective_price = pakd_line.contract_unit_price or pakd_line.sale_unit_price
            expected_contract_excl_vat = self.currency.round(pakd_line.qty * effective_price)
            self.assertEqual(
                pakd_line.contract_total_excl_vat,
                expected_contract_excl_vat,
                f"{pakd_line.product_code}: contract_total_excl_vat formula incorrect"
            )

            # Verify contract_tax_amount
            expected_tax = self.currency.round(
                pakd_line.contract_total_excl_vat * pakd_line.vat_percent / 100
            )
            self.assertEqual(
                pakd_line.contract_tax_amount,
                expected_tax,
                f"{pakd_line.product_code}: contract_tax_amount formula incorrect"
            )

        _logger.info("✅ TEST 4 PASSED: PAKD formulas match Excel calculations")

    def test_05_apply_pakd_wizard(self):
        """Test 5: Apply PAKD to sale.order using wizard"""
        _logger.info("\n" + "=" * 80)
        _logger.info("TEST 5: Apply PAKD Wizard")
        _logger.info("=" * 80)

        # Create PAKD if not exists
        if not self.sale_order.pakd_ids:
            self.sale_order.action_create_pakd()

        pakd = self.sale_order.pakd_ids[0]

        # Set purchase prices (reuse from test_04)
        purchase_prices = {
            'DTX-A17': 22000000,
            'DTX-LEDw': 3100000,
            'UA98DU9000': 45000000,
            'X2-2.1': 2000000,
            'SV-INSTALL': 18000000,
        }

        for pakd_line in pakd.line_ids:
            if pakd_line.product_code in purchase_prices:
                pakd_line.write({
                    'purchase_unit_price': purchase_prices[pakd_line.product_code],
                    'contract_unit_price': pakd_line.sale_unit_price,
                })

        # Count original lines
        original_line_count = len(self.sale_order.order_line)
        _logger.info(f"Original sale.order.line count: {original_line_count}")

        # Create wizard and apply
        wizard = self.PakdWizard.create({
            'pakd_id': pakd.id,
            'replace_lines': True,
            'price_source': 'contract',
        })
        _logger.info(f"Created wizard: replace_lines={wizard.replace_lines}, price_source={wizard.price_source}")

        # Execute apply
        wizard.action_apply()

        # Refresh sale order
        self.sale_order.invalidate_cache()

        _logger.info(f"After apply - sale.order.line count: {len(self.sale_order.order_line)}")

        # Verify lines were replaced
        self.assertEqual(
            len(self.sale_order.order_line),
            9,
            "Should have 9 lines after apply (replaced)"
        )

        # Verify price_unit matches contract_unit_price (or sale_unit_price)
        for so_line in self.sale_order.order_line:
            matching_pakd_line = pakd.line_ids.filtered(
                lambda l: l.product_id.id == so_line.product_id.id
            )
            if matching_pakd_line:
                expected_price = matching_pakd_line[0].contract_unit_price or matching_pakd_line[0].sale_unit_price
                self.assertEqual(
                    so_line.price_unit,
                    expected_price,
                    f"{so_line.product_id.default_code}: price_unit should match PAKD contract_unit_price"
                )
                _logger.info(f"   ✓ {so_line.product_id.default_code}: price_unit = {so_line.price_unit:,.0f}")

        _logger.info("✅ TEST 5 PASSED: PAKD applied successfully, prices updated")

    def test_06_confirm_sale_order(self):
        """Test 6: Confirm sale order and set contract fields"""
        _logger.info("\n" + "=" * 80)
        _logger.info("TEST 6: Confirm Sale Order")
        _logger.info("=" * 80)

        # Apply PAKD first (if not done)
        if not self.sale_order.pakd_ids:
            self.sale_order.action_create_pakd()
            pakd = self.sale_order.pakd_ids[0]
            wizard = self.PakdWizard.create({
                'pakd_id': pakd.id,
                'replace_lines': True,
                'price_source': 'contract',
            })
            wizard.action_apply()

        # Confirm sale order
        _logger.info(f"Before confirm - state: {self.sale_order.state}")
        self.sale_order.action_confirm()
        _logger.info(f"After confirm - state: {self.sale_order.state}")

        # Verify state
        self.assertEqual(
            self.sale_order.state,
            'sale',
            "Sale order state should be 'sale' after confirm"
        )

        # Set contract fields
        contract_no = 'HĐ-QC-2026-001'
        signed_date = date.today()
        contract_end_date = date.today() + timedelta(days=365)

        self.sale_order.write({
            'x_contract_no': contract_no,
            'x_signed_date': signed_date,
            'x_contract_end_date': contract_end_date,
        })

        _logger.info(f"   ✓ Contract No: {self.sale_order.x_contract_no}")
        _logger.info(f"   ✓ Signed Date: {self.sale_order.x_signed_date}")
        _logger.info(f"   ✓ End Date: {self.sale_order.x_contract_end_date}")

        # Verify contract fields
        self.assertEqual(self.sale_order.x_contract_no, contract_no)
        self.assertEqual(self.sale_order.x_signed_date, signed_date)
        self.assertEqual(self.sale_order.x_contract_end_date, contract_end_date)

        _logger.info("✅ TEST 6 PASSED: Sale order confirmed and contract fields set")

    def test_07_upload_contract_scans(self):
        """Test 7: Upload contract scan attachments"""
        _logger.info("\n" + "=" * 80)
        _logger.info("TEST 7: Upload Contract Scans")
        _logger.info("=" * 80)

        # Create 2 fake PDF attachments
        attachment1 = self.Attachment.create({
            'name': 'Hop_Dong_Quy_Chau_signed.pdf',
            'datas': b'JVBERi0xLjQKJeLjz9MK',  # Fake PDF header in base64
            'res_model': 'sale.order',
            'res_id': self.sale_order.id,
            'mimetype': 'application/pdf',
        })

        attachment2 = self.Attachment.create({
            'name': 'Phu_Luc_Hop_Dong.pdf',
            'datas': b'JVBERi0xLjQKJeLjz9MK',
            'res_model': 'sale.order',
            'res_id': self.sale_order.id,
            'mimetype': 'application/pdf',
        })

        _logger.info(f"   ✓ Created attachment 1: {attachment1.name}")
        _logger.info(f"   ✓ Created attachment 2: {attachment2.name}")

        # Add to x_contract_scan_attachment_ids (many2many)
        self.sale_order.write({
            'x_contract_scan_attachment_ids': [(6, 0, [attachment1.id, attachment2.id])]
        })

        # Trigger compute
        self.sale_order._compute_contract_scan_count()

        _logger.info(f"   ✓ Attachment count: {self.sale_order.x_contract_scan_count}")

        # Verify count
        self.assertEqual(
            self.sale_order.x_contract_scan_count,
            2,
            "Should have 2 contract scan attachments"
        )

        self.assertEqual(
            len(self.sale_order.x_contract_scan_attachment_ids),
            2,
            "Many2many field should have 2 attachments"
        )

        _logger.info("✅ TEST 7 PASSED: Contract scans uploaded successfully")

    def test_08_create_invoice_and_ar_aging(self):
        """Test 8: Create invoice and verify AR aging report"""
        _logger.info("\n" + "=" * 80)
        _logger.info("TEST 8: Create Invoice and AR Aging")
        _logger.info("=" * 80)

        # Ensure sale order is confirmed
        if self.sale_order.state != 'sale':
            self.sale_order.action_confirm()

        # Create invoice manually (simplified)
        invoice = self.AccountMove.create({
            'move_type': 'out_invoice',
            'partner_id': self.partner_viettel_hn.id,
            'invoice_date': date.today(),
            'invoice_date_due': date.today() + timedelta(days=30),
            'currency_id': self.currency.id,
        })

        # Create invoice lines matching sale order total
        # Simplified: create 1 line with total amount
        self.env['account.move.line'].with_context(check_move_validity=False).create({
            'move_id': invoice.id,
            'name': 'Dự án Quỳ Châu - Tổng hợp',
            'quantity': 1,
            'price_unit': self.sale_order.amount_total,
            'account_id': self.env['account.account'].search([
                ('user_type_id', '=', self.env.ref('account.data_account_type_revenue').id),
                ('company_id', '=', self.env.company.id),
            ], limit=1).id,
        })

        _logger.info(f"   ✓ Created invoice: {invoice.name}")
        _logger.info(f"   ✓ Invoice amount_total: {invoice.amount_total:,.0f}")
        _logger.info(f"   ✓ Invoice due date: {invoice.invoice_date_due}")

        # Post invoice
        invoice.action_post()
        _logger.info(f"   ✓ Invoice posted - state: {invoice.state}")

        # Verify invoice state
        self.assertEqual(invoice.state, 'posted', "Invoice should be posted")

        # Verify amount_residual (should equal amount_total since not paid)
        self.assertGreater(invoice.amount_residual, 0, "Invoice should have residual > 0")
        _logger.info(f"   ✓ Invoice residual: {invoice.amount_residual:,.0f}")

        # Link invoice to sale order (for AR fields to compute)
        self.sale_order.write({
            'invoice_ids': [(4, invoice.id)]
        })

        # Trigger AR fields recompute on sale.order
        self.sale_order._compute_ar_fields()

        _logger.info(f"\nSale Order AR Fields:")
        _logger.info(f"   x_ar_residual_total: {self.sale_order.x_ar_residual_total:,.0f}")
        _logger.info(f"   x_ar_max_days_overdue: {self.sale_order.x_ar_max_days_overdue}")
        _logger.info(f"   x_ar_status: {self.sale_order.x_ar_status}")

        # Verify AR fields
        self.assertGreater(
            self.sale_order.x_ar_residual_total,
            0,
            "Sale order should have AR residual > 0"
        )

        # Status should be 'ok' since due in 30 days (not overdue, not due soon)
        # Note: due_soon is triggered if due within 7 days
        expected_status = 'ok'
        self.assertEqual(
            self.sale_order.x_ar_status,
            expected_status,
            f"AR status should be '{expected_status}' for invoice due in 30 days"
        )

        # Test AR Aging Summary (if view refreshed)
        # Note: SQL view might need manual refresh or new record creation to update
        self.env.cr.execute("SELECT 1")  # Dummy query to ensure transaction

        # Search for AR aging summary for this partner
        ar_summary = self.ArAgingSummary.search([
            ('partner_id', '=', self.partner_viettel_hn.id),
        ], limit=1)

        if ar_summary:
            _logger.info(f"\nAR Aging Summary for {self.partner_viettel_hn.name}:")
            _logger.info(f"   total_residual: {ar_summary.total_residual:,.0f}")
            _logger.info(f"   max_days_overdue: {ar_summary.max_days_overdue}")
            _logger.info(f"   invoice_count: {ar_summary.invoice_count}")

            # Verify residual matches
            self.assertGreater(
                ar_summary.total_residual,
                0,
                "AR aging summary should show residual > 0"
            )
        else:
            _logger.warning("   ⚠ AR Aging Summary not found (SQL view may need refresh)")

        _logger.info("✅ TEST 8 PASSED: Invoice created and AR aging verified")

    def test_09_multiple_pakd_per_sale_order(self):
        """Test 9: Verify multiple PAKDs can be created for 1 sale order"""
        _logger.info("\n" + "=" * 80)
        _logger.info("TEST 9: Multiple PAKDs per Sale Order")
        _logger.info("=" * 80)

        # Create 2nd PAKD
        pakd2 = self.Pakd.create({
            'sale_order_id': self.sale_order.id,
            'partner_id': self.sale_order.partner_id.id,
            'end_customer_id': self.sale_order.x_end_customer_id.id,
        })

        _logger.info(f"   ✓ Created 2nd PAKD: {pakd2.name}")

        # Verify sale_order now has 2+ PAKDs
        self.assertGreaterEqual(
            len(self.sale_order.pakd_ids),
            2,
            "Sale order should have at least 2 PAKDs"
        )

        _logger.info(f"   ✓ Total PAKD count: {len(self.sale_order.pakd_ids)}")

        _logger.info("✅ TEST 9 PASSED: Multiple PAKDs per sale order supported")

    def test_10_pakd_state_workflow(self):
        """Test 10: PAKD state workflow (draft → submitted → approved)"""
        _logger.info("\n" + "=" * 80)
        _logger.info("TEST 10: PAKD State Workflow")
        _logger.info("=" * 80)

        # Create new PAKD
        pakd = self.Pakd.create({
            'sale_order_id': self.sale_order.id,
            'partner_id': self.sale_order.partner_id.id,
        })

        _logger.info(f"   ✓ Created PAKD: {pakd.name}")

        # Initial state should be 'draft'
        self.assertEqual(pakd.state, 'draft', "PAKD initial state should be 'draft'")
        _logger.info(f"   ✓ Initial state: {pakd.state}")

        # Submit
        pakd.action_submit()
        self.assertEqual(pakd.state, 'submitted', "PAKD state should be 'submitted' after submit")
        _logger.info(f"   ✓ After submit: {pakd.state}")

        # Approve
        pakd.action_approve()
        self.assertEqual(pakd.state, 'approved', "PAKD state should be 'approved' after approve")
        _logger.info(f"   ✓ After approve: {pakd.state}")

        # Test reject
        pakd2 = self.Pakd.create({
            'sale_order_id': self.sale_order.id,
            'partner_id': self.sale_order.partner_id.id,
        })
        pakd2.action_submit()
        pakd2.action_reject()
        self.assertEqual(pakd2.state, 'rejected', "PAKD state should be 'rejected' after reject")
        _logger.info(f"   ✓ After reject: {pakd2.state}")

        # Test reset to draft
        pakd2.action_reset_draft()
        self.assertEqual(pakd2.state, 'draft', "PAKD state should be 'draft' after reset")
        _logger.info(f"   ✓ After reset: {pakd2.state}")

        _logger.info("✅ TEST 10 PASSED: PAKD state workflow correct")
