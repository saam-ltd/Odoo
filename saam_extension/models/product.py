from odoo import models, fields, api
import logging

from odoo.exceptions import AccessError, UserError, ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    scale_code = fields.Char(string='Scale Code',copy=False, tracking=True)
    
