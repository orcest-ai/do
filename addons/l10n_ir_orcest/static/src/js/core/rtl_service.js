/** @odoo-module **/

/**
 * سرویس راست‌چین (RTL) برای رابط کاربری فارسی
 * RTL Service for Persian UI - ensures full RTL support across the application
 */

import { registry } from "@web/core/registry";
import { session } from "@web/session";
import { localization } from "@web/core/l10n/localization";

function getIrConfig() {
    return session.l10n_ir_orcest || {};
}

/**
 * RTL Enhancement Service
 * Ensures proper RTL behavior for all components
 */
export const rtlService = {
    dependencies: ["localization"],
    start(env) {
        const config = getIrConfig();

        // Only activate RTL enhancements for Persian localization
        if (localization.direction !== "rtl") {
            return {};
        }

        // Set document direction
        document.documentElement.setAttribute("dir", "rtl");
        document.documentElement.setAttribute("lang", "fa");

        // Add Persian font and RTL class
        document.body.classList.add("o_rtl", "o_lang_fa");

        // Override document title with Persian branding
        const originalTitle = document.title;
        if (originalTitle.includes('Odoo')) {
            document.title = originalTitle.replace('Odoo', 'سامانه اورکست');
        }

        return {
            isRtl: true,
            direction: "rtl",
        };
    },
};

registry.category("services").add("rtl_enhancement", rtlService);
