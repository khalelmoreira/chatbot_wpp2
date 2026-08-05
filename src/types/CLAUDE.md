<!-- Verified against the actual repo on 2026-08-04. Loads only when Claude Code reads files in src/types/. -->

# Type system conventions (src/types/)

- Each entity file (`user.py`, `tomador.py`, `nfs.py`, `conversation.py`, `wpp_msg.py`) owns its own `StrEnum`s and dataclasses together — there's no separate `enums.py`.
- `ContextBase(Generic[T])` (`base.py`) carries `user`, `text`, `msg_type`, `button_id`, `new_data`, `db_data`, `merged`, `valid: T`, and a `validation: ValidationResult`. `TypeVar T` is bound to `Mergeable`. `ContextPrestador` / `ContextTomador` (`context.py`) are the concrete `ContextBase[PrestadorData]` / `ContextBase[TomadorData]`.
- `MergeableMixin.merge()` recursively merges via `isinstance(valor, Mergeable)`; non-mergeable fields fall back to "new value if not None, else keep current."
- `FromDictMixin.from_dict()` builds an instance from a mapping and *does* recurse into nested fields whose type is itself `FromDictMixin` (via `_unwrap_optional` on `X | None`) — it isn't limited to flat, non-nested dataclasses.
- `TextMixin.to_str()` renders WhatsApp-formatted text, skipping `None` fields and any field marked `field(metadata={"oculto": True})`; `field(metadata={"label": ...})` overrides the display label. `TextMixin.from_row()` builds an instance from a `Mapping` or another dataclass plus keyword overrides.
- `ValidationOutput(Generic[T])` is defined in `src/services/validators/validador_prestador.py`, not in `src/types/` — don't go looking for it here. It pairs a typed `valid: T` with a `ValidationResult`. The private `_validar(data, validations, factory)` helper is already generic; the public entry points (`ValidatorPrestador.validar`, `ValidatorAddress.validar`) are still per-entity. Treat a fully generic, exposed `Validator.validar()` as a planned direction, not the current API.
- Address validation only runs when `data.address is not None` — don't let a validator report a missing address for a `PrestadorData` that never had one.
- There's no `PrestadorExtraido`-style schema class that structurally excludes `address`. Instead, address extraction is just a separate AI operation: `PrestExtractKey.DATA` vs `PrestExtractKey.ADDRESS`, each with its own prompt and `output_type` (see `src/services/ai/CLAUDE.md`).
- `AIOperations.extract()` returns `object | None` — extraction spans heterogeneous domains (`PrestadorData`, `Address`, `TomadorData`, ...) so the return type can't be narrower. Callers `cast()` to the concrete type at the call site.
