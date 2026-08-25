<!-- Verified against the actual repo on 2026-08-04. Loads only when Claude Code reads files in src/types/. -->

# Type system conventions (src/types/)

- Each entity file (`user.py`, `tomador.py`, `nfs.py`, `conversation.py`, `wpp_msg.py`) owns its own `StrEnum`s and dataclasses together — no separate `enums.py`.
- `ContextBase(Generic[T])` (`base.py`) carries `user`, `text`, `msg_type`, `button_id`, `new_data`, `db_data`, `merged`, `valid: T`, `validation: ValidationResult`. `TypeVar T` is bound to `Mergeable`. `ContextPrestador` / `ContextTomador` (`context.py`) are `ContextBase[PrestadorData]` / `ContextBase[TomadorData]`.
- `MergeableMixin.merge()` recursively merges via `isinstance(valor, Mergeable)`; non-mergeable fields: new value if not None, else keep current.
- `FromDictMixin.from_dict()` recurses into nested fields whose type is itself `FromDictMixin` (via `_unwrap_optional` on `X | None`) — not limited to flat dataclasses.
- `TextMixin.to_str()` renders WhatsApp-formatted text, skipping `None` fields and `field(metadata={"oculto": True})`; `field(metadata={"label": ...})` overrides the display label. `TextMixin.from_row()` builds an instance from a `Mapping` or another dataclass plus keyword overrides.
- `ValidationOutput(Generic[T])` is defined in `src/services/validators/validador_prestador.py`, not here. Pairs a typed `valid: T` with a `ValidationResult`. `_validar(data, validations, factory)` is generic; the public entry points (`ValidatorPrestador.validar`, `ValidatorAddress.validar`) are still per-entity — a generic exposed `Validator.validar()` is a planned direction, not current.
- Address validation only runs when `data.address is not None` — don't report a missing address for a `PrestadorData` that never had one.
- No `PrestadorExtraido`-style schema class excluding `address`. Address extraction is a separate AI operation: `PrestExtractKey.DATA` vs `PrestExtractKey.ADDRESS`, each with its own prompt and `output_type` (see `src/services/ai/CLAUDE.md`).
- `AIOperations.extract()` returns `object | None` — extraction spans heterogeneous domains (`PrestadorData`, `Address`, `TomadorData`, ...). Callers `cast()` to the concrete type at the call site.
