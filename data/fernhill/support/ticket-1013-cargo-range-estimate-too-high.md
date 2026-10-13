# Support ticket FH-T-1013: Cargo range estimate is far too hopeful

| Field | Value |
|---|---|
| Ticket | FH-T-1013 |
| Opened | 10 September 2025 |
| Resolved | 11 September 2025 |
| Customer | Chloe |
| Agent | Tom |
| Model | Cargo 700 |
| Topic | Battery range |
| Channel | Chat |
| Resolution type | Firmware update |

## Customer's question

Chloe wrote in chat: "My Cargo 700 said 60 km left at the start of a school run with two children and shopping. I was
flat after 38 km. Is the battery failing?"

## Conversation

**Tom:** The battery is probably fine, Chloe. Which firmware version do you have, and what assist level did you use?

**Chloe:** v2.4. Sport, because of the hills.

**Tom:** That fits a known issue. Before v2.5 the range estimate on the Cargo 700 ignored the load you carried, so with a
heavy load it could be up to 25% too high. With two children and shopping you might have been near 150 kg in total. For Sport at full load the
manual gives up to 40 km, so 38 km matches. Firmware v2.5, released on 28 August 2025, adds a Load menu: Empty, Half or Full.

**Chloe:** Where do I find it?

**Tom:** Update with the Fernhill Service app, then go to Menu > Load. Set it to Half or Full when you carry people or cargo.
The estimate then includes the weight. v2.5 also adds Battery care mode if you want to stop charging at 80%.

*11 September 2025.* Chloe updated, set Load to Full and rode the same route. The estimate was within 3 km of the real
range.

## Resolution

Known issue in firmware v2.3 and v2.4 (Cargo 700 range estimate ignored the load), fixed in v2.5. Customer updated and used
the new Load menu. No fault with the battery.

## Note for the support team

Cargo 700 range estimate ignored the load until v2.5, which added the Load menu.
