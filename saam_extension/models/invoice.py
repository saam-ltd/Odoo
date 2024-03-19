from odoo import models, fields, api
import logging
from datetime import datetime, timedelta
_logger = logging.getLogger(__name__)
from odoo.http import request
import logging, requests


class AccountMove(models.Model):
	_inherit = 'account.move'

	# CUSTOM_FIELD_STATES = {
	#     state: [('readonly', False)]
	#     for state in {'draft','posted'}
	# }
	# invoice_date = fields.Date(string="Invoice Date",states=CUSTOM_FIELD_STATES,copy=False, track_visibility="onchange")

	p_o_ref = fields.Char(string='Custom PO Reference')
	custom_salesperson_id = fields.Many2one('custom.salesperson',string='Custom Salesperson', track_visibility="onchange")
	customer_category_id =  fields.Many2one('customer.catgeory',string='Customer Category',related='partner_id.customer_category_id',tracking=2,copy=False)
	customer_remarks =  fields.Text(string='Customer Remarks',related='partner_id.cus_remarks', tracking=2,copy=False)


class AccountMoveLine(models.Model):
	_inherit = "account.move.line"

	bill_item_code = fields.Char(string='Item Code',copy=False)
	sku = fields.Char(string="Transaction Type", related='product_id.default_code')
	custom_salesperson_id = fields.Many2one('custom.salesperson',string='Custom Salesperson', related='move_id.custom_salesperson_id')
	move_line_type = fields.Selection(selection=[
			('entry', 'Journal Entry'),
			('out_invoice', 'Customer Invoice'),
			('out_refund', 'Customer Credit Note'),
			('in_invoice', 'Vendor Bill'),
			('in_refund', 'Vendor Credit Note'),
			('out_receipt', 'Sales Receipt'),
			('in_receipt', 'Purchase Receipt'),
		], string='Type', compute='_compute_move_type', store=True)
	prod_boxes = fields.Text(string='Boxes')

	def _compute_move_type(self):
		for rec in self:
			if rec.move_id.move_type:
				rec.move_line_type = rec.move_id.move_type
