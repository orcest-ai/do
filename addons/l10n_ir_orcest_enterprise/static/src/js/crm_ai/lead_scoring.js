/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { FormController } from "@web/views/form/form_controller";
import { useService } from "@web/core/utils/hooks";

/**
 * امتیازدهی هوشمند سرنخ‌های CRM
 * AI-powered Lead Scoring for CRM
 */

// Extend CRM form to show AI score indicator
patch(FormController.prototype, {
    setup() {
        super.setup(...arguments);
        this.notification = useService("notification");
    },

    async onRecordSaved(record) {
        await super.onRecordSaved(...arguments);

        // Auto-score CRM leads if AI scoring is enabled
        if (record.resModel === "crm.lead" && record.data.l10n_ir_ai_score === 0) {
            const config = this.env.services.rpc;
            try {
                const result = await config("/web/dataset/call_kw", {
                    model: "crm.lead",
                    method: "action_ai_score",
                    args: [[record.resId]],
                    kwargs: {},
                });
                if (result) {
                    this.notification.add(
                        "امتیازدهی هوشمند سرنخ انجام شد",
                        { type: "success" }
                    );
                }
            } catch (e) {
                // AI scoring is optional, don't block on failure
                console.warn("Auto AI scoring skipped:", e);
            }
        }
    },
});
