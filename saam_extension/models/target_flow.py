from odoo import models, fields, api, _
import logging
from collections import defaultdict
from datetime import timedelta
import json
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta


_logger = logging.getLogger(__name__)

class TargetFlow(models.Model):
	_name = 'target.flow'
	_description ='Target Tracking'
	_inherit = ['portal.mixin','mail.thread', 'mail.activity.mixin']
	_order = 'id desc'

	name = fields.Char('Name')
	custom_salesperson_id = fields.Many2one('custom.salesperson', string="Salesperson", tracking=2)
	manager_id = fields.Many2one('res.users', string="Manager", tracking=2)
	linked_user_id = fields.Many2one('res.users', string="Linked User", tracking=2)
	company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
	date_from = fields.Date('Start Date', states={'confirm': [('readonly', True)]},tracking=2)
	date_to = fields.Date('End Date', states={'confirm': [('readonly', True)]}, tracking=2)
	state = fields.Selection([
		('draft', 'Draft'),
		('confirm', 'Confirmed'),
		('cancel', 'Cancelled')], 'Status', default='draft',tracking=2)
	target_tracking_lines = fields.One2many('target.tracking.lines', 'target_id', 'Target Tracking Lines')
	target_tracking_lines_week = fields.One2many('target.tracking.lines.week', 'target_week_id', 'Target Tracking Lines - Week')

	yearly_target_amt = fields.Monetary('Yearly Target', tracking=2)
	yearly_achieved_amt = fields.Monetary('Yearly Achieved', compute="_compute_yearly_achievedd_amt")
	progress = fields.Integer(string="Progress", compute='_compute_progress')
	currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True)
	cancel_reason = fields.Char(string="Cancel Reason", tracking=2)

	# @api.constrains('target_tracking_lines','target_tracking_lines.monthly_target_amt')
	# def _check_monthly_amount(self):
	# 	for record in self:
	# 		total_amount = sum(record.target_tracking_lines.mapped('monthly_target_amt'))
	# 		if total_amount > record.yearly_target_amt:
	# 			raise UserError(_("Total Monthly Target amount should not exceed than the Yearly Target Amount!"))

	@api.constrains('date_from', 'date_to')
	def _check_dates(self):
		for record in self:
			if record.date_from > record.date_to:
				raise UserError("From date cannot be greater than End date.")

	def generate_target_line_entries(self):
		if not self.date_from and not self.date_to:raise UserError(_("Kindly fill From date and To date in Period."))
		if not self.custom_salesperson_id:raise UserError(_("Kindly map the salesperson."))
		if self.custom_salesperson_id:
			if not self.custom_salesperson_id.linked_user_id:raise UserError(_('Kindly Map the Lined user in Salesperson'))
			self.linked_user_id = self.custom_salesperson_id.linked_user_id.id
			if not self.custom_salesperson_id.manager_id:raise UserError(_('Kindly Map the Manager in Salesperson'))
			self.manager_id = self.custom_salesperson_id.manager_id.id

		# Week target
		self.target_tracking_lines_week.unlink()  
		current_date = self.date_from
		while current_date <= self.date_to:
			if current_date.weekday() < 5:  # Weekday (Monday to Friday)
				week_start = current_date
				week_end = min(current_date + timedelta(days=4 - current_date.weekday()), self.date_to)
				self.target_tracking_lines_week.create({
					'date_from': week_start,
					'date_to': week_end,
					'target_week_id': self.id,
					'custom_salesperson_id': self.custom_salesperson_id.id,
					'state': self.state,
				})
			current_date += timedelta(days=7 - current_date.weekday())

		# Monthly Target
		self.target_tracking_lines.unlink()
		start = fields.Date.from_string(self.date_from)
		end = fields.Date.from_string(self.date_to)

		while start <= end:
			next_month = (start.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
			if next_month > end:
				next_month = end
			self.target_tracking_lines.create({
				'target_id': self.id,
				'date_from': start,
				'date_to': next_month,
				'custom_salesperson_id': self.custom_salesperson_id.id,
				'state': self.state,
			})
			start = next_month + timedelta(days=1)

	def _compute_progress(self):
		for rec in self:
			rec.progress = 0
			if rec.yearly_achieved_amt > 1 and rec.yearly_target_amt > 1:
				rec.progress = (rec.yearly_achieved_amt / rec.yearly_target_amt) * 100

	@api.model
	def create(self, vals):
		res =super(TargetFlow,self).create(vals)
		res.name= self.env['ir.sequence'].next_by_code('target.flow.seq') or _('New')
		return res

	def _compute_yearly_achievedd_amt(self):
		yearly_achieved_amt = 0.0
		for i in self.target_tracking_lines:
			yearly_achieved_amt += i.monthly_achieved_amt
		self.yearly_achieved_amt = yearly_achieved_amt

	# @api.constrains('custom_salesperson_id','date_from')
	# def _check_salesperson(self):
	# 	for rec in self:
	# 		for i in rec.search([('custom_salesperson_id', '=', rec.custom_salesperson_id.id),('id','!=', rec.id)]):
	# 			if rec.date_from >= i.date_from and rec.date_from <=  i.date_to:
	# 				raise UserError(_('A record has already been created for the salesperson between the same date range'))


	@api.onchange('custom_salesperson_id')
	def _onchange_custom_salesperson_id(self):
		if self.custom_salesperson_id:
			if not self.custom_salesperson_id.linked_user_id:raise UserError(_('Kindly Map the Lined user in Salesperson'))
			self.linked_user_id = self.custom_salesperson_id.linked_user_id.id
			if not self.custom_salesperson_id.manager_id:raise UserError(_('Kindly Map the Manager in Salesperson'))
			self.manager_id = self.custom_salesperson_id.manager_id.id

	def action_target_confirm(self):
		if not self.yearly_target_amt:raise UserError(_('Kindly fill the Yearly Target Amount.'))
		for month in self.target_tracking_lines:
			total_amount = 0.0
			for week in self.target_tracking_lines_week:
				if week.date_from <= month.date_to and week.date_to >= month.date_from:
					# Week overlaps with the month
					if week.date_from >= month.date_from and week.date_to <= month.date_to:
						# Week is fully within the month
						total_amount += week.weekly_target_amt
					elif week.date_from >= month.date_from and week.date_from <= month.date_to:
						# Week starts within the month
						total_amount += week.prev_days_target_amt or 0.0
					else:
						# Week ends within the month
						total_amount += week.end_days_target_amt or 0.0
			month.write({'monthly_target_amt': total_amount})

		total_amount_monthly = sum(self.target_tracking_lines.mapped('monthly_target_amt'))
		if total_amount_monthly > self.yearly_target_amt:
			raise UserError(_("Total Monthly Target amount should not exceed than the Yearly Target Amount!"))
		self.write({"state": "confirm"})

	def action_target_cancel(self):
		if not self.cancel_reason:
			raise UserError(_('Kindly give the Cancel Reason'))
		self.write({"state": "cancel"})

	def action_target_draft(self):
		self.write({"state": "draft"})

class TargetTrackingLines(models.Model):
	_name = "target.tracking.lines"
	_description = "Target Tracking Line"

	target_id = fields.Many2one('target.flow', 'Target')
	date_from = fields.Date('Start Date', required=True)
	date_to = fields.Date('End Date', required=True)
	custom_salesperson_id = fields.Many2one('custom.salesperson', string="Salesperson", tracking=2)
	currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True)
	monthly_target_amt = fields.Monetary('Monthly Target Amount')
	company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
	monthly_achieved_amt = fields.Monetary(string= 'Monthly Achieved Amount', compute='_compute_monthly_achievedd_amt')
	progress = fields.Integer(string="progress", compute='_compute_progress')
	state = fields.Selection([
		('draft', 'Draft'),
		('confirm', 'Confirmed'),
		('cancel', 'Cancelled')], 'Status', default='draft')

	@api.onchange('date_from')
	def _onchange_custom_salesperson_id(self):
		if not self.target_id.custom_salesperson_id:
			raise UserError(_('Kindly choose the salesperson'))
		self.custom_salesperson_id = self.target_id.custom_salesperson_id.id

	def _compute_progress(self):
		for rec in self:
			rec.progress = 0
			if rec.monthly_achieved_amt > 1 and rec.monthly_target_amt > 1:
				rec.progress = (rec.monthly_achieved_amt / rec.monthly_target_amt) * 100


	def _compute_monthly_achievedd_amt(self):
		for rec in self:
			monthly_achieved_amt = 0.0
			for i in self.env['account.move'].search([('custom_salesperson_id', '=', rec.custom_salesperson_id.id),
				('invoice_date', '>=', rec.date_from),
				('invoice_date', '<=', rec.date_to),
				('move_type', '=', 'out_invoice'),('state', '=', 'posted')]):
				monthly_achieved_amt += i.amount_diff

			rec.monthly_achieved_amt = monthly_achieved_amt


	def action_open_target_entries_month(self):
		view_id = self.env.ref('saam_extension.view_out_invoice_tree_inherit_target').id  # Replace with your actual module and view ID

		action = {
			"name": "Tracking Report - Monthly",
			"type": "ir.actions.act_window",
			"view_mode": "tree",
			"res_model": "account.move",
			# "view_id": view_id,  # Specify the view ID here
			"target": "current",
			"domain": [
				('custom_salesperson_id', '=', self.custom_salesperson_id.id),
				('invoice_date', '>=', self.date_from),
				('invoice_date', '<=', self.date_to),
				('move_type', '=', 'out_invoice'),('state', '=', 'posted')],
			}
		# Create records with the weekly target amount set to each line
		move_ids = self.env['account.move'].search(action['domain'])
		for move in move_ids:
			for customer in move.partner_id.customer_target_tracking_lines:
				if move.invoice_date >= customer.date_from and move.invoice_date <= customer.date_to and move.custom_salesperson_id.id == customer.custom_salesperson_id.id:
					move.customer_target_amt = customer.customer_target_amt
			move.write({
				'salesperson_target_amt': self.monthly_target_amt})

		return action

