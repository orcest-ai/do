# Part of Orcest AI. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # --- تقویم و زبان ---
    l10n_ir_calendar_type = fields.Selection(
        [('jalali', 'هجری شمسی (جلالی)'), ('gregorian', 'میلادی')],
        string='نوع تقویم',
        config_parameter='l10n_ir_orcest.calendar_type',
        default='jalali',
    )
    l10n_ir_timezone = fields.Selection(
        [('Asia/Tehran', 'ایران (تهران)')],
        string='منطقه زمانی',
        config_parameter='l10n_ir_orcest.timezone',
        default='Asia/Tehran',
    )
    l10n_ir_first_day_of_week = fields.Selection(
        [('6', 'شنبه'), ('0', 'دوشنبه'), ('7', 'یکشنبه')],
        string='اولین روز هفته',
        config_parameter='l10n_ir_orcest.first_day_of_week',
        default='6',
    )
    l10n_ir_use_persian_digits = fields.Boolean(
        string='استفاده از اعداد فارسی',
        config_parameter='l10n_ir_orcest.use_persian_digits',
        default=True,
    )

    # --- SSO سازمانی ---
    l10n_ir_sso_enabled = fields.Boolean(
        string='فعال‌سازی SSO سازمانی',
        config_parameter='l10n_ir_orcest.sso_enabled',
        default=False,
    )
    l10n_ir_sso_url = fields.Char(
        string='آدرس سرور SSO',
        config_parameter='l10n_ir_orcest.sso_url',
        default='https://login.orcest.ai',
    )
    l10n_ir_sso_client_id = fields.Char(
        string='شناسه کلاینت SSO',
        config_parameter='l10n_ir_orcest.sso_client_id',
        default='do-orcest',
    )
    l10n_ir_sso_client_secret = fields.Char(
        string='رمز کلاینت SSO',
        config_parameter='l10n_ir_orcest.sso_client_secret',
    )
    l10n_ir_sso_only_login = fields.Boolean(
        string='فقط ورود از طریق SSO',
        help='فقط کاربران login.orcest.ai اجازه ورود دارند',
        config_parameter='l10n_ir_orcest.sso_only_login',
        default=True,
    )

    # --- هوش مصنوعی RainyModel ---
    l10n_ir_rainymodel_enabled = fields.Boolean(
        string='فعال‌سازی هوش مصنوعی',
        config_parameter='l10n_ir_orcest.rainymodel_enabled',
        default=True,
    )
    l10n_ir_rainymodel_url = fields.Char(
        string='آدرس RainyModel API',
        config_parameter='l10n_ir_orcest.rainymodel_url',
        default='https://rm.orcest.ai/v1',
    )
    l10n_ir_rainymodel_api_key = fields.Char(
        string='کلید API هوش مصنوعی',
        config_parameter='l10n_ir_orcest.rainymodel_api_key',
    )
    l10n_ir_rainymodel_model = fields.Selection(
        [
            ('rainymodel/auto', 'خودکار (پیشنهادی)'),
            ('rainymodel/chat', 'گفتگو'),
            ('rainymodel/code', 'کدنویسی'),
            ('rainymodel/agent', 'عامل هوشمند'),
        ],
        string='مدل هوش مصنوعی',
        config_parameter='l10n_ir_orcest.rainymodel_model',
        default='rainymodel/auto',
    )

    # --- حسابداری ایرانی ---
    l10n_ir_accounting_standard = fields.Selection(
        [
            ('iranian', 'استاندارد حسابداری ایران'),
            ('ifrs', 'استانداردهای بین‌المللی (IFRS)'),
        ],
        string='استاندارد حسابداری',
        config_parameter='l10n_ir_orcest.accounting_standard',
        default='iranian',
    )
    l10n_ir_default_currency = fields.Selection(
        [
            ('IRR', 'ریال ایران (IRR)'),
            ('IRT', 'تومان ایران (IRT)'),
        ],
        string='واحد پول پیش‌فرض',
        config_parameter='l10n_ir_orcest.default_currency',
        default='IRR',
    )
    l10n_ir_multi_currency = fields.Boolean(
        string='پشتیبانی چند ارزی',
        help='فعال‌سازی فاکتور و پرداخت با ارزهای مختلف بین‌المللی',
        config_parameter='l10n_ir_orcest.multi_currency',
        default=True,
    )
    l10n_ir_fiscal_year_start_month = fields.Selection(
        [('1', 'فروردین'), ('4', 'تیر'), ('7', 'مهر'), ('10', 'دی')],
        string='شروع سال مالی',
        config_parameter='l10n_ir_orcest.fiscal_year_start_month',
        default='1',
    )
