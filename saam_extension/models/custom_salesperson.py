from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError, AccessError,ValidationError

class CustomSalesperson(models.Model):
	_name = 'custom.salesperson'
	_description ='Custom Salesperson'
	_inherit = ['portal.mixin','mail.thread', 'mail.activity.mixin']
	_order = 'id desc'

	name = fields.Char(string='Salesperson',  tracking=True)
	active = fields.Boolean(string='Archive', default=True)
	code = fields.Char(string='code',  tracking=True)
	company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
	manager_id = fields.Many2one('res.users', string="Manager",  tracking=True)
	linked_user_id = fields.Many2one('res.users', string="Linked User",  tracking=True)

	_sql_constraints = [('unique_code','UNIQUE(code)', 'Code already exist.')]
