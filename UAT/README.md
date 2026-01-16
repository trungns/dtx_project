# UAT Documentation - DTX Odoo 16

## 📋 Overview

This directory contains User Acceptance Testing (UAT) documentation for DTX Odoo 16 implementation, including manual test cases, test data, and validation guides.

## 📁 Files

### Main UAT Guides

1. **[MANUAL_UAT_TEST_CASES.md](MANUAL_UAT_TEST_CASES.md)** ⭐
   - Comprehensive end-to-end test scenarios
   - Covers full business workflow from quotation to support
   - Includes Help Desk/Support module requirements
   - **Most important file** - contains real-world test cases

2. **[MANUAL_UAT_GUIDE.md](MANUAL_UAT_GUIDE.md)**
   - Step-by-step UAT execution guide
   - Test environment setup
   - User role assignments
   - Sign-off procedures

3. **[TESTING_COMPLETE_SUMMARY.md](TESTING_COMPLETE_SUMMARY.md)**
   - Summary of testing implementation
   - Test coverage report
   - Known issues and resolutions

### Module-Specific UAT

4. **[UAT_AR_AGING.md](UAT_AR_AGING.md)**
   - Accounts Receivable aging report testing
   - Payment tracking validation
   - AR bucket calculations

5. **[UAT_CONTRACT_COST_TRACKING.md](UAT_CONTRACT_COST_TRACKING.md)**
   - Contract cost import validation
   - Profit/loss calculations
   - Cost variance analysis

6. **[UAT_EXCEL_PAKD_FORMULAS.md](UAT_EXCEL_PAKD_FORMULAS.md)**
   - PAKD formula validation against Excel
   - Profit margin calculations
   - VAT handling

### Test Data

7. **[TEST_DATA_SUMMARY.md](TEST_DATA_SUMMARY.md)**
   - Master data setup guide
   - Sample products, customers, suppliers
   - Test scenarios data

---

## 🔥 Quick Start

### For New QA/UAT Testers

1. **Read First**: [MANUAL_UAT_TEST_CASES.md](MANUAL_UAT_TEST_CASES.md)
   - Contains complete workflow test scenarios
   - Real business cases (Kiosk project, SeQMS, etc.)

2. **Setup Environment**: Follow [MANUAL_UAT_GUIDE.md](MANUAL_UAT_GUIDE.md)
   - Create test users
   - Load master data
   - Configure security groups

3. **Load Test Data**: Use [TEST_DATA_SUMMARY.md](TEST_DATA_SUMMARY.md)
   - Products, customers, suppliers
   - Price lists, payment terms

4. **Execute Tests**: Run through test cases sequentially
   - Mark pass/fail for each test case
   - Document any deviations

---

## 📊 Business Workflow Covered

The UAT test cases cover complete DTX business workflow:

| Step | Process | Modules |
|------|---------|---------|
| 1 | Master Data Setup | Product, Contact, Inventory |
| 2 | PAKD & Quotation | dtx_sales_pakd_contract |
| 3 | Procurement & Resupply | Purchase, Inventory |
| 4 | Production (Subcontracting) | Inventory |
| 5 | Deployment & Acceptance | Project (optional) |
| 6 | Invoicing | Accounting |
| 7 | Collection & AR | Accounting, AR |
| 8 | **Maintenance & Support** | **Helpdesk (to be implemented)** |

---

## 🎯 Help Desk Module - Requirements

Based on [MANUAL_UAT_TEST_CASES.md](MANUAL_UAT_TEST_CASES.md#7-bảo-trì--support), the Help Desk module should support:

### Features Required

1. **Support Team Configuration**
   - Create support teams (e.g., "Kiosk Support Team")
   - Team email alias (e.g., kiosk-support@dtx.com)
   - Assign team members

2. **SLA Management**
   - Response time SLA (e.g., 4 hours)
   - Resolution time SLA (e.g., 24 hours)
   - Auto-calculate deadlines
   - SLA violation alerts

3. **Ticket Management**
   - Create tickets from customer emails
   - Link tickets to Sale Orders
   - Priority levels (Low, Medium, High, Urgent)
   - Ticket stages (New, In Progress, Solved, Closed)

4. **Warranty Tracking**
   - Link warranty costs to tickets
   - Track replacement parts
   - Update contract profit/loss with warranty costs

5. **Customer Portal**
   - Customers can submit tickets
   - View ticket status
   - Attach files/screenshots

### Integration Points

- **Sale Orders**: Link tickets to specific SO/contracts
- **Contract Costs**: Track warranty expenses
- **Inventory**: Track replacement parts
- **Email**: Auto-create tickets from support email

### Test Scenarios

See [MANUAL_UAT_TEST_CASES.md - Section 7](MANUAL_UAT_TEST_CASES.md#7-bảo-trì--support):
- Test Case 21: Activate Maintenance
- Test Case 22: Customer Support Request

---

## 📝 Notes for Developers

### UAT vs Production

- UAT files here are based on **test scenarios**
- Do NOT confuse with production documentation in `/PRODUCTION_DOCS/`
- UAT focuses on **testing & validation**
- Production docs focus on **user training & operations**

### Version Tracking

- Current module version: **v1.8.0** (dtx_sales_pakd_contract)
- Last UAT update: 2026-01-04 (restored from git history)
- **TODO**: Update test cases for v1.8.0 (revenue calculation fix)

### Adding New Test Cases

1. Follow existing format in MANUAL_UAT_TEST_CASES.md
2. Include:
   - Test case number
   - Scenario description
   - Step-by-step actions
   - Expected results with ✅/❌ checkboxes
3. Link to relevant production documentation

---

## 🚀 Next Steps

1. **Review Help Desk Requirements**: See section above
2. **Plan Help Desk Implementation**:
   - Evaluate Odoo standard Helpdesk module
   - Customize for DTX workflow
   - Integrate with Sale Orders & Contract Costs
3. **Update Test Cases for v1.8.0**:
   - Add subscription lifecycle tests
   - Update revenue calculation validation
   - Test paid invoice tracking

---

## 📞 Support

For questions about UAT:
- Contact: QA Team / Project Manager
- See also: `/PRODUCTION_DOCS/` for production user guides

---

**Last Updated**: 2026-01-15
**Maintained By**: DTX Development Team
