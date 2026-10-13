# Firmware v2.5 Release Notes

**Released:** 28 August 2025.
**Display build:** D2.5.0. **Controller build:** C2.5.2.
**Applies to:** Ridge 500, Metro 300 and Cargo 700.

## What changed

### Display (D2.5.0)

- **Battery care mode.** An optional 80% charge limit under Menu > Battery. It reduces stress on the cells and helps the
  battery last longer if you rarely need the full range. This is the feature that the v2.3 notes planned for v2.4 and
  that the v2.4 notes moved to this release.
- **Load setting on the Cargo 700.** A new menu item, Menu > Load, with Empty, Half and Full. The range estimate now
  accounts for the weight you carry. This fixes the over-optimistic range reported in v2.3 and v2.4.
- **Automatic brightness** on the Dash 2 (Ridge 500 and Cargo 700). The Dash 1 on the Metro 300 is not affected.
- Charge cycle count and battery health shown together on one screen.

### Controller (C2.5.2)

- Charging stops at 80% when Battery care mode is on, and the charger light turns green at that point.
- Motor over-temperature protection (E08) is more gradual: the bike reduces power for a few seconds before cutting out.
- Better cold-weather start on the Cargo 700 at temperatures below 0 °C.

## How to update

Use the Fernhill Service app, battery above 50%. The update takes about 12 minutes.

## Known issues

1. **Auto-brightness flicker.** On the Dash 2 the screen can flicker at dusk when the light level hovers around the
   switching point. Workaround: set Menu > Display > Brightness to Manual. This is fixed in v2.6.
2. With Battery care mode on, the Ridge 500 range estimate still assumes a full charge, so it reads about 20% high.
   Fixed in v2.6.

## Checking your version and installing

1. On the display, hold Mode for two seconds and open Menu > Bike. The display and controller builds are listed there.
2. Compare them with the builds above. If the first part (for example 2.5) differs, you have a different release.
3. The Fernhill Service app also shows both build numbers under Bike.
4. If the display and controller show different release numbers, the bike shows E14 until both are updated.

Dealers can install this firmware with the diagnostic cable if you do not have a phone. The installation is free.
