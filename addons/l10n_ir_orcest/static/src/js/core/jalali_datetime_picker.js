/** @odoo-module **/

/**
 * بازنویسی انتخابگر تاریخ برای پشتیبانی از تقویم جلالی
 * Override DateTimePicker to support Jalali calendar with Saturday as first day of week
 */

import { DateTimePicker } from "@web/core/datetime/datetime_picker";
import { localization } from "@web/core/l10n/localization";
import { patch } from "@web/core/utils/patch";
import { session } from "@web/session";
import { _t } from "@web/core/l10n/translation";

const { DateTime } = luxon;

function getIrConfig() {
    return session.l10n_ir_orcest || {};
}

function isJalaliActive() {
    return getIrConfig().calendar_type === 'jalali';
}

/**
 * Patch DateTimePicker to support Jalali calendar
 */
patch(DateTimePicker.prototype, {
    setup() {
        super.setup();
        this._isJalali = isJalaliActive();
    },

    onWillRender() {
        super.onWillRender();

        if (!this._isJalali || typeof jalaali === 'undefined') {
            return;
        }

        // Override titles with Jalali month/year
        if (this.state.focusDate && this.state.precision === 'days') {
            const dt = this.state.focusDate;
            const { jy, jm } = jalaali.toJalaali(dt.year, dt.month, dt.day);
            const config = getIrConfig();
            let titleText = `${jalaali.MONTH_NAMES[jm - 1]} ${jy}`;
            if (config.use_persian_digits) {
                titleText = `${jalaali.MONTH_NAMES[jm - 1]} ${jalaali.toPersianDigits(jy)}`;
            }
            this.title = titleText;
        }

        // Override month items with Jalali names
        if (this.state.precision === 'months' && this.items) {
            for (const item of this.items) {
                if (item.range && item.range[0]) {
                    const dt = item.range[0];
                    const { jm } = jalaali.toJalaali(dt.year, dt.month, dt.day);
                    item.label = jalaali.MONTH_NAMES_SHORT[jm - 1];
                }
            }
        }

        // Override year title with Jalali year
        if (this.state.focusDate && this.state.precision === 'months') {
            const dt = this.state.focusDate;
            const { jy } = jalaali.toJalaali(dt.year, dt.month, dt.day);
            const config = getIrConfig();
            this.title = config.use_persian_digits
                ? jalaali.toPersianDigits(jy)
                : String(jy);
        }

        // Override day labels with Jalali day numbers
        if (this.state.precision === 'days' && this.items) {
            for (const monthItem of this.items) {
                if (!monthItem.weeks) continue;

                // Override days of week labels for Saturday-first
                if (monthItem.daysOfWeek && typeof jalaali !== 'undefined') {
                    const hasWeekNum = monthItem.daysOfWeek.length > 7;
                    const startIdx = hasWeekNum ? 1 : 0;

                    // Reorder weekday headers: Saturday first
                    const weekdayOrder = [5, 6, 0, 1, 2, 3, 4]; // Sat, Sun, Mon, ...
                    const newDaysOfWeek = hasWeekNum
                        ? [monthItem.daysOfWeek[0]]
                        : [];

                    for (const wi of weekdayOrder) {
                        newDaysOfWeek.push([
                            jalaali.WEEKDAY_NAMES_SHORT[wi === 5 ? 0 : wi === 6 ? 1 : wi + 2],
                            jalaali.WEEKDAY_NAMES[wi === 5 ? 0 : wi === 6 ? 1 : wi + 2],
                            jalaali.WEEKDAY_NAMES_SHORT[wi === 5 ? 0 : wi === 6 ? 1 : wi + 2],
                        ]);
                    }
                    monthItem.daysOfWeek = newDaysOfWeek;
                }

                // Override day labels with Jalali day numbers
                for (const week of monthItem.weeks) {
                    for (const day of week.days) {
                        if (day.range && day.range[0]) {
                            const dt = day.range[0];
                            const { jd } = jalaali.toJalaali(dt.year, dt.month, dt.day);
                            const config = getIrConfig();
                            day.label = config.use_persian_digits
                                ? jalaali.toPersianDigits(jd)
                                : String(jd);
                        }
                    }
                }

                // Recalculate Jalali week numbers
                for (const week of monthItem.weeks) {
                    if (week.days && week.days[3] && week.days[3].range) {
                        const midWeekDt = week.days[3].range[0];
                        const midWeekDate = new Date(midWeekDt.year, midWeekDt.month - 1, midWeekDt.day);
                        week.number = jalaali.getJalaaliWeekNumber(midWeekDate);
                    }
                }
            }
        }
    },
});
