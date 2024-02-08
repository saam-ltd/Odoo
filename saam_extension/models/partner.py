from odoo import api, fields, models, SUPERUSER_ID, _
import logging
from odoo.exceptions import UserError, AccessError,ValidationError

class ResPartner(models.Model):
	_inherit = 'res.partner'

	brn = fields.Char(string='Business Registration Number',copy=False,tracking=True)
	custom_salesperson_id = fields.Many2one('custom.salesperson',string='Custom Salesperson', track_visibility="onchange")
	customer_category_id = fields.Many2one('customer.catgeory',string='Customer Category',copy=False)
	customer_logistic_id = fields.Many2one('customer.logistic.timing',string='Logistic Timing',copy=False)
	gl_code = fields.Char(string='Gl Code',copy=False,tracking=True)
	is_cus = fields.Boolean(string='Is Cus',copy=False,tracking=True)
	cus_remarks = fields.Text(string='Customer Remarks',copy=False,tracking=True)
	customer_target_tracking_lines = fields.One2many('customer.target.tracking.lines', 'customer_target_id', 'Customer Target Tracking Lines')

	def target_tracking(self):
		print("target_tracking")

class CustomerTargetTrackingLines(models.Model):
	_name = "customer.target.tracking.lines"
	_description = "Customer Target Tracking Line"

	name = fields.Char(string="Name")
	customer_target_id = fields.Many2one('res.partner', 'Customer Target')
	date_from = fields.Date('Start Date', required=True)
	date_to = fields.Date('End Date', required=True)
	custom_salesperson_id = fields.Many2one('custom.salesperson', string="Salesperson", tracking=2, )
	currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True)
	customer_target_amt = fields.Monetary('Target Amount', required=True)
	customer_achieved_amt = fields.Monetary('Achieved Amount', compute='_compute_cus_achieved_amt')
	company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

	@api.model
	def create(self, vals):
		# Check if custom_salesperson_id has changed in res.partner
		if 'custom_salesperson_id' in vals and vals.get('customer_target_id'):
			customer_id = vals['customer_target_id']
			partner = self.env['res.partner'].browse(customer_id)
			if partner.custom_salesperson_id.id != vals['custom_salesperson_id']:
				vals['custom_salesperson_id'] = partner.custom_salesperson_id.id

		return super(CustomerTargetTrackingLines, self).create(vals)

	@api.constrains('date_from', 'date_to')
	def _check_dates(self):
		for record in self:
			if record.date_from > record.date_to:
				raise UserError("Start date cannot be greater than End date.")


	def _compute_cus_achieved_amt(self):
		for rec in self:
			customer_achieved_amt = 0.0
			for i in self.env['account.move'].search([('custom_salesperson_id', '=', rec.custom_salesperson_id.id),
				('partner_id', '=', self.customer_target_id.id),
				('invoice_date', '>=', rec.date_from),
				('invoice_date', '<=', rec.date_to),
				('move_type', '=', 'out_invoice'),('state', '=', 'posted')]):
				customer_achieved_amt += i.amount_diff
			rec.customer_achieved_amt = customer_achieved_amt

	def action_open_cus_achieved_entries(self):
		view_id = self.env.ref('saam_extension.view_out_invoice_tree_inherit_cus_target').id  # Replace with your actual module and view ID

		action = {
			"name": "Customer Target Tracking Report",
			"type": "ir.actions.act_window",
			"view_mode": "tree",
			"res_model": "account.move",
			# "view_id": view_id,  # Specify the view ID here
			"target": "current",
			"domain": [
				('custom_salesperson_id', '=', self.customer_target_id.custom_salesperson_id.id),
				('partner_id', '=', self.customer_target_id.id),
				('invoice_date', '>=', self.date_from),
				('invoice_date', '<=', self.date_to),
				('move_type', '=', 'out_invoice'),('state', '=', 'posted')],
			}
		return action

class CustomerCategory(models.Model):
	_name = 'customer.catgeory' 
	_inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
	_description = "Customer Category"

	name = fields.Char(string='Name',copy=False,required=True)
	company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)

class CustomerLogisticTiming(models.Model):
	_name = 'customer.logistic.timing' 
	_inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
	_description = "Customer Logistic Timing"

	name = fields.Char(string='Name',copy=False,required=True)
	company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)



	

