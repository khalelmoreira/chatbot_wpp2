from src.models.prompts.consulta_prompts import (
    CONSULTA_HISTORY_RESP,
    CONSULTA_INFO_RESP,
    CONSULTA_REF_PAST_CLASS,
)
from src.models.prompts.conversation_prompts import (
    TOM_HAS_INTENT_CLASS,
    TOM_LOOKSLIKE_ASK_CLASS,
    TOM_NO_INTENT_RESP,
)
from src.models.prompts.iss_prompts import (
    ISS_SERVICE_CODE_CLASS,
)
from src.models.prompts.nfse_prompts import (
    TOM_INCOMPLETE_RESP,
    TOM_INVALID_RESP,
    TOM_NF_EXTRACT,
    TOM_NO_DATA_RESP,
)
from src.models.prompts.prestador_prompts import (
    PREST_ADDRESS_EXTRACT,
    PREST_DATA_EXTRACT,
    PREST_HAS_INTENT_CLASS,
    PREST_HELP_RESP,
    PREST_INCOMPLETE_RESP,
    PREST_INVALID_RESP,
    PREST_NO_DATA_RESP,
    PREST_NO_INTENT_RESP,
)

__all__ = [
    # iss_prompts
    "ISS_SERVICE_CODE_CLASS",
    # nfse_prompts
    "TOM_NF_EXTRACT",
    "TOM_INCOMPLETE_RESP",
    "TOM_INVALID_RESP",
    "TOM_NO_DATA_RESP",
    # consulta_prompts
    "CONSULTA_INFO_RESP",
    "CONSULTA_REF_PAST_CLASS",
    "CONSULTA_HISTORY_RESP",
    # conversation_prompts
    "TOM_NO_INTENT_RESP",
    "TOM_HAS_INTENT_CLASS",
    "TOM_LOOKSLIKE_ASK_CLASS",
    # prestador_prompts
    "PREST_DATA_EXTRACT",
    "PREST_INCOMPLETE_RESP",
    "PREST_INVALID_RESP",
    "PREST_NO_DATA_RESP",
    "PREST_ADDRESS_EXTRACT",
    "PREST_HAS_INTENT_CLASS",
    "PREST_HELP_RESP",
    "PREST_NO_INTENT_RESP",
]
