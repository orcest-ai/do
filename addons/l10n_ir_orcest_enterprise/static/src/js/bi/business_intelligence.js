/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

/**
 * هوش تجاری اورکست
 * Business Intelligence Module for Orcest Enterprise
 */
class OrcestBusinessIntelligence extends Component {
    static template = "l10n_ir_orcest_enterprise.BusinessIntelligence";

    setup() {
        this.rpc = useService("rpc");
        this.state = useState({
            loading: true,
            reportType: "revenue",
            period: "monthly",
            data: [],
            summary: {},
        });

        onWillStart(async () => {
            await this.loadReport();
        });
    }

    async loadReport() {
        this.state.loading = true;
        try {
            const result = await this.rpc("/orcest/bi/report", {
                report_type: this.state.reportType,
                period: this.state.period,
            });
            this.state.data = result.data || [];
            this.state.summary = result.summary || {};
        } catch (e) {
            console.error("BI report load error:", e);
            this.state.data = [];
            this.state.summary = {};
        }
        this.state.loading = false;
    }

    async onReportTypeChange(type) {
        this.state.reportType = type;
        await this.loadReport();
    }

    async onPeriodChange(period) {
        this.state.period = period;
        await this.loadReport();
    }

    formatNumber(value) {
        if (!value) return "۰";
        return Math.abs(value).toLocaleString("fa-IR");
    }

    getStatusClass(status) {
        const classes = {
            excellent: "badge bg-success",
            good: "badge bg-info",
            warning: "badge bg-warning",
            critical: "badge bg-danger",
        };
        return classes[status] || "badge bg-secondary";
    }
}

registry.category("actions").add("orcest_business_intelligence", OrcestBusinessIntelligence);
