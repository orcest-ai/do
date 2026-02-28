/**
 * jalaali.js - Jalaali (Solar Hijri / Persian) calendar conversion
 * Based on Kazimierz M. Borkowski's algorithm
 * Adapted for Odoo 19 / Orcest AI (do.orcest.ai)
 *
 * تبدیل تاریخ میلادی به هجری شمسی (جلالی)
 */

const jalaali = (function () {
    'use strict';

    // Persian month names
    const MONTH_NAMES = [
        'فروردین', 'اردیبهشت', 'خرداد',
        'تیر', 'مرداد', 'شهریور',
        'مهر', 'آبان', 'آذر',
        'دی', 'بهمن', 'اسفند',
    ];

    const MONTH_NAMES_SHORT = [
        'فرو', 'ارد', 'خرد',
        'تیر', 'مرد', 'شهر',
        'مهر', 'آبا', 'آذر',
        'دی', 'بهم', 'اسف',
    ];

    // Persian weekday names (Saturday first)
    const WEEKDAY_NAMES = [
        'شنبه', 'یکشنبه', 'دوشنبه', 'سه‌شنبه',
        'چهارشنبه', 'پنجشنبه', 'جمعه',
    ];

    const WEEKDAY_NAMES_SHORT = ['ش', 'ی', 'د', 'س', 'چ', 'پ', 'ج'];

    const PERSIAN_DIGITS = '۰۱۲۳۴۵۶۷۸۹';

    /**
     * Convert a number to Persian digits string
     */
    function toPersianDigits(num) {
        return String(num).replace(/[0-9]/g, (d) => PERSIAN_DIGITS[parseInt(d)]);
    }

    /**
     * Convert Persian digits to Latin
     */
    function toLatinDigits(str) {
        return String(str).replace(/[۰-۹]/g, (d) => PERSIAN_DIGITS.indexOf(d));
    }

    /**
     * Jalaali calendar helper
     */
    function jalaaliCal(jy) {
        const breaks = [
            -61, 9, 38, 199, 426, 686, 756, 818, 1111, 1181, 1210,
            1635, 2060, 2097, 2192, 2262, 2324, 2394, 2456, 3178
        ];

        const bl = breaks.length;
        const gy = jy + 621;
        let leapJ = -14;
        let jp = breaks[0];
        let jump;

        for (let i = 1; i < bl; i++) {
            const jm = breaks[i];
            jump = jm - jp;
            if (jy < jm) break;
            leapJ += Math.floor(jump / 33) * 8 + Math.floor((jump % 33) / 4);
            jp = jm;
        }

        let n = jy - jp;
        leapJ += Math.floor(n / 33) * 8 + Math.floor((n % 33 + 3) / 4);

        if ((jump % 33) === 4 && (jump - n) === 4) {
            leapJ += 1;
        }

        const leapG = Math.floor(gy / 4) - Math.floor((Math.floor(gy / 100) + 1) * 3 / 4) - 150;
        const march = 20 + leapJ - leapG;

        if ((jump - n) < 6) {
            n = n - jump + Math.floor((jump + 4) / 33) * 33;
        }

        let leap = (((n + 1) % 33) - 1) % 4;
        if (leap === -1) leap = 4;

        return { leap, gy, march };
    }

    /**
     * Check if a Jalaali year is a leap year
     */
    function isLeapJalaaliYear(jy) {
        return jalaaliCal(jy).leap === 0;
    }

    /**
     * Get days in a Jalaali month
     */
    function jalaaliMonthLength(jy, jm) {
        if (jm <= 6) return 31;
        if (jm <= 11) return 30;
        return isLeapJalaaliYear(jy) ? 30 : 29;
    }

    /**
     * Convert Gregorian date to Jalaali
     */
    function toJalaali(gy, gm, gd) {
        const gdm = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334];
        let gy2 = (gm > 2) ? (gy + 1) : gy;
        let days = 355666 + (365 * gy) + Math.floor((gy2 + 3) / 4) -
            Math.floor((gy2 + 99) / 100) + Math.floor((gy2 + 399) / 400) + gd + gdm[gm - 1];

        let jy = -1595 + (33 * Math.floor(days / 12053));
        days = days % 12053;

        jy += 4 * Math.floor(days / 1461);
        days %= 1461;

        if (days > 365) {
            jy += Math.floor((days - 1) / 365);
            days = (days - 1) % 365;
        }

        let jm, jd;
        if (days < 186) {
            jm = 1 + Math.floor(days / 31);
            jd = 1 + (days % 31);
        } else {
            jm = 7 + Math.floor((days - 186) / 30);
            jd = 1 + ((days - 186) % 30);
        }

        return { jy, jm, jd };
    }

    /**
     * Convert Jalaali date to Gregorian
     */
    function toGregorian(jy, jm, jd) {
        const { leap, gy: gYear, march } = jalaaliCal(jy);

        let gy = jy + 621;
        const isLeapG = (gy % 4 === 0 && gy % 100 !== 0) || (gy % 400 === 0);
        const gdm = [0, 31, isLeapG ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];

        let jdSum;
        if (jm <= 7) {
            jdSum = (jm - 1) * 31;
        } else {
            jdSum = (jm - 7 - 1) * 30 + 186;
        }
        jdSum += jd;

        let gd = jdSum + march - 1;
        let gm;

        if (gd > 0) {
            gm = 3;
        } else {
            gy -= 1;
            const isLeapPrev = (gy % 4 === 0 && gy % 100 !== 0) || (gy % 400 === 0);
            gd += 365 + (isLeapPrev ? 1 : 0);
            gm = 1;
            gdm[2] = isLeapPrev ? 29 : 28;
        }

        while (gm < 12 && gd > gdm[gm]) {
            gd -= gdm[gm];
            gm++;
        }

        return { gy, gm, gd };
    }

    /**
     * Convert a JavaScript Date to Jalaali
     */
    function dateToJalaali(date) {
        return toJalaali(date.getFullYear(), date.getMonth() + 1, date.getDate());
    }

    /**
     * Convert Jalaali date to JavaScript Date
     */
    function jalaaliToDate(jy, jm, jd) {
        const { gy, gm, gd } = toGregorian(jy, jm, jd);
        return new Date(gy, gm - 1, gd);
    }

    /**
     * Format a Jalaali date
     */
    function formatJalaali(jy, jm, jd, fmt = 'YYYY/MM/DD') {
        let result = fmt;
        result = result.replace('YYYY', String(jy).padStart(4, '0'));
        result = result.replace('MM', String(jm).padStart(2, '0'));
        result = result.replace('DD', String(jd).padStart(2, '0'));
        result = result.replace('MMMM', MONTH_NAMES[jm - 1]);
        result = result.replace('MMM', MONTH_NAMES_SHORT[jm - 1]);
        return result;
    }

    /**
     * Get the Iranian weekday (0=Saturday, 6=Friday)
     */
    function getIranianWeekday(date) {
        // JS: 0=Sunday, 6=Saturday
        return (date.getDay() + 1) % 7;
    }

    /**
     * Get week number in Jalaali calendar (week starts Saturday)
     */
    function getJalaaliWeekNumber(date) {
        const { jy, jm, jd } = dateToJalaali(date);
        const firstDay = jalaaliToDate(jy, 1, 1);
        const firstDayWeekday = getIranianWeekday(firstDay);
        const dayOfYear = Math.floor((date - firstDay) / 86400000);
        return Math.floor((dayOfYear + firstDayWeekday) / 7) + 1;
    }

    /**
     * Get today's Jalaali date
     */
    function today() {
        return dateToJalaali(new Date());
    }

    return {
        toJalaali,
        toGregorian,
        dateToJalaali,
        jalaaliToDate,
        isLeapJalaaliYear,
        jalaaliMonthLength,
        formatJalaali,
        getIranianWeekday,
        getJalaaliWeekNumber,
        today,
        toPersianDigits,
        toLatinDigits,
        MONTH_NAMES,
        MONTH_NAMES_SHORT,
        WEEKDAY_NAMES,
        WEEKDAY_NAMES_SHORT,
        PERSIAN_DIGITS,
    };
})();

// Make available globally and as ES module
if (typeof globalThis !== 'undefined') {
    globalThis.jalaali = jalaali;
}
if (typeof window !== 'undefined') {
    window.jalaali = jalaali;
}
