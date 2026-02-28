# Part of Orcest AI. See LICENSE file for full copyright and licensing details.

import json
from odoo import http, fields
from odoo.http import request


class OrcestDashboardController(http.Controller):

    @http.route('/orcest/dashboard/data', type='json', auth='user')
    def get_dashboard_data(self):
        """Get executive dashboard data."""
        company = request.env.company
        today = fields.Date.today()

        # Revenue this month
        first_day = today.replace(day=1)
        invoices = request.env['account.move'].search([
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('invoice_date', '>=', first_day),
            ('invoice_date', '<=', today),
            ('company_id', '=', company.id),
        ])
        revenue = sum(invoices.mapped('amount_total'))

        # Expenses this month
        bills = request.env['account.move'].search([
            ('move_type', '=', 'in_invoice'),
            ('state', '=', 'posted'),
            ('invoice_date', '>=', first_day),
            ('invoice_date', '<=', today),
            ('company_id', '=', company.id),
        ])
        expenses = sum(bills.mapped('amount_total'))

        # Employee count
        employees = request.env['hr.employee'].search_count([
            ('company_id', '=', company.id),
        ])

        # Open CRM leads
        leads = request.env['crm.lead'].search_count([
            ('type', '=', 'opportunity'),
            ('active', '=', True),
            ('company_id', '=', company.id),
        ])

        # Open projects
        projects = request.env['project.project'].search_count([
            ('company_id', '=', company.id),
            ('active', '=', True),
        ])

        # KPI summary
        kpi_values = request.env['orcest.kpi.value'].search([
            ('date', '>=', first_day),
            ('company_id', '=', company.id),
        ], order='date desc')
        kpi_summary = []
        seen_kpis = set()
        for kv in kpi_values:
            if kv.kpi_id.id not in seen_kpis:
                seen_kpis.add(kv.kpi_id.id)
                kpi_summary.append({
                    'name': kv.kpi_id.name,
                    'target': kv.target_value,
                    'actual': kv.actual_value,
                    'achievement': kv.achievement_percent,
                    'status': kv.status,
                    'unit': kv.kpi_id.unit,
                })

        # Jalali date
        from odoo.addons.l10n_ir_orcest.models.jalali_date_utils import (
            format_jalali_date, get_jalali_today, JALALI_MONTH_NAMES,
        )
        jy, jm, jd = get_jalali_today()
        jalali_today = f'{jd} {JALALI_MONTH_NAMES[jm-1]} {jy}'

        return {
            'jalali_today': jalali_today,
            'revenue': revenue,
            'expenses': expenses,
            'profit': revenue - expenses,
            'employees': employees,
            'leads': leads,
            'projects': projects,
            'currency': company.currency_id.symbol,
            'kpi_summary': kpi_summary[:10],
        }

    @http.route('/orcest/dashboard/charts', type='json', auth='user')
    def get_chart_data(self, chart_type='revenue', period='monthly'):
        """Get chart data for dashboard."""
        company = request.env.company
        today = fields.Date.today()

        from odoo.addons.l10n_ir_orcest.models.jalali_date_utils import (
            date_to_jalali, JALALI_MONTH_NAMES,
        )

        if chart_type == 'revenue':
            labels = []
            values = []
            for i in range(12, 0, -1):
                month_start = (today.replace(day=1) - __import__('datetime').timedelta(days=30 * i)).replace(day=1)
                month_end = (month_start.replace(day=28) + __import__('datetime').timedelta(days=4)).replace(day=1) - __import__('datetime').timedelta(days=1)

                invoices = request.env['account.move'].search([
                    ('move_type', '=', 'out_invoice'),
                    ('state', '=', 'posted'),
                    ('invoice_date', '>=', month_start),
                    ('invoice_date', '<=', month_end),
                    ('company_id', '=', company.id),
                ])
                jy, jm, _ = date_to_jalali(month_start)
                labels.append(JALALI_MONTH_NAMES[jm - 1])
                values.append(sum(invoices.mapped('amount_total')))

            return {'labels': labels, 'values': values, 'label': 'درآمد'}

        return {'labels': [], 'values': [], 'label': ''}
