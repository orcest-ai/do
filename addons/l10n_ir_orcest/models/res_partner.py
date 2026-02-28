# Part of Orcest AI. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    l10n_ir_national_code = fields.Char(
        string='کد ملی',
        help='کد ملی شخص حقیقی (۱۰ رقمی)',
        size=10,
    )
    l10n_ir_national_id = fields.Char(
        string='شناسه ملی',
        help='شناسه ملی شخص حقوقی (۱۱ رقمی)',
        size=11,
    )
    l10n_ir_economic_code = fields.Char(
        string='کد اقتصادی',
        size=12,
    )
    l10n_ir_postal_code = fields.Char(
        string='کد پستی',
        help='کد پستی ۱۰ رقمی',
        size=10,
    )
    l10n_ir_province = fields.Selection(
        [
            ('tehran', 'تهران'), ('isfahan', 'اصفهان'), ('fars', 'فارس'),
            ('khorasan_razavi', 'خراسان رضوی'), ('east_azarbaijan', 'آذربایجان شرقی'),
            ('west_azarbaijan', 'آذربایجان غربی'), ('khuzestan', 'خوزستان'),
            ('mazandaran', 'مازندران'), ('alborz', 'البرز'), ('gilan', 'گیلان'),
            ('kermanshah', 'کرمانشاه'), ('kerman', 'کرمان'), ('golestan', 'گلستان'),
            ('hormozgan', 'هرمزگان'), ('hamadan', 'همدان'), ('markazi', 'مرکزی'),
            ('bushehr', 'بوشهر'), ('zanjan', 'زنجان'), ('lorestan', 'لرستان'),
            ('ardabil', 'اردبیل'), ('qom', 'قم'), ('qazvin', 'قزوین'),
            ('semnan', 'سمنان'), ('yazd', 'یزد'), ('kurdistan', 'کردستان'),
            ('north_khorasan', 'خراسان شمالی'), ('south_khorasan', 'خراسان جنوبی'),
            ('ilam', 'ایلام'), ('kohgiluyeh', 'کهگیلویه و بویراحمد'),
            ('chaharmahal', 'چهارمحال و بختیاری'),
            ('sistan', 'سیستان و بلوچستان'),
        ],
        string='استان',
    )

    @api.constrains('l10n_ir_national_code')
    def _check_national_code(self):
        """Validate Iranian national code (code melli)."""
        for rec in self:
            code = rec.l10n_ir_national_code
            if not code:
                continue
            if len(code) != 10 or not code.isdigit():
                continue  # Skip validation if format is wrong
            # National code validation algorithm
            check = int(code[9])
            s = sum(int(code[i]) * (10 - i) for i in range(9)) % 11
            valid = (s < 2 and check == s) or (s >= 2 and check == 11 - s)
            if not valid:
                from odoo.exceptions import ValidationError
                raise ValidationError('کد ملی وارد شده معتبر نیست.')

    @api.constrains('l10n_ir_national_id')
    def _check_national_id(self):
        """Validate Iranian legal entity national ID."""
        for rec in self:
            nid = rec.l10n_ir_national_id
            if not nid:
                continue
            if len(nid) != 11 or not nid.isdigit():
                from odoo.exceptions import ValidationError
                raise ValidationError('شناسه ملی باید ۱۱ رقم باشد.')
