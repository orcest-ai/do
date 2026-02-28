# Part of Orcest AI. See LICENSE file for full copyright and licensing details.

"""
دروازه API سازمانی و امنیت پیشرفته
Enterprise API Gateway & Advanced Security

- مدیریت کلیدهای API
- محدودیت نرخ درخواست (Rate Limiting)
- لاگ دسترسی API
- رمزنگاری داده‌های حساس
"""

import hashlib
import secrets
import time
from collections import defaultdict

from odoo import api, fields, models, _
from odoo.exceptions import AccessDenied


class OrcestAPIKey(models.Model):
    _name = 'orcest.api.key'
    _description = 'کلید API سازمانی'
    _order = 'create_date desc'

    name = fields.Char(string='نام', required=True)
    key = fields.Char(string='کلید API', readonly=True, copy=False)
    key_prefix = fields.Char(string='پیشوند کلید', compute='_compute_prefix')
    user_id = fields.Many2one('res.users', string='کاربر', required=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    active = fields.Boolean(default=True)
    expires_at = fields.Datetime(string='تاریخ انقضا')
    scopes = fields.Selection([
        ('read', 'فقط خواندن'),
        ('write', 'خواندن و نوشتن'),
        ('admin', 'مدیریت کامل'),
    ], string='سطح دسترسی', default='read', required=True)
    allowed_ips = fields.Text(
        string='IP‌های مجاز',
        help='هر IP در یک خط. خالی = همه مجاز',
    )
    rate_limit = fields.Integer(
        string='سقف درخواست (در دقیقه)',
        default=60,
    )
    total_requests = fields.Integer(string='تعداد کل درخواست‌ها', readonly=True)
    last_used = fields.Datetime(string='آخرین استفاده', readonly=True)
    description = fields.Text(string='توضیحات')

    def _compute_prefix(self):
        for rec in self:
            rec.key_prefix = rec.key[:12] + '...' if rec.key else ''

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('key'):
                vals['key'] = 'orcest_' + secrets.token_hex(32)
        return super().create(vals_list)

    def action_regenerate_key(self):
        """Regenerate API key."""
        for rec in self:
            rec.key = 'orcest_' + secrets.token_hex(32)
            # Audit log
            self.env['orcest.audit.log'].log_action(
                'security', 'orcest.api.key', rec.id, rec.name,
                description=f'کلید API «{rec.name}» بازتولید شد.',
                severity='warning',
            )

    @api.model
    def validate_key(self, key, ip_address=''):
        """Validate an API key and return associated user."""
        api_key = self.sudo().search([
            ('key', '=', key),
            ('active', '=', True),
        ], limit=1)

        if not api_key:
            raise AccessDenied(_('کلید API نامعتبر است.'))

        # Check expiry
        if api_key.expires_at and api_key.expires_at < fields.Datetime.now():
            raise AccessDenied(_('کلید API منقضی شده است.'))

        # Check IP restriction
        if api_key.allowed_ips:
            allowed = [ip.strip() for ip in api_key.allowed_ips.split('\n') if ip.strip()]
            if allowed and ip_address and ip_address not in allowed:
                raise AccessDenied(_('دسترسی از این IP مجاز نیست.'))

        # Update usage stats
        api_key.sudo().write({
            'total_requests': api_key.total_requests + 1,
            'last_used': fields.Datetime.now(),
        })

        return api_key.user_id


class OrcestAPILog(models.Model):
    _name = 'orcest.api.log'
    _description = 'لاگ دسترسی API'
    _order = 'create_date desc'

    api_key_id = fields.Many2one('orcest.api.key', string='کلید API')
    endpoint = fields.Char(string='آدرس API')
    method = fields.Selection([
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('DELETE', 'DELETE'),
        ('PATCH', 'PATCH'),
    ], string='متد')
    ip_address = fields.Char(string='آدرس IP')
    user_agent = fields.Char(string='مرورگر')
    status_code = fields.Integer(string='کد وضعیت')
    response_time_ms = fields.Integer(string='زمان پاسخ (ms)')
    request_body_size = fields.Integer(string='حجم درخواست (بایت)')
    response_body_size = fields.Integer(string='حجم پاسخ (بایت)')
    error_message = fields.Text(string='پیام خطا')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)


class OrcestSecurityPolicy(models.Model):
    _name = 'orcest.security.policy'
    _description = 'سیاست امنیتی'

    name = fields.Char(string='عنوان', required=True)
    policy_type = fields.Selection([
        ('password', 'رمز عبور'),
        ('session', 'نشست'),
        ('access', 'دسترسی'),
        ('data', 'داده'),
        ('api', 'API'),
    ], string='نوع سیاست', required=True)
    description = fields.Html(string='توضیحات')
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    # Password policy
    min_password_length = fields.Integer(string='حداقل طول رمز عبور', default=12)
    require_uppercase = fields.Boolean(string='حروف بزرگ الزامی', default=True)
    require_numbers = fields.Boolean(string='اعداد الزامی', default=True)
    require_special_chars = fields.Boolean(string='کاراکترهای خاص الزامی', default=True)
    password_expiry_days = fields.Integer(string='مدت اعتبار رمز (روز)', default=90)
    max_login_attempts = fields.Integer(string='حداکثر تلاش ورود ناموفق', default=5)
    lockout_duration_minutes = fields.Integer(string='مدت قفل حساب (دقیقه)', default=30)

    # Session policy
    session_timeout_minutes = fields.Integer(string='مهلت نشست (دقیقه)', default=120)
    concurrent_sessions = fields.Integer(string='نشست‌های همزمان', default=3)

    # Data policy
    data_retention_days = fields.Integer(string='نگهداری داده (روز)', default=3650)
    encrypt_sensitive_data = fields.Boolean(string='رمزنگاری داده‌های حساس', default=True)
