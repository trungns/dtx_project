# Help Desk Module Implementation Plan

## 📋 Overview

Implement Help Desk / Support Ticket system to complete DTX business workflow (Step 8: Maintenance & Support).

**Based on**: [MANUAL_UAT_TEST_CASES.md - Section 7](MANUAL_UAT_TEST_CASES.md#7-bảo-trì--support)

**Current Situation**:
- DTX has complete workflow from Quotation → Invoicing → Collection
- Missing: Post-sales support & warranty tracking
- Currently using manual Chatter notes (inefficient)

**Solution**: Implement Odoo Helpdesk module with DTX customizations

---

## 🎯 Business Requirements

### From UAT Test Cases

**Test Case 21: Activate Maintenance**
- Track maintenance contracts
- Link to Sale Orders
- Set maintenance period & terms
- Support contact information

**Test Case 22: Customer Support Request**
- Customer reports: "Camera at Kiosk #5 not working"
- Need to:
  1. Create support ticket
  2. Assign to technician
  3. Track resolution (replace camera)
  4. Update warranty costs
  5. Close ticket with customer satisfaction

### Key Requirements

1. **Support Team Management**
   - Multiple support teams (e.g., Kiosk Support, SeQMS Support)
   - Team email aliases (auto-create tickets from email)
   - Team members with different permissions

2. **SLA (Service Level Agreement)**
   - Response time: 4 hours (example)
   - Resolution time: 24 hours (example)
   - Auto-calculate deadlines
   - Alert when SLA violated

3. **Ticket Workflow**
   - Stages: New → In Progress → Solved → Closed
   - Priority: Low, Medium, High, Urgent
   - Categories: Technical, Billing, Training, etc.

4. **Integration with Sale Orders**
   - Link ticket to specific SO/contract
   - View all tickets for a contract
   - Smart button on SO: "Support Tickets (X)"

5. **Warranty Cost Tracking**
   - Add warranty costs to Contract Costs
   - Cost type: "warranty" or "additional"
   - Impact profit/loss calculation
   - Example: Replace camera = -595,000 VND profit

6. **Customer Portal**
   - Customers submit tickets online
   - View ticket status
   - Upload attachments (screenshots, logs)
   - Receive email notifications

---

## 🏗️ Technical Design

### Option 1: Use Odoo Standard Helpdesk Module ✅ **RECOMMENDED**

**Pros**:
- Battle-tested, feature-rich
- Includes SLA, teams, portal, email gateway
- Easy to customize
- Good documentation

**Cons**:
- Enterprise license required (or use OCA version)
- May have features we don't need

**Action**: Install `helpdesk` module from Odoo Community (OCA)

### Option 2: Build Custom Support Module

**Pros**:
- Full control
- Only features we need
- No license cost

**Cons**:
- Time-consuming
- Need to build SLA, email gateway, portal
- Maintenance burden

**Decision**: Use **Option 1** (OCA Helpdesk)

---

## 📦 Module Selection

### OCA Helpdesk Module

**Repository**: https://github.com/OCA/helpdesk

**Key Modules**:
1. `helpdesk_mgmt` - Core helpdesk management
2. `helpdesk_mgmt_sla` - SLA management
3. `helpdesk_mgmt_project` - Link to projects
4. `helpdesk_sale` - Link to sale orders ⭐ **CRITICAL**

**Installation**:
```bash
# Add OCA repository
cd /Users/trungns/dtx_project/odoo-dev/addons
git clone https://github.com/OCA/helpdesk.git oca-helpdesk -b 16.0

# Install modules
docker-compose restart odoo
# Then install via UI: Apps → helpdesk_mgmt, helpdesk_sale
```

---

## 🔧 DTX Customizations

### 1. Create DTX Helpdesk Extension Module

**Module Name**: `dtx_helpdesk_warranty`

**Purpose**: Integrate helpdesk with DTX contract cost tracking

**Features**:
- Link tickets to Sale Orders (extends `helpdesk_sale`)
- Add "Warranty Cost" button on tickets
- Auto-create Contract Cost when adding warranty expense
- Update SO profit/loss when warranty cost added

### 2. Ticket → Contract Cost Flow

**Scenario**: Customer reports broken camera

**Workflow**:
1. Support team creates ticket
2. Technician replaces camera
3. Click "Add Warranty Cost" on ticket
4. **Wizard opens**:
   - Sale Order: SO001 (from ticket)
   - Product: Camera 5MP
   - Quantity: 1
   - Unit Cost: 595,000 VND
   - Cost Type: warranty
   - Description: "Replacement for Ticket #TKT-001"
5. **Save** → Creates Contract Cost record
6. **Profit recalculates**: Original profit - 595,000

### 3. Sale Order Smart Button

**On Sale Order Form**:
- Add smart button: "Support Tickets (X)"
- Clicking opens related tickets
- Shows ticket status (New, In Progress, Solved)

---

## 📊 Data Model

### Extend helpdesk.ticket

```python
class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    sale_order_id = fields.Many2one('sale.order', string='Related Contract')
    warranty_cost_ids = fields.One2many('dtx.contract.cost', 'ticket_id', string='Warranty Costs')
    warranty_cost_total = fields.Monetary(compute='_compute_warranty_cost')

    def _compute_warranty_cost(self):
        for ticket in self:
            ticket.warranty_cost_total = sum(ticket.warranty_cost_ids.mapped('total_purchase'))

    def action_add_warranty_cost(self):
        """Open wizard to add warranty cost"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Add Warranty Cost',
            'res_model': 'dtx.helpdesk.warranty.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_ticket_id': self.id,
                'default_sale_order_id': self.sale_order_id.id,
            }
        }
```

### Extend dtx.contract.cost

```python
class ContractCost(models.Model):
    _inherit = 'dtx.contract.cost'

    ticket_id = fields.Many2one('helpdesk.ticket', string='Related Ticket', ondelete='set null')
    cost_type = fields.Selection(
        selection_add=[('warranty', 'Warranty')],
        ondelete={'warranty': 'cascade'}
    )
```

### Extend sale.order

```python
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    ticket_ids = fields.One2many('helpdesk.ticket', 'sale_order_id', string='Support Tickets')
    ticket_count = fields.Integer(compute='_compute_ticket_count')

    def _compute_ticket_count(self):
        for order in self:
            order.ticket_count = len(order.ticket_ids)

    def action_view_tickets(self):
        """Open related tickets"""
        return {
            'name': f'Support Tickets - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'helpdesk.ticket',
            'view_mode': 'tree,form',
            'domain': [('sale_order_id', '=', self.id)],
        }
```

---

## 🎨 UI Changes

### 1. Sale Order Form View

**Add after PAKD smart button**:

```xml
<button name="action_view_tickets" type="object" class="oe_stat_button" icon="fa-life-ring"
        attrs="{'invisible': [('ticket_count', '=', 0)]}">
    <field name="ticket_count" widget="statinfo" string="Support Tickets"/>
</button>
```

### 2. Ticket Form View

**Add warranty cost section**:

```xml
<page string="Warranty Costs" attrs="{'invisible': [('sale_order_id', '=', False)]}">
    <group>
        <field name="warranty_cost_total" widget="monetary"/>
    </group>
    <button name="action_add_warranty_cost" string="Add Warranty Cost"
            type="object" class="btn-primary"/>
    <field name="warranty_cost_ids" readonly="1">
        <tree>
            <field name="product_id"/>
            <field name="quantity"/>
            <field name="unit_purchase"/>
            <field name="total_purchase"/>
            <field name="description"/>
        </tree>
    </field>
</page>
```

### 3. Warranty Cost Wizard

```xml
<record id="view_warranty_cost_wizard" model="ir.ui.view">
    <field name="name">Add Warranty Cost</field>
    <field name="model">dtx.helpdesk.warranty.wizard</field>
    <field name="arch" type="xml">
        <form>
            <group>
                <field name="ticket_id" readonly="1"/>
                <field name="sale_order_id" readonly="1"/>
            </group>
            <group>
                <field name="product_id" required="1"/>
                <field name="quantity" required="1"/>
                <field name="unit_cost" required="1"/>
                <field name="description"/>
            </group>
            <footer>
                <button string="Add Cost" type="object" name="action_add_cost" class="btn-primary"/>
                <button string="Cancel" special="cancel"/>
            </footer>
        </form>
    </field>
</record>
```

---

## 🔄 Workflow

### Complete Support Flow

```
Customer Reports Issue
        ↓
Email to support@dtx.com
        ↓
Auto-create Ticket (via email gateway)
        ↓
Assign to Support Team
        ↓
Technician Investigates
        ↓
Needs Replacement? → Yes
        ↓
Add Warranty Cost (wizard)
        ↓
Contract Cost Created
        ↓
Profit Updated
        ↓
Ticket Solved
        ↓
Customer Notified
        ↓
Ticket Closed
```

---

## 📋 Implementation Steps

### Phase 1: Setup OCA Helpdesk (Week 1)

1. Clone OCA helpdesk repository
2. Install core modules:
   - `helpdesk_mgmt`
   - `helpdesk_mgmt_sla`
   - `helpdesk_sale` (link to SO)
3. Configure support teams
4. Setup email gateway
5. Test basic ticket creation

### Phase 2: DTX Extension Module (Week 2)

1. Create `dtx_helpdesk_warranty` module
2. Extend models:
   - `helpdesk.ticket` - add SO link, warranty costs
   - `dtx.contract.cost` - add ticket_id, warranty type
   - `sale.order` - add ticket_ids, smart button
3. Create warranty cost wizard
4. Add views

### Phase 3: Testing & UAT (Week 3)

1. Run Test Case 21: Activate Maintenance
2. Run Test Case 22: Customer Support Request
3. Test warranty cost flow
4. Test profit/loss update
5. Test customer portal
6. Get user feedback

### Phase 4: Production Deployment (Week 4)

1. Backup database
2. Deploy to production
3. Train support team
4. Document user guide
5. Go live!

---

## ✅ Acceptance Criteria

### From UAT Test Cases

**Test Case 21: Activate Maintenance**
- [ ] Can create support team with email alias
- [ ] Can configure SLA policies
- [ ] Maintenance contracts visible in Helpdesk

**Test Case 22: Customer Support Request**
- [ ] Customer emails create tickets automatically
- [ ] Tickets linked to Sale Orders
- [ ] Can add warranty costs from tickets
- [ ] Warranty costs update contract profit
- [ ] Customer receives email notifications
- [ ] SLA deadlines calculated correctly
- [ ] Ticket stages work: New → In Progress → Solved → Closed

### Additional Criteria

- [ ] Support Tickets smart button on Sale Order
- [ ] Ticket list filterable by SO, customer, team
- [ ] Warranty cost type in Contract Costs
- [ ] Reports: Tickets by team, SLA violations
- [ ] Customer portal: Submit & view tickets

---

## 📊 Expected Impact

### Business Benefits

1. **Organized Support**
   - No more scattered Chatter notes
   - Centralized ticket tracking
   - SLA compliance

2. **Better Customer Service**
   - Faster response times
   - Clear escalation paths
   - Customer portal for self-service

3. **Accurate Profit Tracking**
   - Warranty costs properly tracked
   - Real profit/loss per contract
   - Better pricing for future contracts

4. **Data-Driven Decisions**
   - Which products need most support?
   - Which customers have most issues?
   - Is warranty period too long/short?

---

## 📚 Resources

### Documentation

- OCA Helpdesk: https://github.com/OCA/helpdesk
- Odoo Helpdesk Guide: https://www.odoo.com/documentation/16.0/applications/services/helpdesk.html
- UAT Test Cases: [MANUAL_UAT_TEST_CASES.md](MANUAL_UAT_TEST_CASES.md#7-bảo-trì--support)

### Similar Implementations

- Check how other Odoo users handle warranty tracking
- OCA `repair` module for RMA/warranty management
- Integration patterns with sale orders

---

## 🚀 Next Actions

1. **Review this plan** with business users
2. **Approve budget** for OCA Helpdesk (if needed)
3. **Assign developer** for implementation
4. **Schedule UAT sessions** after Phase 2
5. **Plan go-live date** (target: 4 weeks from start)

---

**Created**: 2026-01-15
**Author**: DTX Development Team
**Status**: **DRAFT - Awaiting Approval**
