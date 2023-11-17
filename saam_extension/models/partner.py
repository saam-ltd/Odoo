from odoo import api, fields, models, SUPERUSER_ID, _
import logging


class ResPartner(models.Model):
    _inherit = 'res.partner'


    brn = fields.Char(string='Business Registration Number',copy=False,tracking=True)
    custom_salesperson_id = fields.Many2one('custom.salesperson',string='Custom Salesperson', track_visibility="onchange")
    gl_code = fields.Char(string='Gl Code',copy=False,tracking=True)
    is_cus = fields.Boolean(string='Is Cus',copy=False,tracking=True)
    

