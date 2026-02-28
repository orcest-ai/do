# Part of Orcest AI. See LICENSE file for full copyright and licensing details.

"""
قیمت‌گذاری انتقالی بین‌شرکتی
Transfer Pricing for Intercompany Transactions

- ثبت و مدیریت معاملات بین‌شرکتی
- بررسی قیمت منصفانه (arm's length)
- مستندسازی قیمت‌گذاری انتقالی
- گزارش‌های انتقالی
"""

from odoo import api, fields, models, _


class OrcestTransferPricing(models.Model):
    _name = 'orcest.transfer.pricing'
    _description = 'قیمت‌گذاری انتقالی'
    _inherit = ['mail.thread']
    _order = 'transaction_date desc'

    name = fields.Char(string='شماره معامله', required=True, copy=False, default='جدید')
    transaction_date = fields.Date(string='تاریخ معامله', required=True)
    jalali_date = fields.Char(string='تاریخ شمسی', compute='_compute_jalali', store=True)

    seller_company_id = fields.Many2one('res.company', string='شرکت فروشنده', required=True)
    buyer_company_id = fields.Many2one('res.company', string='شرکت خریدار', required=True)

    transaction_type = fields.Selection([
        ('goods', 'کالا'),
        ('services', 'خدمات'),
        ('royalty', 'حق امتیاز'),
        ('interest', 'بهره'),
        ('management_fee', 'کارمزد مدیریت'),
        ('cost_sharing', 'تسهیم هزینه'),
    ], string='نوع معامله', required=True)

    pricing_method = fields.Selection([
        ('cup', 'قیمت قابل مقایسه غیروابسته (CUP)'),
        ('resale', 'قیمت فروش مجدد'),
        ('cost_plus', 'بهای تمام‌شده به اضافه سود'),
        ('tnmm', 'روش حاشیه سود خالص (TNMM)'),
        ('profit_split', 'تسهیم سود'),
    ], string='روش قیمت‌گذاری', required=True)

    currency_id = fields.Many2one('res.currency', string='ارز معامله', required=True)
    amount = fields.Monetary(string='مبلغ معامله', currency_field='currency_id')
    arm_length_amount = fields.Monetary(string='مبلغ منصفانه', currency_field='currency_id')
    variance = fields.Monetary(string='انحراف', compute='_compute_variance', store=True, currency_field='currency_id')
    variance_percent = fields.Float(string='درصد انحراف', compute='_compute_variance', store=True)

    is_compliant = fields.Boolean(string='منطبق با اصل منصفانه', compute='_compute_compliance', store=True)
    compliance_notes = fields.Text(string='یادداشت انطباق')

    state = fields.Selection([
        ('draft', 'پیش‌نویس'),
        ('documented', 'مستندسازی شده'),
        ('reviewed', 'بررسی شده'),
        ('approved', 'تأیید شده'),
    ], default='draft', tracking=True)

    description = fields.Text(string='شرح معامله')
    supporting_docs = fields.Many2many('ir.attachment', string='مستندات')
    economic_analysis = fields.Text(string='تحلیل اقتصادی')
    comparability_analysis = fields.Text(string='تحلیل قابلیت مقایسه')

    @api.depends('transaction_date')
    def _compute_jalali(self):
        from odoo.addons.l10n_ir_orcest.models.jalali_date_utils import format_jalali_date
        for rec in self:
            rec.jalali_date = format_jalali_date(rec.transaction_date) if rec.transaction_date else ''

    @api.depends('amount', 'arm_length_amount')
    def _compute_variance(self):
        for rec in self:
            rec.variance = rec.amount - rec.arm_length_amount
            if rec.arm_length_amount:
                rec.variance_percent = (rec.variance / abs(rec.arm_length_amount)) * 100
            else:
                rec.variance_percent = 0

    @api.depends('variance_percent')
    def _compute_compliance(self):
        for rec in self:
            # Generally within +/- 25% is considered arm's length
            rec.is_compliant = abs(rec.variance_percent) <= 25

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'جدید') == 'جدید':
                vals['name'] = self.env['ir.sequence'].next_by_code('orcest.transfer.pricing') or 'جدید'
        return super().create(vals_list)
