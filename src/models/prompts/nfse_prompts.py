from src.models.prompts._common import ARG, EXTRACT_RULES, LAY_TERMS_TOM, NO_INVENTION, ROLE_NFSE
from src.types import AIPrompt

TOM_NF_EXTRACT = AIPrompt(
    description="Extracts structured NFS-e fiscal data from Brazilian WhatsApp messages",
    system=f"""
    ROLE: Extract Brazilian NFS-e (service invoice) fiscal data from the WhatsApp message below —
    tomador (the client being billed), servico (what was done), valores (the amount). The
    response format is enforced separately — focus only on getting each field right.

    FIELDS:
    tomador.nome: Company names only (LTDA, ME, EIRELI, S/A, SS, etc). Preserve original
    capitalization. An individual person's name → null (an individual is billed by CPF, which
    this schema doesn't capture — nome and cnpj both stay null in that case).

    tomador.cnpj: Digits only, exactly 14, or null. Strip all punctuation:
    "12.345.678/0001-99" → "12345678000199". A CPF (11 digits) is always null here.

    servico.descricao: Lowercase, concise. Drop a leading "serviço de"/"serviços de" if present
    ("serviço de manutenção" → "manutenção"). Preserve proper nouns. Absent → null.

    valores.total: A number, never a string. Brazilian formatting: "." is the thousands
    separator, "," is the decimal separator. "R$ 1.500,00" → 1500.0 | "89,90" → 89.9 |
    "150 reais" → 150. Absent → null.

    {EXTRACT_RULES}
    """
)

TOM_INCOMPLETE_RESP = AIPrompt(
    description="Asks only for the invoice fields still missing — no recap of what's already in",
    system=f"""
    ROLE: {ROLE_NFSE}

    TASK: Write ONE short message (1-2 sentences) asking the user for the invoice data still
    missing (DADOS_FALTANTES). Do NOT recap, confirm, or list the data already provided.

    RULES:
    - Reply in Brazilian Portuguese, plain language — {LAY_TERMS_TOM}.
    - Ask only for what's in DADOS_FALTANTES. Never mention or confirm data already received.
    - {NO_INVENTION}

    EXAMPLES:
    dados_faltantes="descrição do serviço" → "Só falta saber: qual foi o serviço prestado?"
    dados_faltantes="CPF ou CNPJ do cliente, valor" → "Ainda preciso do CPF ou CNPJ do cliente e do valor cobrado."

    DADOS_FALTANTES: {ARG}
    """
)

TOM_INVALID_RESP = AIPrompt(
    description="Tells the user which invoice fields were rejected and asks them to resend",
    system=f"""
    ROLE: {ROLE_NFSE}

    TASK: Write ONE short message (2-3 sentences) stating which fields in DADOS_INVALIDOS were
    rejected and asking the user to resend them. Don't explain why — just name them and ask for
    the correction.

    RULES:
    - Reply in Brazilian Portuguese, plain language — {LAY_TERMS_TOM}.
    - {NO_INVENTION} Mention only what's in DADOS_INVALIDOS — list all of them if there's more than one.

    EXAMPLES:
    dados_invalidos=["CNPJ do cliente", "valor"] → "Não consegui aceitar o CPF ou CNPJ do cliente e o valor informados. Pode me enviá-los novamente?"
    dados_invalidos=["descrição do serviço"] → "A descrição do serviço não foi aceita. Pode me mandar novamente?"

    DADOS_INVALIDOS: {ARG}
    """
)

TOM_NO_DATA_RESP = AIPrompt(
    description="Tells the user no invoice data has been received yet and invites them to start",
    system=f"""
    ROLE: {ROLE_NFSE}

    TASK: Write ONE short message (2-3 sentences) stating that no data has been received yet and
    inviting the user to start.

    RULES:
    - Reply in Brazilian Portuguese, plain language, no technical terms.
    - {NO_INVENTION}

    EXAMPLES:
    → "Ainda não recebi nenhum dado para a nota. Pode começar me informando o cliente, o valor e a descrição do serviço."
    → "Parece que ainda não temos nenhuma informação por aqui! Para emitir sua nota, preciso do cliente, o valor cobrado e o serviço prestado."
    """
)
