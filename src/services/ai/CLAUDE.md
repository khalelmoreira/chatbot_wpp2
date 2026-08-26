<!-- Verified against the actual repo on 2026-08-04. Loads only when Claude Code reads files in src/services/ai/. -->

# AI service layer (src/services/ai/)

- `AIOperations(Generic[KE, KC, KR])` (`ai_service.py`) is the core: three method families, `extract`, `classify`, `respond`, each keyed by its own `StrEnum` (`KE`/`KC`/`KR`). Don't merge these into one call — extraction and classification for one message are two calls.
- `AIService` builds one `AIOperations` instance per entity: `self.prest` (keys: `PrestExtractKey`, `PrestClassKey`, `PrestRespKey`) and `self.tom` (keys: `TomExtractKey`, `TomClassKey`, `TomRespKey`), all in `src/types/ai_types.py`.
- Address is extracted separately from the rest of the prestador data: `PrestExtractKey.DATA` → `PrestadorData`, `PrestExtractKey.ADDRESS` → `Address`, each with its own prompt (`PREST_DATA_EXTRACT` / `PREST_ADDRESS_EXTRACT`) and `output_type`.
- Prompt text lives in `src/models/prompts/`, one file per concern (`prestador_prompts.py`, `onboard_prompts.py`, `nfse_prompts.py`, `conversation_prompts.py`), not a flat `prompts/` at `src/` root.
- `extract()` returns `object | None`, needs a `cast()` at the call site (see `src/types/CLAUDE.md`). `classify()` returns `object`; `respond()` returns `str`.
- `AIClient` is an `ABC`, not a `Protocol` — an intentional exception, not an inconsistency with the Protocol-preference convention elsewhere.
- `ResultExtract` (`src/types/conversation.py`) separates `campos: dict` from `parece_pergunta: bool` — keep "is this a question" classification separate from extraction.
