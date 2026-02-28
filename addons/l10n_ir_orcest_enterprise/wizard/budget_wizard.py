# Part of Orcest AI. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class BudgetCreateWizard(models.TransientModel):
    _name = 'orcest.budget.create.wizard'
    _description = 'ایجاد بودجه جدید'

    name = fields.Char(string='عنوان بودجه', required=True)
    jalali_year = fields.Char(string='سال شمسی', required=True)
    date_from = fields.Date(string='از تاریخ', required=True)
    date_to = fields.Date(string='تا تاریخ', required=True)
    department_id = fields.Many2one('hr.department', string='واحد سازمانی')
    copy_from_id = fields.Many2one('orcest.budget', string='کپی از بودجه')
    adjustment_percent = fields.Float(string='درصد تعدیل', help='درصد افزایش/کاهش نسبت به بودجه قبلی')

    def action_create_budget(self):
        budget = self.env['orcest.budget'].create({
            'name': self.name,
            'jalali_year': self.jalali_year,
            'fiscal_year': self.jalali_year,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'department_id': self.department_id.id if self.department_id else False,
        })

        if self.copy_from_id:
            factor = 1 + (self.adjustment_percent / 100)
            for line in self.copy_from_id.line_ids:
                self.env['orcest.budget.line'].create({
                    'budget_id': budget.id,
                    'category_id': line.category_id.id,
                    'account_id': line.account_id.id if line.account_id else False,
                    'name': line.name,
                    'm1': line.m1 * factor,
                    'm2': line.m2 * factor,
                    'm3': line.m3 * factor,
                    'm4': line.m4 * factor,
                    'm5': line.m5 * factor,
                    'm6': line.m6 * factor,
                    'm7': line.m7 * factor,
                    'm8': line.m8 * factor,
                    'm9': line.m9 * factor,
                    'm10': line.m10 * factor,
                    'm11': line.m11 * factor,
                    'm12': line.m12 * factor,
                })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'orcest.budget',
            'res_id': budget.id,
            'view_mode': 'form',
        }
