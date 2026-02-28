/** @odoo-module **/

/**
 * مدل تقویم جلالی - بازنویسی تقویم Odoo برای پشتیبانی از هجری شمسی
 * Jalali Calendar Model - Override Odoo calendar for Solar Hijri support
 */

import { CalendarModel } from "@web/views/calendar/calendar_model";
import { patch } from "@web/core/utils/patch";
import { session } from "@web/session";

const { DateTime } = luxon;

function getIrConfig() {
    return session.l10n_ir_orcest || {};
}

function isJalaliActive() {
    return getIrConfig().calendar_type === 'jalali';
}

patch(CalendarModel.prototype, {
    setup(params, services) {
        super.setup(params, services);
        this._isJalali = isJalaliActive();
    },

    /**
     * Override to use Saturday as first day of week for Jalali calendar
     */
    get firstDayOfWeek() {
        if (this._isJalali) {
            return 6; // Saturday (Luxon: 6 = Saturday)
        }
        return super.firstDayOfWeek;
    },

    /**
     * Override date range title to show Jalali dates
     */
    get rangeTitle() {
        if (!this._isJalali || typeof jalaali === 'undefined') {
            return super.rangeTitle;
        }

        const { startDate, endDate, scale } = this.meta;
        if (!startDate) return '';

        const config = getIrConfig();
        const usePersian = config.use_persian_digits;

        const startJ = jalaali.toJalaali(startDate.year, startDate.month, startDate.day);

        if (scale === 'day') {
            const dayName = jalaali.WEEKDAY_NAMES[jalaali.getIranianWeekday(
                new Date(startDate.year, startDate.month - 1, startDate.day)
            )];
            let dateStr = `${dayName} ${startJ.jd} ${jalaali.MONTH_NAMES[startJ.jm - 1]} ${startJ.jy}`;
            return usePersian ? jalaali.toPersianDigits(dateStr) : dateStr;
        }

        if (scale === 'week') {
            const endJ = jalaali.toJalaali(endDate.year, endDate.month, endDate.day);
            if (startJ.jm === endJ.jm) {
                let dateStr = `${startJ.jd} - ${endJ.jd} ${jalaali.MONTH_NAMES[startJ.jm - 1]} ${startJ.jy}`;
                return usePersian ? jalaali.toPersianDigits(dateStr) : dateStr;
            }
            let dateStr = `${startJ.jd} ${jalaali.MONTH_NAMES_SHORT[startJ.jm - 1]} - ${endJ.jd} ${jalaali.MONTH_NAMES_SHORT[endJ.jm - 1]} ${startJ.jy}`;
            return usePersian ? jalaali.toPersianDigits(dateStr) : dateStr;
        }

        if (scale === 'month') {
            let dateStr = `${jalaali.MONTH_NAMES[startJ.jm - 1]} ${startJ.jy}`;
            return usePersian ? jalaali.toPersianDigits(dateStr) : dateStr;
        }

        if (scale === 'year') {
            let dateStr = String(startJ.jy);
            return usePersian ? jalaali.toPersianDigits(dateStr) : dateStr;
        }

        return super.rangeTitle;
    },
});
