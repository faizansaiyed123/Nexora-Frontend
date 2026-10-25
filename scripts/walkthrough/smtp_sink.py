"""STARTTLS SMTP receiver for the ephemeral Nexora walkthrough environment."""
from __future__ import annotations

import argparse
import json
import ssl
import time
from pathlib import Path

from aiosmtpd.controller import Controller
from aiosmtpd.smtp import AuthResult


class Mailbox:
    def __init__(self, output: Path) -> None:
        self.output = output
        self.output.parent.mkdir(parents=True, exist_ok=True)

    async def handle_DATA(self, server, session, envelope):
        data = envelope.content
        if isinstance(data, bytes):
            data = data.decode("utf-8", "replace")
        message = {
            "mail_from": envelope.mail_from,
            "rcpt_tos": envelope.rcpt_tos,
            "data": data,
        }
        with self.output.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(message, ensure_ascii=False) + "\n")
        return "250 Message accepted by the isolated Nexora inbox"


def accept_ephemeral_test_login(server, session, envelope, mechanism, auth_data):
    return AuthResult(success=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=2525)
    parser.add_argument("--cert", required=True)
    parser.add_argument("--key", required=True)
    parser.add_argument("--mailbox", required=True)
    args = parser.parse_args()
    tls = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    tls.load_cert_chain(args.cert, args.key)
    controller = Controller(
        Mailbox(Path(args.mailbox)),
        hostname=args.host,
        port=args.port,
        tls_context=tls,
        require_starttls=True,
        auth_required=True,
        authenticator=accept_ephemeral_test_login,
    )
    controller.start()
    print(f"Test inbox listening on {args.host}:{args.port}", flush=True)
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        controller.stop()


if __name__ == "__main__":
    main()
