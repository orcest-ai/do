# Part of Orcest AI. See LICENSE file for full copyright and licensing details.

"""
مدیریت پروژه سازمانی پیشرفته
Enterprise Project Management with Resource Planning and Risk Management
"""

from odoo import api, fields, models, _


class ProjectProject(models.Model):
    _inherit = 'project.project'

    # === بودجه پروژه ===
    l10n_ir_budget_planned = fields.Monetary(string='بودجه برنامه‌ریزی شده', currency_field='currency_id')
    l10n_ir_budget_spent = fields.Monetary(string='بودجه مصرف‌شده', currency_field='currency_id')
    l10n_ir_budget_remaining = fields.Monetary(
        string='بودجه باقیمانده',
        compute='_compute_budget_remaining',
        currency_field='currency_id',
    )
    l10n_ir_budget_percent = fields.Float(
        string='درصد مصرف بودجه',
        compute='_compute_budget_remaining',
    )
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')

    # === مدیریت ریسک ===
    l10n_ir_risk_level = fields.Selection([
        ('low', 'کم'),
        ('medium', 'متوسط'),
        ('high', 'زیاد'),
        ('critical', 'بحرانی'),
    ], string='سطح ریسک', default='low')
    l10n_ir_risk_ids = fields.One2many('orcest.project.risk', 'project_id', string='ریسک‌ها')

    # === تاریخ شمسی ===
    l10n_ir_start_date_jalali = fields.Char(
        string='تاریخ شروع شمسی',
        compute='_compute_jalali_dates',
    )
    l10n_ir_end_date_jalali = fields.Char(
        string='تاریخ پایان شمسی',
        compute='_compute_jalali_dates',
    )

    # === تحلیل هوشمند ===
    l10n_ir_health_score = fields.Float(
        string='امتیاز سلامت پروژه',
        compute='_compute_health_score',
    )
    l10n_ir_health_status = fields.Selection([
        ('on_track', 'در مسیر'),
        ('at_risk', 'در معرض خطر'),
        ('off_track', 'منحرف'),
    ], string='وضعیت سلامت', compute='_compute_health_score')

    # === منابع ===
    l10n_ir_team_size = fields.Integer(string='اندازه تیم', compute='_compute_team_size')
    l10n_ir_total_hours_planned = fields.Float(string='ساعات برنامه‌ریزی شده')
    l10n_ir_total_hours_logged = fields.Float(string='ساعات ثبت‌شده')

    @api.depends('l10n_ir_budget_planned', 'l10n_ir_budget_spent')
    def _compute_budget_remaining(self):
        for project in self:
            project.l10n_ir_budget_remaining = project.l10n_ir_budget_planned - project.l10n_ir_budget_spent
            if project.l10n_ir_budget_planned:
                project.l10n_ir_budget_percent = (
                    project.l10n_ir_budget_spent / project.l10n_ir_budget_planned * 100
                )
            else:
                project.l10n_ir_budget_percent = 0

    def _compute_jalali_dates(self):
        from odoo.addons.l10n_ir_orcest.models.jalali_date_utils import format_jalali_date
        for project in self:
            project.l10n_ir_start_date_jalali = format_jalali_date(project.date_start) if project.date_start else ''
            project.l10n_ir_end_date_jalali = format_jalali_date(project.date) if project.date else ''

    def _compute_health_score(self):
        for project in self:
            score = 100
            # Budget overrun
            if project.l10n_ir_budget_percent > 90:
                score -= 30
            elif project.l10n_ir_budget_percent > 70:
                score -= 15
            # Risk level
            if project.l10n_ir_risk_level == 'critical':
                score -= 30
            elif project.l10n_ir_risk_level == 'high':
                score -= 20
            elif project.l10n_ir_risk_level == 'medium':
                score -= 10

            project.l10n_ir_health_score = max(0, score)
            if score >= 70:
                project.l10n_ir_health_status = 'on_track'
            elif score >= 40:
                project.l10n_ir_health_status = 'at_risk'
            else:
                project.l10n_ir_health_status = 'off_track'

    def _compute_team_size(self):
        for project in self:
            project.l10n_ir_team_size = len(project.task_ids.mapped('user_ids'))


class OrcestProjectRisk(models.Model):
    _name = 'orcest.project.risk'
    _description = 'ریسک پروژه'
    _order = 'risk_score desc'

    project_id = fields.Many2one('project.project', ondelete='cascade')
    name = fields.Char(string='عنوان ریسک', required=True)
    description = fields.Text(string='توضیحات')
    probability = fields.Selection([
        ('1', 'بسیار کم'),
        ('2', 'کم'),
        ('3', 'متوسط'),
        ('4', 'زیاد'),
        ('5', 'بسیار زیاد'),
    ], string='احتمال وقوع', required=True, default='3')
    impact = fields.Selection([
        ('1', 'ناچیز'),
        ('2', 'کم'),
        ('3', 'متوسط'),
        ('4', 'زیاد'),
        ('5', 'فاجعه‌بار'),
    ], string='شدت تأثیر', required=True, default='3')
    risk_score = fields.Integer(
        string='امتیاز ریسک',
        compute='_compute_risk_score',
        store=True,
    )
    risk_level = fields.Selection([
        ('low', 'کم'),
        ('medium', 'متوسط'),
        ('high', 'زیاد'),
        ('critical', 'بحرانی'),
    ], string='سطح ریسک', compute='_compute_risk_score', store=True)
    mitigation_plan = fields.Text(string='برنامه کاهش ریسک')
    owner_id = fields.Many2one('hr.employee', string='مسئول مدیریت ریسک')
    status = fields.Selection([
        ('identified', 'شناسایی شده'),
        ('mitigating', 'در حال مدیریت'),
        ('resolved', 'حل شده'),
        ('accepted', 'پذیرفته شده'),
    ], string='وضعیت', default='identified')

    @api.depends('probability', 'impact')
    def _compute_risk_score(self):
        for risk in self:
            score = int(risk.probability or 1) * int(risk.impact or 1)
            risk.risk_score = score
            if score >= 16:
                risk.risk_level = 'critical'
            elif score >= 9:
                risk.risk_level = 'high'
            elif score >= 4:
                risk.risk_level = 'medium'
            else:
                risk.risk_level = 'low'


class ProjectTask(models.Model):
    _inherit = 'project.task'

    l10n_ir_jalali_deadline = fields.Char(
        string='مهلت شمسی',
        compute='_compute_jalali_deadline',
    )
    l10n_ir_priority_score = fields.Integer(
        string='امتیاز اولویت',
        help='امتیاز اولویت بر اساس فوریت و اهمیت',
    )
    l10n_ir_estimated_cost = fields.Float(string='هزینه تخمینی')
    l10n_ir_actual_cost = fields.Float(string='هزینه واقعی')

    def _compute_jalali_deadline(self):
        from odoo.addons.l10n_ir_orcest.models.jalali_date_utils import format_jalali_date
        for task in self:
            task.l10n_ir_jalali_deadline = format_jalali_date(task.date_deadline) if task.date_deadline else ''
