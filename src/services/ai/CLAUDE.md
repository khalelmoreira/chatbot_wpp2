<!-- Verified against the actual repo on 2026-08-04. Loads only when Claude Code reads files in src/services/ai/. -->

# AI service layer (src/services/ai/)

- `AIOperations(Generic[KE, KC, KR])` (`ai_service.py`) is the core: three separate method families, `extract`, `classify`, `respond`, each keyed by its own `StrEnum` (`KE`/`KC`/`KR`). Don't merge these into one call — a message that needs both extraction and classification gets two calls.
- `AIService` builds one `AIOperations` instance per entity: `self.prest` (keys: `PrestExtractKey`, `PrestClassKey`, `PrestRespKey`) and `self.tom` (keys: `TomExtractKey`, `TomClassKey`, `TomRespKey`), all defined in `src/types/ai_types.py`.
- Address is extracted separately from the rest of the prestador data: `PrestExtractKey.DATA` → `PrestadorData`, `PrestExtractKey.ADDRESS` → `Address`, each with its own prompt (`PREST_DATA_EXTRACT` / `PREST_ADDRESS_EXTRACT`) and `output_type`. This is how address extraction stays decoupled from the main extraction — there's no schema class that structurally hides the field.
- Prompt text lives in `src/models/prompts/`, one file per concern (`prestador_prompts.py`, `onboard_prompts.py`, `nfse_prompts.py`, `conversation_prompts.py`) — not a flat `prompts/` at `src/` root.
- `extract()` returns `object | None` and needs a `cast()` at the call site (see `src/types/CLAUDE.md`). `classify()` returns `object`; `respond()` returns `str`.
- `AIClient` is an `ABC`, not a `Protocol` — it's a real external boundary (the LLM client), so this is intentional, not an inconsistency with the Protocol-preference convention elsewhere.
- `ResultExtract` (`src/types/conversation.py`) already separates `campos: dict` from `parece_pergunta: bool` — keep "is this a question" classification as its own concern rather than folding it back into extraction.
