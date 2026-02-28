/** @odoo-module **/

/**
 * سرویس هوش مصنوعی RainyModel برای سامانه اورکست
 * RainyModel AI Service for Orcest system (rm.orcest.ai)
 */

import { registry } from "@web/core/registry";
import { session } from "@web/session";
import { rpc } from "@web/core/network/rpc";

function getIrConfig() {
    return session.l10n_ir_orcest || {};
}

export const rainyModelService = {
    dependencies: [],
    start() {
        return {
            /**
             * Check if AI service is enabled
             */
            isEnabled() {
                const config = getIrConfig();
                return config.rainymodel_enabled === true;
            },

            /**
             * Send a chat completion request via the backend
             */
            async chat(messages, model = null) {
                return rpc("/l10n_ir_orcest/ai/chat", { messages, model });
            },

            /**
             * Summarize text using AI
             */
            async summarize(text) {
                return rpc("/l10n_ir_orcest/ai/summarize", { text });
            },

            /**
             * Translate text using AI
             */
            async translate(text, sourceLang = "en", targetLang = "fa") {
                return rpc("/l10n_ir_orcest/ai/translate", {
                    text,
                    source_lang: sourceLang,
                    target_lang: targetLang,
                });
            },

            /**
             * Check AI service health
             */
            async checkHealth() {
                return rpc("/l10n_ir_orcest/ai/health");
            },
        };
    },
};

registry.category("services").add("rainy_model", rainyModelService);
