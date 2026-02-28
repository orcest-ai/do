# Part of Orcest AI. See LICENSE file for full copyright and licensing details.

"""
شاخص‌های کلیدی عملکرد (KPI) و اهداف سازمانی (OKR)
Key Performance Indicators and Objectives & Key Results
"""

from odoo import api, fields, models, _
from datetime import timedelta


class OrcestKPI(models.Model):
    _name = 'orcest.kpi'
    _description = 'شاخص کلیدی عملکرد'
    _order = 'category, code'

    name = fields.Char(string='عنوان', required=True)
    code = fields.Char(string='کد', required=True)
    category = fields.Selection([
        ('financial', 'مالی'),
        ('sales', 'فروش'),
        ('hr', 'منابع انسانی'),
        ('operations', 'عملیات'),
        ('customer', 'مشتری'),
        ('growth', 'رشد'),
    ], string='دسته‌بندی', required=True)
    unit = fields.Selection([
        ('%', 'درصد'),
        ('currency', 'ارز'),
        ('ratio', 'نسبت'),
        ('count', 'تعداد'),
        ('score', 'امتیاز'),
        ('days', 'روز'),
    ], string='واحد', required=True)
    direction = fields.Selection([
        ('higher_better', 'بیشتر بهتر'),
        ('lower_better', 'کمتر بهتر'),
        ('target', 'هدف مشخص'),
    ], string='جهت بهبود', required=True)
    description = fields.Text(string='توضیحات')
    formula = fields.Text(string='فرمول محاسبه')
    active = fields.Boolean(default=True)

    value_ids = fields.One2many('orcest.kpi.value', 'kpi_id', string='مقادیر')


class OrcestKPIValue(models.Model):
    _name = 'orcest.kpi.value'
    _description = 'مقدار شاخص عملکرد'
    _order = 'date desc'

    kpi_id = fields.Many2one('orcest.kpi', ondelete='cascade', required=True)
    date = fields.Date(string='تاریخ', required=True, default=fields.Date.today)
    period = fields.Selection([
        ('daily', 'روزانه'),
        ('weekly', 'هفتگی'),
        ('monthly', 'ماهانه'),
        ('quarterly', 'فصلی'),
        ('yearly', 'سالانه'),
    ], string='دوره', default='monthly')
    jalali_period = fields.Char(string='دوره شمسی', compute='_compute_jalali', store=True)
    target_value = fields.Float(string='هدف')
    actual_value = fields.Float(string='عملکرد')
    achievement_percent = fields.Float(
        string='درصد تحقق',
        compute='_compute_achievement',
        store=True,
    )
    status = fields.Selection([
        ('excellent', 'عالی'),
        ('good', 'خوب'),
        ('warning', 'هشدار'),
        ('critical', 'بحرانی'),
    ], string='وضعیت', compute='_compute_achievement', store=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    department_id = fields.Many2one('hr.department', string='واحد سازمانی')
    notes = fields.Text(string='یادداشت')

    @api.depends('date')
    def _compute_jalali(self):
        from odoo.addons.l10n_ir_orcest.models.jalali_date_utils import (
            date_to_jalali, JALALI_MONTH_NAMES,
        )
        for rec in self:
            if rec.date:
                jy, jm, _ = date_to_jalali(rec.date)
                rec.jalali_period = f'{JALALI_MONTH_NAMES[jm-1]} {jy}'
            else:
                rec.jalali_period = ''

    @api.depends('target_value', 'actual_value')
    def _compute_achievement(self):
        for rec in self:
            if rec.target_value:
                if rec.kpi_id.direction == 'lower_better':
                    rec.achievement_percent = (rec.target_value / rec.actual_value * 100) if rec.actual_value else 100
                else:
                    rec.achievement_percent = (rec.actual_value / rec.target_value * 100)
            else:
                rec.achievement_percent = 0

            if rec.achievement_percent >= 100:
                rec.status = 'excellent'
            elif rec.achievement_percent >= 80:
                rec.status = 'good'
            elif rec.achievement_percent >= 60:
                rec.status = 'warning'
            else:
                rec.status = 'critical'


class OrcestOKR(models.Model):
    _name = 'orcest.okr'
    _description = 'اهداف و نتایج کلیدی (OKR)'
    _inherit = ['mail.thread']
    _order = 'period desc, sequence'

    name = fields.Char(string='هدف', required=True)
    description = fields.Text(string='توضیحات')
    sequence = fields.Integer(default=10)
    period = fields.Char(string='دوره', required=True)
    responsible_id = fields.Many2one('hr.employee', string='مسئول')
    department_id = fields.Many2one('hr.department', string='واحد سازمانی')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    state = fields.Selection([
        ('draft', 'پیش‌نویس'),
        ('active', 'فعال'),
        ('completed', 'تکمیل شده'),
        ('cancelled', 'لغو شده'),
    ], default='draft', tracking=True)
    progress = fields.Float(string='پیشرفت (%)', compute='_compute_progress', store=True)
    key_result_ids = fields.One2many('orcest.okr.key_result', 'okr_id', string='نتایج کلیدی')

    @api.depends('key_result_ids.progress')
    def _compute_progress(self):
        for okr in self:
            if okr.key_result_ids:
                okr.progress = sum(okr.key_result_ids.mapped('progress')) / len(okr.key_result_ids)
            else:
                okr.progress = 0


class OrcestOKRKeyResult(models.Model):
    _name = 'orcest.okr.key_result'
    _description = 'نتیجه کلیدی'
    _order = 'sequence'

    okr_id = fields.Many2one('orcest.okr', ondelete='cascade')
    name = fields.Char(string='نتیجه کلیدی', required=True)
    sequence = fields.Integer(default=10)
    target_value = fields.Float(string='هدف')
    current_value = fields.Float(string='مقدار فعلی')
    unit = fields.Char(string='واحد')
    progress = fields.Float(string='پیشرفت (%)', compute='_compute_progress', store=True)
    responsible_id = fields.Many2one('hr.employee', string='مسئول')

    @api.depends('target_value', 'current_value')
    def _compute_progress(self):
        for kr in self:
            if kr.target_value:
                kr.progress = min(100, (kr.current_value / kr.target_value) * 100)
            else:
                kr.progress = 0
