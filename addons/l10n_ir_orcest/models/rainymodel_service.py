# Part of Orcest AI. See LICENSE file for full copyright and licensing details.

import json
import logging
import requests

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class RainyModelService(models.AbstractModel):
    _name = 'l10n_ir_orcest.rainymodel'
    _description = 'سرویس هوش مصنوعی RainyModel'

    @api.model
    def _get_config(self):
        """Get RainyModel configuration from system parameters."""
        IrConfig = self.env['ir.config_parameter'].sudo()
        return {
            'url': IrConfig.get_param('l10n_ir_orcest.rainymodel_url', 'https://rm.orcest.ai/v1'),
            'api_key': IrConfig.get_param('l10n_ir_orcest.rainymodel_api_key', ''),
            'model': IrConfig.get_param('l10n_ir_orcest.rainymodel_model', 'rainymodel/auto'),
            'enabled': IrConfig.get_param('l10n_ir_orcest.rainymodel_enabled', 'True') == 'True',
        }

    @api.model
    def chat_completion(self, messages, model=None, max_tokens=1024, temperature=0.7):
        """Send a chat completion request to RainyModel API.

        Args:
            messages: List of message dicts [{role, content}]
            model: Model name (default from config)
            max_tokens: Maximum tokens in response
            temperature: Creativity parameter

        Returns:
            str: Assistant's response content
        """
        config = self._get_config()
        if not config['enabled']:
            raise UserError(_('سرویس هوش مصنوعی غیرفعال است. لطفاً از تنظیمات فعال کنید.'))

        if not config['api_key']:
            raise UserError(_('کلید API هوش مصنوعی تنظیم نشده است.'))

        url = f"{config['url']}/chat/completions"
        headers = {
            'Authorization': f"Bearer {config['api_key']}",
            'Content-Type': 'application/json',
        }
        payload = {
            'model': model or config['model'],
            'messages': messages,
            'max_tokens': max_tokens,
            'temperature': temperature,
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            data = response.json()
            return data['choices'][0]['message']['content']
        except requests.exceptions.Timeout:
            raise UserError(_('سرور هوش مصنوعی پاسخ نمی‌دهد. لطفاً دوباره تلاش کنید.'))
        except requests.exceptions.ConnectionError:
            raise UserError(_('اتصال به سرور هوش مصنوعی برقرار نشد.'))
        except Exception as e:
            _logger.exception('RainyModel API error')
            raise UserError(_('خطا در ارتباط با هوش مصنوعی: %s') % str(e))

    @api.model
    def summarize_text(self, text, lang='fa'):
        """Summarize text using RainyModel AI."""
        messages = [
            {'role': 'system', 'content': 'شما یک دستیار هوشمند فارسی‌زبان هستید. لطفاً متن زیر را خلاصه کنید.'},
            {'role': 'user', 'content': f'لطفاً این متن را خلاصه کنید:\n\n{text}'},
        ]
        return self.chat_completion(messages)

    @api.model
    def translate_text(self, text, source_lang='en', target_lang='fa'):
        """Translate text using RainyModel AI."""
        lang_names = {'fa': 'فارسی', 'en': 'انگلیسی', 'ar': 'عربی', 'tr': 'ترکی'}
        source = lang_names.get(source_lang, source_lang)
        target = lang_names.get(target_lang, target_lang)
        messages = [
            {'role': 'system', 'content': f'شما یک مترجم حرفه‌ای هستید. لطفاً متن زیر را از {source} به {target} ترجمه کنید.'},
            {'role': 'user', 'content': text},
        ]
        return self.chat_completion(messages)

    @api.model
    def analyze_financial_data(self, data_description):
        """Analyze financial data using RainyModel AI."""
        messages = [
            {
                'role': 'system',
                'content': (
                    'شما یک تحلیلگر مالی متخصص هستید که با استانداردهای حسابداری ایران آشنا هستید. '
                    'لطفاً داده‌های مالی زیر را تحلیل کنید و گزارش فارسی ارائه دهید. '
                    'در تحلیل خود بهای تمام‌شده، EBITDA، نسبت‌های مالی و شاخص‌های کلیدی را بررسی کنید.'
                ),
            },
            {'role': 'user', 'content': data_description},
        ]
        return self.chat_completion(messages, max_tokens=2048)

    @api.model
    def generate_invoice_description(self, product_name, quantity, unit_price):
        """Generate Persian invoice line description using AI."""
        messages = [
            {'role': 'system', 'content': 'شما یک دستیار حسابداری هستید. لطفاً شرح فاکتور حرفه‌ای به فارسی بنویسید.'},
            {
                'role': 'user',
                'content': f'شرح فاکتور برای محصول «{product_name}» به تعداد {quantity} و قیمت واحد {unit_price} بنویسید.',
            },
        ]
        return self.chat_completion(messages, max_tokens=256)

    @api.model
    def check_health(self):
        """Check RainyModel API health status."""
        config = self._get_config()
        try:
            url = config['url'].rstrip('/v1').rstrip('/')
            response = requests.get(f"{url}/health", timeout=10)
            return response.status_code == 200
        except Exception:
            return False
