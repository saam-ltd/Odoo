from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError, AccessError,ValidationError

class CustomSalesperson(models.Model):
	_name = 'custom.salesperson'
	_description ='Custom Salesperson'
	_inherit = ['portal.mixin','mail.thread', 'mail.activity.mixin']
	_order = 'id desc'

	name = fields.Char(string='Salesperson', track_visibility="onchange")
	active = fields.Boolean(string='Archive', default=True)
	code = fields.Char(string='code', track_visibility="onchange")
	company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
	manager_id = fields.Many2one('res.users', string="Manager", tracking=2)
	linked_user_id = fields.Many2one('res.users', string="Linked User", tracking=2)
	activity_lines = fields.One2many('custom.salesperson.activity.line','activity_id',string="Activity lines")

	_sql_constraints = [('unique_code','UNIQUE(code)', 'Code already exist.')]


class CustomSalespersonActivityLines(models.Model):
	_name = 'custom.salesperson.activity.line'
	_description = "Custom Salesperson Activity Line"

	activity_id = fields.Many2one('custom.salesperson', 'Custom Salesperson')
	dayofweek = fields.Selection([
		('0', 'Monday'),
		('1', 'Tuesday'),
		('2', 'Wednesday'),
		('3', 'Thursday'),
		('4', 'Friday'),
		('5', 'Saturday'),
		('6', 'Sunday')], 'Day of Week', required=True, index=True, default='0')

	customer_ids = fields.Many2many('res.partner', string="Customer")
	company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

	@api.constrains('dayofweek', 'activity_id')
	def _check_unique_dayofweek(self):
		for line in self:
			if line.dayofweek and line.activity_id:
				duplicate_lines = self.env['custom.salesperson.activity.line'].search([
					('id', '!=', line.id),
					('activity_id', '=', line.activity_id.id),
					('dayofweek', '=', line.dayofweek)
				])
				if duplicate_lines:
					raise UserError(f"Day of the week '{dict(self._fields['dayofweek'].selection).get(line.dayofweek)}' is already selected for this activity.")
					
