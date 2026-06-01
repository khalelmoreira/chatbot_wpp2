from typing import Optional
from dataclasses import dataclass
from src.types.context_base import ContextBase

@dataclass
class DadosCadastro:
    nome: Optional[str] = None
    cpf_cnpj: Optional[str] = None
    email: Optional[str] = None

    def merge(self, novos: "DadosCadastro") -> "DadosCadastro":
        return DadosCadastro(
            nome=novos.nome or self.nome,
            cpf_cnpj=novos.cpf_cnpj or self.cpf_cnpj,
            email=novos.email or self.email,
        )
    
    def campos_faltantes(self) -> list[str]:
        return [k for k, v in vars(self).items() if v is None]
    
    def is_complete(self) -> bool:
        return not self.campos_faltantes()


ContextCadastro = ContextBase[DadosCadastro]