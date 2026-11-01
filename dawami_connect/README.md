# Dawami Connect

Links Odoo Attendances to [Dawami](https://dawamihr.solutions), a mobile attendance app.
Employees check in from their phones; Dawami verifies the branch geofence, fake GPS and
device, and writes the attendance into `hr.attendance` with that verification.

## What the module adds

- **Dawami → Connection** (administrators): creates the integration user `dawami.connect`
  (HR officer + Attendance administrator) and an API key, shown once to copy into Dawami.
  Generating again revokes the old key. *Disconnect* revokes the key and archives the user.
- Fields on `hr.attendance`: `dawami_recorded`, `dawami_in_flag` / `dawami_out_flag`
  (`ok`, `outside`, `no_location`, `mocked`, `new_device`, `mission`),
  `dawami_in_distance` / `dawami_out_distance`, and the stored `dawami_suspicious`.
- Badges in the attendance list and form, and filters: From Dawami, Needs review,
  Outside the branch, Fake GPS, New device.
- **Dawami → Attendance from Dawami** (attendance officers).
- English and Arabic.

Dawami detects the module with `fields_get` and sends the flags only when they exist,
so Odoo databases without it keep receiving check-in and check-out times only.

## Compatibility

Odoo 18.0 and 19.0, Community and Enterprise, on-premise and Odoo.sh.
(Odoo Online cannot install third-party modules; where its API is available, Dawami still sends check-in and check-out times.)

## Tests

```
odoo -d <db> -i dawami_connect --test-tags /dawami_connect --stop-after-init
```

## License

LGPL-3. Author: etriplesoft.
