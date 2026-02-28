# Part of Orcest AI. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    l10n_ir_insurance_number = fields.Char(string='شماره بیمه تأمین اجتماعی')
    l10n_ir_national_code = fields.Char(string='کد ملی', size=10)
    l10n_ir_birth_certificate_no = fields.Char(string='شماره شناسنامه')
    l10n_ir_father_name = fields.Char(string='نام پدر')
    l10n_ir_military_status = fields.Selection([
        ('exempt', 'معاف'),
        ('completed', 'پایان خدمت'),
        ('active', 'در حال خدمت'),
        ('educational', 'معافیت تحصیلی'),
        ('not_applicable', 'مشمول نیست'),
    ], string='وضعیت نظام وظیفه')
    l10n_ir_bank_account = fields.Char(string='شماره حساب بانکی')
    l10n_ir_sheba_number = fields.Char(string='شماره شبا', size=26)
    l10n_ir_contract_type = fields.Selection([
        ('permanent', 'دائم'),
        ('temporary', 'موقت'),
        ('project', 'پروژه‌ای'),
        ('part_time', 'پاره‌وقت'),
        ('intern', 'کارآموز'),
    ], string='نوع قرارداد')
    l10n_ir_children_count = fields.Integer(string='تعداد فرزندان')
    l10n_ir_marital_status = fields.Selection([
        ('single', 'مجرد'),
        ('married', 'متأهل'),
    ], string='وضعیت تأهل')
    l10n_ir_hire_date_jalali = fields.Char(
        string='تاریخ استخدام شمسی',
        compute='_compute_hire_date_jalali',
        store=True,
    )
    l10n_ir_payroll_structure_id = fields.Many2one(
        'orcest.payroll.structure',
        string='ساختار حقوقی',
    )
    l10n_ir_base_salary = fields.Float(string='حقوق پایه')
    l10n_ir_seniority_years = fields.Float(
        string='سنوات خدمت',
        compute='_compute_seniority',
        store=True,
    )

    # Performance tracking
    l10n_ir_performance_score = fields.Float(
        string='امتیاز عملکرد',
        help='امتیاز ارزیابی عملکرد (0-100)',
    )
    l10n_ir_skill_level = fields.Selection([
        ('junior', 'کارشناس'),
        ('mid', 'کارشناس ارشد'),
        ('senior', 'مدیر'),
        ('executive', 'مدیر ارشد'),
        ('c_level', 'مدیرعامل/هیئت مدیره'),
    ], string='سطح سازمانی')

    @api.depends('first_contract_date')
    def _compute_hire_date_jalali(self):
        from odoo.addons.l10n_ir_orcest.models.jalali_date_utils import format_jalali_date
        for emp in self:
            if emp.first_contract_date:
                emp.l10n_ir_hire_date_jalali = format_jalali_date(emp.first_contract_date)
            else:
                emp.l10n_ir_hire_date_jalali = ''

    @api.depends('first_contract_date')
    def _compute_seniority(self):
        today = fields.Date.today()
        for emp in self:
            if emp.first_contract_date:
                delta = today - emp.first_contract_date
                emp.l10n_ir_seniority_years = round(delta.days / 365.25, 1)
            else:
                emp.l10n_ir_seniority_years = 0
