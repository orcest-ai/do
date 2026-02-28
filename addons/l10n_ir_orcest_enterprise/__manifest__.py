# Part of Orcest AI. See LICENSE file for full copyright and licensing details.
{
    'name': 'اورکست اینترپرایز - نسخه پیشرفته چند ملیتی',
    'version': '19.0.1.0.0',
    'category': 'Hidden/Tools',
    'summary': 'امکانات پیشرفته سازمانی، هوش تجاری، مدیریت منابع انسانی، حسابداری پیشرفته',
    'description': """
اورکست اینترپرایز - نسخه Premium و Advanced
=====================================================

ماژول جامع سازمانی برای شرکت‌های بزرگ چند ملیتی شامل:

امکانات مالی و حسابداری پیشرفته:
* صورت‌های مالی تلفیقی (Consolidated Financial Statements)
* داشبورد EBITDA و شاخص‌های کلیدی عملکرد
* قیمت‌گذاری انتقالی بین‌شرکتی (Transfer Pricing)
* مدیریت بودجه پیشرفته با تحلیل انحراف
* گزارش‌های مالیاتی و ارزش افزوده خودکار
* مدیریت چند ارزی پیشرفته با نرخ تسعیر لحظه‌ای
* بهای تمام‌شده ABC (Activity-Based Costing)
* تحلیل نقطه سربه‌سر

مدیریت منابع انسانی:
* حقوق و دستمزد مطابق قانون کار ایران
* بیمه تأمین اجتماعی و مالیات حقوق
* مدیریت مرخصی و حضور غیاب
* ارزیابی عملکرد کارکنان با هوش مصنوعی

هوش تجاری (BI):
* داشبورد مدیریتی لحظه‌ای
* تحلیل پیش‌بینی فروش با هوش مصنوعی
* گزارش‌ساز پیشرفته فارسی
* KPI و OKR سازمانی

CRM پیشرفته:
* امتیازدهی هوشمند سرنخ‌ها (AI Lead Scoring)
* پیش‌بینی خط لوله فروش
* تحلیل رفتار مشتری

مدیریت پروژه سازمانی:
* برنامه‌ریزی منابع و ظرفیت
* مدیریت ریسک پروژه
* گزارش پیشرفت با تقویم جلالی

زنجیره تأمین و انبار:
* پیش‌بینی تقاضا با هوش مصنوعی
* مدیریت موجودی پیشرفته
* ردیابی محموله و لجستیک

انطباق و حاکمیت:
* مسیر حسابرسی کامل
* مدیریت اسناد دیجیتال
* انطباق با مقررات ایران و بین‌المللی
* GDPR و حفاظت داده

امنیت سازمانی:
* احراز هویت دو مرحله‌ای پیشرفته
* دروازه API سازمانی
* رمزنگاری داده‌های حساس
* گزارش‌های امنیتی
    """,
    'author': 'Orcest AI',
    'website': 'https://do.orcest.ai',
    'countries': ['ir'],
    'depends': [
        'l10n_ir_orcest',
        'account',
        'hr',
        'project',
        'crm',
        'stock',
        'sale',
        'purchase',
        'calendar',
        'mail',
        'web',
        'base_setup',
        'analytic',
        'digest',
    ],
    'data': [
        'security/ir_groups.xml',
        'security/ir.model.access.csv',
        'data/enterprise_data.xml',
        'data/hr_payroll_data.xml',
        'data/budget_template_data.xml',
        'views/dashboard_views.xml',
        'views/hr_payroll_views.xml',
        'views/financial_report_views.xml',
        'views/budget_views.xml',
        'views/crm_views.xml',
        'views/project_views.xml',
        'views/compliance_views.xml',
        'views/supply_chain_views.xml',
        'views/res_config_settings_views.xml',
        'views/menu_views.xml',
        'report/financial_report_templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'l10n_ir_orcest_enterprise/static/src/js/dashboard/executive_dashboard.js',
            'l10n_ir_orcest_enterprise/static/src/js/bi/business_intelligence.js',
            'l10n_ir_orcest_enterprise/static/src/js/crm_ai/lead_scoring.js',
            'l10n_ir_orcest_enterprise/static/src/css/enterprise.scss',
            'l10n_ir_orcest_enterprise/static/src/xml/dashboard_templates.xml',
            'l10n_ir_orcest_enterprise/static/src/xml/bi_templates.xml',
        ],
    },
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'post_init_hook': '_enterprise_post_init',
}
