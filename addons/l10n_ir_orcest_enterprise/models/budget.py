# Part of Orcest AI. See LICENSE file for full copyright and licensing details.

"""
مدیریت بودجه پیشرفته سازمانی
Advanced Enterprise Budget Management

Includes:
- بودجه‌بندی بر اساس مراکز هزینه
- تحلیل انحراف بودجه
- بودجه پروژه‌ای
- بودجه ارزی چندگانه
- پیش‌بینی هوشمند بودجه
"""

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class OrcestBudgetCategory(models.Model):
    _name = 'orcest.budget.category'
    _description = 'گروه بودجه'
    _order = 'code'

    name = fields.Char(string='عنوان', required=True)
    code = fields.Char(string='کد', required=True)
    category_type = fields.Selection([
        ('income', 'درآمد'),
        ('expense', 'هزینه'),
    ], string='نوع', required=True)
    parent_id = fields.Many2one('orcest.budget.category', string='گروه والد')
    active = fields.Boolean(default=True)


class OrcestBudget(models.Model):
    _name = 'orcest.budget'
    _description = 'بودجه سازمانی'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'fiscal_year desc'

    name = fields.Char(string='عنوان بودجه', required=True, tracking=True)
    fiscal_year = fields.Char(string='سال مالی', required=True)
    jalali_year = fields.Char(string='سال شمسی')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    department_id = fields.Many2one('hr.department', string='واحد سازمانی')
    state = fields.Selection([
        ('draft', 'پیش‌نویس'),
        ('submitted', 'ارسال شده'),
        ('approved', 'تأیید شده'),
        ('revised', 'بازنگری'),
        ('closed', 'بسته شده'),
    ], default='draft', tracking=True)

    date_from = fields.Date(string='از تاریخ', required=True)
    date_to = fields.Date(string='تا تاریخ', required=True)

    line_ids = fields.One2many('orcest.budget.line', 'budget_id', string='اقلام بودجه')

    total_budget_income = fields.Monetary(
        string='جمع بودجه درآمد',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
    )
    total_budget_expense = fields.Monetary(
        string='جمع بودجه هزینه',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
    )
    total_actual_income = fields.Monetary(
        string='جمع عملکرد درآمد',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
    )
    total_actual_expense = fields.Monetary(
        string='جمع عملکرد هزینه',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
    )
    variance = fields.Monetary(
        string='انحراف بودجه',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
    )
    variance_percent = fields.Float(
        string='درصد انحراف',
        compute='_compute_totals',
        store=True,
    )

    notes = fields.Html(string='یادداشت‌ها')

    @api.depends('line_ids.budget_amount', 'line_ids.actual_amount')
    def _compute_totals(self):
        for budget in self:
            income_lines = budget.line_ids.filtered(lambda l: l.category_id.category_type == 'income')
            expense_lines = budget.line_ids.filtered(lambda l: l.category_id.category_type == 'expense')
            budget.total_budget_income = sum(income_lines.mapped('budget_amount'))
            budget.total_budget_expense = sum(expense_lines.mapped('budget_amount'))
            budget.total_actual_income = sum(income_lines.mapped('actual_amount'))
            budget.total_actual_expense = sum(expense_lines.mapped('actual_amount'))

            total_budget = budget.total_budget_income - budget.total_budget_expense
            total_actual = budget.total_actual_income - budget.total_actual_expense
            budget.variance = total_actual - total_budget
            budget.variance_percent = (
                (budget.variance / abs(total_budget) * 100) if total_budget else 0
            )

    def action_submit(self):
        self.write({'state': 'submitted'})

    def action_approve(self):
        self.write({'state': 'approved'})

    def action_revise(self):
        self.write({'state': 'revised'})

    def action_close(self):
        self.write({'state': 'closed'})

    def action_update_actuals(self):
        """Update actual amounts from accounting entries."""
        for budget in self:
            for line in budget.line_ids:
                line._compute_actual_amount()


class OrcestBudgetLine(models.Model):
    _name = 'orcest.budget.line'
    _description = 'اقلام بودجه'
    _order = 'category_id, sequence'

    budget_id = fields.Many2one('orcest.budget', ondelete='cascade')
    sequence = fields.Integer(default=10)
    category_id = fields.Many2one('orcest.budget.category', string='گروه بودجه', required=True)
    account_id = fields.Many2one('account.account', string='حساب')
    name = fields.Char(string='شرح')
    currency_id = fields.Many2one('res.currency', related='budget_id.currency_id')

    # Monthly breakdown
    m1 = fields.Monetary(string='ماه ۱', currency_field='currency_id')
    m2 = fields.Monetary(string='ماه ۲', currency_field='currency_id')
    m3 = fields.Monetary(string='ماه ۳', currency_field='currency_id')
    m4 = fields.Monetary(string='ماه ۴', currency_field='currency_id')
    m5 = fields.Monetary(string='ماه ۵', currency_field='currency_id')
    m6 = fields.Monetary(string='ماه ۶', currency_field='currency_id')
    m7 = fields.Monetary(string='ماه ۷', currency_field='currency_id')
    m8 = fields.Monetary(string='ماه ۸', currency_field='currency_id')
    m9 = fields.Monetary(string='ماه ۹', currency_field='currency_id')
    m10 = fields.Monetary(string='ماه ۱۰', currency_field='currency_id')
    m11 = fields.Monetary(string='ماه ۱۱', currency_field='currency_id')
    m12 = fields.Monetary(string='ماه ۱۲', currency_field='currency_id')

    budget_amount = fields.Monetary(
        string='بودجه مصوب',
        compute='_compute_budget_amount',
        store=True,
        currency_field='currency_id',
    )
    actual_amount = fields.Monetary(
        string='عملکرد',
        currency_field='currency_id',
    )
    variance = fields.Monetary(
        string='انحراف',
        compute='_compute_variance',
        store=True,
        currency_field='currency_id',
    )
    variance_percent = fields.Float(
        string='درصد انحراف',
        compute='_compute_variance',
        store=True,
    )
    consumption_percent = fields.Float(
        string='درصد مصرف',
        compute='_compute_variance',
        store=True,
    )

    @api.depends('m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'm7', 'm8', 'm9', 'm10', 'm11', 'm12')
    def _compute_budget_amount(self):
        for line in self:
            line.budget_amount = sum([
                line.m1, line.m2, line.m3, line.m4, line.m5, line.m6,
                line.m7, line.m8, line.m9, line.m10, line.m11, line.m12,
            ])

    @api.depends('budget_amount', 'actual_amount')
    def _compute_variance(self):
        for line in self:
            line.variance = line.actual_amount - line.budget_amount
            if line.budget_amount:
                line.variance_percent = (line.variance / abs(line.budget_amount)) * 100
                line.consumption_percent = (line.actual_amount / abs(line.budget_amount)) * 100
            else:
                line.variance_percent = 0
                line.consumption_percent = 0

    def _compute_actual_amount(self):
        """Compute actual amount from posted journal entries."""
        for line in self:
            if not line.account_id or not line.budget_id.date_from:
                continue
            domain = [
                ('account_id', '=', line.account_id.id),
                ('date', '>=', line.budget_id.date_from),
                ('date', '<=', line.budget_id.date_to),
                ('parent_state', '=', 'posted'),
            ]
            move_lines = self.env['account.move.line'].search(domain)
            if line.category_id.category_type == 'income':
                line.actual_amount = sum(move_lines.mapped('credit')) - sum(move_lines.mapped('debit'))
            else:
                line.actual_amount = sum(move_lines.mapped('debit')) - sum(move_lines.mapped('credit'))
