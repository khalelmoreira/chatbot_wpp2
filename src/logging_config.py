"""Central logging setup — MVP Week 6 step 1: structured logs for remote
debugging (VPS has no APM, so `journalctl -u nfse-app` / `-u
nfse-emissao-worker` is the only place logs are read), without full
CPF/CNPJ/amounts ending up in them.

This is separate from *messages to the user* — those go through `print()`
(stand-in for `WhatsAppService.send_msg_text`, see `src/services/wpp/`) and
are never routed through this module. `setup_logging()` only configures the
`logging` module, which the rest of the codebase uses for internal
diagnostics (request/flow tracing, external API calls, worker state).

Redaction is regex-based, applied once as a logging filter on the root
handler — every module logger propagates to it, so nothing needs to opt in.
It's a best-effort MVP shortcut, not a guarantee: it catches CPF/CNPJ shaped
digit runs (formatted or not) and the `valor_total`/`total`/`aliquota_iss`
fields that show up when a dataclass or dict gets logged via `%s`. It won't
catch a CPF that got relabeled under an unrelated key, so don't rely on it
as the only safeguard — prefer logging identifiers (id, phone) over whole
payloads in new code.
"""

import json
import logging
import re
import sys
from datetime import UTC, datetime

_CNPJ_FORMATTED = re.compile(r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}")
_CNPJ_DIGITS = re.compile(r"(?<!\d)\d{14}(?!\d)")
_CPF_FORMATTED = re.compile(r"\d{3}\.\d{3}\.\d{3}-\d{2}")
_CPF_DIGITS = re.compile(r"(?<!\d)\d{11}(?!\d)")
_MONEY_BRL = re.compile(r"R\$\s?\d{1,3}(?:\.\d{3})*(?:,\d{2})?")
_AMOUNT_FIELD = re.compile(
    r"""(['"]?(?:valor_total|aliquota_iss|total)['"]?\s*[:=]\s*)[\d.]+""",
    re.IGNORECASE,
)

_REDACTED = "[REDACTED]"


def _redact(text: str) -> str:
    text = _CNPJ_FORMATTED.sub(_REDACTED, text)
    text = _CPF_FORMATTED.sub(_REDACTED, text)
    text = _CNPJ_DIGITS.sub(_REDACTED, text)
    text = _CPF_DIGITS.sub(_REDACTED, text)
    text = _MONEY_BRL.sub(_REDACTED, text)
    text = _AMOUNT_FIELD.sub(rf"\1{_REDACTED}", text)
    return text


class RedactSensitiveFilter(logging.Filter):
    """Rewrites `record.msg` to its already-%-formatted, redacted form and
    clears `record.args` so the formatter doesn't re-interpolate raw args."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = _redact(record.getMessage())
        record.args = ()
        return True


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def setup_logging(level: int = logging.INFO) -> None:
    """Call once, at process start (app.py / worker entrypoints). Idempotent —
    safe to call more than once (e.g. app.py + a `python -m` worker script in
    the same process) since it clears any handlers it previously added."""

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()

    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(JsonFormatter())
    handler.addFilter(RedactSensitiveFilter())
    root.addHandler(handler)
