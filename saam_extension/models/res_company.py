from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = 'res.company'

    zero_registration_number = fields.Char(string="Zero Registration Number", tracking=True)
    uid = fields.Char(string="Govt. UID", tracking=True)
    brn = fields.Char(string="BRN", tracking=True)
