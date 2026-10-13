# Fernhill Service App Guide

Edition January 2026. The Fernhill Service app is free and works on phones. It connects to your bike wirelessly, reads
its status and installs firmware updates. It does not replace the display, and it cannot register your bike; use
fernhillbikes.example/register for that.

## What the app shows

| Screen | What you see |
|---|---|
| Bike | Model, serial number, display and controller build numbers (for example D2.6.0 and C2.6.0) |
| Battery | Charge percentage, health percentage, charge cycle count, whether Battery care mode is on |
| History | The last 20 error codes with the date and the firmware version at the time |
| Service | Distance since the last service and the date the next service is due |
| Updates | Whether a newer firmware version is available, and the release notes |

## Connecting your bike

1. Install the app and open it. Allow the app to use wireless connections when it asks.
2. Switch the bike on and stand within 3 metres of it.
3. On the display, open Menu > Bike > Pair. The display shows a six-digit pairing number.
4. Enter the number in the app. The bike appears under Bike.

Each bike pairs with one phone at a time. To pair another phone, open Menu > Bike > Pair again.

## Updating the firmware

1. Check that the battery is above 50%. The app refuses to start the update below that.
2. Stay within 3 metres of the bike and keep the phone screen on.
3. Tap Updates, then Install. The display and the controller update together, one after the other.
4. The update takes about 12 minutes. The display shows a progress bar. Do not switch off the bike, remove the battery
   or move away.
5. When the display restarts, check Menu > Bike. Both build numbers must start with the same version number.

If the update stops halfway the display shows UPD and the bike will not start. This is not damage. Keep the battery in,
bring the phone close and start the update again. If it still fails, a dealer can restore the firmware with the service
cable.

A bike with different versions on display and controller shows error E14 until both are updated to the same version.

## What the app sends to Fernhill

The app sends the bike's serial number, firmware versions, charge cycle count and error code history to Fernhill, so that support
can help with a claim and engineers can find common faults. It does not collect your location. The privacy notice has
the retention periods.

## Battery cycle count and warranty claims

The cycle count in the Battery screen is the same number as Menu > Battery > Cycles on the display. For battery warranty claims
we ask for a screenshot of the Battery screen. One cycle counts when the battery has delivered energy equal to its full capacity
in total, so top-ups are added together.

## Tips

- Update the firmware before a long trip, not on the morning of one.
- If the app cannot find the bike, switch the bike off and on again, and make sure the pairing has not been taken over by another phone.
- Dealers use a separate diagnostic cable. You do not need one.
- The app does not control the motor or change the speed limit.

## Questions about the app

**Does the app work without the bike nearby?** You can read the release notes and the last synchronised status, but updates and live readings need the bike within 3 metres.

**Will the update delete my settings?** No. The assist level, units and brightness are kept. Battery care mode stays on if you had switched it on.

**Can I use one phone for several bikes?** Yes. Each bike has its own entry in the app. A bike pairs with only one phone at a time, so a family that shares one Cargo 700 should choose one phone to be the main one.

**What if I lose my phone?** The bike works without the app. Pair a new phone through Menu > Bike > Pair.

**Is the app needed to ride?** No. The app is for updates and diagnostics only; every riding function is on the display and the remote pad.

**How often should I look at the app?** Open it before long trips and after any error code, and when a new release is announced. The app tells you when an update is available.
