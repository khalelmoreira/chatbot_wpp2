from dataclasses import dataclass
from typing import Any


@dataclass
class HandlerResult:
    status: int
    body: dict[str, Any]

    @property
    def ok(self) -> bool:
        return self.status < 400