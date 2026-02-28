# Part of Orcest AI. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Enterprise features
    orcest_enable_payroll = fields.Boolean(
        string='ماژول حقوق و دستمزد',
        config_parameter='orcest.enterprise.enable_payroll',
        default=True,
    )
    orcest_enable_budget = fields.Boolean(
        string='مدیریت بودجه پیشرفته',
        config_parameter='orcest.enterprise.enable_budget',
        default=True,
    )
    orcest_enable_bi = fields.Boolean(
        string='هوش تجاری (BI)',
        config_parameter='orcest.enterprise.enable_bi',
        default=True,
    )
    orcest_enable_consolidation = fields.Boolean(
        string='صورت‌های مالی تلفیقی',
        config_parameter='orcest.enterprise.enable_consolidation',
        default=True,
    )
    orcest_enable_transfer_pricing = fields.Boolean(
        string='قیمت‌گذاری انتقالی',
        config_parameter='orcest.enterprise.enable_transfer_pricing',
        default=True,
    )
    orcest_enable_crm_ai = fields.Boolean(
        string='CRM هوشمند',
        config_parameter='orcest.enterprise.enable_crm_ai',
        default=True,
    )
    orcest_enable_supply_chain = fields.Boolean(
        string='زنجیره تأمین هوشمند',
        config_parameter='orcest.enterprise.enable_supply_chain',
        default=True,
    )
    orcest_enable_compliance = fields.Boolean(
        string='انطباق و حاکمیت',
        config_parameter='orcest.enterprise.enable_compliance',
        default=True,
    )
    orcest_enable_api_gateway = fields.Boolean(
        string='دروازه API سازمانی',
        config_parameter='orcest.enterprise.enable_api_gateway',
        default=True,
    )
    orcest_audit_trail = fields.Boolean(
        string='مسیر حسابرسی کامل',
        config_parameter='orcest.compliance.audit_trail',
        default=True,
    )
    orcest_data_retention_days = fields.Integer(
        string='نگهداری داده (روز)',
        config_parameter='orcest.compliance.data_retention_days',
        default=3650,
    )
