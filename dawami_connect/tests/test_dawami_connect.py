from datetime import datetime, timedelta

from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestDawamiConnect(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env['hr.employee'].create({'name': 'Mona Test'})
        cls.Setup = cls.env['dawami.connect.setup']
        cls.Keys = cls.env['res.users.apikeys']

    def _key_uid(self, key):
        return self.Keys._check_credentials(scope='rpc', key=key)

    def test_generate_creates_user_and_working_key(self):
        wiz = self.Setup.create({})
        wiz.action_generate()
        user = self.env['res.users'].search([('login', '=', 'dawami.connect')])
        self.assertTrue(user.active)
        self.assertTrue(user.has_group('hr_attendance.group_hr_attendance_manager'))
        self.assertTrue(user.has_group('hr.group_hr_user'))
        self.assertFalse(user.has_group('base.group_system'))
        self.assertEqual(wiz.state, 'key')
        self.assertEqual(self._key_uid(wiz.api_key), user.id)
        self.assertEqual(wiz.database, self.env.cr.dbname)

    def test_new_key_revokes_old_one(self):
        wiz = self.Setup.create({})
        wiz.action_generate()
        old = wiz.api_key
        wiz.action_generate()
        self.assertNotEqual(old, wiz.api_key)
        self.assertFalse(self._key_uid(old))
        self.assertTrue(self._key_uid(wiz.api_key))
        user = self.env['res.users'].search([('login', '=', 'dawami.connect')])
        self.assertEqual(self.Keys.sudo().search_count([('user_id', '=', user.id)]), 1)

    def test_disconnect(self):
        wiz = self.Setup.create({})
        wiz.action_generate()
        key = wiz.api_key
        wiz.action_disconnect()
        self.assertFalse(self._key_uid(key))
        user = self.env['res.users'].with_context(active_test=False).search([('login', '=', 'dawami.connect')])
        self.assertFalse(user.active)
        # connecting again reuses the same user
        wiz.action_generate()
        self.assertTrue(user.active)
        self.assertEqual(self._key_uid(wiz.api_key), user.id)

    def test_only_admin_can_generate(self):
        hr = self.env['res.users'].create({
            'name': 'HR officer', 'login': 'hr.officer.dawami',
            'groups_id' if 'groups_id' in self.env['res.users']._fields else 'group_ids':
                [(6, 0, [self.env.ref('base.group_user').id,
                         self.env.ref('hr_attendance.group_hr_attendance_officer').id])],
        })
        wiz = self.Setup.create({})
        with self.assertRaises(UserError):
            wiz.with_user(hr).action_generate()

    def test_integration_user_writes_attendance_with_flags(self):
        """What Dawami does with the key: create an attendance with its verification."""
        wiz = self.Setup.create({})
        wiz.action_generate()
        user = self.env['res.users'].search([('login', '=', 'dawami.connect')])
        Att = self.env['hr.attendance'].with_user(user)
        now = datetime.now().replace(microsecond=0)
        att = Att.create({
            'employee_id': self.employee.id, 'check_in': now - timedelta(hours=2), 'check_out': now,
            'dawami_recorded': True, 'dawami_in_flag': 'mocked', 'dawami_in_distance': 1200,
            'dawami_out_flag': 'ok', 'dawami_out_distance': 20,
            'in_latitude': 30.0444, 'in_longitude': 31.2357,
        })
        self.assertTrue(att.dawami_suspicious)
        att.write({'dawami_in_flag': 'mission'})
        self.assertFalse(att.dawami_suspicious)
        fields_info = Att.fields_get(['dawami_in_flag'], ['type'])
        self.assertIn('dawami_in_flag', fields_info)

    def test_dashboard_counts(self):
        now = datetime.now().replace(microsecond=0)
        Att = self.env['hr.attendance']
        before = self.Setup.create({})
        Att.create({'employee_id': self.employee.id, 'check_in': now - timedelta(minutes=5),
                    'dawami_recorded': True, 'dawami_in_flag': 'outside'})
        wiz = self.Setup.create({})
        self.assertEqual(wiz.dawami_today, before.dawami_today + 1)
        self.assertEqual(wiz.suspicious_today, before.suspicious_today + 1)
        self.assertGreaterEqual(wiz.last_dawami, now - timedelta(minutes=5))
        action = wiz.action_open_review()
        self.assertEqual(action['res_model'], 'hr.attendance')
