# Odoo Apps by etriplesoft

Modules published on [apps.odoo.com](https://apps.odoo.com). One branch per Odoo version
(`18.0`, `19.0`), with each module as a top-level folder, as the Odoo Apps scanner expects.

| Module | What it does | Price |
|---|---|---|
| [dawami_connect](dawami_connect) | Mobile attendance with branch geofence and fake-GPS detection, synced into Odoo Attendances by [Dawami](https://dawamihr.solutions) | Free |

## Adding a module

1. Put the module folder at the root of each version branch, with `version` like `18.0.1.0.0`.
2. Include `static/description/icon.png`, `static/description/index.html` and a `license`
   (`LGPL-3` for free modules, `OPL-1` for paid ones).
3. Run its tests on that Odoo version, then push. Odoo Apps rescans the branch.
