from dataclasses import fields, is_dataclass
from types import NoneType, UnionType
from typing import Any, Mapping, Self, cast, get_args, get_origin, get_type_hints

from src.types.protocols import IsDataclass, Mergeable


class MergeableMixin:
    def merge(self, novos: "Self") -> "Self":
        kwargs = {}
        for f in fields(cast(IsDataclass, self)):
            valor_atual = getattr(self, f.name)
            valor_novo = getattr(novos, f.name)

            if isinstance(valor_atual, Mergeable) and isinstance(valor_novo, Mergeable):
                kwargs[f.name] = valor_atual.merge(valor_novo)

            else:
                kwargs[f.name] = valor_novo if valor_novo is not None else valor_atual

        return type(self)(**kwargs)

class TextMixin:
    @classmethod
    def from_row(cls, data: Mapping[str, Any] | IsDataclass, **aliases: Any):
        if is_dataclass(data) and not isinstance(data, type):
            base = {f.name: getattr(data, f.name) for f in fields(data)}
        else:
            base = dict(cast(Mapping[str, Any], data))

        merged = {**base, **aliases}
        return cls(**{f.name: merged.get(f.name) for f in fields(cast(IsDataclass, cls))})

    def to_str(self, sep: str = "\n") -> str:
        rows = []
        for f in fields(cast(IsDataclass, self)):
            v = getattr(self, f.name)
            if v is None or f.metadata.get("oculto"):
                continue

            label = f.metadata.get("label", f.name)
            rows.append(f"{label}: {v}")

        return sep.join(rows)

class FromDictMixin:
    @classmethod
    def from_dict(cls, data: Mapping[str, Any] | None) -> Self:
        if not data:
            return cls()

        hints = get_type_hints(cls)
        kwargs = {}

        for f in fields(cast(IsDataclass, cls)):
            tipo = hints.get(f.name)
            tipo_base = cls._unwrap_optional(tipo)

            if isinstance(tipo_base, type) and issubclass(tipo_base, FromDictMixin):
                kwargs[f.name] = tipo_base.from_dict(data)
            elif f.name in data:
                kwargs[f.name] = data.get(f.name)

        return cls(**kwargs)

    @staticmethod
    def _unwrap_optional(tipo: Any) -> Any:
        if get_origin(tipo) is UnionType:
            args = [a for a in get_args(tipo) if a is not NoneType]
            if len(args) == 1:
                return args[0]

        return tipo