class TargetTrackingLinesWeek(models.Model):
	_name = "target.tracking.lines.week"
	_description = "Target Tracking Lines - Week"

	target_week_id = fields.Many2one('target.flow', 'Target')
	date_from = fields.Date('Start Date', required=True)
	date_to = fields.Date('End Date', required=True)
	custom_salesperson_id = fields.Many2one('custom.salesperson', string="Salesperson", tracking=2)
	currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True)
	weekly_target_amt = fields.Monetary('Weekly Target Amount')
	weekly_achieved_amt = fields.Monetary('Weekly Achieved Amount', compute='_compute_weekly_achievedd_amt')
	company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
	progress = fields.Integer(string="progress", compute='_compute_progress')
	state = fields.Selection([
		('draft', 'Draft'),
		('confirm', 'Confirmed'),
		('cancel', 'Cancelled')], 'Status', default='draft')
	prev_days_target_amt = fields.Monetary(string="Previous Week Amount")
	end_days_target_amt = fields.Monetary(string="End Amount", compute="_compute_end_days_target_amt")

	def _compute_end_days_target_amt(self):
		for rec in self:
			rec.end_days_target_amt = rec.weekly_target_amt - rec.prev_days_target_amt


	@api.onchange('date_from')
	def _onchange_custom_salesperson_id(self):
		if not self.target_week_id.custom_salesperson_id:
			raise UserError(_('Kindly choose the salesperson'))
		self.custom_salesperson_id = self.target_week_id.custom_salesperson_id.id

	def _compute_progress(self):
		for rec in self:
			rec.progress = 0
			if rec.weekly_achieved_amt > 1 and rec.weekly_target_amt > 1:
				rec.progress = (rec.weekly_achieved_amt / rec.weekly_target_amt) * 100

	def _compute_weekly_achievedd_amt(self):
		for rec in self:
			weekly_achieved_amt = 0.0
			for i in self.env['account.move'].search([('custom_salesperson_id', '=', rec.custom_salesperson_id.id),
				('invoice_date', '>=', rec.date_from),
				('invoice_date', '<=', rec.date_to),
				('move_type', '=', 'out_invoice'),('state', '=', 'posted')]):
				weekly_achieved_amt += i.amount_diff
			rec.weekly_achieved_amt = weekly_achieved_amt


	def action_open_target_entries_week(self):
		view_id = self.env.ref('saam_extension.view_out_invoice_tree_inherit_target').id  # Replace with your actual module and view ID

		action = {
			"name": "Tracking Report - Weekly",
			"type": "ir.actions.act_window",
			"view_mode": "tree",
			"res_model": "account.move",
			# "view_id": view_id,  # Specify the view ID here
			"target": "current",
			"domain": [
				('custom_salesperson_id', '=', self.target_week_id.custom_salesperson_id.id),
				('invoice_date', '>=', self.date_from),
				('invoice_date', '<=', self.date_to),
				('move_type', '=', 'out_invoice'),('state', '=', 'posted')],
			}

		# Create records with the weekly target amount set to each line
		move_ids = self.env['account.move'].search(action['domain'])
		# for move in move_ids:
		for move in move_ids:
			for customer in move.partner_id.customer_target_tracking_lines:
				if move.invoice_date >= customer.date_from and move.invoice_date <= customer.date_to and move.custom_salesperson_id.id == customer.custom_salesperson_id.id:
					move.customer_target_amt = customer.customer_target_amt
			move.write({'salesperson_target_amt': self.weekly_target_amt})

		return action

