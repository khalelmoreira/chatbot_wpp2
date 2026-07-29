from typing import Any
from dataclasses import dataclass

@dataclass
class HandlerResult:
    status: int
    body: dict[str, Any]

    @property
    def ok(self) -> bool:
        return self.status < 400