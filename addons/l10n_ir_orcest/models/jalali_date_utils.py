# Part of Orcest AI. See LICENSE file for full copyright and licensing details.

"""
تبدیل تاریخ میلادی به هجری شمسی (جلالی) و بالعکس
Gregorian to Jalali (Solar Hijri) date conversion utilities
Based on the Jalaali algorithm by Kazimierz M. Borkowski
"""

import math
from datetime import date, datetime, timedelta


# Persian month names
JALALI_MONTH_NAMES = [
    'فروردین', 'اردیبهشت', 'خرداد',
    'تیر', 'مرداد', 'شهریور',
    'مهر', 'آبان', 'آذر',
    'دی', 'بهمن', 'اسفند',
]

JALALI_MONTH_NAMES_SHORT = [
    'فرو', 'ارد', 'خرد',
    'تیر', 'مرد', 'شهر',
    'مهر', 'آبا', 'آذر',
    'دی', 'بهم', 'اسف',
]

# Persian weekday names (starting from Saturday)
JALALI_WEEKDAY_NAMES = [
    'شنبه', 'یکشنبه', 'دوشنبه', 'سه‌شنبه',
    'چهارشنبه', 'پنجشنبه', 'جمعه',
]

JALALI_WEEKDAY_NAMES_SHORT = [
    'ش', 'ی', 'د', 'س', 'چ', 'پ', 'ج',
]

# Persian digit mapping
PERSIAN_DIGITS = '۰۱۲۳۴۵۶۷۸۹'
LATIN_DIGITS = '0123456789'


def to_persian_digits(text):
    """Convert Latin digits to Persian digits."""
    text = str(text)
    for i, d in enumerate(LATIN_DIGITS):
        text = text.replace(d, PERSIAN_DIGITS[i])
    return text


def to_latin_digits(text):
    """Convert Persian digits to Latin digits."""
    text = str(text)
    for i, d in enumerate(PERSIAN_DIGITS):
        text = text.replace(d, LATIN_DIGITS[i])
    return text


