{
    'name': 'Dawami Connect - Mobile Attendance with GPS & Anti-Fraud | دوامي حضور وانصراف بالموبايل',
    'version': '19.0.1.0.4',
    'category': 'Human Resources/Attendances',
    'summary': 'Mobile check-in with branch geofence, fake-GPS and new-device detection, '
               'synced into Odoo Attendances by the Dawami app',
    'description': """
Dawami Connect links Odoo Attendances to Dawami (https://dawamihr.solutions),
a mobile attendance app for employees on Android, iPhone and the web.

* One-click setup: creates a dedicated integration user and API key.
* Employees and departments stay managed in Odoo; Dawami reads them.
* Check-ins and check-outs from the Dawami app are written to hr.attendance,
  with the employee's location.
* Each record carries Dawami's verification: inside or outside the branch
  circle, fake GPS, new device, or on an approved mission, with the distance.
* Filters and colour badges for suspicious attendance in the Odoo list view.

A Dawami subscription is required (free trial available).
""",
    'author': 'etriplesoft',
    'website': 'https://dawamihr.solutions',
    'live_test_url': 'https://dawamihr.solutions/?utm_source=odoo_apps',
    'license': 'LGPL-3',
    'depends': ['hr_attendance'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_attendance_views.xml',
        'wizard/dawami_setup_views.xml',
        'views/menus.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
}
