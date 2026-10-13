# Firmware v2.1 Release Notes

**Released:** 19 September 2023.
**Display build:** D2.1.0. **Controller build:** C2.1.2.
**Applies to:** Ridge 500 and Metro 300.

## What changed

### Display (D2.1.0)

- E05 no longer appears when water on the remote pad presses a button. The pad must now be held for 3 seconds before the
  bike counts it as stuck. (Before, rain on the Metro 300 could show E05 mid-ride.)
- Trip distance now shows to one decimal place.
- The display remembers the last assist level after switching off.

### Controller (C2.1.2)

- **Fixes the walk-assist run-on** reported in v2.0. The motor now stops within 0.2 seconds of releasing the button.
- Lower idle current: the controller now sleeps after 5 minutes without use, saving charge during storage.
- Boost level on the Ridge 500 reaches full power about 0.3 seconds sooner.

## How to update

Use the Fernhill Service app, battery above 50%, or visit a dealer. The update takes about 10 minutes.

## Known issues

1. **False E06 in sunshine.** On a Ridge 500 ridden in direct sun at about 30 °C the display can show E06 (battery
   over-temperature) although the battery is within its limits. Park in shade for a few minutes and restart. This is
   fixed in v2.3.
2. The Metro 300 range estimate still resets after a battery swap (fixed in v2.4).

## Checking your version and installing

1. On the display, hold Mode for two seconds and open Menu > Bike. The display and controller builds are listed there.
2. Compare them with the builds above. If the first part (for example 2.1) differs, you have a different release.
3. The Fernhill Service app also shows both build numbers under Bike.
4. If the display and controller show different release numbers, the bike shows E14 until both are updated.

Dealers can install this firmware with the diagnostic cable if you do not have a phone. The installation is free.