def _jalali_cal(jy):
    """Jalaali calendar helper for calculating leap years and offsets."""
    breaks = [
        -61, 9, 38, 199, 426, 686, 756, 818, 1111, 1181, 1210,
        1635, 2060, 2097, 2192, 2262, 2324, 2394, 2456, 3178
    ]

    bl = len(breaks)
    gy = jy + 621
    leapJ = -14
    jp = breaks[0]

    if jy < jp or jy >= breaks[bl - 1]:
        raise ValueError(f'Invalid Jalaali year: {jy}')

    jump = 0
    for i in range(1, bl):
        jm = breaks[i]
        jump = jm - jp
        if jy < jm:
            break
        leapJ = leapJ + (jump // 33) * 8 + (jump % 33) // 4
        jp = jm

    n = jy - jp
    leapJ = leapJ + (n // 33) * 8 + ((n % 33) + 3) // 4

    if (jump % 33) == 4 and (jump - n) == 4:
        leapJ += 1

    leapG = gy // 4 - ((gy // 100 + 1) * 3 // 4) - 150
    march = 20 + leapJ - leapG

    if (jump - n) < 6:
        n = n - jump + ((jump + 4) // 33) * 33

    leap = ((((n + 1) % 33) - 1) % 4)
    if leap == -1:
        leap = 4

    return leap, gy, march


def is_jalali_leap_year(jy):
    """Check if a Jalaali year is a leap year."""
    leap, _, _ = _jalali_cal(jy)
    return leap == 0


def jalali_month_length(jy, jm):
    """Get the number of days in a Jalaali month."""
    if jm <= 6:
        return 31
    if jm <= 11:
        return 30
    return 30 if is_jalali_leap_year(jy) else 29


def gregorian_to_jalali(gy, gm, gd):
    """Convert Gregorian date to Jalaali (Solar Hijri) date.

    Args:
        gy: Gregorian year
        gm: Gregorian month (1-12)
        gd: Gregorian day (1-31)

    Returns:
        tuple: (jy, jm, jd) - Jalaali year, month, day
    """
    g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]

    gy2 = gy + 1 if gm > 2 else gy
    days = 355666 + (365 * gy) + ((gy2 + 3) // 4) - ((gy2 + 99) // 100) + \
           ((gy2 + 399) // 400) + gd + g_d_m[gm - 1]

    jy = -1595 + (33 * (days // 12053))
    days = days % 12053

    jy += 4 * (days // 1461)
    days %= 1461

    if days > 365:
        jy += (days - 1) // 365
        days = (days - 1) % 365

    if days < 186:
        jm = 1 + (days // 31)
        jd = 1 + (days % 31)
    else:
        jm = 7 + ((days - 186) // 30)
        jd = 1 + ((days - 186) % 30)

    return jy, jm, jd


def jalali_to_gregorian(jy, jm, jd):
    """Convert Jalaali (Solar Hijri) date to Gregorian date.

    Args:
        jy: Jalaali year
        jm: Jalaali month (1-12)
        jd: Jalaali day (1-31)

    Returns:
        tuple: (gy, gm, gd) - Gregorian year, month, day
    """
    leap, gy, march = _jalali_cal(jy)

    g_d_m = [0, 31, 29 if ((gy % 4 == 0 and gy % 100 != 0) or (gy % 400 == 0)) else 28,
             31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    jd_sum = (jm - 1) * 31 if jm <= 7 else ((jm - 7 - 1) * 30 + 186)
    jd_sum += jd

    gy = gy - 621 + jy
    gd = jd_sum + march - 1

    # Adjust for Gregorian calendar
    if gd > 0:
        gm = 3  # March
    else:
        gy -= 1
        gd += 365 + (1 if ((gy % 4 == 0 and gy % 100 != 0) or (gy % 400 == 0)) else 0)
        gm = 1

    while gm < 12 and gd > g_d_m[gm]:
        gd -= g_d_m[gm]
        gm += 1

    return gy, gm, gd


def date_to_jalali(d):
    """Convert a Python date/datetime to Jalaali tuple.

    Args:
        d: date or datetime object

    Returns:
        tuple: (jy, jm, jd) - Jalaali year, month, day
    """
    if isinstance(d, datetime):
        d = d.date()
    return gregorian_to_jalali(d.year, d.month, d.day)


def jalali_to_date(jy, jm, jd):
    """Convert Jalaali date to Python date object.

    Args:
        jy: Jalaali year
        jm: Jalaali month (1-12)
        jd: Jalaali day (1-31)

    Returns:
        date: Python date object
    """
    gy, gm, gd = jalali_to_gregorian(jy, jm, jd)
    return date(gy, gm, gd)


def format_jalali_date(d, fmt='%Y/%m/%d'):
    """Format a Gregorian date/datetime as Jalaali string.

    Args:
        d: date or datetime object
        fmt: format string using strftime conventions

    Returns:
        str: Formatted Jalaali date string with Persian digits
    """
    if not d:
        return ''
    jy, jm, jd = date_to_jalali(d)
    result = fmt.replace('%Y', str(jy).zfill(4))
    result = result.replace('%m', str(jm).zfill(2))
    result = result.replace('%d', str(jd).zfill(2))
    result = result.replace('%B', JALALI_MONTH_NAMES[jm - 1])
    result = result.replace('%b', JALALI_MONTH_NAMES_SHORT[jm - 1])

    if isinstance(d, datetime):
        result = result.replace('%H', str(d.hour).zfill(2))
        result = result.replace('%M', str(d.minute).zfill(2))
        result = result.replace('%S', str(d.second).zfill(2))

    return to_persian_digits(result)


def format_jalali_datetime(dt, fmt='%Y/%m/%d %H:%M:%S'):
    """Format a Gregorian datetime as Jalaali datetime string."""
    return format_jalali_date(dt, fmt)


def parse_jalali_date(s, fmt='%Y/%m/%d'):
    """Parse a Jalaali date string to Python date.

    Args:
        s: Jalaali date string (with Persian or Latin digits)
        fmt: format string

    Returns:
        date: Python date object
    """
    s = to_latin_digits(s)
    # Simple parsing for standard format
    if fmt == '%Y/%m/%d':
        parts = s.split('/')
        if len(parts) == 3:
            jy, jm, jd = int(parts[0]), int(parts[1]), int(parts[2])
            return jalali_to_date(jy, jm, jd)
    raise ValueError(f'Cannot parse Jalaali date: {s}')


def get_jalali_today():
    """Get today's date in Jalaali calendar.

    Returns:
        tuple: (jy, jm, jd)
    """
    return date_to_jalali(date.today())


def get_jalali_week_number(d):
    """Get the week number in Jalaali calendar (week starts on Saturday).

    Args:
        d: date or datetime object

    Returns:
        int: Week number (1-53)
    """
    jy, jm, jd = date_to_jalali(d)
    # First day of Jalali year
    first_day = jalali_to_date(jy, 1, 1)
    # Day of week (0=Saturday, 6=Friday)
    first_day_weekday = (first_day.weekday() + 2) % 7
    # Days from start of year
    day_of_year = (d if isinstance(d, date) else d.date()) - first_day
    days = day_of_year.days
    # Week number
    return (days + first_day_weekday) // 7 + 1


def get_jalali_weekday(d):
    """Get the weekday for a date in Iranian convention.
    Saturday=0, Sunday=1, ..., Friday=6

    Args:
        d: date or datetime object

    Returns:
        int: 0 (Saturday) to 6 (Friday)
    """
    if isinstance(d, datetime):
        d = d.date()
    # Python weekday: Monday=0, Sunday=6
    # Iranian weekday: Saturday=0, Friday=6
    return (d.weekday() + 2) % 7


def get_jalali_quarter(jm):
    """Get the Jalali quarter for a given Jalali month.

    Args:
        jm: Jalaali month (1-12)

    Returns:
        int: Quarter number (1-4)
    """
    return (jm - 1) // 3 + 1


def jalali_year_start(jy):
    """Get the Gregorian date for the start of a Jalaali year (1st Farvardin)."""
    return jalali_to_date(jy, 1, 1)


def jalali_year_end(jy):
    """Get the Gregorian date for the end of a Jalaali year (29/30 Esfand)."""
    last_day = 30 if is_jalali_leap_year(jy) else 29
    return jalali_to_date(jy, 12, last_day)
