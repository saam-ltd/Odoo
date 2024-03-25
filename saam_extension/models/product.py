from odoo import models, fields, api
import logging

from odoo.exceptions import AccessError, UserError, ValidationError
import json
from lxml import etree


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    scale_code = fields.Char(string='Scale Code',copy=False)
    is_product_cost_hide = fields.Boolean(string='Is product cost hide', compute="_compute_product_cost_hide")

    def _compute_product_cost_hide(self):
        for order in self:
            order.is_product_cost_hide = False
            if order.env.user.has_group('saam_extension.group_hide_product_cost'):
                order.is_product_cost_hide = True
    
class ProductProduct(models.Model):
    _inherit = 'product.product'

    is_product_cost_hide = fields.Boolean(string='Is product cost hide', compute="_compute_product_cost_hide")

    def _compute_product_cost_hide(self):
        for order in self:
            order.is_product_cost_hide = False
            if order.env.user.has_group('saam_extension.group_hide_product_cost'):
                order.is_product_cost_hide = True
