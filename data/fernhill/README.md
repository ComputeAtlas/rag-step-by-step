# Fernhill Bikes: demo document set

This folder holds the documents for **Fernhill Bikes**, the company used in every lesson of the course *RAG, Step by Step*.
Fernhill is **made up**. It is an electric-bike maker with three models (Ridge 500 mountain, Metro 300 city, Cargo 700 cargo),
and every document here was written for the course. No real company, person, product or e-mail domain is used; all
addresses end in `fernhillbikes.example`, telephone numbers use the reserved fictional 01632 960 range, and the towns are invented.

**This README describes the corpus; it is not part of it.** Skip `README.md` when you load the documents for the course, so that
it never turns up as a search result.

The corpus is deliberately a little messy, like a real company's files, because each lesson needs a different hard case.

## What is in it

| Folder | Files | Words | Contents |
|---|---|---|---|
| `fernhill/` | 4 | 4,760 | `warranty-policy.md` (2026 warranty, from lesson 1), `faq.md`, `company.md`, `store-locations.md` |
| `fernhill/manuals/` | 12 | 15,990 | Owner's manuals for the Ridge 500, Metro 300 and Cargo 700 (spec tables, charging and care, maintenance schedules, error-code tables E01 to E20), quick-start guides, an error-codes comparison, and guides (winter riding, battery and charging, the service app, new-owner tips, the dealer service checklist) |
| `fernhill/parts/` | 6 | 3,887 | Parts catalogue: overview and part-number rules, batteries and chargers, brakes and tyres, displays/motors/controllers, drivetrain/lights/accessories, accessories and fitting |
| `fernhill/policies/` | 13 | 7,719 | `warranty-policy-2025.md` (the old policy), `warranty-changes-2026.md`, returns, shipping and delivery, terms of sale, service and repair pricing, the Cargo 700 business plan and its FAQ, dealer programme, battery safety and transport, safety notice SN-2025-03, recycling, privacy |
| `fernhill/support/` | 44 | 14,762 | 44 resolved support tickets, one file each (`ticket-1001-...md` to `ticket-1044-...md`) |
| `fernhill/release-notes/` | 8 | 3,202 | Firmware notes v2.0 to v2.6 (display and controller together) and a version overview |
| **Total** | **87** | **50,320** | Counted with `wc -w` over every `.md` file, not counting this README |

## Hard cases on purpose

| Hard case | Where to find it | Lesson that needs it |
|---|---|---|
| Facts that only appear in a table (torque values, ranges, prices, opening hours) | the manuals, `parts/`, `policies/shipping-and-delivery.md`, `store-locations.md` | Parsing, chunking |
| Part numbers and error codes that embeddings blur (`FH-2291-B` vs `FH-2219-B`, `FH-3105-A` vs `FH-3105-B`, `E03` on three models) | `parts/`, the three manuals, `manuals/error-codes-compared.md` | Hybrid search |
| A warranty in two versions that disagree (2026 vs 2025: battery 3 years or 800 cycles vs 2 years or 500 cycles, 70% vs 60%, registration bonus, frame cover, delivery use) | `warranty-policy.md`, `policies/warranty-policy-2025.md`, `policies/warranty-changes-2026.md` | Freshness, metadata, conflicting sources |
| A fact stated in one document and corrected in a later one (cycle counter, Battery care mode release, display auto-off 10 to 5 minutes, "latest" firmware) | `release-notes/`, the manuals and `faq.md` | Freshness, conflicting sources |
| Questions that need two documents (price plus labour, part plus firmware, policy plus business plan) | `parts/` with `policies/`, `release-notes/` | Multi-hop, agentic RAG |
| Questions about the whole corpus (the most common complaint, tickets per model) | `support/` | GraphRAG, summaries |
| Things the documents never say (the chief executive, sales totals, euro prices, v2.7 date) | nowhere, on purpose | Grounded answers, "I don't know" |
| Messy real-world text | `support/` tickets, `faq.md` | Chunking, query rewriting |

### Support tickets

Each ticket file starts with a small table (ticket, dates, customer first name, agent, model, topic, channel, resolution type) and
ends with a short note for the support team. The topics are battery range (9), charging problems (6), error codes (6), brakes (5),
warranty (5), tyres and punctures (3), delivery and damage (3), firmware (3), fleet and business (2) and returns (2).

## The test questions

`data/fernhill-questions.json` holds exactly 100 questions. Each entry has:

```json
{"id": "q001", "question": "...", "answer": "...", "sources": ["company.md"], "category": "lookup"}
```

| Category | Questions |
|---|---|
| lookup | 30 |
| part-number/error-code | 15 |
| table | 15 |
| multi-document | 15 |
| whole-corpus | 10 |
| conflicting-versions | 5 |
| unanswerable | 10 |

- `sources` paths are relative to `data/fernhill/`. A multi-document question lists every file that is needed.
- For **conflicting-versions** questions the first source is the document with the correct answer. The other sources are the
  versions it conflicts with, so a good system must see both and choose.
- For **whole-corpus** questions the sources are all 44 ticket files, and the answers are counts you can reproduce from the
  ticket tables.
- For **unanswerable** questions `sources` is empty and `answer` is `"Not in the documents"`.
- Every answer was checked against the files with a script (each answer's supporting text, every source path, the ticket counts).

## Reading order for a first look

1. `warranty-policy.md` (the 2026 policy used in lesson 1).
2. `manuals/ridge-500-owners-manual.md` for tables and error codes.
3. `parts/batteries-and-chargers.md` for part numbers.
4. `support/ticket-1001-range-half-in-winter.md` for a ticket.
5. `release-notes/firmware-overview.md` for the version history.

When the whole set is written, an empty file named `CORPUS_READY` appears in this folder.
