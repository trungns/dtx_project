# DTX Sales PAKD Contract - Automated Tests

## Test Files

- `test_uat_quy_chau.py`: UAT test case for Quỳ Châu project (197.5M VND contract)

## Test Coverage

### TestUATQuyChau - Full Workflow Test

Comprehensive test simulating real Quỳ Châu project:

1. ✅ **test_01_quotation_total**: Verify quotation total = 197,500,000 VND
2. ✅ **test_02_end_customer_field**: Verify end customer field setup
3. ✅ **test_03_create_pakd_from_sale_order**: Create PAKD via button action
4. ✅ **test_04_pakd_formulas**: Verify PAKD formulas match Excel
5. ✅ **test_05_apply_pakd_wizard**: Apply PAKD to sale order
6. ✅ **test_06_confirm_sale_order**: Confirm SO and set contract fields
7. ✅ **test_07_upload_contract_scans**: Upload PDF attachments
8. ✅ **test_08_create_invoice_and_ar_aging**: Invoice creation and AR aging
9. ✅ **test_09_multiple_pakd_per_sale_order**: Multiple PAKDs support
10. ✅ **test_10_pakd_state_workflow**: PAKD state transitions

## Running Tests

### Prerequisites

- Odoo 16 Community installed
- Module `dtx_sales_pakd_contract` available in addons path
- Docker environment (if using docker-compose)

### Method 1: Upgrade Module + Run Tests

```bash
cd odoo-dev
docker-compose run --rm odoo odoo -d odoo -u dtx_sales_pakd_contract --test-enable --stop-after-init
```

This will:
- Upgrade the module
- Run all tests in the module
- Stop after completion

### Method 2: Install Module + Run Tests

```bash
docker-compose run --rm odoo odoo -d odoo -i dtx_sales_pakd_contract --test-enable --stop-after-init
```

### Method 3: Run Specific Test File

```bash
docker-compose run --rm odoo odoo -d odoo \
  --test-enable \
  --test-tags=dtx_sales_pakd_contract.test_uat_quy_chau \
  --stop-after-init
```

### Method 4: Run Without Docker

```bash
# If running Odoo directly (not in docker)
odoo -c /path/to/odoo.conf -d odoo_db -u dtx_sales_pakd_contract --test-enable --stop-after-init
```

### Method 5: Run Tests for All Installed Modules

```bash
docker-compose run --rm odoo odoo -d odoo --test-enable --stop-after-init
```

## Reading Test Output

### Success Output

```
...
2026-01-04 10:30:15,123 1 INFO odoo.tests TEST 1 PASSED: Quotation total matches UAT expectation
...
✅ TEST 8 PASSED: Invoice created and AR aging verified
...
Ran 10 tests in 5.234s

OK
```

### Failure Output

```
FAIL: test_01_quotation_total (odoo.addons.dtx_sales_pakd_contract.tests.test_uat_quy_chau.TestUATQuyChau)
...
AssertionError: Sale Order total should be 197500000 ± 1
```

## Test Data

### Products Created

| Code | Name | Type | VAT | Sale Price |
|------|------|------|-----|------------|
| SEQMS-BrA | SEQMS-BrA License | Service | 0% | 45,628,000 |
| SEQMS-Counter | SEQMS-Counter Module | Service | 0% | 4,000,000 |
| DTX-A17 | DTX-A17 LED Display | Product | 10% | 34,560,000 |
| DTX-LEDw | DTX-LEDw LED Panel | Product | 10% | 4,320,000 |
| UA98DU9000 | Samsung TV | Product | 10% | 49,680,000 |
| X2-2.1 | Speaker X2-2.1 | Product | 10% | 2,592,000 |
| SV-VC | Videoconference Service | Service | 10% | 2,160,000 |
| SV-INSTALL | Installation Service | Service | 10% | 1,620,000 |
| SV-TRAIN | Training Service | Service | 10% | 3,240,000 |

### Partners Created

- **Viettel Hà Nội**: Đại lý (partner_id)
- **UBND Quỳ Châu**: End customer (x_end_customer_id)

### Expected Totals

- **Quotation Lines**: 9 lines
- **Amount Total**: 197,500,000 VND (with ±1 tolerance)
- **PAKD Lines**: 9 lines matching quotation
- **Contract Scans**: 2 PDF attachments

## Troubleshooting

### Test Fails with "Module not found"

Ensure module is in addons path:
```bash
# Check addons path in odoo.conf
addons_path = /mnt/extra-addons
```

### Test Fails with "Database connection error"

Ensure PostgreSQL is running:
```bash
docker-compose up -d db
```

### Tests Pass but No Output

Add `--log-level=test` for verbose output:
```bash
docker-compose run --rm odoo odoo -d odoo \
  -u dtx_sales_pakd_contract \
  --test-enable \
  --log-level=test \
  --stop-after-init
```

### AR Aging Summary Not Found

SQL views may need manual refresh. Run in psql:
```sql
-- Refresh AR aging view
DROP VIEW IF EXISTS dtx_ar_aging_summary;
-- Then re-run module upgrade
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Odoo Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_DB: odoo
          POSTGRES_PASSWORD: odoo
    steps:
      - uses: actions/checkout@v2
      - name: Run Odoo Tests
        run: |
          docker-compose run --rm odoo \
            odoo -d odoo -i dtx_sales_pakd_contract \
            --test-enable --stop-after-init
```

## Contributing

When adding new tests:

1. Follow naming convention: `test_XX_description`
2. Add docstring explaining test purpose
3. Use `_logger.info()` for test progress logging
4. Use `self.assert*()` methods from `unittest.TestCase`
5. Clean up test data in `tearDown()` if needed (optional with SavepointCase)

## License

LGPL-3 (same as module license)
