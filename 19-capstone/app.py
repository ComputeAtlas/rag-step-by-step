"""A small web server for the "chat with your docs" app. It uses only Python's standard library.

- GET  /            the page (index.html)
- POST /ask         a question (and the chat so far) -> the sources, then the answer as it is written
- GET  /source/7    a source document, with section 7 highlighted (the links under each answer)

Run from the repository root:  python 19-capstone/app.py   then open http://localhost:8000
(Build the index first: python 19-capstone/ingest.py)"""
import html
import json
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from answer import check_citations, rewrite_follow_up, stream_answer
from search import find_sections, sections

HERE = Path(__file__).parent
DOCUMENTS_FOLDER = HERE.parent / "data" / "fernhill"
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000


def ask(question, chat, send):
    """Answer one question. `send` writes one line of JSON to the browser."""
    started = time.time()
    if chat:  # a follow-up like "and on the Ridge?": make it a question that stands alone
        question = rewrite_follow_up(chat, question)
    found = find_sections(question)
    send({"question": question,
          "sources": [{"source": s["source"], "number": s["number"]} for s in found]})
    searched = time.time()

    answer = ""
    for piece in stream_answer(question, found):
        answer += piece
        send({"text": piece})  # each piece goes to the browser as soon as the model writes it
    send({"problems": check_citations(question, answer, found)})
    print(f"{question[:60]!r}: search {searched - started:.2f} s, answer {time.time() - searched:.2f} s", flush=True)


def source_page(number):
    """The whole document, with the section the answer used highlighted."""
    section = sections[number]
    text = (DOCUMENTS_FOLDER / section["source"]).read_text()
    start = text.find(section["text"])
    if start == -1:
        body = f"<mark id='here'>{html.escape(section['text'])}</mark>"
    else:
        end = start + len(section["text"])
        body = (html.escape(text[:start]) + "<mark id='here'>" + html.escape(text[start:end])
                + "</mark>" + html.escape(text[end:]))
    return f"""<!doctype html><meta charset="utf-8"><title>{section['source']}</title>
<style>body{{font:18px/1.6 system-ui,sans-serif;max-width:860px;margin:40px auto;padding:0 24px;color:#222}}
h1{{font-size:22px;font-family:ui-monospace,monospace;position:sticky;top:0;margin:0;padding:14px 0;
background:white;border-bottom:1px solid #ddd}} pre{{white-space:pre-wrap;font:inherit}}
mark{{background:#fde68a;padding:2px 0}}</style>
<h1>{section['source']}</h1><pre>{body}</pre>
<script>document.getElementById('here').scrollIntoView({{block: 'center'}})</script>"""


# http.server asks for a class with one method per kind of request (do_GET, do_POST).
class Handler(BaseHTTPRequestHandler):
    def reply(self, content, content_type="text/html; charset=utf-8"):
        data = content.encode()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/":
            self.reply((HERE / "index.html").read_text())
        elif self.path.startswith("/source/"):
            self.reply(source_page(int(self.path.split("/")[-1])))
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path != "/ask":
            self.send_error(404)
            return
        length = int(self.headers["Content-Length"])
        request = json.loads(self.rfile.read(length))
        self.send_response(200)
        self.send_header("Content-Type", "application/x-ndjson")  # one JSON object per line
        self.end_headers()  # no length: we stream, and the browser reads until we close

        def send(message):
            self.wfile.write((json.dumps(message) + "\n").encode())
            self.wfile.flush()  # send it now, don't wait for the rest

        ask(request["question"], request.get("chat", []), send)
        self.close_connection = True

    def log_message(self, *args):
        pass  # keep the terminal quiet: ask() prints one line per question


print(f"Fernhill docs chat on http://localhost:{PORT}  (Ctrl+C to stop)", flush=True)
ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
