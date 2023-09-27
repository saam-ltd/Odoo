from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    p_o_ref = fields.Char(string='Custom PO Reference')
    