from odoo import api, fields, models, SUPERUSER_ID, _

import logging
_logger = logging.getLogger(__name__)
from odoo.exceptions import AccessError, UserError, ValidationError
from lxml import etree

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    CUSTOM_FIELD_STATES = {
        state: [('readonly', False)]
        for state in {'sale', 'done', 'cancel'}
    }
    date_order = fields.Datetime(string="Order Date",states=CUSTOM_FIELD_STATES,copy=False, track_visibility="onchange")

    p_o_ref = fields.Char(string='Custom PO Reference')
    custom_salesperson_id = fields.Many2one('custom.salesperson',string='Custom Salesperson', track_visibility="onchange")

    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals['p_o_ref'] = self.p_o_ref
        invoice_vals['custom_salesperson_id'] = self.custom_salesperson_id.id 
        return invoice_vals
