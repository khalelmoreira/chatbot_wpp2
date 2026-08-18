import logging
from dataclasses import replace
from enum import StrEnum
from typing import Generic, TypeVar

from src.models.prompts import (
    ONBOARD_HISTORY_RESP,
    ONBOARD_INFO_RESP,
    ONBOARD_REF_PAST_CLASS,
    PREST_ADDRESS_EXTRACT,
    PREST_DATA_EXTRACT,
    PREST_GENERAL_ASK_RESP,
    PREST_HAS_INTENT_CLASS,
    PREST_INCOMPLETE_RESP,
    PREST_INVALID_RESP,
    PREST_NO_DATA_RESP,
    PREST_NO_INTENT_RESP,
    TOM_HAS_INTENT_CLASS,
    TOM_INCOMPLETE_RESP,
    TOM_INVALID_RESP,
    TOM_NF_EXTRACT,
    TOM_NO_DATA_RESP,
    TOM_NO_INTENT_RESP,
)
from src.types import (
    Address,
    AIClassifier,
    AIClient,
    AIExtractor,
    AIInterpreter,
    AIPrompt,
    ClassificationConfig,
    ExtractionConfig,
    IntentType,
    IntentUserType,
    PrestadorData,
    PrestClassKey,
    PrestExtractKey,
    PrestRespKey,
    ResponseConfig,
    TomadorData,
    TomClassKey,
    TomExtractKey,
    TomRespKey,
)

logger = logging.getLogger(__name__)

KE = TypeVar('KE', bound=StrEnum)
KC = TypeVar('KC', bound=StrEnum)
KR = TypeVar('KR', bound=StrEnum)

def _value_schema(value_schema: dict) -> dict:
    """Envelope de um valor unico usado por classify() — AIClassifier le response["value"]."""
    return {
        "type": "object",
        "properties": {"value": value_schema},
        "required": ["value"],
        "additionalProperties": False,
    }

BOOL_VALUE_SCHEMA = _value_schema({"type": "boolean"})

PREST_HAS_INTENT_SCHEMA = _value_schema(
    {"type": "string", "enum": ["ONBOARDING", "GENERAL_ASK", "NENHUM"]}
)

TOM_HAS_INTENT_SCHEMA = _value_schema(
    {"type": "string", "enum": ["EMITIR", "CONSULTA", "NENHUM"]}
)

PREST_DATA_SCHEMA = {
    "type": "object",
    "properties": {
        "razao_social":      {"type": ["string", "null"]},
        "cnpj":              {"type": ["string", "null"]},
        "email":             {"type": ["string", "null"]},
        "regime_tributario": {"type": ["string", "null"], "enum": ["1", "2", "3", "3e", None]},
        "cep":               {"type": ["string", "null"]},
    },
    "required": ["razao_social", "cnpj", "email", "regime_tributario", "cep"],
    "additionalProperties": False,
}

PREST_ADDRESS_SCHEMA = {
    "type": "object",
    "properties": {
        "razao_social":      {"type": ["string", "null"]},
        "cnpj":              {"type": ["string", "null"]},
        "email":             {"type": ["string", "null"]},
        "regime_tributario": {"type": ["string", "null"], "enum": ["1", "2", "3", "3e", None]},
        "cep":               {"type": ["string", "null"]},
        "logradouro":        {"type": ["string", "null"]},
        "numero":            {"type": ["string", "null"]},
        "complemento":       {"type": ["string", "null"]},
        "bairro":            {"type": ["string", "null"]},
        "cidade":            {"type": ["string", "null"]},
        "uf":                {"type": ["string", "null"]},
    },
    "required": [
        "razao_social", "cnpj", "email", "regime_tributario", "cep",
        "logradouro", "numero", "complemento", "bairro", "cidade", "uf",
    ],
    "additionalProperties": False,
}

TOM_NF_SCHEMA = {
    "type": "object",
    "properties": {
        "tomador": {
            "type": "object",
            "properties": {
                "nome": {"type": ["string", "null"]},
                "cnpj": {"type": ["string", "null"]},
            },
            "required": ["nome", "cnpj"],
            "additionalProperties": False,
        },
        "servico": {
            "type": "object",
            "properties": {
                "descricao": {"type": ["string", "null"]},
            },
            "required": ["descricao"],
            "additionalProperties": False,
        },
        "valores": {
            "type": "object",
            "properties": {
                "total": {"type": ["number", "null"]},
            },
            "required": ["total"],
            "additionalProperties": False,
        },
    },
    "required": ["tomador", "servico", "valores"],
    "additionalProperties": False,
}

