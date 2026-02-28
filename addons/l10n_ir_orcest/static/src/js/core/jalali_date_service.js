/** @odoo-module **/

/**
 * سرویس تاریخ جلالی (هجری شمسی) برای سامانه do.orcest.ai
 * Jalali (Solar Hijri) date service for Odoo web client
 *
 * This service patches the localization to support Jalali calendar
 * with Saturday as the first day of the week.
 */

import { registry } from "@web/core/registry";
import { session } from "@web/session";
import { localization } from "@web/core/l10n/localization";
import { formatDate, formatDateTime } from "@web/core/l10n/dates";
import { patch } from "@web/core/utils/patch";

const { DateTime } = luxon;

/**
 * Get l10n_ir_orcest config from session
 */
function getIrConfig() {
    return session.l10n_ir_orcest || {};
}

/**
 * Check if Jalali calendar is active
 */
function isJalaliActive() {
    const config = getIrConfig();
    return config.calendar_type === 'jalali';
}

/**
 * Convert Gregorian date to Jalaali using the global jalaali library
 */
function toJalaali(gy, gm, gd) {
    if (typeof jalaali !== 'undefined') {
        return jalaali.toJalaali(gy, gm, gd);
    }
    // Fallback if library not loaded
    return { jy: gy, jm: gm, jd: gd };
}

/**
 * Convert Jalaali date to Gregorian
 */
function toGregorian(jy, jm, jd) {
    if (typeof jalaali !== 'undefined') {
        return jalaali.toGregorian(jy, jm, jd);
    }
    return { gy: jy, gm: jm, gd: jd };
}

/**
 * Format a Luxon DateTime to Jalali string
 */
function formatJalaliDate(dt, fmt) {
    if (!dt || !dt.isValid) return '';
    const { jy, jm, jd } = toJalaali(dt.year, dt.month, dt.day);

    if (!fmt) {
        fmt = localization.dateFormat || 'yyyy/MM/dd';
    }

    let result = fmt;
    result = result.replace(/yyyy/g, String(jy).padStart(4, '0'));
    result = result.replace(/MM/g, String(jm).padStart(2, '0'));
    result = result.replace(/dd/g, String(jd).padStart(2, '0'));

    // Month names
    if (typeof jalaali !== 'undefined') {
        result = result.replace(/MMMM/g, jalaali.MONTH_NAMES[jm - 1]);
        result = result.replace(/MMM/g, jalaali.MONTH_NAMES_SHORT[jm - 1]);
    }

    // Time parts from original DateTime
    result = result.replace(/HH/g, String(dt.hour).padStart(2, '0'));
    result = result.replace(/mm/g, String(dt.minute).padStart(2, '0'));
    result = result.replace(/ss/g, String(dt.second).padStart(2, '0'));

    // Convert to Persian digits if configured
    const config = getIrConfig();
    if (config.use_persian_digits && typeof jalaali !== 'undefined') {
        result = jalaali.toPersianDigits(result);
    }

    return result;
}

/**
 * Format a Luxon DateTime to Jalali datetime string
 */
function formatJalaliDateTime(dt, fmt) {
    if (!fmt) {
        fmt = localization.dateTimeFormat || 'yyyy/MM/dd HH:mm:ss';
    }
    return formatJalaliDate(dt, fmt);
}

/**
 * Get Jalali month info for a given Gregorian DateTime
 */
function getJalaliMonthInfo(dt) {
    const { jy, jm, jd } = toJalaali(dt.year, dt.month, dt.day);
    const daysInMonth = typeof jalaali !== 'undefined'
        ? jalaali.jalaaliMonthLength(jy, jm)
        : 30;

    // First day of Jalali month in Gregorian
    const { gy, gm, gd } = toGregorian(jy, jm, 1);
    const firstDayGreg = DateTime.local(gy, gm, gd);

    // Get weekday of first day (Saturday = 0)
    const firstDayWeekday = (firstDayGreg.weekday + 1) % 7; // Luxon: 1=Mon, 7=Sun -> Saturday=0

    return {
        jy, jm, jd,
        daysInMonth,
        firstDayGreg,
        firstDayWeekday,
        monthName: typeof jalaali !== 'undefined' ? jalaali.MONTH_NAMES[jm - 1] : '',
        monthNameShort: typeof jalaali !== 'undefined' ? jalaali.MONTH_NAMES_SHORT[jm - 1] : '',
    };
}

/**
 * Jalali Date Service - provides Jalali date conversion globally
 */
export const jalaliDateService = {
    dependencies: [],
    start() {
        return {
            isActive: isJalaliActive,
            toJalaali,
            toGregorian,
            formatJalaliDate,
            formatJalaliDateTime,
            getJalaliMonthInfo,
            getConfig: getIrConfig,
        };
    },
};

registry.category("services").add("jalali_date", jalaliDateService);

// Export utilities for use in other modules
export {
    isJalaliActive,
    toJalaali,
    toGregorian,
    formatJalaliDate,
    formatJalaliDateTime,
    getJalaliMonthInfo,
    getIrConfig,
};
