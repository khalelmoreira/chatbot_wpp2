from src.models.national_service_codes import NATIONAL_SERVICE_CODES, UNCLASSIFIED
from src.types import AIPrompt

_CANDIDATE_LIST = "\n".join(f"{c.codigo}: {c.descricao}" for c in NATIONAL_SERVICE_CODES)

ISS_SERVICE_CODE_CLASS = AIPrompt(
    description="Classifies a free-text service description into a national service code (cTribNac) or UNCLASSIFIED",
    system=f"""
    ROLE: Classify the Brazilian service description below into one of the national service
    codes (código de tributação nacional / cTribNac) listed in CANDIDATOS, or "{UNCLASSIFIED}"
    if none fits with confidence.

    CANDIDATOS:
    {_CANDIDATE_LIST}

    RULES:
    - Only pick a code if the description clearly matches its meaning. Never guess the closest
      code when the match is ambiguous or the description doesn't fit any candidate.
    - If the description is ambiguous, out of scope, or doesn't match any CANDIDATOS entry,
      respond with "{UNCLASSIFIED}" — do not invent or approximate a code.
    - Respond with only the 6-digit code or "{UNCLASSIFIED}", nothing else.
    """
)
