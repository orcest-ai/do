# Part of Orcest AI. See LICENSE file for full copyright and licensing details.

import json
import logging

from odoo import http, _
from odoo.http import request

_logger = logging.getLogger(__name__)


class L10nIrOrcestController(http.Controller):

    @http.route('/l10n_ir_orcest/jalali_date', type='json', auth='user')
    def get_jalali_date(self, date_str):
        """Convert a Gregorian date string to Jalali."""
        from ..models.jalali_date_utils import gregorian_to_jalali, format_jalali_date
        from datetime import date
        try:
            parts = date_str.split('-')
            d = date(int(parts[0]), int(parts[1]), int(parts[2]))
            jy, jm, jd = gregorian_to_jalali(d.year, d.month, d.day)
            return {
                'jalali': f'{jy}/{jm:02d}/{jd:02d}',
                'year': jy, 'month': jm, 'day': jd,
                'formatted': format_jalali_date(d),
            }
        except Exception as e:
            return {'error': str(e)}

    @http.route('/l10n_ir_orcest/gregorian_date', type='json', auth='user')
    def get_gregorian_date(self, jy, jm, jd):
        """Convert a Jalali date to Gregorian."""
        from ..models.jalali_date_utils import jalali_to_gregorian
        try:
            gy, gm, gd = jalali_to_gregorian(int(jy), int(jm), int(jd))
            return {
                'gregorian': f'{gy}-{gm:02d}-{gd:02d}',
                'year': gy, 'month': gm, 'day': gd,
            }
        except Exception as e:
            return {'error': str(e)}

    @http.route('/l10n_ir_orcest/ai/chat', type='json', auth='user')
    def ai_chat(self, messages, model=None):
        """Proxy for RainyModel AI chat completion."""
        try:
            service = request.env['l10n_ir_orcest.rainymodel']
            result = service.chat_completion(messages, model=model)
            return {'response': result}
        except Exception as e:
            return {'error': str(e)}

    @http.route('/l10n_ir_orcest/ai/summarize', type='json', auth='user')
    def ai_summarize(self, text):
        """Summarize text using RainyModel AI."""
        try:
            service = request.env['l10n_ir_orcest.rainymodel']
            result = service.summarize_text(text)
            return {'summary': result}
        except Exception as e:
            return {'error': str(e)}

    @http.route('/l10n_ir_orcest/ai/translate', type='json', auth='user')
    def ai_translate(self, text, source_lang='en', target_lang='fa'):
        """Translate text using RainyModel AI."""
        try:
            service = request.env['l10n_ir_orcest.rainymodel']
            result = service.translate_text(text, source_lang, target_lang)
            return {'translation': result}
        except Exception as e:
            return {'error': str(e)}

    @http.route('/l10n_ir_orcest/ai/health', type='json', auth='user')
    def ai_health(self):
        """Check RainyModel API health."""
        try:
            service = request.env['l10n_ir_orcest.rainymodel']
            healthy = service.check_health()
            return {'status': 'ok' if healthy else 'unreachable'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
