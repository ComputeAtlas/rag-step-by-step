# Fernhill Display Error Codes Compared Across Models

Edition January 2026, written for firmware v2.5 and v2.6. Every Fernhill display shows a fault as the letter E and two digits,
from E01 to E20. The numbers are shared across the range, but some of them mean different things on different models,
and some are not used on every model. This page puts the three meanings side by side. For the fix, always read the table in the owner's manual of your own model.

## All codes side by side

| Code | Ridge 500 | Metro 300 | Cargo 700 |
|---|---|---|---|
| E01 | Battery not detected: no communication with the battery pack | Battery not detected: no communication with the battery pack | Battery not detected: no communication with the battery pack |
| E02 | Motor not responding | Motor not responding | Motor not responding |
| E03 | Torque sensor signal out of range | Cadence sensor signal missing | Torque sensor signal out of range |
| E04 | Speed sensor: no signal | Hub motor speed signal missing | Speed sensor: no signal |
| E05 | Walk-assist button pressed at switch-on | Remote pad button stuck at switch-on | Walk-assist button pressed at switch-on |
| E06 | Battery over-temperature (above 60 °C) | Battery over-temperature (above 60 °C) | Battery over-temperature (above 60 °C) |
| E07 | Battery too cold (below -10 °C) | Battery too cold (below -10 °C) | Battery too cold (below -10 °C) |
| E08 | Motor over-temperature (above 85 °C) | Motor over-temperature (above 90 °C) | Motor over-temperature (above 85 °C) |
| E09 | Battery voltage too low | Battery voltage too low | Battery voltage too low |
| E10 | Charger fault: charger voltage outside range | Charger fault: charger voltage outside range | Charger fault: charger voltage outside range |
| E11 | Brake cut-off switch active at switch-on | Brake cut-off switch active at switch-on | Brake cut-off switch active at switch-on (either lever) |
| E12 | Shift-assist sensor fault | Not used on this model | Shift-assist sensor fault |
| E13 | Accessory port overload (more than 6 W drawn) | Front or rear light circuit short | Light circuit short or overload (includes the brake light) |
| E14 | Display and controller firmware do not match | Display and controller firmware do not match | Display and controller firmware do not match |
| E15 | Controller over-current | Controller over-current | Controller over-current (often a stall on a slope with a heavy load) |
| E16 | Battery cells out of balance | Not used on this model | Battery cells out of balance |
| E17 | Battery calibration drift (added in firmware v2.4): range estimate unreliable | Battery calibration drift (added in firmware v2.4): range estimate unreliable | Battery calibration drift (added in firmware v2.4): range estimate unreliable |
| E18 | Battery not locked fully | Battery not locked fully | Battery not locked fully |
| E19 | Motor phase fault | Motor phase fault | Motor phase fault |
| E20 | Display memory fault | Display memory fault | Display memory fault |

## Which codes mean the same thing everywhere?

These codes have the same meaning on all three models: E01, E02, E06, E07, E09, E10, E14, E17, E18, E19, E20.

## Which codes differ between models?

These codes are worded differently on at least one model, either because the bikes have different hardware or because the fix differs: E03, E04, E05, E08, E11, E12, E13, E15, E16.

The most important differences:

- **E03:** a torque sensor problem on the Ridge 500 and Cargo 700 (their mid-drive motors sense pedal force), but a missing cadence sensor signal on the Metro 300, which has a hub motor.
- **E04:** a speed sensor with a wheel magnet on the Ridge 500 and Cargo 700 (gap 3 to 5 mm), but the speed signal of the hub motor on the Metro 300, which cannot be fixed at home.
- **E10:** the Ridge 500 and Metro 300 need the 36 V charger FH-2310-B, the Cargo 700 needs the 48 V charger FH-2320-A.
- **E12:** a shift-assist sensor fault on the Ridge 500 and Cargo 700. The Metro 300 has a hub gear and does not use E12.
- **E13:** an accessory port overload on the Ridge 500, but a light circuit fault on the Metro 300 and Cargo 700.
- **E16:** battery cell imbalance on the Ridge 500 and Cargo 700; not used on the Metro 300.
- **E08:** the motor over-temperature threshold is 85 °C on the Ridge 500 and Cargo 700 and 90 °C on the Metro 300. The recommended wait is 20 minutes on the Ridge 500 and Metro 300 and 30 minutes on the Cargo 700.

## When were the codes added?

| Firmware | Codes first defined |
|---|---|
| v2.0 (March 2023) | E01 to E14, E19, E20 |
| v2.2 (June 2024) | E15, E16 |
| v2.3 (November 2024) | E18 |
| v2.4 (April 2025) | E17 |

## First steps for any code

1. Switch the bike off and wait ten seconds.
2. Switch it on again without touching the pedals or the brake levers.
3. If the code returns, find it in your model's table and follow the fix.
4. If the fix does not help, note the code and the firmware version (Menu > Bike) and contact a dealer or support@fernhillbikes.example.

The Fernhill Service app also stores the last 20 error codes with the date, so a dealer can see what happened even if the code cleared.
