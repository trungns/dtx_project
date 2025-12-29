# 📊 DTX TEST DATA SUMMARY

**Last Updated:** 2025-12-29
**Status:** ✅ Ready for testing

---

## 🏢 VENDORS (6 companies)

| # | Vendor Name | Specialization | Location | Contact |
|---|-------------|----------------|----------|---------|
| 1 | **LGMEC** | Đối tác gia công lắp ráp Kiosk | KCN Tân Bình, TP.HCM | 0909123456, lgmec@example.com |
| 2 | **Công ty TNHH Touch Display Việt Nam** | Nhà cung cấp màn hình cảm ứng | Quận 7, TP.HCM | 0281234567, touchvn@example.com |
| 3 | **Công ty CP Thiết bị In Hà Nội** | Nhà cung cấp máy in nhiệt | Cầu Giấy, Hà Nội | 0241234567, printhn@example.com |
| 4 | **Công ty TNHH PC Components VN** | Nhà cung cấp Mini PC | Quận 1, TP.HCM | 0283456789, pcvn@example.com |
| 5 | **Công ty TNHH Camera & Security** | Nhà cung cấp Camera IP | Quận Tân Bình, TP.HCM | 0909876543, camsec@example.com |
| 6 | **Công ty TNHH NFC Technology** | Nhà cung cấp đầu đọc CCCD | Hoàn Kiếm, Hà Nội | 0243456789, nfctech@example.com |

---

## 📦 PRODUCT CATEGORIES (4 categories)

| Category | Costing Method | Valuation | Purpose |
|----------|----------------|-----------|---------|
| Linh kiện DTX | AVCO (Average Cost) | Real Time | Linh kiện có serial hoặc không serial |
| Thành phẩm DTX | AVCO (Average Cost) | Real Time | Kiosk hoàn chỉnh |
| Dịch vụ gia công | Standard Cost | Manual Periodic | Dịch vụ lắp ráp, gia công |
| License phần mềm | Standard Cost | Manual Periodic | Phần mềm, license |

---

## 🔧 COMPONENTS (5 products)

### With Serial Tracking

| # | Product Name | Category | DTX Type | Tracking | Purchase Price | Sales Price | Vendor |
|---|--------------|----------|----------|----------|----------------|-------------|---------|
| 1 | Touch Screen 15.6" | Linh kiện DTX | Thiết bị quản lý theo Serial | By Unique Serial Number | 2,500,000 VND | 3,000,000 VND | Touch Display VN |
| 2 | Thermal Printer 80mm | Linh kiện DTX | Thiết bị quản lý theo Serial | By Unique Serial Number | 1,800,000 VND | 2,000,000 VND | Thiết bị In HN |
| 3 | Mini PC Intel i5 | Linh kiện DTX | Thiết bị quản lý theo Serial | By Unique Serial Number | 4,500,000 VND | 6,000,000 VND | PC Components VN |
| 4 | Camera IP 2MP | Linh kiện DTX | Thiết bị quản lý theo Serial | By Unique Serial Number | 1,200,000 VND | 1,500,000 VND | Camera & Security |
| 5 | CCCD Reader NFC | Linh kiện DTX | Thiết bị quản lý theo Serial | By Unique Serial Number | 800,000 VND | 1,000,000 VND | NFC Technology |

**Total Component Cost (for 3 Kiosks):**
- Touch Screen: 3 × 2,500,000 = 7,500,000 VND
- Thermal Printer: 3 × 1,800,000 = 5,400,000 VND
- Mini PC: 3 × 4,500,000 = 13,500,000 VND
- Camera: 3 × 1,200,000 = 3,600,000 VND
- CCCD Reader: 3 × 800,000 = 2,400,000 VND
- **TOTAL: 32,400,000 VND**

---

## 🏭 FINISHED PRODUCTS (1 product)

| # | Product Name | Category | DTX Type | Tracking | Can Purchase | Can Sell | Sales Price | Subcontractor |
|---|--------------|----------|----------|----------|--------------|----------|-------------|---------------|
| 1 | Kiosk lấy số DTX-A17 | Thành phẩm DTX | Kiosk / Thiết bị hoàn chỉnh | By Unique Serial Number | ✓ (for subcontracting) | ✓ | 30,000,000 VND | LGMEC |

