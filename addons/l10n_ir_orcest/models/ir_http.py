# Part of Orcest AI. See LICENSE file for full copyright and licensing details.

import json
from odoo import api, models
from odoo.http import request


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _get_translation_frontend_modules_name(cls):
        mods = super()._get_translation_frontend_modules_name()
        return mods + ['l10n_ir_orcest']

    def session_info(self):
        result = super().session_info()
        IrConfig = request.env['ir.config_parameter'].sudo()

        result['l10n_ir_orcest'] = {
            'calendar_type': IrConfig.get_param('l10n_ir_orcest.calendar_type', 'jalali'),
            'timezone': IrConfig.get_param('l10n_ir_orcest.timezone', 'Asia/Tehran'),
            'first_day_of_week': int(IrConfig.get_param('l10n_ir_orcest.first_day_of_week', '6')),
            'use_persian_digits': IrConfig.get_param('l10n_ir_orcest.use_persian_digits', 'True') == 'True',
            'rainymodel_enabled': IrConfig.get_param('l10n_ir_orcest.rainymodel_enabled', 'True') == 'True',
            'rainymodel_url': IrConfig.get_param('l10n_ir_orcest.rainymodel_url', 'https://rm.orcest.ai/v1'),
        }
        return result
