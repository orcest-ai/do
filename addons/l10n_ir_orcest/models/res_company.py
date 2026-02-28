# Part of Orcest AI. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    l10n_ir_national_id = fields.Char(
        string='شناسه ملی',
        help='شناسه ملی شخص حقوقی (۱۱ رقمی)',
        size=11,
    )
    l10n_ir_economic_code = fields.Char(
        string='کد اقتصادی',
        help='کد اقتصادی شرکت',
        size=12,
    )
    l10n_ir_registration_number = fields.Char(
        string='شماره ثبت',
        help='شماره ثبت شرکت',
    )
    l10n_ir_tax_office = fields.Char(
        string='اداره مالیاتی',
        help='نام اداره مالیاتی',
    )
    l10n_ir_branch_code = fields.Char(
        string='کد شعبه',
        help='کد شعبه (برای کسب و کار چند ملیتی)',
    )
    l10n_ir_company_type = fields.Selection(
        [
            ('private', 'سهامی خاص'),
            ('public', 'سهامی عام'),
            ('limited', 'مسئولیت محدود'),
            ('cooperative', 'تعاونی'),
            ('branch', 'شعبه خارجی'),
            ('representative', 'نمایندگی'),
        ],
        string='نوع شرکت',
        default='private',
    )
    l10n_ir_fiscal_year_type = fields.Selection(
        [
            ('jalali', 'سال هجری شمسی (فروردین تا اسفند)'),
            ('gregorian', 'سال میلادی (ژانویه تا دسامبر)'),
        ],
        string='نوع سال مالی',
        default='jalali',
    )
