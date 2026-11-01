from odoo import api, fields, models

# Same keys Dawami uses for its own check-in verification.
CHECK_FLAGS = [
    ('ok', 'Inside the branch'),
    ('outside', 'Outside the branch'),
    ('no_location', 'No location'),
    ('mocked', 'Fake GPS'),
    ('new_device', 'New device'),
    ('mission', 'On a mission'),
]
SUSPICIOUS = ('outside', 'no_location', 'mocked', 'new_device')


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    dawami_recorded = fields.Boolean('From Dawami', index=True, copy=False, readonly=True,
                                     help='Recorded by an employee in the Dawami app.')
    dawami_in_flag = fields.Selection(CHECK_FLAGS, 'Check-in verification', copy=False, readonly=True)
    dawami_in_distance = fields.Integer('Check-in distance (m)', copy=False, readonly=True,
                                        help='Distance from the branch when checking in.')
    dawami_out_flag = fields.Selection(CHECK_FLAGS, 'Check-out verification', copy=False, readonly=True)
    dawami_out_distance = fields.Integer('Check-out distance (m)', copy=False, readonly=True,
                                         help='Distance from the branch when checking out.')
    dawami_suspicious = fields.Boolean('Needs review', compute='_compute_dawami_suspicious', store=True,
                                       help='Checked in or out outside the branch, without location, '
                                            'with fake GPS or from a new device.')

    @api.depends('dawami_in_flag', 'dawami_out_flag')
    def _compute_dawami_suspicious(self):
        for att in self:
            att.dawami_suspicious = att.dawami_in_flag in SUSPICIOUS or att.dawami_out_flag in SUSPICIOUS
