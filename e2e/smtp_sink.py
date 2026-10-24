"""Ephemeral STARTTLS SMTP inbox for Nexora GitHub Actions."""
from __future__ import annotations
import argparse
import json
import ssl
import time
from pathlib import Path
from aiosmtpd.controller import Controller
from aiosmtpd.smtp import AuthResult

class Handler:
    def __init__(self, outbox: Path):
        self.outbox = outbox
        self.outbox.parent.mkdir(parents=True, exist_ok=True)
    async def handle_DATA(self, server, session, envelope):
        data = envelope.content.decode("utf-8", "replace") if isinstance(envelope.content, bytes) else str(envelope.content)
        row = {"mail_from": envelope.mail_from, "rcpt_tos": envelope.rcpt_tos, "data": data}
        with self.outbox.open("a", encoding="utf-8") as output:
            output.write(json.dumps(row, ensure_ascii=False) + "\n")
        return "250 Stored in disposable Nexora CI inbox"

def auth(server, session, envelope, mechanism, auth_data):
    return AuthResult(success=True)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--host",default="127.0.0.1")
    p.add_argument("--port",type=int,default=2525)
    p.add_argument("--cert",required=True)
    p.add_argument("--key",required=True)
    p.add_argument("--outbox",required=True)
    a=p.parse_args()
    tls=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    tls.load_cert_chain(a.cert,a.key)
    controller=Controller(Handler(Path(a.outbox)),hostname=a.host,port=a.port,tls_context=tls,require_starttls=True,authenticator=auth)
    controller.start()
    print("Disposable Nexora STARTTLS inbox ready",flush=True)
    try:
        while True: time.sleep(3600)
    except KeyboardInterrupt:
        controller.stop()
if __name__=="__main__": main()
