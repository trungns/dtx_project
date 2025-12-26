# DTX Project Structure

Professional Odoo development project structure.

## 📂 Directory Structure

```
dtx_project/
│
├── README.md                          ← Project overview & main entry
├── PROJECT_STRUCTURE.md               ← This file
│
├── docs/                              ← 📚 ALL DOCUMENTATION HERE
│   ├── README.md                      ← Documentation index
│   ├── START_HERE.md                  ← Main getting started guide
│   ├── DOCUMENTATION_INDEX.md         ← Complete documentation index
│   │
│   ├── user-guide/                    ← 📘 End-user documentation
│   │   ├── README.md
│   │   ├── quick-start.md
│   │   └── dtx-serial-extension.md
│   │
│   ├── developer-guide/               ← 👨‍💻 Developer documentation
│   │   ├── README.md
│   │   ├── development-environment.md
│   │   ├── api-reference.md
│   │   ├── code-quality-checklist.md
│   │   └── DEV_ENVIRONMENT_READY.md
│   │
│   ├── deployment/                    ← 🚀 Deployment documentation
│   │   ├── README.md
│   │   ├── installation-guide.md
│   │   └── production-deployment.md
│   │
│   └── architecture/                  ← 🏗️ Architecture documentation
│       ├── README.md
│       ├── system-overview.md
│       └── module-dtx-serial-ext.md
│
├── odoo-dev/                          ← 🐳 Development environment (Docker)
│   ├── README.md -> ../docs/developer-guide/development-environment.md
│   ├── QUICKSTART.md -> ../docs/user-guide/quick-start.md
│   │
│   ├── docker-compose.yml             ← Docker configuration
│   ├── .gitignore
│   │
│   ├── config/                        ← Odoo configuration
│   │   └── odoo.conf
│   │
│   ├── scripts/ (as shell files)      ← Utility scripts
│   │   ├── start.sh                   ← Start Odoo
│   │   ├── stop.sh                    (TBD)
│   │   ├── upgrade-module.sh          ← Upgrade module after code changes
│   │   ├── logs.sh                    ← View logs
│   │   └── reset.sh                   ← Reset database
│   │
│   └── addons/                        ← 📦 Custom Odoo modules
│       ├── dtx_serial_ext/            ← Module 1: Serial tracking
│       ├── dtx_vendorbill_alert/      (🚧 Coming soon)
│       └── dtx_ops_project/           (🚧 Coming soon)
│
└── dtx_serial_ext/                    ← 📦 Module source (production-ready backup)
    ├── README.md                      ← Module README (links to docs/)
    ├── __init__.py
    ├── __manifest__.py
    ├── models/
    │   ├── __init__.py
    │   ├── stock_lot.py
    │   └── stock_move_line.py
    ├── views/
    │   └── stock_lot_views.xml
    ├── security/
    │   └── ir.model.access.csv
    └── static/description/
        └── index.html
```

## 🎯 Key Principles

### 1. **Documentation Centralized in `docs/`**
- ✅ All documentation in one place
- ✅ Organized by category (user, developer, deployment, architecture)
- ✅ Each category has README index
- ✅ Main entry: `docs/START_HERE.md`

### 2. **Separation of Concerns**
- `docs/` - Documentation only
- `odoo-dev/` - Development environment
- `dtx_serial_ext/` - Production module source

### 3. **Professional Odoo Project Layout**
Follows industry best practices:
- Dedicated `addons/` folder for custom modules
- Docker-based dev environment
- Centralized documentation
- Utility scripts for common tasks

### 4. **Easy Navigation**
- Symlinks in `odoo-dev/` point to relevant docs
- Each folder has README explaining its purpose
- Cross-references use relative paths

## 📚 Documentation Categories

### 📘 User Guides
**Location:** `docs/user-guide/`
**For:** End users, inventory managers
**Contains:** How to use the system, feature guides

### 👨‍💻 Developer Guides
**Location:** `docs/developer-guide/`
**For:** Developers, technical staff
**Contains:** Setup, API reference, coding standards

### 🚀 Deployment Guides
**Location:** `docs/deployment/`
**For:** System administrators, DevOps
**Contains:** Installation, configuration, production deployment

### 🏗️ Architecture Docs
**Location:** `docs/architecture/`
**For:** Technical architects, senior developers
**Contains:** System design, data models, technical decisions

## 🔗 Quick Access

### From Project Root

```bash
# Read main README
cat README.md

# Get started
cat docs/START_HERE.md

# For developers
cat docs/developer-guide/development-environment.md

# For users
cat docs/user-guide/quick-start.md
```

### From odoo-dev/

```bash
cd odoo-dev

# Quick start (symlink)
cat QUICKSTART.md

# Full dev guide (symlink)
cat README.md

# Start Odoo
./start.sh
```

## 🎓 Finding What You Need

### New to Project?
1. Read [`README.md`](README.md) - Project overview
2. Read [`docs/START_HERE.md`](docs/START_HERE.md) - Getting started

### Want to Develop?
1. Read [`docs/developer-guide/development-environment.md`](docs/developer-guide/development-environment.md)
2. Setup: `cd odoo-dev && ./start.sh`
3. Reference: [`docs/developer-guide/api-reference.md`](docs/developer-guide/api-reference.md)

### Want to Deploy?
1. Read [`docs/deployment/installation-guide.md`](docs/deployment/installation-guide.md)
2. Follow step-by-step installation
3. Run test scenarios

### Want Architecture Info?
1. Read [`docs/architecture/README.md`](docs/architecture/README.md)
2. Review module specs in `docs/architecture/`

## 📊 File Counts

| Category | Files | Status |
|----------|-------|--------|
| Documentation | 17 MD files | ✅ Organized |
| Modules | 1 (3 planned) | ✅ Ready |
| Scripts | 4 shell scripts | ✅ Functional |
| Config files | 3 | ✅ Ready |

## 🔧 Maintenance

### Adding New Module

```bash
# 1. Create in addons/
mkdir -p odoo-dev/addons/new_module

# 2. Develop and test
cd odoo-dev && ./start.sh

# 3. Document
# Add to docs/user-guide/
# Add to docs/developer-guide/api-reference.md
# Add to docs/architecture/

# 4. Copy to project root when stable
cp -r odoo-dev/addons/new_module ./
```

### Adding Documentation

```bash
# Choose category
cd docs/user-guide/        # or developer-guide, deployment, architecture

# Create markdown file
vim new-guide.md

# Update category README
vim README.md

# Update main docs/README.md
```

## ✅ Structure Validation

Run this to validate structure:

```bash
cd dtx_project

# Check documentation exists
[ -d docs/user-guide ] && echo "✅ User guides exist"
[ -d docs/developer-guide ] && echo "✅ Developer guides exist"
[ -d docs/deployment ] && echo "✅ Deployment guides exist"
[ -d docs/architecture ] && echo "✅ Architecture docs exist"

# Check dev environment
[ -f odoo-dev/docker-compose.yml ] && echo "✅ Docker config exists"
[ -x odoo-dev/start.sh ] && echo "✅ Start script executable"

# Check modules
[ -d odoo-dev/addons/dtx_serial_ext ] && echo "✅ Module in dev environment"
[ -d dtx_serial_ext ] && echo "✅ Module source exists"
```

---

**This structure follows:**
- ✅ Industry best practices for Odoo development
- ✅ Clear separation of concerns
- ✅ Professional documentation organization
- ✅ Easy navigation and maintenance
- ✅ Scalable for future modules

**Last Updated:** 2025-12-23