class AccountMove(models.Model):
	_inherit = 'account.move'

	credit_note_numbers = fields.Char(string='Credit Note Numbers', compute='_compute_credit_note_numbers')
	payment_ref = fields.Char(string='Payment Ref')
	credit_amt = fields.Monetary('Credit Note Amount', readonly='True', store='True')
	amount_diff = fields.Monetary(string= 'Amount Difference', compute='_compute_difference_amount', readonly='True', store='True')
	paid_amount = fields.Monetary(string='Paid Amount',compute='_compute_payment_info')
	salesperson_target_amt = fields.Monetary('Salesperson Target Amount')
	customer_target_amt = fields.Monetary('Salesperson Target Amount')


	@api.depends('reversal_move_id')
	def _compute_credit_note_numbers(self):
		for move in self:
			credit_note_numbers = ", ".join(move.reversal_move_id.mapped('name'))
			move.credit_note_numbers = credit_note_numbers

			total_credit_amt = sum(move.reversal_move_id.mapped('amount_untaxed_signed'))
			move.credit_amt = total_credit_amt

	@api.depends('amount_untaxed_signed', 'credit_amt')
	def _compute_difference_amount(self):
		for move in self:
			move.amount_diff = move.amount_untaxed_signed + move.credit_amt

	def _compute_payment_info(self):
		for i in self:
			pay_amt = 0.0
			payment_refs = []
			if i.invoice_payments_widget and json.loads(i.invoice_payments_widget) and json.loads(i.invoice_payments_widget).get('content'):
				for j in json.loads(i.invoice_payments_widget).get('content'):
					pay_amt+= j.get('amount') if j.get('account_payment_id') else 0.0
					payment_ref = j.get('ref') if j.get('payment_id') else ''
					payment_refs.append(payment_ref)

			i.paid_amount = pay_amt
			i.payment_ref = ", ".join(payment_refs)

	