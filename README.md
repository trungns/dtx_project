# DTX Odoo Project

Enterprise Resource Planning system for DTX Smart Queue Management Systems

## Overview

This project implements a custom Odoo 16 Community Edition solution designed specifically for DTX's business operations, including:

- Hardware device tracking with dual serial numbers
- Vendor invoice management
- Device lifecycle tracking
- Project/contract management (coming soon)
- Profitability analysis (coming soon)

## Project Status

| Module | Status | Description |
|--------|--------|-------------|
| `dtx_serial_ext` | ✅ Complete | Serial/lot tracking with lifecycle management |
| `dtx_vendorbill_alert` | 🚧 Planned | Warning system for deliveries without vendor invoices |
| `dtx_ops_project` | 🚧 Planned | Lightweight project/contract management |

**Target Go-Live:** 01/01/2026

## Quick Start

### For End Users
👉 **[Start Here](docs/START_HERE.md)** - Begin your journey

👉 **[Quick Start Guide](docs/user-guide/quick-start.md)** - 5-minute setup

### For Developers
👉 **[Development Environment](docs/developer-guide/development-environment.md)** - Setup dev environment

👉 **[API Reference](docs/developer-guide/api-reference.md)** - Developer reference

## Project Structure

```
dtx_project/
├── README.md                      # This file
│
├── odoo-dev/                      # Development environment (Docker-based)
│   ├── docker-compose.yml
│   ├── config/
│   ├── addons/                    # Custom modules
│   │   ├── dtx_serial_ext/
│   │   ├── dtx_vendorbill_alert/  (coming soon)
│   │   └── dtx_ops_project/       (coming soon)
│   └── scripts/
│       ├── start.sh
│       ├── upgrade-module.sh
│       ├── logs.sh
│       └── reset.sh
│
├── dtx_serial_ext/                # Module source (production-ready)
│   ├── __manifest__.py
│   ├── models/
│   ├── views/
│   ├── security/
│   └── static/
│
└── docs/                          # Documentation
    ├── START_HERE.md              # Main entry point
    ├── user-guide/                # End-user documentation
    ├── developer-guide/           # Developer documentation
    ├── deployment/                # Deployment guides
    └── architecture/              # Technical architecture
```

## Documentation

### 📘 User Guides
- [Start Here](docs/START_HERE.md) - Main entry point
- [Quick Start (5 min)](docs/user-guide/quick-start.md) - Fast setup guide
- [DTX Serial Extension](docs/user-guide/dtx-serial-extension.md) - User manual

### 👨‍💻 Developer Guides
- [Development Environment Setup](docs/developer-guide/development-environment.md) - Complete dev setup
- [API Reference](docs/developer-guide/api-reference.md) - Fields, methods, examples
- [Code Quality Checklist](docs/developer-guide/code-quality-checklist.md) - Standards

### 🚀 Deployment
- [Installation Guide](docs/deployment/installation-guide.md) - Step-by-step installation
- [Production Deployment](docs/deployment/production-deployment.md) - Deploy to production

### 🏗️ Architecture
- [System Architecture](docs/architecture/system-overview.md) - High-level design
- [Module: dtx_serial_ext](docs/architecture/module-dtx-serial-ext.md) - Module technical spec

## Key Features

### dtx_serial_ext (Serial Extension Module)

**Dual Serial Tracking:**
- Supplier serial (primary key for warranty)
- DTX internal serial (customer-facing)
- Both searchable and displayed together

**Lifecycle Management:**
- 6 states: Stock → Allocated → Delivered → Installed → Maintenance → Scrapped
- Automatic state updates based on stock moves
- Manual override capability

**Vendor Invoice Tracking:**
- Track invoice state per serial: Missing → Linked → Replaced
- Auto-update when invoice reference entered
- Solves real-world issue of receiving goods before invoices

**Warranty Management:**
- Start/end dates
- Active/inactive indicator
- Searchable and filterable

## Development

### Prerequisites
- Docker Desktop (for Mac with Apple Silicon)
- Git
- Text editor / IDE

### Setup Development Environment

```bash
# Navigate to project
cd dtx_project/odoo-dev

# Start Odoo (first time will download images)
./start.sh

# Open browser
open http://localhost:8069

# Create database: dtx_dev
# Install module: DTX Serial Extension
```

### Development Workflow

```bash
# Edit code in odoo-dev/addons/dtx_serial_ext/

# Upgrade module after changes
./upgrade-module.sh dtx_serial_ext

# View logs
./logs.sh

# Restart Odoo
docker-compose restart odoo
```

See [Development Environment Guide](docs/developer-guide/development-environment.md) for details.

## Testing

### Manual Testing
See [Installation Guide - Testing Section](docs/deployment/installation-guide.md#testing-guide) for 10 detailed test scenarios.

### Automated Testing
(Coming soon)

## Deployment

### To Development
Already configured via Docker. See [Quick Start](docs/user-guide/quick-start.md).

### To Production
See [Production Deployment Guide](docs/deployment/production-deployment.md).

## Technology Stack

| Component | Version | Purpose |
|-----------|---------|---------|
| Odoo | 16.0 Community | ERP Platform |
| PostgreSQL | 15 | Database |
| Python | 3.10 | Backend |
| Docker | Latest | Development environment |
| XML | - | Views/UI |

## Business Context

DTX sells and deploys smart queue management systems including:
- Hardware: Kiosks, screens, printers, tablets, LED displays
- Software: License management
- Services: Deployment, installation, maintenance

### Key Business Challenges Solved

1. **Serial Tracking:** Dual serial numbers (supplier + internal) with lifecycle states
2. **Vendor Invoice Lag:** Devices received before invoices arrive
3. **Costing:** Average cost auto-calculation
4. **Project Management:** Lightweight contract tracking (coming soon)
5. **Profitability:** Revenue vs. cost analysis (coming soon)

## Design Principles

✅ **SIMPLE FIRST** - Manual fields over complex automation
✅ **MANAGEMENT > ACCOUNTING** - Visibility over strict accounting
✅ **SERIAL IS KING** - Everything revolves around serial tracking
✅ **WARNING > BLOCKING** - Warn users, don't block workflows
✅ **MOBILE FRIENDLY** - All forms work on Odoo mobile app
✅ **SMALL ADDONS** - Multiple focused modules vs. monolithic

## Contributing

This is an internal DTX project. For questions or suggestions:
- Contact DTX development team
- Submit issues/requests through internal channels

## License

Proprietary - DTX Internal Use Only

Individual modules may use LGPL-3 (Odoo standard) where applicable.

## Support

For support:
1. Check documentation in `docs/` folder
2. Review troubleshooting guides
3. Contact DTX development team

## Roadmap

### Phase 1: Foundation (Current)
- [x] Development environment setup
- [x] Module: dtx_serial_ext
- [ ] Testing and validation

### Phase 2: Vendor Invoice Alert
- [ ] Module: dtx_vendorbill_alert
- [ ] Integration testing

### Phase 3: Project Management
- [ ] Module: dtx_ops_project
- [ ] Profitability tracking
- [ ] Cost management

### Phase 4: Production Deployment
- [ ] Production environment setup
- [ ] Data migration (if needed)
- [ ] User training
- [ ] Go-live: 01/01/2026

## Changelog

### 2025-12-23
- ✅ Initial project structure
- ✅ Development environment (Docker-based)
- ✅ Module: dtx_serial_ext v16.0.1.0.0
- ✅ Complete documentation suite

---

**Built with ❤️ for DTX Smart Queue Management Systems**
