# Architecture Documentation

Technical architecture and design documentation for DTX Odoo project.

## 🏗️ Available Documentation

### [System Overview](system-overview.md) *(Coming Soon)*
**Audience:** Technical architects, senior developers
**Content:**
- High-level system architecture
- Data flow diagrams
- Integration points
- Technology stack decisions
- Scalability considerations

---

### [Module: dtx_serial_ext](module-dtx-serial-ext.md)
**Audience:** Developers, technical leads
**Content:**
- Module specification
- Data models and relationships
- Automatic behaviors
- Code metrics
- Technical decisions

**Read this to:** Understand the technical implementation of the serial extension module.

---

## 🎯 Architecture Overview

### System Layers

```
┌─────────────────────────────────────────────┐
│           User Interface Layer              │
│  (Odoo Web UI, Mobile App, XML Views)       │
└─────────────────────────────────────────────┘
                    ↕
┌─────────────────────────────────────────────┐
│         Business Logic Layer                │
│  (Python Models, Computed Fields, Methods)  │
└─────────────────────────────────────────────┘
                    ↕
┌─────────────────────────────────────────────┐
│            Data Layer                       │
│  (PostgreSQL Database, ORM)                 │
└─────────────────────────────────────────────┘
```

### Module Architecture

```
┌──────────────────────┐
│  dtx_serial_ext      │ ✅ Complete
│  (Serial Tracking)   │
└──────────────────────┘
          ↓
┌──────────────────────┐
│ dtx_vendorbill_alert │ 🚧 Planned
│ (Warning System)     │
└──────────────────────┘
          ↓
┌──────────────────────┐
│  dtx_ops_project     │ 🚧 Planned
│ (Project Management) │
└──────────────────────┘
```

Each module builds on the previous one, maintaining clean separation of concerns.

---

## 📊 Data Architecture

### Core Entities

```
┌─────────────────┐         ┌─────────────────┐
│   stock.lot     │────────▶│  res.partner    │
│   (Extended)    │         │  (Customer)     │
└─────────────────┘         └─────────────────┘
         │
         │ (Future)
         ↓
┌─────────────────┐
│ dtx.ops.project │  🚧 Coming Soon
│  (New Model)    │
└─────────────────┘
```

### Extended Models

| Odoo Model | Extension | Fields Added | New Tables |
|------------|-----------|--------------|------------|
| `stock.lot` | dtx_serial_ext | 11 | 0 |
| `stock.move.line` | dtx_serial_ext | 0 (logic only) | 0 |

**Design Principle:** Extend existing models rather than creating new tables when possible.

---

## 🔄 Data Flow

### Serial Creation Flow

```
Purchase Order Created
    ↓
Receipt Validated
    ↓
Serial Number Entered ──────┐
    ↓                       │
stock.lot Created           │
    ↓                       │
Fields Populated:           │
- name (supplier serial)    │
- product_id                │
- lifecycle_state = 'stock' │
- vendor_invoice_state = 'missing' ◄──┘
```

### Lifecycle Update Flow

```
Stock Move Validated
    ↓
_action_done() Triggered
    ↓
Check Source/Destination Locations
    ↓
Determine New State:
- From supplier → 'stock'
- To customer → 'delivered'
- To maintenance → 'maintenance'
- To scrap → 'scrapped'
    ↓
Update serial.lifecycle_state
    ↓
Log to Chatter
```

---

## 🎨 Design Principles

### 1. Simple First
- Manual fields over complex automation
- Warning over blocking
- Computed fields only when necessary

### 2. Extend, Don't Replace
- Inherit existing Odoo models
- Use standard workflows where possible
- Minimal custom tables

### 3. Mobile-First UI
- Responsive layouts
- Touch-friendly controls
- No horizontal scrolling

### 4. Data Integrity
- Required fields enforced
- State transitions logged
- Audit trail via chatter

### 5. Performance
- Indexed search fields
- Efficient ORM queries
- Minimal computed fields

See [Code Quality Checklist](../developer-guide/code-quality-checklist.md) for implementation details.

---

## 🔌 Integration Points

### With Standard Odoo

| Odoo Module | Integration Point | Purpose |
|-------------|-------------------|---------|
| `stock` | Extends `stock.lot`, `stock.move.line` | Serial tracking |
| `purchase` | Auto-link vendor bills | Invoice tracking |
| `product` | Product categories, AVCO costing | Cost management |

### With Future DTX Modules

| Module | Integration | Data Shared |
|--------|-------------|-------------|
| `dtx_vendorbill_alert` | Read `vendor_invoice_state` | Invoice status |
| `dtx_ops_project` | Many2one relationship | Serial ↔ Project link |

