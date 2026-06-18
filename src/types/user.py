from enum import Enum
from dataclasses import dataclass

class EstadoUser(str, Enum):
    NOVO                   = "novo"
    CADASTRO_PRESTADOR     = "cadastro_prestador"
    CADASTRO_ENDERECO      = "cadastro_endereco"
    CADASTRO_ENDERECO_MANUAL = "cadastro_endereco_manual"
    CRIANDO_PROJETO_NOTAAS = "criando_projeto_notaas"
    AGUARDANDO_CERTIFICADO = "aguardando_certificado"
    ATIVO                  = "ativo"

@dataclass
class User:
    id: int
    phone: str
    name: str
    estado: EstadoUser