# Part of Orcest AI. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from .jalali_date_utils import (
    format_jalali_date, format_jalali_datetime, date_to_jalali,
    JALALI_MONTH_NAMES, get_jalali_quarter, jalali_year_start, jalali_year_end,
)


class AccountMove(models.Model):
    _inherit = 'account.move'

    l10n_ir_jalali_date = fields.Char(
        string='تاریخ شمسی',
        compute='_compute_jalali_date',
        store=True,
    )
    l10n_ir_jalali_due_date = fields.Char(
        string='سررسید شمسی',
        compute='_compute_jalali_due_date',
        store=True,
    )
    l10n_ir_invoice_serial = fields.Char(
        string='سریال فاکتور',
        help='شماره سریال فاکتور رسمی',
        copy=False,
    )
    l10n_ir_payment_currency_id = fields.Many2one(
        'res.currency',
        string='ارز پرداخت',
        help='ارز مورد استفاده برای پرداخت (کارت اعتباری بین‌المللی)',
    )
    l10n_ir_exchange_rate = fields.Float(
        string='نرخ تبدیل ارز',
        digits=(12, 6),
        help='نرخ تبدیل ارز پرداخت به ریال',
    )
    l10n_ir_amount_irr = fields.Monetary(
        string='مبلغ به ریال',
        compute='_compute_amount_irr',
        store=True,
        currency_field='l10n_ir_irr_currency_id',
    )
    l10n_ir_irr_currency_id = fields.Many2one(
        'res.currency',
        compute='_compute_irr_currency',
    )

    @api.depends('invoice_date')
    def _compute_jalali_date(self):
        for move in self:
            if move.invoice_date:
                move.l10n_ir_jalali_date = format_jalali_date(move.invoice_date)
            else:
                move.l10n_ir_jalali_date = ''

    @api.depends('invoice_date_due')
    def _compute_jalali_due_date(self):
        for move in self:
            if move.invoice_date_due:
                move.l10n_ir_jalali_due_date = format_jalali_date(move.invoice_date_due)
            else:
                move.l10n_ir_jalali_due_date = ''

    def _compute_irr_currency(self):
        irr = self.env.ref('base.IRR', raise_if_not_found=False)
        for move in self:
            move.l10n_ir_irr_currency_id = irr

    @api.depends('amount_total', 'currency_id', 'l10n_ir_exchange_rate')
    def _compute_amount_irr(self):
        irr = self.env.ref('base.IRR', raise_if_not_found=False)
        for move in self:
            if move.currency_id and irr and move.currency_id != irr:
                if move.l10n_ir_exchange_rate:
                    move.l10n_ir_amount_irr = move.amount_total * move.l10n_ir_exchange_rate
                else:
                    move.l10n_ir_amount_irr = move.currency_id._convert(
                        move.amount_total, irr, move.company_id,
                        move.invoice_date or fields.Date.today()
                    )
            elif move.currency_id == irr:
                move.l10n_ir_amount_irr = move.amount_total
            else:
                move.l10n_ir_amount_irr = 0.0

    def get_jalali_fiscal_period(self):
        """Get the Jalali fiscal period for this move."""
        self.ensure_one()
        if not self.invoice_date:
            return ''
        jy, jm, jd = date_to_jalali(self.invoice_date)
        quarter = get_jalali_quarter(jm)
        return f'{jy} - فصل {quarter} ({JALALI_MONTH_NAMES[jm - 1]})'


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    l10n_ir_cost_center = fields.Char(
        string='مرکز هزینه',
        help='کد مرکز هزینه ایرانی',
    )
    l10n_ir_project_code = fields.Char(
        string='کد پروژه',
        help='کد پروژه برای حسابداری پروژه‌ای',
    )
