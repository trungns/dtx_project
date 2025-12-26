# Developer Guide

Technical documentation for developers working on DTX Odoo customizations.

## 👨‍💻 Available Guides

### [Development Environment Setup](development-environment.md)
**Audience:** Developers, system administrators
**Time:** 15 minutes
**Content:**
- Docker-based development environment
- Odoo 16 + PostgreSQL setup
- Development workflow
- Utility scripts
- Troubleshooting

**Read this to:** Set up your local development environment and understand the workflow.

---

### [API Reference](api-reference.md)
**Audience:** Odoo developers
**Time:** 20 minutes
**Content:**
- Field definitions and types
- Method signatures
- Automatic behaviors
- Python API examples
- Integration points

**Read this to:** Understand the technical implementation and extend the modules.

---

### [Code Quality Checklist](code-quality-checklist.md)
**Audience:** Developers, code reviewers
**Time:** 10 minutes
**Content:**
- Code standards (PEP 8, Odoo best practices)
- Security audit checklist
- Performance guidelines
- Testing requirements
- Documentation standards

**Read this to:** Ensure your code meets quality standards before deployment.

---

## 🛠️ Development Setup

### Prerequisites
```bash
# macOS with Apple Silicon (M1/M2)
- Docker Desktop
- Git
- Text editor (VSCode recommended)
```

### Quick Setup
```bash
cd dtx_project/odoo-dev
./start.sh
```

See [Development Environment](development-environment.md) for details.

---

## 🔄 Development Workflow

### 1. Make Changes
```bash
# Edit files in: odoo-dev/addons/dtx_serial_ext/
vim odoo-dev/addons/dtx_serial_ext/models/stock_lot.py
```

### 2. Upgrade Module
```bash
cd odoo-dev
./upgrade-module.sh dtx_serial_ext
```

### 3. Test Changes
```bash
# Open browser
open http://localhost:8069

# Test your changes
# Check logs if needed
./logs.sh
```

### 4. Commit Code
```bash
git add .
git commit -m "feat: add new field to serial tracking"
```

---

## 📚 Key Concepts

### Module Structure
```
dtx_serial_ext/
├── __manifest__.py         # Module metadata
├── __init__.py            # Python package init
├── models/                # Business logic
│   ├── __init__.py
│   ├── stock_lot.py       # Serial extension
│   └── stock_move_line.py # Auto-update logic
├── views/                 # UI definitions
│   └── stock_lot_views.xml
├── security/              # Access rights
│   └── ir.model.access.csv
└── static/description/    # Module description
    └── index.html
```

### Data Models
- **Extends:** `stock.lot` (no new tables)
- **Fields Added:** 11 new fields
- **Relationships:** Many2one to `res.partner`, prepared for `dtx.ops.project`

### Automatic Behaviors
- Lifecycle state updates on stock moves
- Vendor invoice state on reference entry
- Warranty active calculation
- Auto-linking bills to serials

See [API Reference](api-reference.md) for details.

---

## 🎯 Common Development Tasks

### Add a New Field

1. **Edit model:**
```python
# models/stock_lot.py
new_field = fields.Char(string='New Field')
```

2. **Add to view:**
```xml
<!-- views/stock_lot_views.xml -->
<field name="new_field"/>
```

3. **Upgrade module:**
```bash
./upgrade-module.sh dtx_serial_ext
```

---

### Add a Computed Field

```python
# models/stock_lot.py
@api.depends('field1', 'field2')
def _compute_new_field(self):
    for record in self:
        record.new_field = record.field1 + record.field2

new_field = fields.Float(
    compute='_compute_new_field',
    store=True
)
```

---

### Add an Onchange

```python
# models/stock_lot.py
@api.onchange('trigger_field')
def _onchange_trigger_field(self):
    if self.trigger_field:
        self.other_field = 'value'
```

---

### Override a Method

```python
# models/stock_move_line.py
def _action_done(self):
    res = super()._action_done()
    # Your custom logic here
    return res
```

---

## 🧪 Testing

### Manual Testing
See [Installation Guide](../deployment/installation-guide.md#testing-guide) for test scenarios.

### Automated Testing (Coming Soon)
```python
# tests/test_stock_lot.py
from odoo.tests.common import TransactionCase

class TestStockLot(TransactionCase):
    def test_vendor_invoice_auto_update(self):
        # Test code here
        pass
```

---

## 📊 Code Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Python files | Small | 2 ✅ |
| Lines per file | <300 | 169 max ✅ |
| Cyclomatic complexity | <10 | Low ✅ |
| Test coverage | >80% | TBD |
| Documentation | 100% | 100% ✅ |

---

## 🔐 Security Guidelines

### ✅ DO
- Use ORM methods (never raw SQL)
- Validate user input
- Use proper security groups
- Log security-relevant actions

### ❌ DON'T
- Execute raw SQL queries
- Trust user input without validation
- Bypass access rights
- Store sensitive data in logs

See [Code Quality Checklist](code-quality-checklist.md) for details.

---

## 🚀 Performance Tips

### Database
- Add indexes on frequently searched fields
- Use `store=True` judiciously
- Avoid N+1 queries

### Python
- Use list comprehensions
- Avoid heavy computations in `name_get()`
- Cache computed fields when appropriate

### UI
- Mark optional fields in tree views
- Use minimal widgets
- Lazy-load heavy data

---

## 📖 Learning Resources

### Odoo Official
- [Odoo 16 Documentation](https://www.odoo.com/documentation/16.0/)
- [Odoo ORM API](https://www.odoo.com/documentation/16.0/developer/reference/backend/orm.html)

### Best Practices
- [Odoo Guidelines](https://www.odoo.com/documentation/16.0/contributing/development/coding_guidelines.html)
- PEP 8 (Python style guide)

### DTX Project
- [API Reference](api-reference.md)
- [Code Quality Checklist](code-quality-checklist.md)

---

## 🆘 Getting Help

### Documentation
1. Check this guide
2. Review [API Reference](api-reference.md)
3. Check Odoo official docs

### Debugging
```bash
# View logs
./logs.sh

# Enter Odoo container
docker exec -it dtx_odoo16 bash

# Enter PostgreSQL
docker exec -it dtx_postgres psql -U odoo -d dtx_dev
```

### Support
- Contact DTX development team
- Review code in other modules
- Check Odoo community forums

---

## ✅ Pre-Deployment Checklist

Before deploying code:

- [ ] Code follows [quality standards](code-quality-checklist.md)
- [ ] All fields documented
- [ ] Methods have docstrings
- [ ] No security vulnerabilities
- [ ] Tested manually (all scenarios)
- [ ] Module upgrades cleanly
- [ ] No console errors
- [ ] Mobile-friendly UI
- [ ] Performance acceptable

---

**Last Updated:** 2025-12-23
**Maintained By:** DTX Development Team
