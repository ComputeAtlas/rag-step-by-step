# Support ticket FH-T-1016: New battery gives E01

| Field | Value |
|---|---|
| Ticket | FH-T-1016 |
| Opened | 8 October 2025 |
| Resolved | 9 October 2025 |
| Customer | Rosa |
| Agent | Isla |
| Model | Ridge 500 |
| Topic | Error codes |
| Channel | Email |
| Resolution type | Firmware update |

## Customer's question

Rosa wrote: "I bought a replacement battery for my 2023 Ridge 500 from your site. It is part FH-2291-B. When I fit it the
display shows E01 and the bike will not start. Is the battery dead on arrival?"

## Conversation

**Isla:** Thank you, Rosa. The battery is almost certainly fine. FH-2291-B is the current Ridge 500 pack and it uses a newer
battery-management protocol. Bikes built before 2025 only talk to it if their firmware is v2.3 or later. On older firmware
the bike cannot find the battery and shows E01, which means battery not detected. Which firmware does your bike show?

**Rosa:** I cannot read it because the bike will not switch on with the new battery. Before, it said v2.2.

**Isla:** That confirms it. v2.2 is too old for the B pack. Here is the fix: refit your old battery (FH-2291-A, which
works with any firmware), update the bike to v2.3 or later with the Fernhill Service app (the battery must be above 50%),
then fit the new pack. We recommend updating to v2.5, the latest, while you are doing it.

**Rosa:** My old battery is dead, though.

**Isla:** In that case, take the bike to a Service-level dealer or a Fernhill service centre. They can update it with the
service cable, which does not need the old battery. It is free.

*9 October 2025.* Rosa had the bike updated at a Fernhill service centre. The new battery works.

## Resolution

Not a fault. A Ridge 500 built in 2023 on firmware v2.2 cannot use the B battery pack FH-2291-B; it needs v2.3 or later. A
dealer updated the firmware to v2.5 at no charge, after which the new pack was detected.

## Note for the support team

B packs need firmware v2.3 or later on bikes built before 2025. A packs work with any version.
