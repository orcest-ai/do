# Part of Orcest AI. See LICENSE file for full copyright and licensing details.

"""
انطباق، حاکمیت و مسیر حسابرسی
Compliance, Governance & Audit Trail

- مسیر حسابرسی کامل
- مدیریت اسناد دیجیتال
- GDPR و حفاظت داده
- انطباق با مقررات ایران
"""

from odoo import api, fields, models, _
import hashlib
import json


class OrcestAuditLog(models.Model):
    _name = 'orcest.audit.log'
    _description = 'مسیر حسابرسی'
    _order = 'create_date desc'
    _rec_name = 'action'

    action = fields.Selection([
        ('create', 'ایجاد'),
        ('write', 'ویرایش'),
        ('unlink', 'حذف'),
        ('approve', 'تأیید'),
        ('reject', 'رد'),
        ('login', 'ورود'),
        ('logout', 'خروج'),
        ('export', 'صدور گزارش'),
        ('access', 'دسترسی'),
        ('security', 'امنیتی'),
    ], string='عملیات', required=True, index=True)
    model_name = fields.Char(string='مدل', index=True)
    record_id = fields.Integer(string='شناسه رکورد')
    record_name = fields.Char(string='نام رکورد')
    user_id = fields.Many2one('res.users', string='کاربر', default=lambda self: self.env.user)
    ip_address = fields.Char(string='آدرس IP')
    user_agent = fields.Char(string='مرورگر')
    old_values = fields.Text(string='مقادیر قبلی')
    new_values = fields.Text(string='مقادیر جدید')
    description = fields.Text(string='توضیحات')
    severity = fields.Selection([
        ('info', 'اطلاعاتی'),
        ('warning', 'هشدار'),
        ('error', 'خطا'),
        ('critical', 'بحرانی'),
    ], string='شدت', default='info')
    checksum = fields.Char(string='کد یکپارچگی', compute='_compute_checksum', store=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    @api.depends('action', 'model_name', 'record_id', 'user_id', 'create_date')
    def _compute_checksum(self):
        for log in self:
            data = f"{log.action}|{log.model_name}|{log.record_id}|{log.user_id.id}|{log.create_date}"
            log.checksum = hashlib.sha256(data.encode()).hexdigest()[:32]

    @api.model
    def log_action(self, action, model_name='', record_id=0, record_name='',
                   old_values=None, new_values=None, description='',
                   severity='info', ip_address='', user_agent=''):
        """Create an audit log entry."""
        return self.sudo().create({
            'action': action,
            'model_name': model_name,
            'record_id': record_id,
            'record_name': record_name,
            'old_values': json.dumps(old_values, ensure_ascii=False, default=str) if old_values else '',
            'new_values': json.dumps(new_values, ensure_ascii=False, default=str) if new_values else '',
            'description': description,
            'severity': severity,
            'ip_address': ip_address,
            'user_agent': user_agent,
        })


class OrcestDocument(models.Model):
    _name = 'orcest.document'
    _description = 'مدیریت اسناد دیجیتال'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(string='عنوان سند', required=True, tracking=True)
    document_type = fields.Selection([
        ('contract', 'قرارداد'),
        ('invoice', 'فاکتور'),
        ('receipt', 'رسید'),
        ('report', 'گزارش'),
        ('letter', 'نامه'),
        ('memo', 'یادداشت اداری'),
        ('policy', 'خط مشی'),
        ('procedure', 'رویه'),
        ('certificate', 'گواهینامه'),
        ('license', 'مجوز'),
        ('other', 'سایر'),
    ], string='نوع سند', required=True, tracking=True)
    document_number = fields.Char(string='شماره سند', copy=False)
    attachment_ids = fields.Many2many(
        'ir.attachment',
        string='فایل‌های پیوست',
    )
    state = fields.Selection([
        ('draft', 'پیش‌نویس'),
        ('review', 'بررسی'),
        ('approved', 'تأیید شده'),
        ('archived', 'بایگانی'),
        ('expired', 'منقضی'),
    ], string='وضعیت', default='draft', tracking=True)
    department_id = fields.Many2one('hr.department', string='واحد سازمانی')
    responsible_id = fields.Many2one('hr.employee', string='مسئول')
    approver_id = fields.Many2one('hr.employee', string='تأیید‌کننده')
    expiry_date = fields.Date(string='تاریخ انقضا')
    jalali_expiry = fields.Char(string='انقضا شمسی', compute='_compute_jalali_expiry')
    confidentiality = fields.Selection([
        ('public', 'عمومی'),
        ('internal', 'داخلی'),
        ('confidential', 'محرمانه'),
        ('secret', 'سری'),
    ], string='سطح محرمانگی', default='internal')
    tags = fields.Char(string='برچسب‌ها')
    description = fields.Html(string='توضیحات')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    version = fields.Integer(string='نسخه', default=1)

    def _compute_jalali_expiry(self):
        from odoo.addons.l10n_ir_orcest.models.jalali_date_utils import format_jalali_date
        for doc in self:
            doc.jalali_expiry = format_jalali_date(doc.expiry_date) if doc.expiry_date else ''

    def action_submit_review(self):
        self.write({'state': 'review'})

    def action_approve(self):
        self.write({'state': 'approved'})
        # Audit log
        self.env['orcest.audit.log'].log_action(
            'approve', 'orcest.document', self.id, self.name,
            description=f'سند «{self.name}» تأیید شد.',
        )

    def action_archive(self):
        self.write({'state': 'archived'})


class OrcestComplianceChecklist(models.Model):
    _name = 'orcest.compliance.checklist'
    _description = 'چک‌لیست انطباق'
    _inherit = ['mail.thread']
    _order = 'due_date'

    name = fields.Char(string='عنوان', required=True)
    framework = fields.Selection([
        ('iran_tax', 'مالیاتی ایران'),
        ('iran_labor', 'قانون کار ایران'),
        ('iran_social_security', 'تأمین اجتماعی'),
        ('iran_vat', 'ارزش افزوده'),
        ('gdpr', 'GDPR / حفاظت داده'),
        ('iso_9001', 'ISO 9001'),
        ('iso_27001', 'ISO 27001'),
        ('soc2', 'SOC 2'),
        ('internal', 'سیاست‌های داخلی'),
        ('custom', 'سفارشی'),
    ], string='چارچوب', required=True)
    status = fields.Selection([
        ('pending', 'در انتظار'),
        ('in_progress', 'در حال انجام'),
        ('compliant', 'منطبق'),
        ('non_compliant', 'غیرمنطبق'),
        ('waived', 'صرف‌نظر شده'),
    ], string='وضعیت', default='pending', tracking=True)
    responsible_id = fields.Many2one('hr.employee', string='مسئول')
    due_date = fields.Date(string='مهلت')
    evidence = fields.Text(string='مستندات و شواهد')
    remediation_plan = fields.Text(string='برنامه اصلاحی')
    priority = fields.Selection([
        ('low', 'کم'),
        ('medium', 'متوسط'),
        ('high', 'زیاد'),
        ('critical', 'بحرانی'),
    ], string='اولویت', default='medium')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
