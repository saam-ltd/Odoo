from odoo import api, fields, models, SUPERUSER_ID, _
import logging


class ResPartner(models.Model):
    _inherit = 'res.partner'


    brn = fields.Char(string='Business Registration Number',copy=False,tracking=True)
    contact_sale_person = fields.Char(string='Contact Sales Person',copy=False,tracking=True)
    gl_code = fields.Char(string='Gl Code',copy=False,tracking=True)
    is_cus = fields.Boolean(string='Is Cus',copy=False,tracking=True)
    