**BOM Components (5 items per Kiosk):**
1. Touch Screen 15.6" × 1
2. Thermal Printer 80mm × 1
3. Mini PC Intel i5 × 1
4. Camera IP 2MP × 1
5. CCCD Reader NFC × 1

**Subcontracting Fee:** 2,000,000 VND per Kiosk (LGMEC)

**Total Cost per Kiosk:**
- Components: 10,800,000 VND
- Subcontracting: 2,000,000 VND
- **TOTAL: 12,800,000 VND**

**Margin per Kiosk:**
- Sales Price: 30,000,000 VND
- Cost: 12,800,000 VND
- **Profit: 17,200,000 VND (57.3%)**

---

## 🛠️ SERVICES (1 product)

| # | Product Name | Category | DTX Type | Product Type | Purchase Price | Can Purchase | Can Sell |
|---|--------------|----------|----------|--------------|----------------|--------------|----------|
| 1 | Dịch vụ gia công lắp ráp Kiosk | Dịch vụ gia công | Dịch vụ (không quản lý kho) | Service | 5,000,000 VND | ✓ | ❌ |

**Note:** Service này dùng để tính phí gia công khi tạo PO cho LGMEC

---

## 🔢 SERIAL NUMBER FORMAT

### Components

| Product | Prefix | Format | Example |
|---------|--------|--------|---------|
| Touch Screen | TS-DTX- | TS-DTX-XXX | TS-DTX-001, TS-DTX-002, TS-DTX-003 |
| Thermal Printer | PRINTER-DTX- | PRINTER-DTX-XXX | PRINTER-DTX-001, 002, 003 |
| Mini PC | PC-DTX- | PC-DTX-XXX | PC-DTX-001, 002, 003 |
| Camera | CAM-DTX- | CAM-DTX-XXX | CAM-DTX-001, 002, 003 |
| CCCD Reader | CCCD-DTX- | CCCD-DTX-XXX | CCCD-DTX-001, 002, 003 |

### Finished Products

| Product | Prefix | Format | Example |
|---------|--------|--------|---------|
| Kiosk DTX-A17 | KIOSK-A17- | KIOSK-A17-XXX | KIOSK-A17-001, 002, 003 |

**Total Serial Numbers for 3 Kiosks:**
- 15 component serials (5 types × 3 units)
- 3 Kiosk serials
- **TOTAL: 18 serial numbers**

---

## 💰 PRICING SUMMARY

### Purchase Cost (for 3 Kiosks)

| Vendor | Product | Qty | Unit Price | Total |
|--------|---------|-----|------------|-------|
| Touch Display VN | Touch Screen 15.6" | 3 | 2,500,000 | 7,500,000 |
| Thiết bị In HN | Thermal Printer 80mm | 3 | 1,800,000 | 5,400,000 |
| PC Components VN | Mini PC Intel i5 | 3 | 4,500,000 | 13,500,000 |
| Camera & Security | Camera IP 2MP | 3 | 1,200,000 | 3,600,000 |
| NFC Technology | CCCD Reader NFC | 3 | 800,000 | 2,400,000 |
| LGMEC | Subcontracting Fee | 3 | 2,000,000 | 6,000,000 |
| **TOTAL** | | | | **38,400,000** |

### Sales Revenue (for 3 Kiosks)

| Customer | Product | Qty | Unit Price | Total |
|----------|---------|-----|------------|-------|
| Công ty ABC | Kiosk lấy số DTX-A17 | 3 | 50,000,000 | 150,000,000 |

### Profit Analysis

| Item | Amount |
|------|--------|
| **Sales Revenue** | 150,000,000 VND |
| **Total Cost** | 38,400,000 VND |
| Components | 32,400,000 VND |
| Subcontracting | 6,000,000 VND |
| **Gross Profit** | **111,600,000 VND** |
| **Margin** | **74.4%** |

---

## 📋 TEST WORKFLOW OVERVIEW

### Scenario: Produce 3 Kiosks via Subcontracting

