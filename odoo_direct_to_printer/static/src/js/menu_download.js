/** @odoo-module **/

import ActionMenus from "web.ActionMenus";

const Context = require('web.Context');

import { patch } from 'web.utils';

const { useState } = owl;

patch(ActionMenus.prototype, 'odoo_direct_to_printer/static/src/js/menu_download.js', {

    _onItemSelected(ev) {
        ev.stopPropagation();
        const { item } = ev.detail;
        if (item.callback) {
            item.callback([item]);
        } else if (item.action) {
            if ($(ev.currentTarget).find('.odoo_direct_to_printer.show').length){
                this.props.context.print_report_ts = false;
            }else{
                this.props.context.print_report_ts = true;
            }
            this._executeAction(item.action);
        } else if (item.url) {
            // Event has been prevented at its source: we need to redirect manually.
            this.env.services.navigate(item.url);
        }
    },

    async _executeAction(action) {
        let activeIds = this.props.activeIds;
        if (this.props.isDomainSelected) {
            activeIds = await this.rpc({
                model: this.env.action.res_model,
                method: 'search',
                args: [this.props.domain],
                kwargs: {
                    limit: this.env.session.active_ids_limit,
                    context: this.props.context,
                },
            });
        }
        const activeIdsContext = {
            active_id: activeIds[0],
            active_ids: activeIds,
            active_model: this.env.action.res_model,
            print_report_ts: this.props.context.print_report_ts,
        };
        if (this.props.domain) {
            // keep active_domain in context for backward compatibility
            // reasons, and to allow actions to bypass the active_ids_limit
            activeIdsContext.active_domain = this.props.domain;
        }

        const context = new Context(this.props.context, activeIdsContext).eval();
        const result = await this.rpc({
            route: '/web/action/load',
            params: { action_id: action.id, context },
        });
        result.context = new Context(result.context || {}, activeIdsContext)
            .set_eval_context(context);
        result.flags = result.flags || {};
        result.flags.new_window = true;
        this.trigger('do-action', {
            action: result,
            options: {
                on_close: () => this.trigger('reload'),
            },
        });
    },

});

