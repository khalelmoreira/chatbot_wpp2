"""Shared fragments for the message prompts in this package.

Sibling prompts kept drifting because the role line, the anti-invention rule and
the lay-term glossary were copy-pasted and edited in one place but not the
others. Define each once here and compose it into every ``AIPrompt`` with an
f-string.

``ARG`` is the literal ``"{}"`` that ``AIPrompt.render(*args)`` fills at call
time. Write ``{ARG}`` in an f-string prompt wherever a runtime value is injected
(one per positional arg, in the order the call site passes them).
"""

ARG = "{}"

# --- Role lines: the first sentence of a _RESP prompt's ROLE section ----------

ROLE_SIGNUP = "You help Brazilian service providers register to issue invoices over WhatsApp."
ROLE_NFSE = "You help Brazilian service providers issue invoices (NFS-e) over WhatsApp."
ROLE_ASSISTANT = "You are the assistant for a Brazilian NFS-e (service invoice) issuance app on WhatsApp."

# --- Anti-invention: every prompt uses exactly one of these, verbatim --------

NO_INVENTION = "Never invent data — mention only what the user actually sent."

EXTRACT_RULES = """RULES:
    - Never invent a value that isn't present in the message.
    - Leave any field not mentioned as null — don't guess."""

# --- Lay-term glossary: replies must avoid fiscal jargon ---------------------

LAY_TERMS_PREST = (
    'avoid "prestador", "razão social"; say "nome da empresa", "regime tributário", '
    '"CEP", "e-mail", "telefone", "CNPJ", "logradouro", "bairro", "cidade", "uf" instead'
)
LAY_TERMS_TOM = (
    'avoid "tomador", "prestador", "competência", "CNPJ"; '
    'say "cliente", "mês do serviço", "CPF ou CNPJ" instead'
)

# --- Prestador core fields: shared by the data-only and address extractors ---

PREST_CORE_FIELDS = """razao_social: Company names only (LTDA, ME, EIRELI, S/A, SS, EPP, etc). Preserve original
    capitalization exactly as written. A person's name (an individual, not a company) → null.

    cnpj: Digits only, exactly 14, or null. Strip all punctuation: "12.345.678/0001-99" →
    "12345678000199". A CPF (11 digits) is not a valid cnpj → null.

    email: Lowercase. Must contain "@" and a plausible domain extension, or null.
    "FISCAL@EMPRESA.COM.BR" → "fiscal@empresa.com.br".

    regime_tributario — map informal phrasing to the code:
      "MEI", "microempreendedor individual" → "2"
      "simples nacional", "simples", "SN", "ME", "EPP", "microempresa", "pequeno porte" → "3"
      "excesso de sublimite", "SN excesso" → "3e"
      "lucro presumido", "lucro real", "não optante", "regime normal" → "1"
      absent or genuinely ambiguous → null

    cep: Digits only, exactly 8, or null. "01310-100" → "01310100"."""