```
┌─────────────────────────────────────────────────────────┐
│  PHASE 1: MUA LINH KIỆN (5 POs)                         │
│  ─────────────────────────────────────────────────────  │
│  ✓ PO Touch Display VN: 3 Touch Screen                 │
│  ✓ PO Thiết bị In HN: 3 Thermal Printer                │
│  ✓ PO PC Components VN: 3 Mini PC                      │
│  ✓ PO Camera & Security: 3 Camera                      │
│  ✓ PO NFC Technology: 3 CCCD Reader                    │
│  ✓ Nhận 15 linh kiện vào kho (with 15 serials)         │
│  ✓ Tạo 5 Vendor Bills (32,400,000 VND)                 │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  PHASE 2: GIA CÔNG (1 PO)                               │
│  ─────────────────────────────────────────────────────  │
│  ✓ PO LGMEC: 3 Kiosk DTX-A17                            │
│  ✓ Resupply: Gửi 15 linh kiện cho LGMEC                │
│  ✓ Receipt: Nhận 3 Kiosk hoàn chỉnh (with 3 serials)   │
│  ✓ Tạo Vendor Bill (6,000,000 VND)                      │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  PHASE 3: BÁN HÀNG (1 SO)                               │
│  ─────────────────────────────────────────────────────  │
│  ✓ SO Công ty ABC: 3 Kiosk                              │
│  ✓ Delivery: Giao 3 Kiosk                               │
│  ✓ Customer Invoice (150,000,000 VND)                   │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  RESULT: PROFIT 111,600,000 VND (74.4% margin)          │
└─────────────────────────────────────────────────────────┘
```

---

## 📝 SETUP INSTRUCTIONS

### Quick Setup

```bash
cd /Users/trungns/dtx_project/odoo-dev
docker-compose exec odoo python3 /mnt/scripts/setup_dtx_data.py
```

**This will create:**
- ✓ 6 Vendors
- ✓ 4 Product Categories
- ✓ 5 Components
- ✓ 1 Kiosk product
- ✓ 1 Service

**Then:**
1. Login to Odoo: http://localhost:8069
2. Create BOM Template for Kiosk DTX-A17
3. Add 5 components to BOM
4. Set Subcontractor = LGMEC
5. Generate BOM
6. Follow test flow: [KIOSK_PRODUCTION_TEST_FLOW.md](./KIOSK_PRODUCTION_TEST_FLOW.md)

---

## ✅ DATA VERIFICATION

After running setup script, verify:

### Vendors
- [ ] 6 vendors created
- [ ] All have `is_company = True`
- [ ] LGMEC has address in TP.HCM

### Products
- [ ] 5 components with serial tracking
- [ ] 1 Kiosk with serial tracking
- [ ] 1 Service (no tracking)
- [ ] All components: `Can Purchase = True`
- [ ] Kiosk: `Can Purchase = True, Can Sell = True`

### Categories
- [ ] All categories use AVCO costing (except services)
- [ ] Linh kiện DTX category exists
- [ ] Thành phẩm DTX category exists

---

## 🎯 TESTING GOALS

1. **Subcontracting Flow:**
   - ✓ Create PO with subcontractor
   - ✓ Resupply components automatically
   - ✓ Receive finished products
   - ✓ Track component → finished product

2. **Serial Tracking:**
   - ✓ 18 serial numbers created
   - ✓ Traceability from component to Kiosk
   - ✓ Traceability from Kiosk to customer

3. **Multi-Vendor Purchase:**
   - ✓ 5 different vendors for 5 component types
   - ✓ 5 separate POs
   - ✓ 5 separate Vendor Bills
   - ✓ Real-world scenario

4. **Financial Tracking:**
   - ✓ Purchase cost: 38,400,000 VND
   - ✓ Sales revenue: 150,000,000 VND
   - ✓ Gross profit: 111,600,000 VND
   - ✓ Margin: 74.4%

---

**Document Version:** 1.0.0
**Created:** 2025-12-29
**Purpose:** Reference data for KIOSK_PRODUCTION_TEST_FLOW.md

✅ **Ready for testing!**
