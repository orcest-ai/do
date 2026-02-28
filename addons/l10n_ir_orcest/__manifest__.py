# Part of Orcest AI. See LICENSE file for full copyright and licensing details.
{
    'name': 'ایران - بومی‌سازی اورکست',
    'version': '19.0.1.0.0',
    'category': 'Accounting/Localizations/Account Charts',
    'summary': 'بومی‌سازی کامل سامانه اورکست برای ایران - تقویم جلالی، حسابداری ایرانی، راست‌چین',
    'description': """
بومی‌سازی کامل سامانه do.orcest.ai برای ایران
=====================================================

این ماژول شامل موارد زیر است:

* تقویم هجری شمسی (جلالی) با شنبه به عنوان اولین روز هفته
* ساعت و منطقه زمانی ایران (Asia/Tehran)
* راست‌چین (RTL) کامل رابط کاربری
* زبان فارسی با ترجمه‌های کامل
* کد حساب‌های ایرانی مطابق استاندارد حسابداری ایران
* پشتیبانی از چند ارز (ریال، تومان، دلار، یورو و ...)
* محاسبه بهای تمام‌شده و EBITDA به روش ایرانی
* یکپارچه‌سازی با SSO سازمانی (login.orcest.ai)
* یکپارچه‌سازی با هوش مصنوعی RainyModel (rm.orcest.ai)
* فاکتور و گزارش‌های فارسی
    """,
    'author': 'Orcest AI',
    'website': 'https://do.orcest.ai',
    'countries': ['ir'],
    'depends': [
        'account',
        'auth_oauth',
        'base',
        'web',
        'calendar',
        'mail',
        'base_setup',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/l10n_ir_orcest_data.xml',
        'data/res_country_data.xml',
        'data/account_chart_template.xml',
        'data/account_tax_data.xml',
        'data/auth_oauth_data.xml',
        'data/ir_cron_data.xml',
        'views/res_config_settings_views.xml',
        'views/account_move_views.xml',
        'views/webclient_templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'l10n_ir_orcest/static/lib/jalaali.js',
            'l10n_ir_orcest/static/src/js/core/jalali_date_service.js',
            'l10n_ir_orcest/static/src/js/core/jalali_datetime_picker.js',
            'l10n_ir_orcest/static/src/js/core/rtl_service.js',
            'l10n_ir_orcest/static/src/js/calendar/jalali_calendar_model.js',
            'l10n_ir_orcest/static/src/js/ai/rainymodel_service.js',
            'l10n_ir_orcest/static/src/css/rtl_override.scss',
            'l10n_ir_orcest/static/src/css/persian_fonts.scss',
            'l10n_ir_orcest/static/src/xml/jalali_templates.xml',
        ],
        'web.assets_frontend': [
            'l10n_ir_orcest/static/lib/jalaali.js',
            'l10n_ir_orcest/static/src/css/rtl_override.scss',
            'l10n_ir_orcest/static/src/css/persian_fonts.scss',
        ],
    },
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'post_init_hook': '_l10n_ir_orcest_post_init',
}
