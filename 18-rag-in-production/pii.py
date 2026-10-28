"""Remove personal details (PII: personally identifiable information) before text is stored.

- redact_ticket: a support ticket names its customer in its table ("| Customer | Jonas |"),
  so we know the name and can replace it everywhere in that ticket;
- redact: e-mail addresses and phone numbers, in any text (a question, a log line).
Real systems use a proper detector as well (for example Microsoft Presidio); patterns miss things."""
import re

EMAIL = re.compile(r"[\w.+-]+@[\w-]+(\.[\w-]+)+")
PHONE = re.compile(r"\+?\d[\d ]{8,}\d")


def redact(text):
    text = EMAIL.sub("[EMAIL]", text)
    text = PHONE.sub("[PHONE]", text)
    return text


def redact_ticket(text):
    found = re.search(r"\| Customer \| (\w+) \|", text)
    if found:
        name = found.group(1)
        text = re.sub(rf"\b{name}\b", "[CUSTOMER]", text)
    return redact(text)
