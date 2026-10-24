"""Loopback-only STARTTLS inbox sink for Nexora CI."""
from __future__ import annotations
import argparse, json, time
from pathlib import Path
from aiosmtpd.controller import Controller
from aiosmtpd.smtp import AuthResult

class Handler:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
    async def handle_DATA(self, server, session, envelope):
        value = envelope.content.decode("utf-8", "replace") if isinstance(envelope.content, bytes) else str(envelope.content)
        row = {"mail_from": envelope.mail_from, "rcpt_tos": envelope.rcpt_tos, "data": value}
        with self.path.open("a", encoding="utf-8") as out:
            out.write(json.dumps(row, ensure_ascii=False) + "\n")
        return "250 Accepted into the isolated Nexora CI inbox"

def auth(server, session, envelope, mechanism, auth_data):
    return AuthResult(success=True)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=2525)
    parser.add_argument("--cert", required=True)
    parser.add_argument("--key", required=True)
    parser.add_argument("--outbox", required=True)
    args = parser.parse_args()
    import ssl
    tls = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    tls.load_cert_chain(args.cert, args.key)
    server = Controller(Handler(Path(args.outbox)), hostname=args.host, port=args.port,
        tls_context=tls, require_starttls=True, auth_required=True, auth_require_tls=True, authenticator=auth)
    server.start()
    print(f"STARTTLS inbox listening on {args.host}:{args.port}", flush=True)
    try:
        while True: time.sleep(3600)
    except KeyboardInterrupt:
        server.stop()

if __name__ == "__main__":
    main()
