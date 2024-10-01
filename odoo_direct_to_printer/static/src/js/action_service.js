/** @odoo-module **/

import {registry} from "@web/core/registry";
const {_t} = require('web.core');

function _getReportUrl(action, type) {
    let url = `/report/${type}/${action.report_name}`;
    const actionContext = action.context || {};
    if (action.data && JSON.stringify(action.data) !== "{}") {
        const options = encodeURIComponent(JSON.stringify(action.data));
        const context = encodeURIComponent(JSON.stringify(actionContext));
        url += `?options=${options}&context=${context}`;
    } else {
        if (actionContext.active_ids) {
            url += `/${actionContext.active_ids.join(",")}`;
        }
        if (type === "html") {
            const context = encodeURIComponent(JSON.stringify(env.services.user.context));
            url += `?context=${context}`;
        }
    }
    return url;
}

function printJobComplete() {
  $.unblockUI();
}


async function _executeReportAction(action, options, env) {
    if (action.context && action.context.print_report_ts) {
        if (action.report_type === "qweb-pdf") {
            if ($.blockUI) {
                // our message needs to appear above the modal dialog
                $.blockUI.defaults.baseZ = 1100;
                $.blockUI.defaults.message = '<div class="openerp oe_blockui_spin_container" style="background-color: transparent;">';
                $.blockUI.defaults.css.border = '0';
                $.blockUI.defaults.css["background-color"] = '';
                var msg = _t("Just one more second, preparing for printing...");
                $.blockUI({
                    'message': '<h2 class="text-white">' +
                        '    <br />' + msg +
                        '</h2>'
                });
                printJS({printable: _getReportUrl(action, "pdf"), type: 'pdf', 'onPrintDialogClose': printJobComplete});
            }
        } else {
            env.services.notification.add('Only support PDF reports', {
                type: "warning",
                sticky: false,
                title: env._t("Unsupported Report Type"),
            });
        }
        return true;
    } else {
        return false;
    }
}

registry
    .category("ir.actions.report handlers")
    .add('print_or_download_report', _executeReportAction);