---

## 🔐 Security Architecture

### Access Control

```
┌─────────────────────────────────────────┐
│  Odoo Security Groups                   │
├─────────────────────────────────────────┤
│  stock.group_stock_user                 │
│  - Read/Write serial records            │
│  - Cannot delete                        │
├─────────────────────────────────────────┤
│  stock.group_stock_manager              │
│  - Full CRUD on serial records          │
│  - Can upgrade modules                  │
└─────────────────────────────────────────┘
```

**Design:** Uses standard Odoo security groups, no custom groups needed.

### Data Privacy

- No sensitive data stored (no credit cards, passwords, etc.)
- Serial numbers considered business-sensitive (normal Odoo access control)
- Vendor invoice info visible to authorized users only

---

## 📈 Scalability

### Current Capacity

| Metric | Estimate | Basis |
|--------|----------|-------|
| Serials | 100,000+ | PostgreSQL proven scale |
| Users | 50+ concurrent | Standard Odoo capacity |
| Response time | <1s | Simple queries, indexed fields |

### Growth Plan

**Phase 1 (Current):** Single-server deployment
**Phase 2 (If needed):** Database replication for reporting
**Phase 3 (If needed):** Horizontal scaling with load balancer

---

## 🧩 Module Dependencies

### dtx_serial_ext

```
dtx_serial_ext
├── stock (required)
└── product (required)
```

**No external Python dependencies**

### Future Modules

```
dtx_vendorbill_alert
├── dtx_serial_ext (required)
└── stock (required)

dtx_ops_project
├── dtx_serial_ext (required)
├── stock (required)
└── account (optional - for AR aging)
```

---

## 🎯 Technical Decisions

### Why Extend stock.lot Instead of New Model?

✅ **Benefits:**
- Seamless integration with Odoo inventory
- Reuse existing serial tracking infrastructure
- No data duplication
- Familiar UI for users

❌ **Alternatives Considered:**
- New `dtx.device` model → Rejected: Too complex, duplicates stock.lot
- External system → Rejected: Integration overhead

### Why Docker for Development?

✅ **Benefits:**
- Clean, isolated environment
- Easy setup on any OS (especially M1 Mac)
- Matches production environment
- Quick reset capability

❌ **Alternatives Considered:**
- Native install → Rejected: Complex setup, OS-specific issues
- VM → Rejected: Heavy resource usage

### Why AVCO Costing?

✅ **Benefits:**
- Accurate average cost calculation
- Matches real-world procurement patterns
- Simple to understand
- Odoo native support

❌ **Alternatives Considered:**
- FIFO → Rejected: Doesn't match business reality
- Manual costing → Rejected: Error-prone, time-consuming

---

## 📋 Architecture Checklist

### For New Modules

When designing new DTX modules:

- [ ] Extend existing models when possible
- [ ] Follow naming convention: `dtx_<module_name>`
- [ ] Minimize database tables
- [ ] Use standard Odoo patterns
- [ ] Document all customizations
- [ ] Plan for mobile use
- [ ] Consider performance impact
- [ ] Plan migration path
- [ ] Security by design
- [ ] Test with realistic data volume

---

## 📖 Further Reading

### Internal Documentation
- [Module Specification: dtx_serial_ext](module-dtx-serial-ext.md)
- [API Reference](../developer-guide/api-reference.md)
- [Code Quality Standards](../developer-guide/code-quality-checklist.md)

### External Resources
- [Odoo Architecture](https://www.odoo.com/documentation/16.0/developer/reference/backend/orm.html)
- [PostgreSQL Best Practices](https://wiki.postgresql.org/wiki/Don%27t_Do_This)
- [Python Design Patterns](https://refactoring.guru/design-patterns/python)

---

## 🔍 Diagrams

### System Context Diagram *(Coming Soon)*
Shows DTX system in broader context with external systems.

### Data Model Diagram *(Coming Soon)*
Entity-relationship diagram for all DTX models.

### Deployment Diagram *(Coming Soon)*
Physical deployment architecture.

---

## 📊 Metrics

### Current Architecture Stats

| Metric | Value |
|--------|-------|
| Total modules | 1 (3 planned) |
| Database tables | 0 new (extend existing) |
| Lines of Python | ~280 |
| Lines of XML | ~180 |
| External dependencies | 0 |
| Custom security groups | 0 |

**Design Philosophy:** Minimal, focused, maintainable.

---

**Last Updated:** 2025-12-23
**Next Review:** After module 2 completion
