# Support ticket FH-T-1019: Range estimate is too high with Battery care mode on

| Field | Value |
|---|---|
| Ticket | FH-T-1019 |
| Opened | 20 November 2025 |
| Resolved | 14 January 2026 |
| Customer | Farid |
| Agent | Callum |
| Model | Ridge 500 |
| Topic | Battery range |
| Channel | Email |
| Resolution type | Firmware update |

## Customer's question

Farid wrote: "I switched on Battery care mode so the battery stops at 80%. Now the display promises about 20% more range than
I actually get."

## Conversation

**Callum:** That is a documented known issue in firmware v2.5, Farid. With Battery care mode on, the Ridge 500 range estimate
still assumes a full 100% charge, so it reads around 20% high. The charge limit itself works correctly. Until it is fixed,
subtract about a fifth from the number on the screen, or switch the mode off for rides where you need to know the exact range.

**Farid:** Is there an update planned?

**Callum:** Yes, in the next release. I will leave this ticket open and message you when it is out.

*14 January 2026.* **Callum:** Firmware v2.6 came out on 12 January 2026. Its controller build C2.6.0 takes the 80% limit into
account, so the estimate is correct with Battery care mode on.

**Farid:** Updated yesterday. I rode 41 km on a charge-to-80% battery and the display was right to within 2 km.

## Resolution

Known issue in firmware v2.5 (range estimate ignored Battery care mode on the Ridge 500), fixed in v2.6. Customer updated and
confirmed.

## Note for the support team

Range estimate with Battery care mode on was too high in v2.5; fixed in v2.6.
