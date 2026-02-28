/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

/**
 * داشبورد مدیریتی اورکست اینترپرایز
 * Executive Dashboard for Orcest Enterprise
 */
class OrcestExecutiveDashboard extends Component {
    static template = "l10n_ir_orcest_enterprise.ExecutiveDashboard";

    setup() {
        this.rpc = useService("rpc");
        this.action = useService("action");
        this.state = useState({
            loading: true,
            data: {},
            charts: {},
            period: "current_month",
        });

        onWillStart(async () => {
            await this.loadDashboardData();
        });
    }

    async loadDashboardData() {
        this.state.loading = true;
        try {
            const [data, charts] = await Promise.all([
                this.rpc("/orcest/dashboard/data", { period: this.state.period }),
                this.rpc("/orcest/dashboard/charts", { period: this.state.period }),
            ]);
            this.state.data = data;
            this.state.charts = charts;
        } catch (e) {
            console.error("Dashboard load error:", e);
        }
        this.state.loading = false;
    }

    async onPeriodChange(period) {
        this.state.period = period;
        await this.loadDashboardData();
    }

    formatCurrency(value) {
        if (!value) return "۰";
        const formatted = Math.abs(value).toLocaleString("fa-IR");
        return value < 0 ? `(${formatted})` : formatted;
    }

    formatPercent(value) {
        if (!value) return "۰٪";
        return `${value.toFixed(1).replace(/\d/g, (d) => "۰۱۲۳۴۵۶۷۸۹"[d])}٪`;
    }

    getChangeClass(value) {
        if (value > 0) return "text-success";
        if (value < 0) return "text-danger";
        return "text-muted";
    }

    getChangeIcon(value) {
        if (value > 0) return "fa-arrow-up";
        if (value < 0) return "fa-arrow-down";
        return "fa-minus";
    }

    openPayslips() {
        this.action.doAction("l10n_ir_orcest_enterprise.action_payslip");
    }

    openFinancialReports() {
        this.action.doAction("l10n_ir_orcest_enterprise.action_financial_report");
    }

    openBudgets() {
        this.action.doAction("l10n_ir_orcest_enterprise.action_budget");
    }

    openKPIs() {
        this.action.doAction("l10n_ir_orcest_enterprise.action_kpi");
    }
}

registry.category("actions").add("orcest_executive_dashboard", OrcestExecutiveDashboard);
