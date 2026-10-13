# Firmware v2.4 Release Notes

**Released:** 3 April 2025.
**Display build:** D2.4.1. **Controller build:** C2.4.0.
**Applies to:** Ridge 500, Metro 300 and Cargo 700.

## Correction to the v2.3 release notes

The v2.3 notes said that Battery care mode (an optional 80% charge limit) would arrive in v2.4. **It did not.** We moved
the feature to v2.5 because it needed more testing on the Cargo 700. This release does not include it.

## What changed

### Display (D2.4.1)

- New error code **E17**: battery calibration drift. It appears when the battery's measured capacity and the controller's
  estimate disagree by more than 10%. To clear it, ride the battery below 10% and charge it to 100% without
  interruption.
- The Metro 300 keeps its range estimate when the battery is removed and refitted. This fixes the issue listed in
  v2.0, v2.1, v2.2 and v2.3.
- Menu > Bike shows the display and controller build numbers, to help support find mismatches.

### Controller (C2.4.0)

- Smoother Sport level on the Ridge 500: the power ramps up over 0.5 seconds instead of 0.3, which is kinder to the chain.
- Better battery calibration. The controller now relearns the battery's capacity every 20 charge cycles.
- Metro 300 hub motor runs about 4 °C cooler on long climbs.

## How to update

Use the Fernhill Service app, battery above 50%. The update takes about 12 minutes.

## Known issues

1. **Cargo 700 range estimate ignores the load.** With a heavy load the estimate can be up to 25% too optimistic. This is
   fixed in v2.5.
2. E17 can appear once after the update on batteries that have never been fully discharged. Follow the fix above.

## Checking your version and installing

1. On the display, hold Mode for two seconds and open Menu > Bike. The display and controller builds are listed there.
2. Compare them with the builds above. If the first part (for example 2.4) differs, you have a different release.
3. The Fernhill Service app also shows both build numbers under Bike.
4. If the display and controller show different release numbers, the bike shows E14 until both are updated.

Dealers can install this firmware with the diagnostic cable if you do not have a phone. The installation is free.
