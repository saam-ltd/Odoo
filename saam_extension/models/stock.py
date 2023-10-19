from odoo import SUPERUSER_ID, _, api, fields, models
import logging
_logger = logging.getLogger(__name__)


class Picking(models.Model):
    _inherit = 'stock.picking'

    CUSTOM_FIELD_STATES = {
    state: [('readonly', False)]
    for state in { 'done', 'cancel'}
    }

    # scheduled_date = fields.Datetime(string="Scheduled Date",states=CUSTOM_FIELD_STATES,copy=False, required=True,
    #     help="Creation date of draft/sent orders,\nConfirmation date of ""confirmed orders.")

    date_done = fields.Datetime(string='Effective Date',states=CUSTOM_FIELD_STATES,copy=False,required=True,
        help="Date at which the transfer has been processed or cancelled.", track_visibility="onchange")
    p_o_ref = fields.Char(string='Custom PO Reference')
    custom_salesperson_id = fields.Many2one('custom.salesperson',string='Custom Salesperson', track_visibility="onchange")

    def _create_backorder(self):
        """ This method is called when the user chose to create a backorder. It will create a new
        picking, the backorder, and move the stock.moves that are not `done` or `cancel` into it.
        """
        backorders = self.env['stock.picking']
        bo_to_assign = self.env['stock.picking']
        for picking in self:
            moves_to_backorder = picking.move_lines.filtered(lambda x: x.state not in ('done', 'cancel'))
            if moves_to_backorder:
                backorder_picking = picking.copy({
                    'name': '/',
                    'move_lines': [],
                    'move_line_ids': [],
                    'backorder_id': picking.id,
                    'p_o_ref':picking.p_o_ref,
                    'custom_salesperson_id':picking.custom_salesperson_id.id,
                })
                picking.message_post(
                    body=_('The backorder <a href=# data-oe-model=stock.picking data-oe-id=%d>%s</a> has been created.') % (
                        backorder_picking.id, backorder_picking.name))
                moves_to_backorder.write({'picking_id': backorder_picking.id})
                moves_to_backorder.move_line_ids.package_level_id.write({'picking_id':backorder_picking.id})
                moves_to_backorder.mapped('move_line_ids').write({'picking_id': backorder_picking.id})
                backorders |= backorder_picking
                if backorder_picking.picking_type_id.reservation_method == 'at_confirm':
                    bo_to_assign |= backorder_picking
        if bo_to_assign:
            bo_to_assign.action_assign()
        return backorders

class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_new_picking_values(self):
        res = super(StockMove, self)._get_new_picking_values()
        res.update({
            'p_o_ref': self.group_id.sale_id.p_o_ref if self.group_id.sale_id and self.group_id.sale_id.p_o_ref else False,
            'custom_salesperson_id': self.group_id.sale_id.custom_salesperson_id.id if self.group_id.sale_id and self.group_id.sale_id.custom_salesperson_id.id else ''
            })
        return res
