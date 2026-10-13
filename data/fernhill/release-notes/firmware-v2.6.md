# Firmware v2.6 Release Notes

**Released:** 12 January 2026.
**Display build:** D2.6.0. **Controller build:** C2.6.0.
**Applies to:** Ridge 500, Metro 300 and Cargo 700. This is the latest release at the time of writing.

## What changed

### Display (D2.6.0)

- **Fixes the auto-brightness flicker** on the Dash 2 reported in v2.5.
- **Auto-off is now 5 minutes.** Until v2.5 the display switched itself off after 10 minutes without use. The owner's
  manuals (Edition 4, December 2025) and some FAQ answers still say 10 minutes; the correct figure from v2.6 onwards is
  5 minutes.
- **Service reminder.** Menu > Bike now shows when the next service is due, matched to the distance and time intervals in
  each model's manual: 2,000 km or 12 months for the Ridge 500, 2,500 km or 12 months for the Metro 300, and
  1,500 km or 6 months for the Cargo 700.
- Battery care mode can be switched on from the quick menu, with a short press of the mode button and the plus button.

### Controller (C2.6.0)

- **Range estimate with Battery care mode** now takes the 80% limit into account. This fixes the v2.5 known issue.
- Slightly higher maximum charging current when the battery is warm (about 25 °C), cutting charging time by about 5 minutes.
- Faster response of the brake cut-off on all models.

## How to update

Use the Fernhill Service app, battery above 50%. The update takes about 12 minutes.

## Known issues

1. **Cargo 700 service reminder.** The reminder on the Cargo 700 counts 2,000 km, not the 1,500 km interval in the
   manual. Please follow the manual (1,500 km or 6 months). This will be fixed in v2.7, which has not been released yet.

## Checking your version and installing

1. On the display, hold Mode for two seconds and open Menu > Bike. The display and controller builds are listed there.
2. Compare them with the builds above. If the first part (for example 2.6) differs, you have a different release.
3. The Fernhill Service app also shows both build numbers under Bike.
4. If the display and controller show different release numbers, the bike shows E14 until both are updated.

Dealers can install this firmware with the diagnostic cable if you do not have a phone. The installation is free.
