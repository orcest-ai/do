# Part of Orcest AI. See LICENSE file for full copyright and licensing details.

"""
زنجیره تأمین پیشرفته و مدیریت موجودی هوشمند
Advanced Supply Chain & Intelligent Inventory Management

- پیش‌بینی تقاضا با هوش مصنوعی
- نقطه سفارش خودکار
- مدیریت تأمین‌کنندگان
- ردیابی محموله بین‌المللی
"""

from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)


class OrcestDemandForecast(models.Model):
    _name = 'orcest.demand.forecast'
    _description = 'پیش‌بینی تقاضا'
    _order = 'forecast_date desc'

    product_id = fields.Many2one('product.product', string='محصول', required=True)
    product_tmpl_id = fields.Many2one(
        'product.template',
        related='product_id.product_tmpl_id',
    )
    forecast_date = fields.Date(string='تاریخ پیش‌بینی', required=True)
    jalali_period = fields.Char(string='دوره شمسی', compute='_compute_jalali', store=True)
    period_type = fields.Selection([
        ('weekly', 'هفتگی'),
        ('monthly', 'ماهانه'),
        ('quarterly', 'فصلی'),
    ], string='نوع دوره', default='monthly')
    forecast_qty = fields.Float(string='تقاضای پیش‌بینی شده')
    actual_qty = fields.Float(string='تقاضای واقعی')
    variance = fields.Float(string='انحراف', compute='_compute_variance', store=True)
    accuracy = fields.Float(string='دقت (%)', compute='_compute_variance', store=True)
    confidence = fields.Selection([
        ('high', 'بالا'),
        ('medium', 'متوسط'),
        ('low', 'پایین'),
    ], string='سطح اطمینان')
    method = fields.Selection([
        ('ai', 'هوش مصنوعی'),
        ('moving_average', 'میانگین متحرک'),
        ('exponential', 'هموارسازی نمایی'),
        ('manual', 'دستی'),
    ], string='روش پیش‌بینی', default='ai')
    warehouse_id = fields.Many2one('stock.warehouse', string='انبار')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    notes = fields.Text(string='یادداشت')

    @api.depends('forecast_date')
    def _compute_jalali(self):
        from odoo.addons.l10n_ir_orcest.models.jalali_date_utils import (
            date_to_jalali, JALALI_MONTH_NAMES,
        )
        for rec in self:
            if rec.forecast_date:
                jy, jm, _ = date_to_jalali(rec.forecast_date)
                rec.jalali_period = f'{JALALI_MONTH_NAMES[jm-1]} {jy}'
            else:
                rec.jalali_period = ''

    @api.depends('forecast_qty', 'actual_qty')
    def _compute_variance(self):
        for rec in self:
            rec.variance = rec.actual_qty - rec.forecast_qty
            if rec.forecast_qty:
                error = abs(rec.variance) / abs(rec.forecast_qty)
                rec.accuracy = max(0, (1 - error) * 100)
            else:
                rec.accuracy = 0

    def action_ai_forecast(self):
        """Generate AI-based demand forecast."""
        service = self.env['l10n_ir_orcest.rainymodel']
        for rec in self:
            # Get historical data
            sales = self.env['sale.order.line'].search([
                ('product_id', '=', rec.product_id.id),
                ('order_id.state', 'in', ['sale', 'done']),
            ], order='order_id asc', limit=100)

            if not sales:
                continue

            monthly_data = {}
            for line in sales:
                month_key = line.order_id.date_order.strftime('%Y-%m')
                monthly_data.setdefault(month_key, 0)
                monthly_data[month_key] += line.product_uom_qty

            history_str = '\n'.join([f'{k}: {v:.0f}' for k, v in sorted(monthly_data.items())])

            prompt = (
                f"داده‌های فروش ماهانه محصول «{rec.product_id.name}»:\n{history_str}\n\n"
                f"لطفاً تقاضای ماه بعد را پیش‌بینی کنید. فقط عدد را بنویسید."
            )
            try:
                result = service.chat_completion([
                    {'role': 'system', 'content': 'شما یک متخصص زنجیره تأمین هستید. فقط عدد پیش‌بینی را بنویسید.'},
                    {'role': 'user', 'content': prompt},
                ], max_tokens=50)
                forecast_qty = float(''.join(c for c in result if c.isdigit() or c == '.') or '0')
                rec.write({
                    'forecast_qty': forecast_qty,
                    'method': 'ai',
                    'confidence': 'medium',
                })
            except Exception as e:
                _logger.warning('AI forecast failed for product %s: %s', rec.product_id.id, e)


class OrcestSupplierRating(models.Model):
    _name = 'orcest.supplier.rating'
    _description = 'ارزیابی تأمین‌کننده'
    _order = 'overall_score desc'

    partner_id = fields.Many2one('res.partner', string='تأمین‌کننده', required=True)
    evaluation_date = fields.Date(string='تاریخ ارزیابی', default=fields.Date.today)
    evaluator_id = fields.Many2one('hr.employee', string='ارزیاب')

    quality_score = fields.Float(string='کیفیت (0-100)', default=70)
    delivery_score = fields.Float(string='تحویل به‌موقع (0-100)', default=70)
    price_score = fields.Float(string='قیمت رقابتی (0-100)', default=70)
    communication_score = fields.Float(string='ارتباط (0-100)', default=70)
    flexibility_score = fields.Float(string='انعطاف‌پذیری (0-100)', default=70)

    overall_score = fields.Float(
        string='امتیاز کل',
        compute='_compute_overall',
        store=True,
    )
    rating = fields.Selection([
        ('A', 'ممتاز (A)'),
        ('B', 'خوب (B)'),
        ('C', 'متوسط (C)'),
        ('D', 'ضعیف (D)'),
    ], string='رتبه', compute='_compute_overall', store=True)
    notes = fields.Text(string='یادداشت')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    @api.depends('quality_score', 'delivery_score', 'price_score', 'communication_score', 'flexibility_score')
    def _compute_overall(self):
        for rec in self:
            rec.overall_score = (
                rec.quality_score * 0.30 +
                rec.delivery_score * 0.25 +
                rec.price_score * 0.20 +
                rec.communication_score * 0.15 +
                rec.flexibility_score * 0.10
            )
            if rec.overall_score >= 85:
                rec.rating = 'A'
            elif rec.overall_score >= 70:
                rec.rating = 'B'
            elif rec.overall_score >= 55:
                rec.rating = 'C'
            else:
                rec.rating = 'D'
