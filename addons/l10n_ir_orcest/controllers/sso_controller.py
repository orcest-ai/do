# Part of Orcest AI. See LICENSE file for full copyright and licensing details.

import json
import logging
import os
import secrets

import requests
import werkzeug.urls
from werkzeug.exceptions import BadRequest

from odoo import api, http, SUPERUSER_ID, _
from odoo.exceptions import AccessDenied
from odoo.http import request, Response
from odoo.modules.registry import Registry

from odoo.addons.auth_oauth.controllers.main import OAuthLogin, OAuthController
from odoo.addons.web.controllers.utils import ensure_db, _get_login_redirect_url

_logger = logging.getLogger(__name__)


class OrcestSSOLogin(OAuthLogin):
    """Override login to enforce Orcest SSO (login.orcest.ai) for all users."""

    @http.route()
    def web_login(self, *args, **kw):
        ensure_db()
        IrConfig = request.env['ir.config_parameter'].sudo()
        sso_only = IrConfig.get_param('l10n_ir_orcest.sso_only_login', 'True') == 'True'
        sso_enabled = IrConfig.get_param('l10n_ir_orcest.sso_enabled', 'False') == 'True'

        # If SSO-only mode is enabled, redirect to SSO provider automatically
        if sso_enabled and sso_only and request.httprequest.method == 'GET':
            if not request.session.uid and not request.params.get('oauth_error'):
                providers = self.list_providers()
                orcest_provider = None
                for p in providers:
                    if 'login.orcest.ai' in (p.get('auth_endpoint', '') or ''):
                        orcest_provider = p
                        break
                if orcest_provider and orcest_provider.get('auth_link'):
                    return request.redirect(orcest_provider['auth_link'])

        response = super().web_login(*args, **kw)
        return response


class OrcestSSOController(http.Controller):
    """Additional OIDC endpoints for Orcest SSO integration."""

    @http.route('/auth_orcest/callback', type='http', auth='none', readonly=False)
    def orcest_sso_callback(self, **kw):
        """Handle OIDC authorization code callback from login.orcest.ai."""
        code = kw.get('code')
        state = kw.get('state', '{}')
        error = kw.get('error')

        if error:
            _logger.warning('Orcest SSO error: %s - %s', error, kw.get('error_description', ''))
            return request.redirect('/web/login?oauth_error=2')

        if not code:
            return request.redirect('/web/login?oauth_error=2')

        try:
            state_data = json.loads(state) if state else {}
        except (json.JSONDecodeError, TypeError):
            state_data = {}

        ensure_db()
        IrConfig = request.env['ir.config_parameter'].sudo()
        sso_url = IrConfig.get_param('l10n_ir_orcest.sso_url', 'https://login.orcest.ai')
        client_id = IrConfig.get_param('l10n_ir_orcest.sso_client_id', 'do-orcest')
        client_secret = IrConfig.get_param('l10n_ir_orcest.sso_client_secret', '')

        if not client_secret:
            _logger.error('Orcest SSO client secret not configured')
            return request.redirect('/web/login?oauth_error=2')

        # Exchange authorization code for tokens
        redirect_uri = request.httprequest.url_root.rstrip('/') + '/auth_orcest/callback'
        try:
            token_response = requests.post(
                f'{sso_url}/oauth2/token',
                data={
                    'grant_type': 'authorization_code',
                    'code': code,
                    'redirect_uri': redirect_uri,
                    'client_id': client_id,
                    'client_secret': client_secret,
                },
                timeout=30,
            )
            token_response.raise_for_status()
            tokens = token_response.json()
        except Exception as e:
            _logger.exception('Failed to exchange authorization code: %s', e)
            return request.redirect('/web/login?oauth_error=2')

        access_token = tokens.get('access_token')
        if not access_token:
            return request.redirect('/web/login?oauth_error=2')

        # Get user info from SSO
        try:
            userinfo_response = requests.get(
                f'{sso_url}/oauth2/userinfo',
                headers={'Authorization': f'Bearer {access_token}'},
                timeout=15,
            )
            userinfo_response.raise_for_status()
            userinfo = userinfo_response.json()
        except Exception as e:
            _logger.exception('Failed to get user info: %s', e)
            return request.redirect('/web/login?oauth_error=2')

        email = userinfo.get('email', '')
        name = userinfo.get('name', email)

        if not email:
            return request.redirect('/web/login?oauth_error=2')

        # Find or create user in Odoo
        try:
            user = self._find_or_create_user(email, name, userinfo)
            if not user:
                return request.redirect('/web/login?oauth_error=3')

            # Authenticate the user
            credential = {
                'login': user.login,
                'token': access_token,
                'type': 'oauth_token',
            }
            auth_info = request.session.authenticate(request.env, credential)

            redirect = state_data.get('redirect', '/odoo')
            resp = request.redirect(_get_login_redirect_url(auth_info['uid'], redirect), 303)
            resp.autocorrect_location_header = False
            return resp
        except AccessDenied:
            _logger.info('SSO access denied for %s', email)
            return request.redirect('/web/login?oauth_error=3')
        except Exception:
            _logger.exception('SSO authentication error')
            return request.redirect('/web/login?oauth_error=2')

    def _find_or_create_user(self, email, name, userinfo):
        """Find existing user or create new one from SSO data."""
        Users = request.env['res.users'].sudo()

        # Try to find by email/login
        user = Users.search([('login', '=', email)], limit=1)
        if user:
            return user

        # Try by oauth_uid
        user = Users.search([('oauth_uid', '=', email)], limit=1)
        if user:
            return user

        # Auto-create user if SSO authenticated
        IrConfig = request.env['ir.config_parameter'].sudo()
        auto_create = IrConfig.get_param('l10n_ir_orcest.sso_auto_create_users', 'True') == 'True'

        if not auto_create:
            return None

        # Find Orcest SSO provider
        provider = request.env.ref('l10n_ir_orcest.provider_orcest_sso', raise_if_not_found=False)
        if not provider:
            return None

        # Create user
        try:
            user = Users.create({
                'name': name,
                'login': email,
                'email': email,
                'oauth_provider_id': provider.id,
                'oauth_uid': email,
                'oauth_access_token': '',
                'lang': 'fa_IR',
                'tz': 'Asia/Tehran',
                'groups_id': [(4, request.env.ref('base.group_user').id)],
            })
            _logger.info('Created new user from SSO: %s (%s)', name, email)
            return user
        except Exception:
            _logger.exception('Failed to create SSO user: %s', email)
            return None

    @http.route('/auth_orcest/logout', type='http', auth='user')
    def orcest_sso_logout(self, **kw):
        """Logout from both Odoo and Orcest SSO."""
        IrConfig = request.env['ir.config_parameter'].sudo()
        sso_url = IrConfig.get_param('l10n_ir_orcest.sso_url', 'https://login.orcest.ai')

        # Logout from Odoo
        request.session.logout()

        # Redirect to SSO logout
        redirect_uri = request.httprequest.url_root.rstrip('/')
        return request.redirect(f'{sso_url}/logout?redirect_uri={werkzeug.urls.url_quote(redirect_uri)}')
