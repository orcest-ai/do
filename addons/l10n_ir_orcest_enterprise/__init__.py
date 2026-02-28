# Part of Orcest AI. See LICENSE file for full copyright and licensing details.
from . import models
from . import controllers
from . import wizard


def _enterprise_post_init(env):
    """Post-install hook for enterprise module."""
    # Setup default budget categories
    _setup_budget_categories(env)
    # Setup compliance framework
    _setup_compliance(env)
    # Setup KPI definitions
    _setup_kpis(env)


def _setup_budget_categories(env):
    """Create default budget categories for Iranian accounting."""
    BudgetCategory = env['orcest.budget.category']
    categories = [
        ('revenue', 'درآمدها', 'income'),
        ('cogs', 'بهای تمام‌شده', 'expense'),
        ('opex', 'هزینه‌های عملیاتی', 'expense'),
        ('capex', 'هزینه‌های سرمایه‌ای', 'expense'),
        ('hr', 'هزینه‌های پرسنلی', 'expense'),
        ('marketing', 'هزینه‌های بازاریابی', 'expense'),
        ('rd', 'تحقیق و توسعه', 'expense'),
        ('financial', 'هزینه‌های مالی', 'expense'),
    ]
    for code, name, cat_type in categories:
        if not BudgetCategory.search([('code', '=', code)]):
            BudgetCategory.create({
                'code': code,
                'name': name,
                'category_type': cat_type,
            })


def _setup_compliance(env):
    """Setup compliance framework defaults."""
    IrConfig = env['ir.config_parameter'].sudo()
    IrConfig.set_param('orcest.compliance.audit_trail', 'True')
    IrConfig.set_param('orcest.compliance.data_retention_days', '3650')
    IrConfig.set_param('orcest.compliance.gdpr_enabled', 'True')


def _setup_kpis(env):
    """Create default KPI definitions."""
    KPI = env['orcest.kpi']
    kpis = [
        ('revenue_growth', 'رشد درآمد', 'financial', '%', 'higher_better'),
        ('gross_margin', 'حاشیه سود ناخالص', 'financial', '%', 'higher_better'),
        ('ebitda_margin', 'حاشیه EBITDA', 'financial', '%', 'higher_better'),
        ('net_margin', 'حاشیه سود خالص', 'financial', '%', 'higher_better'),
        ('current_ratio', 'نسبت جاری', 'financial', 'ratio', 'higher_better'),
        ('debt_equity', 'نسبت بدهی به حقوق صاحبان سهام', 'financial', 'ratio', 'lower_better'),
        ('customer_acquisition_cost', 'هزینه جذب مشتری', 'sales', 'currency', 'lower_better'),
        ('customer_lifetime_value', 'ارزش طول عمر مشتری', 'sales', 'currency', 'higher_better'),
        ('employee_satisfaction', 'رضایت کارکنان', 'hr', 'score', 'higher_better'),
        ('employee_turnover', 'نرخ ترک خدمت', 'hr', '%', 'lower_better'),
        ('on_time_delivery', 'تحویل به‌موقع', 'operations', '%', 'higher_better'),
        ('inventory_turnover', 'گردش موجودی', 'operations', 'ratio', 'higher_better'),
    ]
    for code, name, category, unit, direction in kpis:
        if not KPI.search([('code', '=', code)]):
            KPI.create({
                'code': code,
                'name': name,
                'category': category,
                'unit': unit,
                'direction': direction,
            })
