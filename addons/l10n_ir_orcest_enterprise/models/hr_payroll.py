# Part of Orcest AI. See LICENSE file for full copyright and licensing details.

"""
حقوق و دستمزد مطابق قانون کار ایران
Iranian Payroll System - Labor Law Compliant

Includes:
- حقوق پایه و مزایا
- بیمه تأمین اجتماعی (سهم کارفرما و کارگر)
- مالیات حقوق (پلکانی)
- عیدی و پاداش
- حق مسکن، بن کارگری، حق اولاد
- سنوات خدمت
- اضافه‌کاری، شب‌کاری، تعطیل‌کاری
"""

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import math


# Iranian Social Security rates (2024)
SOCIAL_SECURITY_EMPLOYEE_RATE = 0.07  # 7% سهم کارگر
SOCIAL_SECURITY_EMPLOYER_RATE = 0.23  # 23% سهم کارفرما (20% بیمه + 3% بیکاری)
UNEMPLOYMENT_INSURANCE_RATE = 0.03   # 3% بیمه بیکاری

# Tax brackets for salary (1404 - Iranian fiscal year)
SALARY_TAX_BRACKETS = [
    (1_200_000_000, 0.00),    # تا ۱۲۰ میلیون تومان معاف
    (1_680_000_000, 0.10),    # تا ۱۶۸ میلیون تومان ۱۰٪
    (2_760_000_000, 0.15),    # تا ۲۷۶ میلیون تومان ۱۵٪
    (3_840_000_000, 0.20),    # تا ۳۸۴ میلیون تومان ۲۰٪
    (float('inf'), 0.25),     # بیش از ۳۸۴ میلیون تومان ۲۵٪
]


