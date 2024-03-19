from odoo import api, fields, models, SUPERUSER_ID, _
import logging
from odoo.exceptions import UserError, AccessError,ValidationError

class ResPartner(models.Model):
	_inherit = 'res.partner'

	brn = fields.Char(string='Business Registration Number',copy=False,tracking=True)
	custom_salesperson_id = fields.Many2one('custom.salesperson',string='Custom Salesperson', track_visibility="onchange")
	customer_category_id = fields.Many2one('customer.catgeory',string='Customer Category',copy=False)
	# customer_logistic_id = fields.Many2one('customer.logistic.timing',string='Logistic Timing',copy=False)
	gl_code = fields.Char(string='Gl Code',copy=False,tracking=True)
	is_cus = fields.Boolean(string='Is Cus',copy=False,tracking=True)
	cus_remarks = fields.Text(string='Customer Remarks',copy=False,tracking=True)


class CustomerCategory(models.Model):
	_name = 'customer.catgeory' 
	_inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
	_description = "Customer Category"

	name = fields.Char(string='Name',copy=False,required=True)
	company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)

	

