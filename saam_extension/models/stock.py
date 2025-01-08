from odoo import SUPERUSER_ID, _, api, fields, models
import logging
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError



class Picking(models.Model):
    _inherit = 'stock.picking'

    # CUSTOM_FIELD_STATES = {
    # state: [('readonly', False)]
    # for state in { 'done', 'cancel'}
    # }

    # scheduled_date = fields.Datetime(string="Scheduled Date",states=CUSTOM_FIELD_STATES,copy=False, required=True,
    #     help="Creation date of draft/sent orders,\nConfirmation date of ""confirmed orders.")

    # date_done = fields.Datetime(string='Effective Date',states=CUSTOM_FIELD_STATES,copy=False,
    #     help="Date at which the transfer has been processed or cancelled.", track_visibility="onchange")
    p_o_ref = fields.Char(string='Custom PO Reference')
    custom_salesperson_id = fields.Many2one('custom.salesperson',string='Custom Salesperson', track_visibility="onchange")
    # logistic_duration_id =  fields.Many2one('customer.logistic.timing',string='Logistic Timing',related='partner_id.customer_logistic_id',tracking=2,copy=False)
    customer_category_id =  fields.Many2one('customer.catgeory',string='Customer Category',related='partner_id.customer_category_id',tracking=2,copy=False)
    customer_remarks =  fields.Text(string='Customer Remarks',related='partner_id.cus_remarks', tracking=2,copy=False)

    is_date_updated = fields.Boolean(string='Is Date Updated')
    code = fields.Selection(related='picking_type_id.code', string='Picking Type - Code', store=True)



    del_schedule_status = fields.Selection([
                                                ('not_scheduled', 'Not Scheduled'),
                                                ('scheduled', 'Scheduled'),
                                                ('re_scheduled', 'Re-Scheduled'),
                                                ('done', 'Done'),
                                                ('scanned', 'Scanned'),
                                            ], string='Delivery Schedule Status',copy=False,default='not_scheduled',readonly=True,tracking=True)

    def button_validate(self):
        if self.picking_type_id.code == 'outgoing' and self.state == 'assigned' and self.del_schedule_status not in ['scheduled','re_scheduled']:
            raise UserError(_("Kinldy Schedule the delivery.."))
        res = super(Picking, self).button_validate()
        return res

    def _set_scheduled_date(self):
        for picking in self:
            # if picking.state in ('done', 'cancel'):
            #     raise UserError(_("You cannot change the Scheduled Date on a done or cancelled transfer."))
            picking.move_lines.write({'date': picking.scheduled_date})
            if picking.picking_type_id.code == 'outgoing':
                if picking.state == 'assigned':
                    if picking.del_schedule_status == 'not_scheduled':
                        picking.del_schedule_status = 'scheduled'
                    elif picking.del_schedule_status == 'scheduled':
                        picking.del_schedule_status = 're_scheduled'
                    elif picking.del_schedule_status == 're_scheduled':
                        picking.del_schedule_status = 're_scheduled'
                elif picking.state == 'cancel':
                     picking.del_schedule_status = 'not_scheduled'

    def _action_done(self):
        """Call `_action_done` on the `stock.move` of the `stock.picking` in `self`.
        This method makes sure every `stock.move.line` is linked to a `stock.move` by either
        linking them to an existing one or a newly created one.

        If the context key `cancel_backorder` is present, backorders won't be created.

        :return: True
        :rtype: bool
        """
        self._check_company()

        todo_moves = self.mapped('move_lines').filtered(lambda self: self.state in ['draft', 'waiting', 'partially_available', 'assigned', 'confirmed'])
        for picking in self:
            if picking.owner_id:
                picking.move_lines.write({'restrict_partner_id': picking.owner_id.id})
                picking.move_line_ids.write({'owner_id': picking.owner_id.id})
        todo_moves._action_done(cancel_backorder=self.env.context.get('cancel_backorder'))
        self.write({'date_done': fields.Datetime.now(), 'priority': '0'})
        
        if self and self.picking_type_id.code == 'outgoing' and self.state == 'done':
            self.write({'del_schedule_status':'done'})

        # if incoming moves make other confirmed/partially_available moves available, assign them
        done_incoming_moves = self.filtered(lambda p: p.picking_type_id.code == 'incoming').move_lines.filtered(lambda m: m.state == 'done')
        done_incoming_moves._trigger_assign()

        self._send_confirmation_email()
        return True

    def action_update_del_status_scan(self):
        if self.state == 'done':
            self.del_schedule_status = 'scanned'

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
                    # 'logistic_duration_id':picking.logistic_duration_id.id,
                    'customer_category_id':picking.customer_category_id.id,
                    'customer_remarks':picking.customer_remarks,
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

    # def action_change_date(self):
    #     count=0
    #     for i in self.search([('picking_type_id.code','=','outgoing'),('is_date_updated','=',False)]):
    #         count+=1
    #         _logger.info("count ==============================================> " + str(count))
    #         for move in i.move_ids_without_package:
    #             move.date = i.date_done
    #             move.date_deadline = i.date_done

    #             update_sql = """UPDATE stock_move SET create_date = %s WHERE id = %s"""
    #             formatted_string = i.date_done.strftime("%Y-%m-%d %H:%M:%S")
    #             self.env.cr.execute(update_sql, (formatted_string,move.id,))

    #             for journal_entry in move.account_move_ids:
    #                 if journal_entry.state == 'posted':
    #                     journal_entry.button_draft()
    #                     journal_entry.name = ''
    #                     journal_entry.date = i.date_done


    #                     update_sql = """UPDATE account_move SET create_date = %s WHERE id = %s"""
    #                     formatted_string = i.date_done.strftime("%Y-%m-%d %H:%M:%S")
    #                     self.env.cr.execute(update_sql, (formatted_string,journal_entry.id,))


    #                     for journal_items in journal_entry.line_ids:
    #                         # journal_items.date = i.date_done

    #                         update_sql = """UPDATE account_move_line SET create_date = %s WHERE id = %s"""
    #                         formatted_string = i.date_done.strftime("%Y-%m-%d %H:%M:%S")
    #                         self.env.cr.execute(update_sql, (formatted_string,journal_items.id,))

    #                     journal_entry.action_post()

    #             for stock_layer in move.stock_valuation_layer_ids:
    #                 update_sql = """UPDATE stock_valuation_layer SET create_date = %s WHERE id = %s"""
    #                 formatted_string = i.date_done.strftime("%Y-%m-%d %H:%M:%S")
    #                 self.env.cr.execute(update_sql, (formatted_string,stock_layer.id,))

    #         for moveline in i.move_line_ids_without_package:
    #             moveline.date = i.date_done

    #             update_sql = """UPDATE stock_move_line SET create_date = %s WHERE id = %s"""
    #             formatted_string = i.date_done.strftime("%Y-%m-%d %H:%M:%S")
    #             self.env.cr.execute(update_sql, (formatted_string,moveline.id,))

    #         i.is_date_updated = True
    #         self.env.cr.commit()

    # def action_change_inventory_dates(self): 
    #     count=0
    #     for move in self.env['stock.move'].search([('name','=','Inventory Adjustment - 2023-10-21')]):
    #         count+=1
    #         _logger.info("count ==============================================> " + str(count))
    #         move.date = '2023-07-01 00:00:00'

    #         update_sql = """UPDATE stock_move SET create_date ='2023-07-01 00:00:00' WHERE id = %s"""

    #         self.env.cr.execute(update_sql, (move.id,))



    # def action_change_inventory_dates_product_move(self): 
    #     count=0
    #     for move_line in self.env['stock.move.line'].search([('reference','=','Inventory Adjustment - 2023-10-21')]):
    #         count+=1
    #         _logger.info("count ==============================================> " + str(count))
    #         move_line.date = '2023-07-01 00:00:00'

    #         update_sql = """UPDATE stock_move_line SET create_date ='2023-07-01 00:00:00' WHERE id = %s"""

    #         self.env.cr.execute(update_sql, (move_line.id,))

    # def action_change_inventory_stock_value(self): 
    #     count=0
    #     for layer in self.env['stock.valuation.layer'].search([('create_date','>','2023-10-21 00:00:00'),('create_date','<','2023-10-21 23:59:00')]):
    #         count+=1
    #         _logger.info("count ==============================================> " + str(count))
    #         update_sql = """UPDATE stock_valuation_layer SET create_date = '2023-07-01 00:00:00' WHERE id = %s"""
    #         self.env.cr.execute(update_sql, (layer.id,))

    # def update_inventory_valuation_journal_entry(self):
    #     count=0
    #     for entry in self.env['account.move'].search([('journal_id','=',6),('create_date','>','2023-10-01 00:00:00'),('create_date','<','2023-10-31 23:59:59')]):
    #         count+=1
    #         _logger.info("count ==============================================> " + str(count))
    #         update_sql = """UPDATE account_move SET create_date = '2023-07-01 00:00:00' WHERE id = %s"""
    #         self.env.cr.execute(update_sql, (entry.id,))


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_new_picking_values(self):
        res = super(StockMove, self)._get_new_picking_values()
        res.update({
            'p_o_ref': self.group_id.sale_id.p_o_ref if self.group_id.sale_id and self.group_id.sale_id.p_o_ref else False,
            'custom_salesperson_id': self.group_id.sale_id.custom_salesperson_id.id if self.group_id.sale_id and self.group_id.sale_id.custom_salesperson_id.id else '',
            # 'logistic_duration_id': self.group_id.sale_id.logistic_duration_id.id if self.group_id.sale_id and self.group_id.sale_id.logistic_duration_id.id else '',
            'customer_category_id': self.group_id.sale_id.customer_category_id.id if self.group_id.sale_id and self.group_id.sale_id.customer_category_id.id else '',
            'customer_remarks': self.group_id.sale_id.customer_remarks if self.group_id.sale_id and self.group_id.sale_id.customer_remarks else False
            })
        return res
