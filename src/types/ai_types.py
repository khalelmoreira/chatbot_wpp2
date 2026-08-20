import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import StrEnum
from typing import Callable, Generic, Type, TypeVar

from src.types.protocols import FromDictable

logger = logging.getLogger(__name__)
TExtracted = TypeVar('TExtracted', bound=FromDictable)
TInterpreted = TypeVar('TInterpreted')

class PrestRespKey(StrEnum):
    INCOMPLETE  = "INCOMPLETE"
    INVALID     = "INVALID"
    NO_DATA     = "NO_DATA"
    GENERAL_ASK = "GENERAL_ASK"
    NO_INTENT   = "NO_INTENT"

class PrestClassKey(StrEnum):
    HAS_INTENT = "HAS_INTENT"

class PrestExtractKey(StrEnum):
    DATA    = "DATA"
    ADDRESS = "ADDRESS"

class TomRespKey(StrEnum):
    INCOMPLETE      = "INCOMPLETE"
    INVALID         = "INVALID"
    NO_DATA         = "NO_DATA"
    ONBOARD_INFO    = "ONBOARD_INFO"
    ONBOARD_HISTORY = "ONBOARD_HISTORY"
    NO_INTENT       = "NO_INTENT"

class TomClassKey(StrEnum):
    ONBOARD_REF_PAST = "ONBOARD_REF_PAST"
    HAS_INTENT       = "HAS_INTENT"
    LOOKSLIKE_ASK    = "LOOKSLIKE_ASK"

class TomExtractKey(StrEnum):
    NF = "NF"

class IssClassKey(StrEnum):
    SERVICE_CODE = "SERVICE_CODE"

class AIClientError(Exception):
    """Chamada ao provedor de IA falhou. Não é retentável por padrão (ex: chave invalida, request malformado)."""

class AIClientRetryableError(AIClientError):
    """Falha transitoria ou do lado do provedor — seguro tentar um provedor de fallback."""

class AIClient(ABC):

    @abstractmethod
    def extract_json(self, system_prompt: str, user_msg: str, schema: dict) -> dict:
        pass

    @abstractmethod
    def extract_text(self, system_prompt: str, user_msg: str) -> str:
        pass

@dataclass
class AIPrompt:
    system:      str
    description: str = ""

    def __str__(self) -> str:
        return self.system

    def render(self, *args: str) -> str:
        return self.system.format(*args)

@dataclass
class AIExtractor(Generic[TExtracted]):
    client:      AIClient
    prompt:      AIPrompt
    output_type: Type[TExtracted]
    schema:      dict

    def extract(self, text: str) -> TExtracted | None:
        try:
            response_json = self.client.extract_json(
                system_prompt=str(self.prompt),
                user_msg=text,
                schema=self.schema,
            )
            logger.debug("extract response=%s", response_json)
            return self.output_type.from_dict(response_json)
        except Exception as e:
            logger.info(f"Erro ao extrair {self.output_type.__name__}: {e}")
            return None

@dataclass(frozen=True)
class ExtractionConfig(Generic[TExtracted]):
    prompt:      AIPrompt
    output_type: Type[TExtracted]
    schema:      dict

@dataclass(frozen=True)
class ClassificationConfig(Generic[TInterpreted]):
    prompt:   AIPrompt
    schema:   dict
    parser:   Callable[[object], TInterpreted]
    fallback: TInterpreted

@dataclass(frozen=True)
class ResponseConfig:
    prompt:   AIPrompt
    fallback: str = "Não entendi, pode reformular?"

@dataclass
class AIInterpreter(Generic[TInterpreted]):
    client:   AIClient
    prompt:   AIPrompt
    parser:   Callable[[str], TInterpreted]
    fallback: TInterpreted

    def interpret(self, text: str) -> TInterpreted:
        try:
            response = self.client.extract_text(
                system_prompt=str(self.prompt),
                user_msg=text
            )
            return self.parser(response)
        except Exception as e:
            logger.info(f"Erro ao classificar com prompt '{self.prompt}': {e}")
            return self.fallback

@dataclass
class AIClassifier(Generic[TInterpreted]):
    client:   AIClient
    prompt:   AIPrompt
    schema:   dict
    parser:   Callable[[object], TInterpreted]
    fallback: TInterpreted

    def classify(self, text: str) -> TInterpreted:
        try:
            response = self.client.extract_json(
                system_prompt=str(self.prompt),
                user_msg=text,
                schema=self.schema,
            )
            return self.parser(response["value"])
        except Exception as e:
            logger.info(f"Erro ao classificar com prompt '{self.prompt}': {e}")
            return self.fallback