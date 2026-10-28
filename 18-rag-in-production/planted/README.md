# A planted document (for the prompt-injection demo only)

`ticket-1045-service-price-question.md` is **not** a Fernhill document. It was written for this lesson to show prompt
injection: text inside a document that tries to give the model orders. Anyone who can write into your documents
(here, a customer filling in the support web form) can write to your model.

`injection_demo.py` adds it to a copy of the index in memory; it is never added to `data/fernhill/`.
