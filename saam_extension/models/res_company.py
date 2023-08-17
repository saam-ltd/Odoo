from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = 'res.company'

    zero_registration_number = fields.Char(string="Zero Registration Number")
    uid = fields.Char(string="Govt. UID")
    brn = fields.Char(string="BRN")
