from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError,ValidationError
from datetime import *


class SchedulePlanning(models.Model):
	_name = "schedule.planning"
	_description = "Schedule Planning"
	_inherit = ['mail.thread', 'mail.activity.mixin']
	# _order = 'id desc'

	# name = fields.Char(string="Name", copy=False, default='New')
	# start_date = fields.Date(string="Start Date", tracking=True)
	# end_date = fields.Date(string="End  Date" ,tracking=True)
	# custom_salesperson_id = fields.Many2one('custom.salesperson', string="Salesperson", tracking=2)
	# manager_id = fields.Many2one('res.users', string="Manager", tracking=2)
	# linked_user_id = fields.Many2one('res.users', string="Linked User", tracking=2)
	# company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
	# state = fields.Selection([
	# 	('draft', 'Draft'),
	# 	('confirm', 'Confirmed'),
	# 	('activity_created', 'Activity Created'),
	# 	('cancel', 'Cancelled')], 'Status', default='draft',tracking=2)
	# schedule_plan_lines = fields.One2many('schedule.planning.line','schedule_id',string="Schedule Plan Lines")
	# note = fields.Text(string="Terms and condition")

	# @api.constrains('start_date', 'end_date')
	# def _check_dates(self):
	# 	for record in self:
	# 		if record.start_date > record.end_date:
	# 			raise UserError("From date cannot be greater than End date.")

	# @api.onchange('custom_salesperson_id')
	# def _onchange_custom_salesperson_id(self):
	#     if self.custom_salesperson_id:
	#         if not self.custom_salesperson_id.activity_lines:raise UserError(_('No Scheduled plan for this Salesperson,\n Kindly Map it.'))
	#         for i in self.custom_salesperson_id.activity_lines:
	#             acitivties = {
	#             'dayofweek' : i.dayofweek,
				
	#         }
	#         i.sudo().create(acitivties)

	# def generate_weekday_entries(self):
	# 	if not self.start_date and not self.end_date:raise UserError(_("Kindly fill From date and To date in Period."))
	# 	if not self.custom_salesperson_id:raise UserError(_("Kindly map the salesperson."))
	# 	if self.custom_salesperson_id:
	# 		if not self.custom_salesperson_id.linked_user_id:raise UserError(_('Kindly Map the Lined user in Salesperson'))
	# 		self.linked_user_id = self.custom_salesperson_id.linked_user_id.id
	# 		if not self.custom_salesperson_id.manager_id:raise UserError(_('Kindly Map the Manager in Salesperson'))
	# 		self.manager_id = self.custom_salesperson_id.manager_id.id

	# 		self.schedule_plan_lines.unlink()  # Clear existing records

	# 		dayofweek_customer_map = {line.dayofweek: line.customer_ids.ids for line in self.custom_salesperson_id.activity_lines}

	# 		start_date = fields.Date.from_string(self.start_date)
	# 		end_date = fields.Date.from_string(self.end_date)

	# 		current_date = start_date
	# 		while current_date <= end_date:
	# 			if current_date.weekday() < 5:  # Weekdays are 0 to 4 (Monday to Friday)
	# 				# Get customer_ids based on the dayofweek
	# 				customer_ids = dayofweek_customer_map.get(str(current_date.weekday()), [])

	# 				self.schedule_plan_lines.create({
	# 					'schedule_id': self.id,
	# 					'date': current_date,
	# 					'dayofweek': str(current_date.weekday()),  # Convert to string to match the selection field
	# 					'customer_ids': [(6, 0, customer_ids)] if customer_ids else False,
	# 				})

	# 			current_date += timedelta(days=1)

	# def action_create_schedule_activity(self):
	# 	# create the schedule activities for respective customers
	# 	model_id = self.env['ir.model'].search([('model','=','res.partner')],limit=1)

	# 	for line in self.schedule_plan_lines:
	# 		for customer in line.customer_ids:
	# 			activity_id = self.env['mail.activity'].create({
	# 				'res_model': 'res.partner',
	# 				'res_id': customer.id,
	# 				'custom_salesperson_id': self.custom_salesperson_id.id,
	# 				'user_id': self.custom_salesperson_id.linked_user_id.id,
	# 				'res_model_id': model_id.id,
	# 				'date_deadline':line.date,
	# 				'customer_id': customer.id,
	# 				'street': customer.street if customer.street else '',
	# 				'street2': customer.street2 if customer.street2 else '',
	# 				'city': customer.city if customer.city else False,
	# 				'state_id': customer.state_id.id if customer.state_id.id else False,
	# 				'country_id': customer.country_id.id if customer.country_id.id else False,
	# 				'zip': customer.zip if customer.zip else '',
	# 				'email': customer.email if customer.email else '',
	# 				'mobile': customer.mobile if customer.mobile else '',
	# 				'phone': customer.phone if customer.phone else '',
	# 				'activity_type_id':line.activity_type_id.id,
	# 				'schedule_plan_line_id':line.id,
	# 				'is_from_scheduled_planning': True
	# 				})
	# 	self.write({"state": "activity_created"})

	# def action_schedule_draft(self):
	# 	self.write({"state": "draft"})

	# def action_schedule_confirm(self):
	# 	self.write({"state": "confirm"})

	# def action_schedule_cancel(self):
	# 	self.write({"state": "cancel"})

	# def action_schedule_draft(self):
	# 	self.write({"state": "draft"})
	
