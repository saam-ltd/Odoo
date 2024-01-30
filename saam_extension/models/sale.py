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
    custom_salesperson_id = fields.Many2one('custom.salesperson',string='Custom Salesperson.', tracking=2)
    logistic_duration_id =  fields.Many2one('customer.logistic.timing',string='Logistic Timing',related='partner_id.customer_logistic_id',tracking=2,copy=False)
    customer_category_id =  fields.Many2one('customer.catgeory',string='Customer Category',related='partner_id.customer_category_id',tracking=2,copy=False)
    customer_remarks =  fields.Text(string='Customer Remarks',related='partner_id.cus_remarks', tracking=2,copy=False)

    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals['p_o_ref'] = self.p_o_ref
        invoice_vals['custom_salesperson_id'] = self.custom_salesperson_id.id 
        invoice_vals['logistic_duration_id'] = self.logistic_duration_id.id 
        invoice_vals['customer_category_id'] = self.customer_category_id.id 
        invoice_vals['customer_remarks'] = self.customer_remarks
        return invoice_vals

    @api.onchange('partner_id')
    def onchange_partner_id_custom_sales_person(self): 
        if self.partner_id: 
            self.custom_salesperson_id = self.partner_id.custom_salesperson_id.id if self.partner_id.custom_salesperson_id else False
