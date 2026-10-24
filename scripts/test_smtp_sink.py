"""STARTTLS SMTP sink for one workflow's isolated inbox."""
from __future__ import annotations
import argparse
import json
import ssl
import time
from pathlib import Path
from aiosmtpd.controller import Controller
from aiosmtpd.smtp import AuthResult

class Inbox:
    def __init__(self, path: Path):
        self.path=path
        self.path.parent.mkdir(parents=True,exist_ok=True)
    async def handle_DATA(self, server, session, envelope):
        raw=envelope.content
        content=raw.decode("utf-8","replace") if isinstance(raw,bytes) else raw
        with self.path.open("a",encoding="utf-8") as stream:
            stream.write(json.dumps({"mail_from":envelope.mail_from,"rcpt_tos":envelope.rcpt_tos,"data":content})+"\n")
        return "250 Accepted into the isolated Nexora test inbox"

def auth(server,session,envelope,mechanism,auth_data):
    return AuthResult(success=True)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--host",default="127.0.0.1")
    parser.add_argument("--port",type=int,default=2525)
    parser.add_argument("--cert",required=True)
    parser.add_argument("--outbox",required=True)
    args=parser.parse_args()
    tls=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    tls.load_cert_chain(args.cert)
    controller=Controller(Inbox(Path(args.outbox)),hostname=args.host,port=args.port,tls_context=tls,require_starttls=True,authenticator=auth)
    controller.start()
    print(f"STARTTLS inbox listening on {args.host}:{args.port}",flush=True)
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        controller.stop()

if __name__=="__main__":
    main()