class AIOperations(Generic[KE, KC, KR]):
    def __init__(
        self,
        client: AIClient,
        extract_conf: dict[KE, ExtractionConfig],
        classify_conf: dict[KC, ClassificationConfig],
        respond_conf: dict[KR, ResponseConfig],
    ):
        self.client = client
        self._extract_conf = extract_conf
        self._classify_conf = classify_conf
        self._respond_conf = respond_conf

    def _render(self, prompt: AIPrompt, params: list[str] | tuple[str, ...] = ()) -> AIPrompt:
        return replace(prompt, system=prompt.render(*params)) if params else prompt

    def extract(self, key: KE, text: str, params: list[str] | tuple[str, ...] = ()) -> object | None:
        config = self._extract_conf[key]
        prompt = self._render(config.prompt, params)
        return AIExtractor(self.client, prompt, config.output_type, config.schema).extract(text)

    def classify(self, key: KC, text: str, params: list[str] | tuple[str, ...] = ()) -> object:
        config = self._classify_conf[key]
        prompt = self._render(config.prompt, params)
        return AIClassifier(self.client, prompt, config.schema, config.parser, config.fallback).classify(text)

    def respond(self, key: KR, text: str, params: list[str] | tuple[str, ...] = ()) -> str:
        config = self._respond_conf[key]
        prompt = self._render(config.prompt, params)
        return AIInterpreter(self.client, prompt, lambda r: r, config.fallback).interpret(text)
        

class AIService:
    def __init__(self, client: AIClient):
        self.client = client

        self.prest = AIOperations(
            client,
            extract_conf={
                PrestExtractKey.DATA: ExtractionConfig(
                    PREST_DATA_EXTRACT, PrestadorData, schema=PREST_DATA_SCHEMA,
                ),
                PrestExtractKey.ADDRESS: ExtractionConfig(
                    PREST_ADDRESS_EXTRACT, Address, schema=PREST_ADDRESS_SCHEMA,
                ),
            },
            classify_conf={
                PrestClassKey.HAS_INTENT: ClassificationConfig(
                    prompt=PREST_HAS_INTENT_CLASS,
                    schema=PREST_HAS_INTENT_SCHEMA,
                    parser=lambda v: IntentUserType(v),
                    fallback=IntentUserType.NENHUM,
                ),
            },
            respond_conf={
                PrestRespKey.NO_INTENT: ResponseConfig(PREST_NO_INTENT_RESP),
                PrestRespKey.NO_DATA: ResponseConfig(PREST_NO_DATA_RESP),
                PrestRespKey.GENERAL_ASK: ResponseConfig(PREST_GENERAL_ASK_RESP),
                PrestRespKey.INCOMPLETE: ResponseConfig(PREST_INCOMPLETE_RESP),
                PrestRespKey.INVALID: ResponseConfig(PREST_INVALID_RESP),
            },
        )

        self.tom = AIOperations(
            client,
            extract_conf={
                TomExtractKey.NF: ExtractionConfig(
                    TOM_NF_EXTRACT, TomadorData, schema=TOM_NF_SCHEMA,
                ),
            },
            classify_conf={
                TomClassKey.HAS_INTENT: ClassificationConfig(
                    TOM_HAS_INTENT_CLASS,
                    schema=TOM_HAS_INTENT_SCHEMA,
                    parser=lambda v: IntentType(v),
                    fallback=IntentType.NENHUM,
                ),
                TomClassKey.ONBOARD_REF_PAST: ClassificationConfig(
                    ONBOARD_REF_PAST_CLASS,
                    schema=BOOL_VALUE_SCHEMA,
                    parser=lambda v: bool(v),
                    fallback=False,
                ),
            },
            respond_conf={
                TomRespKey.NO_DATA: ResponseConfig(TOM_NO_DATA_RESP),
                TomRespKey.NO_INTENT: ResponseConfig(
                    TOM_NO_INTENT_RESP,
                    "Estou aqui para emitir notas fiscais. Me envie os dados do tomador do serviço.",
                ),
                TomRespKey.INCOMPLETE: ResponseConfig(TOM_INCOMPLETE_RESP),
                TomRespKey.INVALID: ResponseConfig(TOM_INVALID_RESP),
                TomRespKey.ONBOARD_INFO: ResponseConfig(ONBOARD_INFO_RESP),
                TomRespKey.ONBOARD_HISTORY: ResponseConfig(ONBOARD_HISTORY_RESP),
            },
        )