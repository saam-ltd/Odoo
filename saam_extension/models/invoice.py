from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    # CUSTOM_FIELD_STATES = {
    #     state: [('readonly', False)]
    #     for state in {'draft','posted'}
    # }
    # invoice_date = fields.Date(string="Invoice Date",states=CUSTOM_FIELD_STATES,copy=False, track_visibility="onchange")

    p_o_ref = fields.Char(string='Custom PO Reference')
    custom_salesperson_id = fields.Many2one('custom.salesperson',string='Custom Salesperson', track_visibility="onchange")
    logistic_duration_id =  fields.Many2one('customer.logistic.timing',string='Logistic Timing',related='partner_id.customer_logistic_id',tracking=2,copy=False)
    customer_category_id =  fields.Many2one('customer.catgeory',string='Customer Category',related='partner_id.customer_category_id',tracking=2,copy=False)
    customer_remarks =  fields.Text(string='Customer Remarks',related='partner_id.cus_remarks', tracking=2,copy=False)
    
class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    bill_item_code = fields.Char(string='Item Code',copy=False)
