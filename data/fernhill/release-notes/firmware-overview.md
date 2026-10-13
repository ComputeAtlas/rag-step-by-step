# Firmware Release History: Overview

A summary of every firmware version for the Ridge 500, Metro 300 and Cargo 700. For the details of a version read its release notes.
The display and the controller share one version number and must match (otherwise E14 appears).

| Version | Date | Headline changes |
|---|---|---|
| v2.0 | 6 March 2023 | First unified display and controller firmware. Four assist levels on the Ridge 500, three on the Metro 300, walk assist, auto-off after 10 minutes. Metro 300 update from 3 April 2023 |
| v2.1 | 19 September 2023 | Fixes the walk-assist run-on. E05 no longer triggered by rain |
| v2.2 | 12 June 2024 | Support for the Cargo 700 (Haul level). Charge cycle counter. New codes E15 and E16 |
| v2.3 | 20 November 2024 | Support for the B battery packs (FH-2291-B, FH-2219-B). Corrects how the cycle counter counts. New code E18 |
| v2.4 | 3 April 2025 | New code E17. Fixes the Metro 300 range reset after a battery swap |
| v2.5 | 28 August 2025 | Battery care mode (80% charge limit). Load menu on the Cargo 700. Automatic brightness on the Dash 2 |
| v2.6 | 12 January 2026 | Fixes auto-brightness flicker. Auto-off changed to 5 minutes. Service reminder. Range estimate with Battery care mode |

## Which version added which feature?

| Feature | First version |
|---|---|
| Walk assist | v2.0 |
| Haul level and Cargo 700 support | v2.2 |
| Charge cycle counter in the menu | v2.2 |
| Battery health percentage in the menu | v2.2 |
| Support for B battery packs | v2.3 |
| Battery care mode | v2.5 |
| Load menu (Cargo 700) | v2.5 |
| Automatic brightness (Dash 2) | v2.5 |
| Service reminder | v2.6 |
| 5-minute auto-off | v2.6 |

## Known issues still open

The only known issue open after v2.6 is the Cargo 700 service reminder, which counts 2,000 km instead of 1,500 km. It is
expected to be fixed in v2.7, which has not been released.

## Corrections made along the way

- The v2.2 notes described the cycle counter wrongly (one cycle per plug-in). The v2.3 notes corrected it: a cycle is counted
  when the battery has delivered its full capacity in total.
- The v2.3 notes said Battery care mode would come in v2.4. The v2.4 notes corrected this; the feature arrived in v2.5.
- The owner's manuals (Edition 4, December 2025) and the FAQ (18 December 2025) say the display switches off after 10 minutes; since
  v2.6 it is 5 minutes. They also name v2.5 as the latest version; v2.6 has since been released.
