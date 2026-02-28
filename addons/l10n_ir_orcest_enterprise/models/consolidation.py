# Part of Orcest AI. See LICENSE file for full copyright and licensing details.

"""
صورت‌های مالی تلفیقی برای شرکت‌های چندملیتی
Consolidated Financial Statements for Multinational Corporations

- تلفیق حساب‌های بین‌شرکتی
- حذف معاملات درون‌گروهی
- تبدیل ارز تلفیقی
- گزارش‌های تلفیقی استاندارد
"""

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class OrcestConsolidationGroup(models.Model):
    _name = 'orcest.consolidation.group'
    _description = 'گروه تلفیقی'
    _inherit = ['mail.thread']

    name = fields.Char(string='نام گروه', required=True)
    parent_company_id = fields.Many2one('res.company', string='شرکت مادر', required=True)
    subsidiary_ids = fields.Many2many('res.company', string='شرکت‌های تابعه')
    consolidation_currency_id = fields.Many2one('res.currency', string='ارز تلفیقی')
    elimination_journal_id = fields.Many2one('account.journal', string='دفتر حذف بین‌شرکتی')
    active = fields.Boolean(default=True)
    notes = fields.Html(string='یادداشت‌ها')


class OrcestConsolidationReport(models.Model):
    _name = 'orcest.consolidation.report'
    _description = 'گزارش تلفیقی'
    _inherit = ['mail.thread']
    _order = 'date_to desc'

    name = fields.Char(string='عنوان', required=True)
    group_id = fields.Many2one('orcest.consolidation.group', string='گروه تلفیقی', required=True)
    date_from = fields.Date(string='از تاریخ', required=True)
    date_to = fields.Date(string='تا تاریخ', required=True)
    jalali_period = fields.Char(string='دوره شمسی', compute='_compute_jalali_period', store=True)
    currency_id = fields.Many2one('res.currency', related='group_id.consolidation_currency_id')
    state = fields.Selection([
        ('draft', 'پیش‌نویس'),
        ('processing', 'در حال پردازش'),
        ('generated', 'تولید شده'),
        ('reviewed', 'بررسی شده'),
        ('approved', 'تأیید شده'),
    ], default='draft', tracking=True)

    # Consolidated P&L
    consolidated_revenue = fields.Monetary(string='درآمد تلفیقی', currency_field='currency_id')
    intercompany_revenue_eliminated = fields.Monetary(string='درآمد بین‌شرکتی حذف‌شده', currency_field='currency_id')
    consolidated_cogs = fields.Monetary(string='بهای تمام‌شده تلفیقی', currency_field='currency_id')
    consolidated_gross_profit = fields.Monetary(string='سود ناخالص تلفیقی', currency_field='currency_id')
    consolidated_opex = fields.Monetary(string='هزینه عملیاتی تلفیقی', currency_field='currency_id')
    consolidated_ebitda = fields.Monetary(string='EBITDA تلفیقی', currency_field='currency_id')
    consolidated_net_income = fields.Monetary(string='سود خالص تلفیقی', currency_field='currency_id')
    fx_translation_adjustment = fields.Monetary(string='تعدیل تسعیر ارز', currency_field='currency_id')
    minority_interest = fields.Monetary(string='سهم اقلیت', currency_field='currency_id')

    # Consolidated Balance Sheet
    consolidated_total_assets = fields.Monetary(string='دارایی تلفیقی', currency_field='currency_id')
    consolidated_total_liabilities = fields.Monetary(string='بدهی تلفیقی', currency_field='currency_id')
    consolidated_equity = fields.Monetary(string='حقوق صاحبان سهام تلفیقی', currency_field='currency_id')
    goodwill = fields.Monetary(string='سرقفلی تلفیقی', currency_field='currency_id')

    line_ids = fields.One2many('orcest.consolidation.report.line', 'report_id', string='اقلام')
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

    def action_generate(self):
        """Generate consolidated financial statements."""
        self.ensure_one()
        if not self.group_id.subsidiary_ids:
            raise UserError(_('هیچ شرکت تابعه‌ای تعریف نشده است.'))

        total_revenue = 0
        total_cogs = 0
        total_opex = 0
        total_assets = 0
        total_liabilities = 0

        for company in self.group_id.subsidiary_ids | self.group_id.parent_company_id:
            domain = [
                ('date', '>=', self.date_from),
                ('date', '<=', self.date_to),
                ('parent_state', '=', 'posted'),
                ('company_id', '=', company.id),
            ]
            lines = self.env['account.move.line'].sudo().search(domain)

            revenue = sum(lines.filtered(
                lambda l: l.account_id.account_type in ('income', 'income_other')
            ).mapped('credit')) - sum(lines.filtered(
                lambda l: l.account_id.account_type in ('income', 'income_other')
            ).mapped('debit'))

            cogs = sum(lines.filtered(
                lambda l: l.account_id.account_type == 'expense_direct_cost'
            ).mapped('debit'))

            opex = sum(lines.filtered(
                lambda l: l.account_id.account_type in ('expense', 'expense_depreciation')
            ).mapped('debit'))

            # Convert to consolidation currency
            if company.currency_id != self.currency_id:
                rate = company.currency_id._get_conversion_rate(
                    company.currency_id, self.currency_id,
                    company, self.date_to
                )
                revenue *= rate
                cogs *= rate
                opex *= rate

            total_revenue += revenue
            total_cogs += cogs
            total_opex += opex

        self.write({
            'consolidated_revenue': total_revenue,
            'consolidated_cogs': total_cogs,
            'consolidated_gross_profit': total_revenue - total_cogs,
            'consolidated_opex': total_opex,
            'consolidated_ebitda': total_revenue - total_cogs - total_opex,
            'consolidated_net_income': total_revenue - total_cogs - total_opex,
            'state': 'generated',
        })


class OrcestConsolidationReportLine(models.Model):
    _name = 'orcest.consolidation.report.line'
    _description = 'اقلام گزارش تلفیقی'
    _order = 'sequence'

    report_id = fields.Many2one('orcest.consolidation.report', ondelete='cascade')
    sequence = fields.Integer(default=10)
    company_id = fields.Many2one('res.company', string='شرکت')
    account_group = fields.Char(string='گروه حساب')
    name = fields.Char(string='شرح')
    original_amount = fields.Float(string='مبلغ اصلی')
    original_currency_id = fields.Many2one('res.currency', string='ارز اصلی')
    converted_amount = fields.Float(string='مبلغ تبدیل‌شده')
    elimination_amount = fields.Float(string='حذف بین‌شرکتی')
    consolidated_amount = fields.Float(string='مبلغ تلفیقی')