class SchedulePlanningLines(models.Model):
	_name = 'schedule.planning.line'
	_description = "Schedule Planning Line"

	schedule_id = fields.Many2one('schedule.planning', 'Schedule Planning')
	date = fields.Date(string="Date")
	dayofweek = fields.Selection([
		('0', 'Monday'),
		('1', 'Tuesday'),
		('2', 'Wednesday'),
		('3', 'Thursday'),
		('4', 'Friday'),
		('5', 'Saturday'),
		('6', 'Sunday')], 'Day of Week', required=True, index=True, default='0')

	# customer_id = fields.Many2one('res.partner', string="Customer")
	customer_ids = fields.Many2many('res.partner', string="Customer")
	activity_type_id = fields.Many2one('mail.activity.type',string="Activity Type")
	company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
	
class MailActivity(models.Model):
	_inherit = 'mail.activity'

	schedule_plan_line_id = fields.Many2one('schedule.planning.line',string="Schedule Plan")
	customer_id = fields.Many2one('res.partner', string="Customer")
	email = fields.Char(string="Email")
	mobile = fields.Char(string="Mobile")
	phone = fields.Char(string="Phone")
	zip = fields.Char(string="Zip")
	city = fields.Char(string="City")
	street = fields.Char(string="Street")
	street2 = fields.Char(string="Street 2")
	state_id = fields.Many2one('res.country.state',string="State")
	country_id = fields.Many2one('res.country',string="Country")
	activity_state = fields.Selection([
		('draft', 'Draft'),
		('running', 'Running'), ('stopped', 'Stopped'),
		('done', 'Activity Done'),
		('cancel', 'Activity Cancelled')], 'Activity Status', default='draft')
	is_from_scheduled_planning = fields.Boolean(string='Is From Scheduled Planning')
	custom_salesperson_id = fields.Many2one('custom.salesperson', string="Salesperson", tracking=2)
	task_timer = fields.Boolean(string='Timer', default=False)

	start_time = fields.Datetime(string='Start Time', readonly=True)
	end_time = fields.Datetime(string='End Time', readonly=True)
	elapsed_time = fields.Char(string='Elapsed Time', compute='_compute_elapsed_time', store=True)

	@api.constrains('custom_salesperson_id', 'activity_state')
	def _check_salesperson(self):
		for rec in self:
			if rec.activity_state in ['running', 'stopped']:
				existing_plans = rec.search([
					('custom_salesperson_id', '=', rec.custom_salesperson_id.id),
					('activity_state', 'in', ['running', 'stopped']),
					('id', '!=', rec.id),
				])
				if existing_plans:
					raise UserError(_('Please complete the previous task before moving on to another plan.'))


	@api.depends('start_time', 'end_time', 'state')
	def _compute_elapsed_time(self):
		for timer in self:
			if timer.activity_state == 'running':
				timer.elapsed_time = (fields.Datetime.now() - timer.start_time).total_seconds() / 3600.0
			elif timer.activity_state == 'stopped':
				diff = fields.Datetime.from_string(timer.end_time) - fields.Datetime.from_string(timer.start_time)
				
				total_seconds = diff.total_seconds()
				hours, remainder = divmod(total_seconds, 3600)
				minutes, _ = divmod(remainder, 60)

				timer.elapsed_time = f"{int(hours):02}:{int(minutes):02}"
			else:
				timer.elapsed_time = 0.0


	def action_timer_start(self):
		self.write({'activity_state': 'running', 'start_time': fields.Datetime.now()})

	# def action_timer_pause(self):
	# 	self.write({'activity_state': 'paused', 'end_time': fields.Datetime.now()})
	# 	print("end_time-----------------------------",self.end_time)


	def action_timer_stop(self):
		self.write({'activity_state': 'stopped', 'end_time': fields.Datetime.now()})


	def action_mark_done(self):
		self.activity_state = 'done'

	def action_mark_cancel(self):
		self.activity_state = 'cancel'
