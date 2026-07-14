from dataclasses import dataclass
import re
import requests
from src.models.urls import NOTAAS_BASE_URL
from src.types import ContextPrestador, CnpjJaCadastradoError, LimitePlanoAtingidoError, DadosInvalidosError

class ProjectService:
    def __init__(self, ctx: ContextPrestador):
        self.validated = ctx.validated
        self.address = ctx.validated.address

    def _only_digits(self, value: str) -> str:
        return re.sub(r"\D", "", value or "")
    
    def create_project(self, org_token: str) -> str | None:
        payload = self.build_payload()

        resp = requests.post(
            f"{NOTAAS_BASE_URL}/org/projects",
            json=payload,
            headers={"x-api-key": org_token},
            timeout=15,
        )

        if resp.status_code == 201:
            return resp.json()["id"]
        
        if resp.status_code == 409:
            existing_id = resp.json().get("existingProjectId")
            raise CnpjJaCadastradoError(existing_id)
        
        if resp.status_code == 403:
            raise LimitePlanoAtingidoError("Limite de projetos do plano atingido.")
        
        if resp.status_code == 400:
            raise DadosInvalidosError(resp.json().get("message", "Dados inválidos."))
        
        resp.raise_for_status()

    def build_payload(self) -> dict:
        payload = {
            "name": self.validated.razao_social,
            "cnpj": self.validated.cnpj,
            "razaoSocial": self.validated.razao_social,
            "regimeTributario": self.validated.regime_tributario,
        }

        opcionais_diretos = {
            "codigoMunicipio": "codigo_municipio",
            "email": "email",
            "telefone": "phone",
        }

        for campos_ntaas, campo_interno in opcionais_diretos.items():
            valor = getattr(self.validated, campo_interno, None)
            if valor:
                payload[campos_ntaas] = valor

        address = {
            "logradouro": self.address.logradouro,
            "numero": self.address.numero,
            "complemento": self.address.complemento,
            "bairro": self.address.bairro,
            "cidade": self.address.cidade,
            "uf": self.address.uf,
            "cep": self.validated.cep,
        }

        address_preenchido = {k: v for k, v in address.items() if v}
        if address_preenchido:
            payload["endereco"] = address_preenchido

        return payload