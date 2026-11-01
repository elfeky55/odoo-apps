from datetime import datetime, time

import pytz

from odoo import _, api, fields, models
from odoo.exceptions import UserError

CONNECT_LOGIN = 'dawami.connect'
KEY_NAME = 'Dawami Connect'
DAWAMI_SITE = 'https://dawamihr.solutions/?utm_source=odoo_apps'
DAWAMI_HR = 'https://app.dawamihr.solutions/hr'
# What the integration user needs: read employees and departments, write attendances.
CONNECT_GROUPS = ('base.group_user', 'hr.group_hr_user', 'hr_attendance.group_hr_attendance_manager')


class DawamiSetup(models.TransientModel):
    _name = 'dawami.connect.setup'
    _description = 'Dawami Connect setup'

    state = fields.Selection([('draft', 'Not generated'), ('key', 'Key generated')], default='draft')
    odoo_url = fields.Char('Odoo URL', readonly=True)
    database = fields.Char('Database', readonly=True)
    login = fields.Char('User', readonly=True)
    api_key = fields.Char('API key', readonly=True)
    connected = fields.Boolean('Integration user active', readonly=True)
    dawami_today = fields.Integer('Check-ins from Dawami today', readonly=True)
    suspicious_today = fields.Integer('Need review today', readonly=True)
    last_dawami = fields.Datetime('Last record from Dawami', readonly=True)

    def _compute_display_name(self):
        for wiz in self:
            wiz.display_name = _('Dawami Connect')

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        user = self._connect_user()
        Att = self.env['hr.attendance'].sudo()
        tz = pytz.timezone(self.env.user.tz or 'UTC')
        start = tz.localize(datetime.combine(fields.Date.context_today(self), time.min))
        start = start.astimezone(pytz.utc).replace(tzinfo=None)
        today = [('dawami_recorded', '=', True), ('check_in', '>=', start)]
        last = Att.search([('dawami_recorded', '=', True)], order='check_in desc', limit=1)
        res.update({
            'odoo_url': self.env['ir.config_parameter'].sudo().get_param('web.base.url'),
            'database': self.env.cr.dbname,
            'login': CONNECT_LOGIN,
            'connected': bool(user and user.active),
            'dawami_today': Att.search_count(today),
            'suspicious_today': Att.search_count(today + [('dawami_suspicious', '=', True)]),
            'last_dawami': last.check_in,
        })
        return res

    def _connect_user(self):
        return self.env['res.users'].sudo().with_context(active_test=False).search(
            [('login', '=', CONNECT_LOGIN)], limit=1)

    def _ensure_user(self):
        Users = self.env['res.users'].sudo().with_context(active_test=False, no_reset_password=True)
        groups_field = 'groups_id' if 'groups_id' in Users._fields else 'group_ids'
        group_ids = [self.env.ref(x).id for x in CONNECT_GROUPS]
        user = self._connect_user()
        if user:
            user.write({'active': True, groups_field: [(4, gid) for gid in group_ids]})
        else:
            user = Users.create({
                'name': 'Dawami Connect',
                'login': CONNECT_LOGIN,
                'company_id': self.env.company.id,
                'company_ids': [(6, 0, self.env.user.company_ids.ids)],
                groups_field: [(6, 0, group_ids)],
            })
        return user

    def _old_keys(self, user):
        return self.env['res.users.apikeys'].sudo().search([('user_id', '=', user.id), ('name', '=', KEY_NAME)])

    def action_generate(self):
        """Create (or reuse) the integration user and give it a new API key.

        Any earlier Dawami Connect key of that user stops working, so a lost key is
        replaced by generating again.
        """
        self.ensure_one()
        if not self.env.user.has_group('base.group_system'):
            raise UserError(_('Only an administrator can create the Dawami connection.'))
        user = self._ensure_user()
        keys = self._old_keys(user)
        if keys:
            keys.with_user(user).sudo()._remove()
        key = self.env['res.users.apikeys'].with_user(user).sudo()._generate('rpc', KEY_NAME, False)
        self.write({'state': 'key', 'api_key': key, 'connected': True})
        return True

    def action_disconnect(self):
        self.ensure_one()
        if not self.env.user.has_group('base.group_system'):
            raise UserError(_('Only an administrator can remove the Dawami connection.'))
        user = self._connect_user()
        if user:
            keys = self._old_keys(user)
            if keys:
                keys.with_user(user).sudo()._remove()
            user.active = False
        self.write({'state': 'draft', 'api_key': False, 'connected': False})
        return True

    def action_open_review(self):
        action = self.env['ir.actions.act_window']._for_xml_id('dawami_connect.action_dawami_attendance')
        action['context'] = {'search_default_dawami_review': 1}
        return action

    def action_open_dawami(self):
        return {'type': 'ir.actions.act_url', 'url': DAWAMI_HR, 'target': 'new'}

    def action_try_dawami(self):
        return {'type': 'ir.actions.act_url', 'url': DAWAMI_SITE, 'target': 'new'}
