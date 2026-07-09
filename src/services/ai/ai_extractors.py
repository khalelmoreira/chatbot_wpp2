from dataclasses import dataclass
from typing import Generic, TypeVar, Callable, Type
from src.integrations.ai_client import AIClient
from src.models.prompts.base import AIPrompt
from src.types import DadosPrestador, DadosTomador, Tomador, Servico, Valores, Endereco

T = TypeVar('T')

@dataclass
class AIExtractor(Generic[T]):
    """Extrator genérico de dados via IA"""

    client: AIClient
    prompt: AIPrompt
    output_type: Type[T]
    parser: Callable[[dict], T]

    def extract(self, text: str) -> T:
        """Extrai dados do texto usando IA e parseia para tipo T"""

        try:
            response_json = self.client.extract_json(
                system_prompt=str(self.prompt),
                user_msg=text
            )
            return self.parser(response_json)
        
        except Exception as e:
            print(f"Erro ao extrair {self.output_type.__name__}: {e}")
            # Retorna instância vazia com None
            return self.output_type()


# Parsers específicos

def parse_prestador_data(data: dict) -> DadosPrestador:

    return DadosPrestador(
        razao_social=data.get("razao_social"),
        cnpj=data.get("cnpj"),
        email=data.get("email"),
        regime_tributario=data.get("regime_tributario"),
        cep=data.get("cep"),
        endereco=data.get("endereco")
    )

def parse_tomador_data(data: dict) -> DadosTomador:

    tomador_data = data.get("tomador", {})
    servico_data = data.get("servico", {})
    valores_data = data.get("valores", {})
    
    return DadosTomador(
        tomador=Tomador(
            nome=tomador_data.get("nome"),
            cnpj=tomador_data.get("cnpj")
        ),
        servico=Servico(
            descricao=servico_data.get("descricao")
        ),
        valores=Valores(
            total=valores_data.get("total"),
            aliquotaIss=valores_data.get("aliquotaIss")
        )
    )

def parse_endereco(data: dict) -> Endereco:

    return Endereco(
        logradouro=data.get("logradouro"),
        numero=data.get("numero"),
        complemento=data.get("complemento"),
        bairro=data.get("bairro"),
        cidade=data.get("cidade"),
        uf=data.get("uf"),
        cep=data.get("cep"),
    )