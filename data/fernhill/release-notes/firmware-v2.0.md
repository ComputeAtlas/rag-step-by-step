# Firmware v2.0 Release Notes

**Released:** 6 March 2023 (Ridge 500). Available for the Metro 300 from 3 April 2023.
**Display build:** D2.0.0. **Controller build:** C2.0.0.
**Applies to:** Ridge 500 (shipped with v2.0) and Metro 300 (previously on v1.8). The Cargo 700 did not exist yet.

From v2.0 the display and the controller share one version number. They must match, otherwise the display shows E14.

## What is new

### Display (D2.0.0)

- New menu structure: Battery, Display, Bike.
- Four assist levels on the Ridge 500 (Eco, Tour, Sport, Boost) and three on the Metro 300 (Eco, Tour, Sport).
- Walk assist at up to 6 km/h. On the Ridge 500 it uses its own button. On the Metro 300 you hold the minus button for
  two seconds.
- Range estimate shown in kilometres or miles, selectable under Menu > Display > Units.
- Auto-off: the display now switches off after 10 minutes of no use.
- Error codes E01 to E14, E19 and E20 are defined. They are listed in the owner's manual for each model. Codes E15 to E18
  were not yet used in this version.

### Controller (C2.0.0)

- Smoother start-up from standstill on the mid-drive motor.
- Motor cut-out at 25 km/h refined so the assist fades out over about 2 km/h instead of stopping abruptly.
- Brake cut-off response time shortened to under 0.2 seconds.
- The battery protocol for the 504 Wh and 324 Wh packs (original type, parts FH-2291-A and FH-2219-A).

## How to update

Use the Fernhill Service app with the battery above 50%, or visit a dealer. The update takes about 10 minutes.

## Known issues

1. **Walk assist runs on.** After you release the walk-assist button the motor keeps turning for about 1 second. This is
   fixed in v2.1.
2. On the Metro 300 the range estimate resets to 100% after the battery is removed and refitted, even if the battery is
   partly empty. This is fixed in v2.4.

## Checking your version and installing

1. On the display, hold Mode for two seconds and open Menu > Bike. The display and controller builds are listed there.
2. Compare them with the builds above. If the first part (for example 2.0) differs, you have a different release.
3. The Fernhill Service app also shows both build numbers under Bike.
4. If the display and controller show different release numbers, the bike shows E14 until both are updated.

Dealers can install this firmware with the diagnostic cable if you do not have a phone. The installation is free.
