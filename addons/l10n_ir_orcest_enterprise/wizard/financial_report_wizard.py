# Part of Orcest AI. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class FinancialReportWizard(models.TransientModel):
    _name = 'orcest.financial.report.wizard'
    _description = 'ایجاد گزارش مالی'

    report_type = fields.Selection([
        ('income_statement', 'صورت سود و زیان'),
        ('balance_sheet', 'ترازنامه'),
        ('cash_flow', 'صورت جریان وجوه نقد'),
        ('ebitda', 'تحلیل EBITDA'),
        ('cost_analysis', 'تحلیل بهای تمام‌شده'),
        ('ratio_analysis', 'نسبت‌های مالی'),
        ('consolidated', 'صورت‌های مالی تلفیقی'),
    ], string='نوع گزارش', required=True, default='income_statement')
    date_from = fields.Date(string='از تاریخ', required=True)
    date_to = fields.Date(string='تا تاریخ', required=True)
    company_ids = fields.Many2many('res.company', string='شرکت‌ها')
    auto_generate = fields.Boolean(string='تولید خودکار از دفاتر', default=True)
    include_ai_analysis = fields.Boolean(string='تحلیل هوش مصنوعی', default=True)

    def action_generate_report(self):
        report = self.env['orcest.financial.report'].create({
            'name': dict(self._fields['report_type'].selection).get(self.report_type, ''),
            'report_type': self.report_type,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'company_ids': [(6, 0, self.company_ids.ids)] if self.company_ids else False,
        })

        if self.auto_generate:
            report.action_generate()

        if self.include_ai_analysis:
            try:
                report.action_ai_analyze()
            except Exception:
                pass  # Don't fail if AI is unavailable

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'orcest.financial.report',
            'res_id': report.id,
            'view_mode': 'form',
        }
