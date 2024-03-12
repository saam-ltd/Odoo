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
	# logistic_duration_id =  fields.Many2one('customer.logistic.timing',string='Logistic Timing',related='partner_id.customer_logistic_id',tracking=2,copy=False)
	customer_category_id =  fields.Many2one('customer.catgeory',string='Customer Category',related='partner_id.customer_category_id',tracking=2,copy=False)
	customer_remarks =  fields.Text(string='Customer Remarks',related='partner_id.cus_remarks', tracking=2,copy=False)

	def invoice_duedate_followup_email_cron(self):
		invoice_due_list = self.env['account.move'].search([('move_type', '=', 'out_invoice'),('invoice_date_due', '=', datetime.now().date()),('payment_state', '!=', ('paid'))])
		if invoice_due_list:
			mail_id = self.send_mail_for_invoice(invoice_list=invoice_due_list)

	def send_mail_for_invoice(self,invoice_list=False):
		context = dict(self._context or {})
		try:
			_logger.error("Entered in Email for Due Invoice Followup Report==============================================> ")
			invoice_list = [{
				'name': order.name,
				'customer_name': order.partner_id.name,
			} for order in invoice_list]
			self.env.ref('saam_extension.email_template_due_invoice').with_user(2).with_context(lines=invoice_list).send_mail(self.id, force_send=True)
			return True
		except Exception as e:
			_logger.error("Error in Sending Email for Due Invoice Followup Report==============================================> " + str(e))
			return False

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
