"""Compare a user-typed company name against the names Receita Federal returns
for a CNPJ (via `get_cnpj_info`).

The bot collects `tomador.nome` as free text and `tomador.cnpj` separately, and
until now nothing tied the two together — a valid CNPJ plus any name would issue.
This module answers one question: *does this name plausibly belong to this CNPJ?*

It is deliberately lenient. `razao_social` is the exact registered legal name
("COMERCIAL SILVA E FILHOS LTDA"); people type the trade name, an abbreviation,
or drop the corporate suffix. We normalise both sides (casefold, strip accents
and punctuation, drop `LTDA/ME/EPP/...` tokens) and accept an exact match or a
substring match in either direction against `razao_social` *or* `nome_fantasia`.
The goal is to catch "wrong company entirely", not to enforce spelling.
"""

import unicodedata

# Corporate-form tokens that carry no identifying information — dropped before
# comparison so "Silva LTDA" and "Silva" match.
_SUFIXOS = {
    "ltda", "me", "epp", "eireli", "sa", "ss", "mei", "ei", "s", "a",
    "cia", "comercio", "e",
}


def normalizar(nome: str) -> str:
    sem_acento = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode()
    bruto = sem_acento.casefold()
    for sep in ("/", ".", "-", ",", "&"):
        bruto = bruto.replace(sep, " ")
    tokens = [t for t in bruto.split() if t and t not in _SUFIXOS]
    return " ".join(tokens)


def nome_confere_com_receita(nome_informado: str, info: dict) -> bool:
    """True when `nome_informado` plausibly matches the CNPJ in `info`.

    Fails *open*: if Receita returned neither `razao_social` nor `nome_fantasia`
    (degraded payload), we cannot contradict the user, so we accept. We only
    return False on a positive mismatch — a name that lines up with nothing
    Receita has on file for that CNPJ.
    """
    alvo = normalizar(nome_informado)
    if not alvo:
        return False

    candidatos = [
        normalizar(c)
        for c in (info.get("razao_social"), info.get("nome_fantasia"))
        if c
    ]
    candidatos = [c for c in candidatos if c]

    if not candidatos:
        return True

    return any(alvo == c or alvo in c or c in alvo for c in candidatos)
