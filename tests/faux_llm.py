"""Un faux point d'accès compatible OpenAI pour les essais : il journalise et imite plusieurs serveurs.

`capacites` règle ce qu'il refuse, comme le ferait un vLLM lancé sans `--enable-auto-tool-choice`
ou une passerelle qui ne connaît pas `max_completion_tokens`.
"""

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


def demarrer(outils: bool = True, requis: bool = True, max_completion: bool = True) -> ThreadingHTTPServer:
    journal: list[dict] = []

    class Gestionnaire(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def _refuser(self, message: str) -> None:
            donnees = json.dumps({"error": {"message": message, "type": "BadRequestError"}}).encode()
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(donnees)))
            self.end_headers()
            self.wfile.write(donnees)

        def do_POST(self):
            corps = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            journal.append({"chemin": self.path, "entetes": dict(self.headers), "corps": corps})
            if "max_completion_tokens" in corps and not max_completion:
                return self._refuser("Unrecognized request argument supplied: max_completion_tokens")
            if corps.get("tools") and not outils:
                return self._refuser('"auto" tool choice requires --enable-auto-tool-choice and --tool-call-parser to be set')
            if corps.get("tool_choice") == "required" and not requis:
                return self._refuser("tool_choice 'required' is not supported")
            outils_demandes = [t["function"]["name"] for t in corps.get("tools", [])]
            if outils_demandes and not any(m.get("role") == "tool" for m in corps["messages"]):
                nom = outils_demandes[0]
                arguments = json.dumps({"code": "print(1)"} if nom == "final_result" else {})
                delta = {"role": "assistant", "tool_calls": [{"index": 0, "id": "a1", "type": "function",
                                                              "function": {"name": nom, "arguments": arguments}}]}
                message = {"role": "assistant", "content": None, "tool_calls": [{**delta["tool_calls"][0]}]}
            else:
                delta = {"role": "assistant", "content": "Bonjour."}
                message = {"role": "assistant", "content": "Bonjour."}
            if corps.get("stream"):
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.end_headers()
                morceau = {"id": "c", "object": "chat.completion.chunk", "model": corps["model"],
                           "choices": [{"index": 0, "delta": delta, "finish_reason": "stop"}]}
                self.wfile.write(f"data: {json.dumps(morceau)}\n\ndata: [DONE]\n\n".encode())
                return
            donnees = json.dumps({"id": "c", "object": "chat.completion", "model": corps["model"],
                                  "choices": [{"index": 0, "message": message, "finish_reason": "stop"}]}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(donnees)))
            self.end_headers()
            self.wfile.write(donnees)

    serveur = ThreadingHTTPServer(("127.0.0.1", 0), Gestionnaire)
    serveur.journal = journal
    threading.Thread(target=serveur.serve_forever, daemon=True).start()
    return serveur
