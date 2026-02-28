# Part of Orcest AI. See LICENSE file for full copyright and licensing details.

import json
import time
import logging

from odoo import http
from odoo.http import request, Response
from odoo.exceptions import AccessDenied

_logger = logging.getLogger(__name__)


class OrcestAPIGateway(http.Controller):
    """Enterprise API Gateway for external integrations."""

    def _authenticate_api(self):
        """Authenticate API request using API key."""
        auth_header = request.httprequest.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            key = auth_header[7:]
        else:
            key = request.params.get('api_key', '')

        if not key:
            return None

        try:
            ip = request.httprequest.remote_addr
            user = request.env['orcest.api.key'].sudo().validate_key(key, ip)
            return user
        except AccessDenied:
            return None

    def _log_request(self, api_key_id, endpoint, method, status_code, start_time, error=''):
        """Log API request."""
        try:
            request.env['orcest.api.log'].sudo().create({
                'api_key_id': api_key_id,
                'endpoint': endpoint,
                'method': method,
                'ip_address': request.httprequest.remote_addr,
                'user_agent': request.httprequest.headers.get('User-Agent', ''),
                'status_code': status_code,
                'response_time_ms': int((time.time() - start_time) * 1000),
                'error_message': error,
            })
        except Exception:
            pass

    @http.route('/api/v1/health', type='http', auth='none', methods=['GET'], csrf=False)
    def api_health(self):
        """Health check endpoint."""
        return Response(
            json.dumps({'status': 'ok', 'service': 'do.orcest.ai'}),
            content_type='application/json',
            status=200,
        )

    @http.route('/api/v1/company', type='http', auth='none', methods=['GET'], csrf=False)
    def api_company_info(self):
        """Get company information."""
        start = time.time()
        user = self._authenticate_api()
        if not user:
            return Response(
                json.dumps({'error': 'Unauthorized'}),
                content_type='application/json',
                status=401,
            )

        company = user.company_id
        data = {
            'id': company.id,
            'name': company.name,
            'currency': company.currency_id.name,
            'country': company.country_id.name if company.country_id else '',
        }
        return Response(
            json.dumps(data, ensure_ascii=False),
            content_type='application/json',
            status=200,
        )

    @http.route('/api/v1/invoices', type='http', auth='none', methods=['GET'], csrf=False)
    def api_invoices(self):
        """List invoices via API."""
        start = time.time()
        user = self._authenticate_api()
        if not user:
            return Response(
                json.dumps({'error': 'Unauthorized'}),
                content_type='application/json',
                status=401,
            )

        limit = int(request.params.get('limit', 20))
        offset = int(request.params.get('offset', 0))

        invoices = request.env['account.move'].with_user(user).search([
            ('move_type', 'in', ['out_invoice', 'in_invoice']),
            ('state', '=', 'posted'),
        ], limit=limit, offset=offset, order='invoice_date desc')

        data = []
        for inv in invoices:
            data.append({
                'id': inv.id,
                'name': inv.name,
                'type': inv.move_type,
                'date': str(inv.invoice_date),
                'jalali_date': inv.l10n_ir_jalali_date or '',
                'partner': inv.partner_id.name,
                'amount_total': inv.amount_total,
                'currency': inv.currency_id.name,
                'state': inv.state,
            })

        return Response(
            json.dumps({'invoices': data, 'count': len(data)}, ensure_ascii=False, default=str),
            content_type='application/json',
            status=200,
        )

    @http.route('/api/v1/kpi', type='http', auth='none', methods=['GET'], csrf=False)
    def api_kpi(self):
        """Get KPI values via API."""
        start = time.time()
        user = self._authenticate_api()
        if not user:
            return Response(
                json.dumps({'error': 'Unauthorized'}),
                content_type='application/json',
                status=401,
            )

        kpis = request.env['orcest.kpi'].with_user(user).search([])
        data = []
        for kpi in kpis:
            latest = kpi.value_ids[:1]
            data.append({
                'code': kpi.code,
                'name': kpi.name,
                'category': kpi.category,
                'unit': kpi.unit,
                'latest_value': latest.actual_value if latest else 0,
                'target': latest.target_value if latest else 0,
                'status': latest.status if latest else '',
            })

        return Response(
            json.dumps({'kpis': data}, ensure_ascii=False),
            content_type='application/json',
            status=200,
        )
