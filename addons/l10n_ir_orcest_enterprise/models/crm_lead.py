# Part of Orcest AI. See LICENSE file for full copyright and licensing details.

"""
CRM پیشرفته با هوش مصنوعی
Advanced CRM with AI-powered Lead Scoring and Pipeline Analytics
"""

from odoo import api, fields, models, _
import json
import logging

_logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    # === امتیازدهی هوشمند ===
    l10n_ir_ai_score = fields.Float(
        string='امتیاز هوش مصنوعی',
        help='امتیاز احتمال تبدیل (0-100)',
    )
    l10n_ir_ai_score_date = fields.Datetime(string='تاریخ امتیازدهی')
    l10n_ir_ai_priority = fields.Selection([
        ('hot', 'داغ 🔥'),
        ('warm', 'گرم'),
        ('cold', 'سرد'),
        ('dead', 'مرده'),
    ], string='اولویت هوشمند', compute='_compute_ai_priority', store=True)
    l10n_ir_ai_insights = fields.Text(string='تحلیل هوش مصنوعی')

    # === اطلاعات تکمیلی ایرانی ===
    l10n_ir_industry = fields.Selection([
        ('oil_gas', 'نفت و گاز'),
        ('petrochemical', 'پتروشیمی'),
        ('mining', 'معدن'),
        ('automotive', 'خودرو'),
        ('construction', 'ساختمان'),
        ('agriculture', 'کشاورزی'),
        ('telecom', 'مخابرات'),
        ('banking', 'بانکداری'),
        ('insurance', 'بیمه'),
        ('pharma', 'دارو'),
        ('food', 'صنایع غذایی'),
        ('textile', 'نساجی'),
        ('it', 'فناوری اطلاعات'),
        ('tourism', 'گردشگری'),
        ('export', 'صادرات'),
        ('import', 'واردات'),
        ('retail', 'خرده‌فروشی'),
        ('manufacturing', 'تولیدی'),
        ('services', 'خدمات'),
        ('other', 'سایر'),
    ], string='صنعت')
    l10n_ir_deal_currency_id = fields.Many2one(
        'res.currency',
        string='ارز معامله',
    )
    l10n_ir_competitor = fields.Char(string='رقیب اصلی')
    l10n_ir_decision_maker = fields.Char(string='تصمیم‌گیرنده نهایی')
    l10n_ir_budget_range = fields.Selection([
        ('under_100m', 'کمتر از ۱۰۰ میلیون تومان'),
        ('100m_500m', '۱۰۰ تا ۵۰۰ میلیون تومان'),
        ('500m_1b', '۵۰۰ میلیون تا ۱ میلیارد تومان'),
        ('1b_5b', '۱ تا ۵ میلیارد تومان'),
        ('5b_10b', '۵ تا ۱۰ میلیارد تومان'),
        ('over_10b', 'بیش از ۱۰ میلیارد تومان'),
    ], string='بازه بودجه مشتری')
    l10n_ir_source_detail = fields.Char(string='جزئیات منبع سرنخ')
    l10n_ir_jalali_create_date = fields.Char(
        string='تاریخ ایجاد شمسی',
        compute='_compute_jalali_dates',
        store=True,
    )
    l10n_ir_expected_close_jalali = fields.Char(
        string='تاریخ بسته‌شدن مورد انتظار شمسی',
        compute='_compute_jalali_dates',
        store=True,
    )

    # === Pipeline Analytics ===
    l10n_ir_days_in_stage = fields.Integer(
        string='روز در مرحله فعلی',
        compute='_compute_days_in_stage',
    )
    l10n_ir_conversion_probability = fields.Float(
        string='احتمال تبدیل (%)',
        compute='_compute_conversion_probability',
        store=True,
    )

    @api.depends('l10n_ir_ai_score')
    def _compute_ai_priority(self):
        for lead in self:
            score = lead.l10n_ir_ai_score
            if score >= 80:
                lead.l10n_ir_ai_priority = 'hot'
            elif score >= 50:
                lead.l10n_ir_ai_priority = 'warm'
            elif score >= 20:
                lead.l10n_ir_ai_priority = 'cold'
            else:
                lead.l10n_ir_ai_priority = 'dead'

    @api.depends('create_date', 'date_deadline')
    def _compute_jalali_dates(self):
        from odoo.addons.l10n_ir_orcest.models.jalali_date_utils import format_jalali_date
        for lead in self:
            if lead.create_date:
                lead.l10n_ir_jalali_create_date = format_jalali_date(lead.create_date)
            else:
                lead.l10n_ir_jalali_create_date = ''
            if lead.date_deadline:
                lead.l10n_ir_expected_close_jalali = format_jalali_date(lead.date_deadline)
            else:
                lead.l10n_ir_expected_close_jalali = ''

    def _compute_days_in_stage(self):
        for lead in self:
            if lead.date_last_stage_update:
                delta = fields.Datetime.now() - lead.date_last_stage_update
                lead.l10n_ir_days_in_stage = delta.days
            else:
                lead.l10n_ir_days_in_stage = 0

    @api.depends('stage_id', 'expected_revenue', 'probability')
    def _compute_conversion_probability(self):
        for lead in self:
            base_prob = lead.probability or 10
            # Boost probability based on revenue
            if lead.expected_revenue and lead.expected_revenue > 0:
                revenue_factor = min(1.2, 1 + (lead.expected_revenue / 1e10))  # Scale by 10B IRR
                lead.l10n_ir_conversion_probability = min(100, base_prob * revenue_factor)
            else:
                lead.l10n_ir_conversion_probability = base_prob

    def action_ai_score(self):
        """Score leads using RainyModel AI."""
        service = self.env['l10n_ir_orcest.rainymodel']
        for lead in self:
            data = (
                f"اطلاعات سرنخ فروش:\n"
                f"نام: {lead.name}\n"
                f"شرکت: {lead.partner_name or '-'}\n"
                f"صنعت: {dict(self._fields['l10n_ir_industry'].selection).get(lead.l10n_ir_industry, '-')}\n"
                f"مبلغ مورد انتظار: {lead.expected_revenue:,.0f}\n"
                f"مرحله: {lead.stage_id.name}\n"
                f"منبع: {lead.source_id.name if lead.source_id else '-'}\n"
                f"روز در مرحله فعلی: {lead.l10n_ir_days_in_stage}\n"
                f"تصمیم‌گیرنده: {lead.l10n_ir_decision_maker or '-'}\n"
                f"رقیب: {lead.l10n_ir_competitor or '-'}\n\n"
                f"لطفاً امتیاز احتمال تبدیل (0-100) و تحلیل کوتاه ارائه دهید.\n"
                f"فرمت پاسخ: عدد|تحلیل"
            )
            try:
                result = service.chat_completion([
                    {'role': 'system', 'content': 'شما یک متخصص فروش B2B هستید. فقط در فرمت خواسته شده پاسخ دهید.'},
                    {'role': 'user', 'content': data},
                ])
                parts = result.split('|', 1)
                score = float(''.join(c for c in parts[0] if c.isdigit() or c == '.') or '50')
                insights = parts[1].strip() if len(parts) > 1 else result
                lead.write({
                    'l10n_ir_ai_score': min(100, max(0, score)),
                    'l10n_ir_ai_score_date': fields.Datetime.now(),
                    'l10n_ir_ai_insights': insights,
                })
            except Exception as e:
                _logger.warning('AI scoring failed for lead %s: %s', lead.id, e)
