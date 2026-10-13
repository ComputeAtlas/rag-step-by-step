# Support ticket FH-T-1017: E10 when charging my Cargo

| Field | Value |
|---|---|
| Ticket | FH-T-1017 |
| Opened | 3 November 2025 |
| Resolved | 3 November 2025 |
| Customer | Maeve |
| Agent | Tom |
| Model | Cargo 700 |
| Topic | Charging problems |
| Channel | Chat |
| Resolution type | Advice only |

## Customer's question

Maeve wrote in chat: "I left my charger at my sister's and borrowed her neighbour's charger. It plugs in fine, but my Cargo
700 now shows E10 and will not charge."

## Conversation

**Tom:** On the Cargo 700, E10 is a charger fault: the charger voltage is outside the allowed range. Do you know what
voltage the borrowed charger is?

**Maeve:** It says 36 V 3 A. It is from a Metro 300, I think.

**Tom:** That is the problem. The Cargo 700 battery is a 48 V pack, 720 Wh, and its charger is the FH-2320-A (48 V, 4 A). The Metro 300 and Ridge 500 use a 36 V
charger (FH-2310-B). The bike protects itself by refusing to charge and showing E10.

**Maeve:** Have I damaged the battery?

**Tom:** The protection worked as designed, and a mismatch like this is rejected before power flows. Disconnect the 36 V
charger, switch the bike off for ten seconds, and charge with the 48 V charger. If you need a replacement, FH-2320-A costs £79.

**Maeve:** I will fetch mine back tomorrow.

*Next day.* Maeve reported that the 48 V charger started normally.

## Resolution

Wrong charger voltage (36 V on a 48 V battery). No damage. Charging resumed with the Cargo 700's own FH-2320-A.
Customer reminded that a charger from another maker can damage a battery and is not covered by the warranty.

## Note for the support team

E10 on a Cargo 700 usually means a 36 V charger. The Cargo 700 uses FH-2320-A (48 V, 4 A).
