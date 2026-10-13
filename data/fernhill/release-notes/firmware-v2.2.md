# Firmware v2.2 Release Notes

**Released:** 12 June 2024.
**Display build:** D2.2.0. **Controller build:** C2.2.1.
**Applies to:** Ridge 500, Metro 300 and Cargo 700. The Cargo 700 ships with v2.2.

## What changed

### Display (D2.2.0)

- **Support for the Cargo 700.** Adds the Haul assist level (250% motor help) and a 4 km/h walk assist for the heavier bike.
- **Charge cycle counter.** The new item Menu > Battery > Cycles shows how many charge cycles the battery has had. The
  counter adds one cycle each time you plug in the charger and charge the battery. (This description was wrong. See the
  correction in the v2.3 notes.)
- New error codes **E15** (controller over-current) and **E16** (battery cells out of balance).
- Battery health is shown as a percentage under Menu > Battery.

### Controller (C2.2.1)

- A 48 V profile for the Cargo 700 battery (FH-2292-A).
- Improved torque response on the Ridge 500 when the rider stands on the pedals.
- Brake cut-off switch on the Cargo 700 handles either lever.
- Shift-assist sensing (Ridge 500 and Cargo 700) now cuts the motor for 0.15 seconds while you change gear. E12 is raised
  if the sensor stops responding.

## How to update

Use the Fernhill Service app, battery above 50%. The update takes about 12 minutes. A dealer can do it with the service
cable.

## Known issues

1. **Cycle counter over-counts.** The counter adds a cycle for every charging session, even a short top-up. A battery used
   with many small charges therefore shows a higher count than the real wear. This is corrected in v2.3.
2. False E06 in sunshine on the Ridge 500 (fixed in v2.3).
3. The Metro 300 range estimate resets after a battery swap (fixed in v2.4).

## Checking your version and installing

1. On the display, hold Mode for two seconds and open Menu > Bike. The display and controller builds are listed there.
2. Compare them with the builds above. If the first part (for example 2.2) differs, you have a different release.
3. The Fernhill Service app also shows both build numbers under Bike.
4. If the display and controller show different release numbers, the bike shows E14 until both are updated.

Dealers can install this firmware with the diagnostic cable if you do not have a phone. The installation is free.
