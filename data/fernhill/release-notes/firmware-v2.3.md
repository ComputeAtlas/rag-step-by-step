# Firmware v2.3 Release Notes

**Released:** 20 November 2024.
**Display build:** D2.3.0. **Controller build:** C2.3.0.
**Applies to:** Ridge 500, Metro 300 and Cargo 700.

## Correction to the v2.2 release notes

The v2.2 notes said that the charge cycle counter adds one cycle each time you plug in the charger. **That was wrong**,
and the v2.2 counter over-counted. From v2.3 the counter adds one full cycle each time the battery has delivered a total
amount of energy equal to its full capacity. Two top-ups of 50% therefore count as one cycle. When you update to v2.3
the controller recalculates the count from the battery's energy record, so a count that was too high is corrected
automatically. The cycle count is used when a battery warranty claim is assessed.

## What changed

### Display (D2.3.0)

- New error code **E18** (battery not locked fully).
- Battery health percentage is refreshed after every full charge.

### Controller (C2.3.0)

- **Support for the new B battery packs**, FH-2291-B (Ridge 500) and FH-2219-B (Metro 300). They use a new
  battery-management protocol. Bikes built before 2025 that are on v2.2 or earlier show **E01** when a B pack is fitted.
  Updating to v2.3 or later fixes it. Bikes built from 2025 ship with B packs and a firmware version that supports them.
  The original A packs (FH-2291-A, FH-2219-A) keep working with every version.
- Fixes the false E06 in direct sunshine on the Ridge 500.
- The Cargo 700 motor is more careful with torque in the first second after standing start with a heavy load.

## Planned for the next release

Battery care mode, an optional 80% charge limit, is planned for v2.4.

## How to update

Use the Fernhill Service app, battery above 50%. The update takes about 12 minutes.

## Known issues

1. **Cargo 700 range estimate ignores the load.** With a heavy load the estimate can be up to 25% too optimistic. A fix is
   in preparation.
2. The Metro 300 range estimate resets after a battery swap (fixed in v2.4).

## Checking your version and installing

1. On the display, hold Mode for two seconds and open Menu > Bike. The display and controller builds are listed there.
2. Compare them with the builds above. If the first part (for example 2.3) differs, you have a different release.
3. The Fernhill Service app also shows both build numbers under Bike.
4. If the display and controller show different release numbers, the bike shows E14 until both are updated.

Dealers can install this firmware with the diagnostic cable if you do not have a phone. The installation is free.