class OrcestPayslip(models.Model):
    _name = 'orcest.payslip'
    _description = 'فیش حقوقی'
    _order = 'date_from desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='شماره فیش',
        required=True,
        readonly=True,
        default='جدید',
        copy=False,
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='کارمند',
        required=True,
        tracking=True,
    )
    department_id = fields.Many2one(
        'hr.department',
        string='واحد سازمانی',
        related='employee_id.department_id',
        store=True,
    )
    company_id = fields.Many2one(
        'res.company',
        string='شرکت',
        default=lambda self: self.env.company,
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='company_id.currency_id',
    )
    date_from = fields.Date(
        string='از تاریخ',
        required=True,
        tracking=True,
    )
    date_to = fields.Date(
        string='تا تاریخ',
        required=True,
        tracking=True,
    )
    jalali_period = fields.Char(
        string='دوره شمسی',
        compute='_compute_jalali_period',
        store=True,
    )
    state = fields.Selection([
        ('draft', 'پیش‌نویس'),
        ('computed', 'محاسبه شده'),
        ('confirmed', 'تأیید شده'),
        ('paid', 'پرداخت شده'),
        ('cancelled', 'لغو شده'),
    ], string='وضعیت', default='draft', tracking=True)

    # === مزایا ===
    base_salary = fields.Monetary(string='حقوق پایه', currency_field='currency_id')
    housing_allowance = fields.Monetary(string='حق مسکن', currency_field='currency_id')
    food_allowance = fields.Monetary(string='بن کارگری', currency_field='currency_id')
    children_allowance = fields.Monetary(string='حق اولاد', currency_field='currency_id')
    transportation_allowance = fields.Monetary(string='حق ایاب و ذهاب', currency_field='currency_id')
    spouse_allowance = fields.Monetary(string='حق عائله‌مندی', currency_field='currency_id')
    seniority_bonus = fields.Monetary(string='پایه سنوات', currency_field='currency_id')
    overtime_amount = fields.Monetary(string='اضافه‌کاری', currency_field='currency_id')
    night_shift_amount = fields.Monetary(string='شب‌کاری', currency_field='currency_id')
    holiday_work_amount = fields.Monetary(string='تعطیل‌کاری', currency_field='currency_id')
    mission_allowance = fields.Monetary(string='حق مأموریت', currency_field='currency_id')
    hardship_allowance = fields.Monetary(string='فوق‌العاده سختی کار', currency_field='currency_id')
    other_benefits = fields.Monetary(string='سایر مزایا', currency_field='currency_id')

    # === ساعات کار ===
    working_days = fields.Float(string='روز کاری', default=30)
    overtime_hours = fields.Float(string='ساعات اضافه‌کاری')
    night_shift_hours = fields.Float(string='ساعات شب‌کاری')
    holiday_work_hours = fields.Float(string='ساعات تعطیل‌کاری')
    absent_days = fields.Float(string='روز غیبت')
    sick_days = fields.Float(string='روز بیماری')
    leave_days = fields.Float(string='روز مرخصی')

    # === مبالغ محاسبه‌شده ===
    gross_salary = fields.Monetary(
        string='حقوق ناخالص',
        compute='_compute_payslip',
        store=True,
        currency_field='currency_id',
    )
    taxable_income = fields.Monetary(
        string='درآمد مشمول مالیات',
        compute='_compute_payslip',
        store=True,
        currency_field='currency_id',
    )

    # === کسورات ===
    social_security_employee = fields.Monetary(
        string='بیمه تأمین اجتماعی (سهم کارگر)',
        compute='_compute_payslip',
        store=True,
        currency_field='currency_id',
    )
    social_security_employer = fields.Monetary(
        string='بیمه تأمین اجتماعی (سهم کارفرما)',
        compute='_compute_payslip',
        store=True,
        currency_field='currency_id',
    )
    income_tax = fields.Monetary(
        string='مالیات حقوق',
        compute='_compute_payslip',
        store=True,
        currency_field='currency_id',
    )
    loan_deduction = fields.Monetary(string='قسط وام', currency_field='currency_id')
    other_deductions = fields.Monetary(string='سایر کسورات', currency_field='currency_id')
    total_deductions = fields.Monetary(
        string='جمع کسورات',
        compute='_compute_payslip',
        store=True,
        currency_field='currency_id',
    )

    # === خالص پرداختی ===
    net_salary = fields.Monetary(
        string='خالص پرداختی',
        compute='_compute_payslip',
        store=True,
        currency_field='currency_id',
    )

    # === سنوات و عیدی ===
    severance_provision = fields.Monetary(
        string='ذخیره سنوات (ماهانه)',
        compute='_compute_payslip',
        store=True,
        currency_field='currency_id',
    )
    bonus_provision = fields.Monetary(
        string='ذخیره عیدی (ماهانه)',
        compute='_compute_payslip',
        store=True,
        currency_field='currency_id',
    )
    employer_total_cost = fields.Monetary(
        string='هزینه کل کارفرما',
        compute='_compute_payslip',
        store=True,
        currency_field='currency_id',
    )

    line_ids = fields.One2many(
        'orcest.payslip.line',
        'payslip_id',
        string='اقلام فیش حقوقی',
    )

    @api.depends('date_from')
    def _compute_jalali_period(self):
        from odoo.addons.l10n_ir_orcest.models.jalali_date_utils import (
            date_to_jalali, JALALI_MONTH_NAMES, format_jalali_date,
        )
        for rec in self:
            if rec.date_from:
                jy, jm, jd = date_to_jalali(rec.date_from)
                rec.jalali_period = f'{JALALI_MONTH_NAMES[jm - 1]} {jy}'
            else:
                rec.jalali_period = ''

    @api.depends(
        'base_salary', 'housing_allowance', 'food_allowance', 'children_allowance',
        'transportation_allowance', 'spouse_allowance', 'seniority_bonus',
        'overtime_amount', 'night_shift_amount', 'holiday_work_amount',
        'mission_allowance', 'hardship_allowance', 'other_benefits',
        'loan_deduction', 'other_deductions', 'working_days', 'absent_days',
    )
    def _compute_payslip(self):
        for rec in self:
            # محاسبه حقوق ناخالص
            gross = (
                rec.base_salary + rec.housing_allowance + rec.food_allowance +
                rec.children_allowance + rec.transportation_allowance +
                rec.spouse_allowance + rec.seniority_bonus +
                rec.overtime_amount + rec.night_shift_amount +
                rec.holiday_work_amount + rec.mission_allowance +
                rec.hardship_allowance + rec.other_benefits
            )

            # کسر غیبت
            if rec.working_days > 0 and rec.absent_days > 0:
                daily_rate = rec.base_salary / rec.working_days
                gross -= daily_rate * rec.absent_days

            rec.gross_salary = gross

            # درآمد مشمول بیمه (سقف بیمه = 7 برابر حداقل حقوق)
            insurable_salary = rec.base_salary + rec.housing_allowance + rec.food_allowance + rec.seniority_bonus

            # بیمه تأمین اجتماعی
            rec.social_security_employee = insurable_salary * SOCIAL_SECURITY_EMPLOYEE_RATE
            rec.social_security_employer = insurable_salary * SOCIAL_SECURITY_EMPLOYER_RATE

            # درآمد مشمول مالیات
            # حق مسکن و بن کارگری از مالیات معاف هستند
            taxable = gross - rec.housing_allowance - rec.food_allowance - rec.social_security_employee
            rec.taxable_income = max(0, taxable)

            # محاسبه مالیات پلکانی (سالانه)
            annual_taxable = rec.taxable_income * 12
            annual_tax = 0
            prev_bracket = 0
            for bracket_limit, rate in SALARY_TAX_BRACKETS:
                if annual_taxable <= 0:
                    break
                bracket_amount = min(annual_taxable, bracket_limit - prev_bracket)
                annual_tax += bracket_amount * rate
                annual_taxable -= bracket_amount
                prev_bracket = bracket_limit
            rec.income_tax = annual_tax / 12

            # جمع کسورات
            rec.total_deductions = (
                rec.social_security_employee + rec.income_tax +
                rec.loan_deduction + rec.other_deductions
            )

            # خالص پرداختی
            rec.net_salary = rec.gross_salary - rec.total_deductions

            # ذخیره سنوات (یک ماه حقوق و مزایا به ازای هر سال)
            rec.severance_provision = rec.base_salary + rec.housing_allowance + rec.food_allowance

            # ذخیره عیدی (۲ ماه حقوق پایه / ۱۲)
            rec.bonus_provision = (rec.base_salary * 2) / 12

            # هزینه کل کارفرما
            rec.employer_total_cost = (
                rec.gross_salary + rec.social_security_employer +
                rec.severance_provision + rec.bonus_provision
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'جدید') == 'جدید':
                vals['name'] = self.env['ir.sequence'].next_by_code('orcest.payslip') or 'جدید'
        return super().create(vals_list)

    def action_compute(self):
        """Compute payslip."""
        self._compute_payslip()
        self._generate_payslip_lines()
        self.write({'state': 'computed'})

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_pay(self):
        self.write({'state': 'paid'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_draft(self):
        self.write({'state': 'draft'})

    def _generate_payslip_lines(self):
        """Generate detailed payslip lines."""
        for rec in self:
            rec.line_ids.unlink()
            lines = [
                ('حقوق پایه', 'benefit', rec.base_salary),
                ('حق مسکن', 'benefit', rec.housing_allowance),
                ('بن کارگری', 'benefit', rec.food_allowance),
                ('حق اولاد', 'benefit', rec.children_allowance),
                ('حق ایاب و ذهاب', 'benefit', rec.transportation_allowance),
                ('حق عائله‌مندی', 'benefit', rec.spouse_allowance),
                ('پایه سنوات', 'benefit', rec.seniority_bonus),
                ('اضافه‌کاری', 'benefit', rec.overtime_amount),
                ('شب‌کاری', 'benefit', rec.night_shift_amount),
                ('تعطیل‌کاری', 'benefit', rec.holiday_work_amount),
                ('حق مأموریت', 'benefit', rec.mission_allowance),
                ('فوق‌العاده سختی کار', 'benefit', rec.hardship_allowance),
                ('سایر مزایا', 'benefit', rec.other_benefits),
                ('بیمه تأمین اجتماعی (سهم کارگر)', 'deduction', rec.social_security_employee),
                ('مالیات حقوق', 'deduction', rec.income_tax),
                ('قسط وام', 'deduction', rec.loan_deduction),
                ('سایر کسورات', 'deduction', rec.other_deductions),
                ('بیمه تأمین اجتماعی (سهم کارفرما)', 'employer', rec.social_security_employer),
                ('ذخیره سنوات', 'employer', rec.severance_provision),
                ('ذخیره عیدی', 'employer', rec.bonus_provision),
            ]
            for label, line_type, amount in lines:
                if amount:
                    self.env['orcest.payslip.line'].create({
                        'payslip_id': rec.id,
                        'name': label,
                        'line_type': line_type,
                        'amount': amount,
                    })


class OrcestPayslipLine(models.Model):
    _name = 'orcest.payslip.line'
    _description = 'اقلام فیش حقوقی'
    _order = 'sequence, id'

    payslip_id = fields.Many2one('orcest.payslip', string='فیش حقوقی', ondelete='cascade')
    name = fields.Char(string='شرح', required=True)
    sequence = fields.Integer(string='ترتیب', default=10)
    line_type = fields.Selection([
        ('benefit', 'مزایا'),
        ('deduction', 'کسورات'),
        ('employer', 'هزینه کارفرما'),
    ], string='نوع', required=True)
    amount = fields.Float(string='مبلغ')
    currency_id = fields.Many2one(
        'res.currency',
        related='payslip_id.currency_id',
    )


class OrcestPayrollStructure(models.Model):
    _name = 'orcest.payroll.structure'
    _description = 'ساختار حقوقی'

    name = fields.Char(string='عنوان', required=True)
    code = fields.Char(string='کد', required=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    min_salary = fields.Float(string='حداقل حقوق')
    housing_allowance = fields.Float(string='حق مسکن')
    food_allowance = fields.Float(string='بن کارگری')
    transportation_allowance = fields.Float(string='حق ایاب و ذهاب')
    overtime_rate = fields.Float(string='ضریب اضافه‌کاری', default=1.4)
    night_shift_rate = fields.Float(string='ضریب شب‌کاری', default=1.35)
    holiday_work_rate = fields.Float(string='ضریب تعطیل‌کاری', default=1.4)
    children_allowance_per_child = fields.Float(string='حق اولاد هر فرزند')
