from enum import Enum
from dataclasses import dataclass

class UserStatus(str, Enum):
    NEW                   = "NEW"
    COLLECTING            = "COLLECTING"
    NO_ADDRESS            = "NO_ADDRESS"
    CONFIRMING            = "CONFIRMING"
    QUEUED                = "QUEUED"
    AGUARDANDO_CERTIFICADO = "aguardando_certificado"
    ATIVO                  = "ativo"

@dataclass
class User:
    id: int
    phone: str
    name: str
    estado: UserStatus