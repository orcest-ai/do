# Part of Orcest AI. See LICENSE file for full copyright and licensing details.
from . import models
from . import controllers


def _l10n_ir_orcest_post_init(env):
    """Post-install hook to configure Iran localization defaults."""
    # Set default language to Persian
    lang = env['res.lang']._activate_lang('fa_IR')
    if lang:
        lang.write({
            'date_format': '%Y/%m/%d',
            'time_format': '%H:%M:%S',
            'direction': 'rtl',
            'week_start': '6',  # Saturday
            'grouping': '[3,0]',
            'decimal_point': '٫',
            'thousands_sep': '٬',
        })

    # Configure timezone for Iran
    IrConfig = env['ir.config_parameter'].sudo()
    IrConfig.set_param('l10n_ir_orcest.timezone', 'Asia/Tehran')
    IrConfig.set_param('l10n_ir_orcest.calendar_type', 'jalali')
    IrConfig.set_param('l10n_ir_orcest.first_day_of_week', '6')  # Saturday

    # Enable SSO provider if configured
    _setup_orcest_sso(env)
    # Setup RainyModel AI
    _setup_rainymodel(env)


def _setup_orcest_sso(env):
    """Configure Orcest SSO (login.orcest.ai) as OAuth provider."""
    import os
    provider = env.ref('l10n_ir_orcest.provider_orcest_sso', raise_if_not_found=False)
    if provider:
        client_id = os.environ.get('ORCEST_SSO_CLIENT_ID', 'do-orcest')
        client_secret = os.environ.get('ORCEST_SSO_CLIENT_SECRET', '')
        login_sso_url = os.environ.get('LOGIN_SSO_URL', 'https://login.orcest.ai')
        provider.write({
            'client_id': client_id,
            'auth_endpoint': f'{login_sso_url}/oauth2/authorize',
            'validation_endpoint': f'{login_sso_url}/oauth2/userinfo',
            'enabled': bool(client_secret),
        })
        if client_secret:
            env['ir.config_parameter'].sudo().set_param(
                'l10n_ir_orcest.sso_client_secret', client_secret
            )


def _setup_rainymodel(env):
    """Configure RainyModel AI integration."""
    import os
    IrConfig = env['ir.config_parameter'].sudo()
    rainymodel_url = os.environ.get('RAINYMODEL_BASE_URL', 'https://rm.orcest.ai/v1')
    rainymodel_key = os.environ.get('RAINYMODEL_API_KEY', '')
    IrConfig.set_param('l10n_ir_orcest.rainymodel_url', rainymodel_url)
    if rainymodel_key:
        IrConfig.set_param('l10n_ir_orcest.rainymodel_api_key', rainymodel_key)
