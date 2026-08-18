from src.models.prompts.conversation_prompts import (
    TOM_HAS_INTENT_CLASS,
    TOM_LOOKSLIKE_ASK_CLASS,
    TOM_NO_INTENT_RESP,
)
from src.models.prompts.nfse_prompts import (
    TOM_INCOMPLETE_RESP,
    TOM_INVALID_RESP,
    TOM_NF_EXTRACT,
    TOM_NO_DATA_RESP,
)
from src.models.prompts.onboard_prompts import (
    ONBOARD_HISTORY_RESP,
    ONBOARD_INFO_RESP,
    ONBOARD_REF_PAST_CLASS,
)
from src.models.prompts.prestador_prompts import (
    PREST_ADDRESS_EXTRACT,
    PREST_DATA_EXTRACT,
    PREST_GENERAL_ASK_RESP,
    PREST_HAS_INTENT_CLASS,
    PREST_INCOMPLETE_RESP,
    PREST_INVALID_RESP,
    PREST_NO_DATA_RESP,
    PREST_NO_INTENT_RESP,
)

__all__ = [
    # nfse_prmpts
    "TOM_NF_EXTRACT",
    "TOM_INCOMPLETE_RESP",
    "TOM_INVALID_RESP",
    "TOM_NO_DATA_RESP",
    # onboard_prmpts
    "ONBOARD_INFO_RESP",
    "ONBOARD_REF_PAST_CLASS",
    "ONBOARD_HISTORY_RESP",
    # conversation prompts
    "TOM_NO_INTENT_RESP",
    "TOM_HAS_INTENT_CLASS",
    "TOM_LOOKSLIKE_ASK_CLASS",
    # prestador prompts
    "PREST_DATA_EXTRACT",
    "PREST_INCOMPLETE_RESP",
    "PREST_INVALID_RESP",
    "PREST_NO_DATA_RESP",
    "PREST_ADDRESS_EXTRACT",
    "PREST_HAS_INTENT_CLASS",
    "PREST_GENERAL_ASK_RESP",
    "PREST_NO_INTENT_RESP",
]