# Part of Orcest AI. See LICENSE file for full copyright and licensing details.

"""
گزارش‌های مالی پیشرفته سازمانی
Advanced Financial Reports for Enterprise

Includes:
- صورت سود و زیان (Income Statement)
- ترازنامه (Balance Sheet)
- صورت جریان وجوه نقد (Cash Flow Statement)
- تحلیل EBITDA
- بهای تمام‌شده تولید/خدمات
- نسبت‌های مالی کلیدی
- تحلیل نقطه سربه‌سر
"""

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class OrcestFinancialReport(models.Model):
    _name = 'orcest.financial.report'
    _description = 'گزارش مالی'
    _order = 'date_to desc'
    _inherit = ['mail.thread']

    name = fields.Char(string='عنوان گزارش', required=True)
    report_type = fields.Selection([
        ('income_statement', 'صورت سود و زیان'),
        ('balance_sheet', 'ترازنامه'),
        ('cash_flow', 'صورت جریان وجوه نقد'),
        ('ebitda', 'تحلیل EBITDA'),
        ('cost_analysis', 'تحلیل بهای تمام‌شده'),
        ('ratio_analysis', 'نسبت‌های مالی'),
        ('breakeven', 'تحلیل نقطه سربه‌سر'),
        ('consolidated', 'صورت‌های مالی تلفیقی'),
    ], string='نوع گزارش', required=True, tracking=True)

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    company_ids = fields.Many2many(
        'res.company',
        string='شرکت‌های مشمول',
        help='برای گزارش‌های تلفیقی',
    )
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    date_from = fields.Date(string='از تاریخ', required=True)
    date_to = fields.Date(string='تا تاریخ', required=True)
    jalali_period = fields.Char(string='دوره شمسی', compute='_compute_jalali_period', store=True)

    state = fields.Selection([
        ('draft', 'پیش‌نویس'),
        ('generated', 'تولید شده'),
        ('reviewed', 'بررسی شده'),
        ('approved', 'تأیید شده'),
    ], default='draft', tracking=True)

    # === درآمدها ===
    total_revenue = fields.Monetary(string='درآمد کل', currency_field='currency_id')
    net_revenue = fields.Monetary(string='درآمد خالص', currency_field='currency_id')
    export_revenue = fields.Monetary(string='درآمد صادراتی', currency_field='currency_id')

    # === بهای تمام‌شده ===
    total_cogs = fields.Monetary(string='بهای تمام‌شده', currency_field='currency_id')
    direct_material = fields.Monetary(string='مواد مستقیم', currency_field='currency_id')
    direct_labor = fields.Monetary(string='دستمزد مستقیم', currency_field='currency_id')
    manufacturing_overhead = fields.Monetary(string='سربار تولید', currency_field='currency_id')

    # === سود ناخالص ===
    gross_profit = fields.Monetary(string='سود ناخالص', compute='_compute_metrics', store=True, currency_field='currency_id')
    gross_margin = fields.Float(string='حاشیه سود ناخالص (%)', compute='_compute_metrics', store=True)

    # === هزینه‌های عملیاتی ===
    admin_expenses = fields.Monetary(string='هزینه‌های اداری و عمومی', currency_field='currency_id')
    selling_expenses = fields.Monetary(string='هزینه‌های فروش و توزیع', currency_field='currency_id')
    rd_expenses = fields.Monetary(string='هزینه‌های تحقیق و توسعه', currency_field='currency_id')
    total_opex = fields.Monetary(string='هزینه‌های عملیاتی', compute='_compute_metrics', store=True, currency_field='currency_id')

    # === EBITDA ===
    depreciation = fields.Monetary(string='استهلاک', currency_field='currency_id')
    amortization = fields.Monetary(string='استهلاک دارایی نامشهود', currency_field='currency_id')
    interest_expense = fields.Monetary(string='هزینه مالی', currency_field='currency_id')
    tax_expense = fields.Monetary(string='مالیات', currency_field='currency_id')
    ebitda = fields.Monetary(string='EBITDA', compute='_compute_metrics', store=True, currency_field='currency_id')
    ebitda_margin = fields.Float(string='حاشیه EBITDA (%)', compute='_compute_metrics', store=True)
    ebit = fields.Monetary(string='EBIT (سود عملیاتی)', compute='_compute_metrics', store=True, currency_field='currency_id')
    net_income = fields.Monetary(string='سود خالص', compute='_compute_metrics', store=True, currency_field='currency_id')
    net_margin = fields.Float(string='حاشیه سود خالص (%)', compute='_compute_metrics', store=True)

    # === ترازنامه ===
    total_assets = fields.Monetary(string='جمع دارایی‌ها', currency_field='currency_id')
    current_assets = fields.Monetary(string='دارایی‌های جاری', currency_field='currency_id')
    non_current_assets = fields.Monetary(string='دارایی‌های غیرجاری', currency_field='currency_id')
    total_liabilities = fields.Monetary(string='جمع بدهی‌ها', currency_field='currency_id')
    current_liabilities = fields.Monetary(string='بدهی‌های جاری', currency_field='currency_id')
    non_current_liabilities = fields.Monetary(string='بدهی‌های غیرجاری', currency_field='currency_id')
    total_equity = fields.Monetary(string='حقوق صاحبان سهام', currency_field='currency_id')

    # === نسبت‌های مالی ===
    current_ratio = fields.Float(string='نسبت جاری', compute='_compute_ratios', store=True)
    quick_ratio = fields.Float(string='نسبت آنی', compute='_compute_ratios', store=True)
    debt_to_equity = fields.Float(string='نسبت بدهی به حقوق صاحبان سهام', compute='_compute_ratios', store=True)
    roe = fields.Float(string='بازده حقوق صاحبان سهام (%)', compute='_compute_ratios', store=True)
    roa = fields.Float(string='بازده دارایی‌ها (%)', compute='_compute_ratios', store=True)

    # === تسعیر ارز ===
    fx_gain_loss = fields.Monetary(string='سود/زیان تسعیر ارز', currency_field='currency_id')

    # === تحلیل هوش مصنوعی ===
    ai_analysis = fields.Text(string='تحلیل هوش مصنوعی')
    ai_recommendations = fields.Text(string='پیشنهادات هوش مصنوعی')

    line_ids = fields.One2many('orcest.financial.report.line', 'report_id', string='اقلام گزارش')
    notes = fields.Html(string='یادداشت‌ها')

    @api.depends('date_from', 'date_to')
    def _compute_jalali_period(self):
        from odoo.addons.l10n_ir_orcest.models.jalali_date_utils import (
            date_to_jalali, JALALI_MONTH_NAMES,
        )
        for rec in self:
            if rec.date_from and rec.date_to:
                jy1, jm1, _ = date_to_jalali(rec.date_from)
                jy2, jm2, _ = date_to_jalali(rec.date_to)
                rec.jalali_period = f'{JALALI_MONTH_NAMES[jm1-1]} {jy1} - {JALALI_MONTH_NAMES[jm2-1]} {jy2}'
            else:
                rec.jalali_period = ''

    @api.depends(
        'total_revenue', 'net_revenue', 'total_cogs',
        'admin_expenses', 'selling_expenses', 'rd_expenses',
        'depreciation', 'amortization', 'interest_expense', 'tax_expense',
    )
    def _compute_metrics(self):
        for rec in self:
            revenue = rec.net_revenue or rec.total_revenue or 1

            rec.gross_profit = revenue - rec.total_cogs
            rec.gross_margin = (rec.gross_profit / revenue * 100) if revenue else 0

            rec.total_opex = rec.admin_expenses + rec.selling_expenses + rec.rd_expenses

            operating_income = rec.gross_profit - rec.total_opex
            rec.ebit = operating_income

            rec.ebitda = operating_income + rec.depreciation + rec.amortization
            rec.ebitda_margin = (rec.ebitda / revenue * 100) if revenue else 0

            rec.net_income = operating_income - rec.interest_expense - rec.tax_expense + rec.fx_gain_loss
            rec.net_margin = (rec.net_income / revenue * 100) if revenue else 0

    @api.depends(
        'current_assets', 'current_liabilities', 'total_liabilities',
        'total_equity', 'total_assets', 'net_income',
    )
    def _compute_ratios(self):
        for rec in self:
            rec.current_ratio = (rec.current_assets / rec.current_liabilities) if rec.current_liabilities else 0
            rec.quick_ratio = rec.current_ratio * 0.8  # Approximation
            rec.debt_to_equity = (rec.total_liabilities / rec.total_equity) if rec.total_equity else 0
            rec.roe = (rec.net_income / rec.total_equity * 100) if rec.total_equity else 0
            rec.roa = (rec.net_income / rec.total_assets * 100) if rec.total_assets else 0

    def action_generate(self):
        """Generate financial report from accounting data."""
        self.ensure_one()
        AccountMoveLine = self.env['account.move.line']
        domain = [
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('parent_state', '=', 'posted'),
            ('company_id', '=', self.company_id.id),
        ]

        lines = AccountMoveLine.search(domain)

        # Aggregate by account type
        revenue = sum(lines.filtered(
            lambda l: l.account_id.account_type in ('income', 'income_other')
        ).mapped('credit')) - sum(lines.filtered(
            lambda l: l.account_id.account_type in ('income', 'income_other')
        ).mapped('debit'))

        cogs = sum(lines.filtered(
            lambda l: l.account_id.account_type == 'expense_direct_cost'
        ).mapped('debit')) - sum(lines.filtered(
            lambda l: l.account_id.account_type == 'expense_direct_cost'
        ).mapped('credit'))

        expenses = sum(lines.filtered(
            lambda l: l.account_id.account_type == 'expense'
        ).mapped('debit')) - sum(lines.filtered(
            lambda l: l.account_id.account_type == 'expense'
        ).mapped('credit'))

        depreciation = sum(lines.filtered(
            lambda l: l.account_id.account_type == 'expense_depreciation'
        ).mapped('debit'))

        self.write({
            'total_revenue': revenue,
            'net_revenue': revenue,
            'total_cogs': cogs,
            'admin_expenses': expenses * 0.6,
            'selling_expenses': expenses * 0.3,
            'rd_expenses': expenses * 0.1,
            'depreciation': depreciation,
            'state': 'generated',
        })

    def action_ai_analyze(self):
        """Analyze financial report using RainyModel AI."""
        self.ensure_one()
        service = self.env['l10n_ir_orcest.rainymodel']
        data = (
            f"گزارش مالی {self.name}\n"
            f"دوره: {self.jalali_period}\n"
            f"درآمد کل: {self.total_revenue:,.0f} ریال\n"
            f"بهای تمام‌شده: {self.total_cogs:,.0f} ریال\n"
            f"سود ناخالص: {self.gross_profit:,.0f} ریال ({self.gross_margin:.1f}%)\n"
            f"EBITDA: {self.ebitda:,.0f} ریال ({self.ebitda_margin:.1f}%)\n"
            f"سود خالص: {self.net_income:,.0f} ریال ({self.net_margin:.1f}%)\n"
            f"نسبت جاری: {self.current_ratio:.2f}\n"
            f"بدهی به حقوق صاحبان سهام: {self.debt_to_equity:.2f}\n"
            f"بازده حقوق صاحبان سهام: {self.roe:.1f}%\n"
        )
        try:
            analysis = service.analyze_financial_data(data)
            self.write({
                'ai_analysis': analysis,
            })
        except Exception as e:
            raise UserError(_('خطا در تحلیل هوش مصنوعی: %s') % str(e))


class OrcestFinancialReportLine(models.Model):
    _name = 'orcest.financial.report.line'
    _description = 'اقلام گزارش مالی'
    _order = 'sequence, id'

    report_id = fields.Many2one('orcest.financial.report', ondelete='cascade')
    name = fields.Char(string='شرح', required=True)
    sequence = fields.Integer(default=10)
    account_code = fields.Char(string='کد حساب')
    amount = fields.Float(string='مبلغ')
    amount_previous = fields.Float(string='مبلغ دوره قبل')
    change_percent = fields.Float(
        string='درصد تغییر',
        compute='_compute_change',
        store=True,
    )
    line_type = fields.Selection([
        ('header', 'سرگروه'),
        ('detail', 'جزئیات'),
        ('subtotal', 'جمع فرعی'),
        ('total', 'جمع کل'),
    ], default='detail')
    indent_level = fields.Integer(string='سطح تورفتگی', default=0)
    currency_id = fields.Many2one('res.currency', related='report_id.currency_id')

    @api.depends('amount', 'amount_previous')
    def _compute_change(self):
        for line in self:
            if line.amount_previous:
                line.change_percent = ((line.amount - line.amount_previous) / abs(line.amount_previous)) * 100
            else:
                line.change_percent = 0
