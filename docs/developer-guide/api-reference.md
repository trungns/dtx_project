# DTX Serial Extension - Quick Reference Card

## Field Reference

### stock.lot (Serial/Lot) - New Fields

| Field Name | Type | Description | Auto-Update |
|------------|------|-------------|-------------|
| `dtx_serial_internal` | Char | Optional DTX internal serial number | Manual |
| `lifecycle_state` | Selection | Device lifecycle state | Auto + Manual |
| `customer_id` | Many2one | Final customer | Manual |
| `vendor_invoice_state` | Selection | Invoice tracking state | Auto + Manual |
| `vendor_invoice_ref` | Char | Vendor invoice number | Manual |
| `vendor_invoice_date` | Date | Invoice date | Manual |
| `vendor_invoice_note` | Text | Invoice notes | Manual |
| `warranty_start` | Date | Warranty start date | Manual |
| `warranty_end` | Date | Warranty end date | Manual |
| `warranty_active` | Boolean | Warranty currently active | Computed |
| `gdrive_link` | Char | Google Drive URL | Manual |

## Lifecycle States

| State | Key | When Auto-Set |
|-------|-----|---------------|
| In Stock | `stock` | Receipt from supplier/production |
| Allocated to Project | `allocated` | Manual (project module) |
| Delivered | `delivered` | Delivery to customer |
| Installed | `installed` | Manual |
| Under Maintenance | `maintenance` | Transfer to maintenance location |
| Scrapped | `scrapped` | Transfer to scrap location |

## Vendor Invoice States

| State | Key | When Auto-Set |
|-------|-----|---------------|
| Invoice Missing | `missing` | Default on creation |
| Invoice Linked | `linked` | When `vendor_invoice_ref` is filled |
| Invoice Replaced | `replaced` | Manual only |

## Automatic Behaviors

### On Stock Move Validation (`stock.move.line._action_done`)

```
FROM supplier/production → TO internal
  └─> lifecycle_state = 'stock'

FROM internal → TO customer
  └─> lifecycle_state = 'delivered'

FROM customer → TO internal
  └─> lifecycle_state = 'stock'

TO maintenance location
  └─> lifecycle_state = 'maintenance'

TO scrap location
  └─> lifecycle_state = 'scrapped'
```

### On Vendor Invoice Reference Change (`@api.onchange`)

```
vendor_invoice_ref filled + state = 'missing'
  └─> vendor_invoice_state = 'linked'

vendor_invoice_ref cleared + state = 'linked'
  └─> vendor_invoice_state = 'missing'
```

### On Purchase Bill Posted (`stock.move.line.write`)

```
PO bill posted → Auto-link serials from that PO:
  - vendor_invoice_ref = bill.name
  - vendor_invoice_date = bill.invoice_date
  - vendor_invoice_state = 'linked'
```

## Search Capabilities

### Search by Serial Numbers
```python
# Search bar accepts:
- Supplier serial (name field)
- DTX internal serial (dtx_serial_internal)
```

### Available Filters
- In Stock
- Allocated
- Delivered
- Installed
- Maintenance
- Invoice Missing
- Invoice Linked
- Warranty Active

### Group By Options
- Lifecycle State
- Vendor Invoice State
- Customer
- Product

## Common Workflows

### Workflow 1: Receive Device from Supplier

1. Create PO → Confirm → Receive Products
2. Enter serial number during receipt
3. Validate receipt
   - ✓ Serial created
   - ✓ lifecycle_state = 'stock'
   - ✓ vendor_invoice_state = 'missing'
4. When vendor bill arrives:
   - Open serial → Enter `vendor_invoice_ref`
   - ✓ Auto-changes to 'linked'

### Workflow 2: Deliver Device to Customer

1. Create SO → Confirm → Delivery
2. Select existing serial
3. Validate delivery
   - ✓ lifecycle_state = 'delivered'
   - ✓ Chatter message logged

### Workflow 3: Track Warranty

1. Open serial
2. Set `warranty_start` and `warranty_end`
3. Save
   - ✓ `warranty_active` auto-computed

### Workflow 4: Send to Maintenance

1. Create Internal Transfer
2. Source: WH/Stock
3. Destination: WH/Stock/Maintenance
4. Select serial → Validate
   - ✓ lifecycle_state = 'maintenance'

## Menu Locations

```
Inventory
└── Products
    └── Device Serials  ← Main menu item
```

## Badge Color Reference

### Lifecycle State Badges
- 🟢 Green: `stock`, `installed`
- 🔵 Blue: `allocated`
- 🟡 Yellow: `maintenance`
- 🔴 Red: `scrapped`

### Vendor Invoice State Badges
- 🔴 Red: `missing`
- 🟢 Green: `linked`
- 🟡 Yellow: `replaced`

## Python API Examples

### Search serials by DTX internal serial
```python
serial = self.env['stock.lot'].search([
    ('dtx_serial_internal', '=', 'DTX-001')
], limit=1)
```

### Get all serials without vendor invoice
```python
missing_invoices = self.env['stock.lot'].search([
    ('vendor_invoice_state', '=', 'missing')
])
```

### Get all devices delivered to specific customer
```python
customer_devices = self.env['stock.lot'].search([
    ('customer_id', '=', customer_id),
    ('lifecycle_state', 'in', ['delivered', 'installed'])
])
```

### Get all devices with active warranty
```python
warranty_devices = self.env['stock.lot'].search([
    ('warranty_active', '=', True)
])
```

### Update lifecycle state manually
```python
serial = self.env['stock.lot'].browse(serial_id)
serial.write({
    'lifecycle_state': 'installed',
})
```

## Integration Points

### For dtx_vendorbill_alert Module
```python
# Check serials in outgoing picking
picking.move_line_ids.mapped('lot_id').filtered(
    lambda l: l.vendor_invoice_state == 'missing'
)
```

### For dtx_ops_project Module
```python
# Will add field to stock.lot:
project_id = fields.Many2one('dtx.ops.project', string='Project')

# And inverse field in dtx.ops.project:
serial_ids = fields.One2many('stock.lot', 'project_id', string='Devices')
```

## Tips & Best Practices

### ✓ DO
- Use supplier serial as primary key (always unique)
- Add DTX internal serial only when needed for customer
- Let lifecycle states auto-update, override only when needed
- Enter vendor invoice ref as soon as bill arrives
- Set warranty dates when known
- Use filters to monitor missing invoices

### ✗ DON'T
- Don't duplicate supplier serial in DTX internal serial
- Don't manually set lifecycle states unnecessarily
- Don't forget to link vendor invoices (causes warnings in dtx_vendorbill_alert)
- Don't delete serials (scrap them instead)

## Performance Notes

- `dtx_serial_internal` is indexed for fast search
- `name_get()` is optimized for large datasets
- `_name_search()` supports both serial fields efficiently
- All state changes logged in chatter (can grow large over time)

## Security

Uses standard Odoo stock security:
- **Inventory User**: Read, Write, Create
- **Inventory Manager**: Read, Write, Create, Delete

No custom security groups added.

## Dependencies

- `stock` (standard Odoo)
- `product` (standard Odoo)

No external Python libraries required.

---

**Version:** 16.0.1.0.0
**License:** LGPL-3
**Author:** DTX
