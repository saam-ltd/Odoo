from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    CUSTOM_FIELD_STATES = {
        state: [('readonly', False)]
        for state in {'draft','posted'}
    }
    invoice_date = fields.Date(string="Invoice Date",states=CUSTOM_FIELD_STATES,copy=False, track_visibility="onchange")

    p_o_ref = fields.Char(string='Custom PO Reference')
    custom_salesperson_id = fields.Many2one('custom.salesperson',string='Custom Salesperson', track_visibility="onchange")
    
class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    bill_item_code = fields.Char(string='Item Code',copy=False)
