from dataclasses import replace
from enum import StrEnum
import logging
from typing import Generic, TypeVar
from src.types import (
    TomadorData,
    PrestadorData,
    IntentType,
    IntentUserType,
    Address,
    AIClient,
    AIInterpreter,
    ClassificationConfig,
    ExtractionConfig,
    AIExtractor,
    PrestRespKey,
    PrestClassKey,
    PrestExtractKey,
    ResponseConfig,
    TomExtractKey,
    TomRespKey,
    TomClassKey,
    AIPrompt,
)
from src.models.prompts import (
    TOM_NF_EXTRACT,
    TOM_HAS_INTENT_CLASS,
    TOM_NO_INTENT_RESP,
    TOM_INCOMPLETE_RESP,
    TOM_INVALID_RESP,
    TOM_NO_DATA_RESP,
    ONBOARD_INFO_RESP,
    ONBOARD_REF_PAST_CLASS,
    ONBOARD_HISTORY_RESP,
    PREST_DATA_EXTRACT,
    PREST_ADDRESS_EXTRACT,
    PREST_NO_INTENT_RESP,
    PREST_NO_DATA_RESP,
    PREST_GENERAL_ASK_RESP,
    PREST_INCOMPLETE_RESP,
    PREST_HAS_INTENT_CLASS,
    PREST_INVALID_RESP,
)

logger = logging.getLogger(__name__)

KE = TypeVar('KE', bound=StrEnum)
KC = TypeVar('KC', bound=StrEnum)
KR = TypeVar('KR', bound=StrEnum)

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
        return AIExtractor(self.client, prompt, config.output_type).extract(text)

    def classify(self, key: KC, text: str, params: list[str] | tuple[str, ...] = ()) -> object:
        config = self._classify_conf[key]
        prompt = self._render(config.prompt, params)
        return AIInterpreter(self.client, prompt, config.parser, config.fallback).interpret(text)

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
                PrestExtractKey.DATA: ExtractionConfig(PREST_DATA_EXTRACT, PrestadorData),
                PrestExtractKey.ADDRESS: ExtractionConfig(PREST_ADDRESS_EXTRACT, Address),
            },
            classify_conf={
                PrestClassKey.HAS_INTENT: ClassificationConfig(
                    prompt=PREST_HAS_INTENT_CLASS,
                    parser=lambda r: IntentUserType(r.strip().upper()),
                    fallback="erro ao classificar",
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
                TomExtractKey.NF: ExtractionConfig(TOM_NF_EXTRACT, TomadorData),
            },
            classify_conf={
                TomClassKey.HAS_INTENT: ClassificationConfig(
                    TOM_HAS_INTENT_CLASS,
                    lambda r: r.lower().startswith("true"),
                    False,
                ),
                TomClassKey.ONBOARD_REF_PAST: ClassificationConfig(
                    ONBOARD_REF_PAST_CLASS,
                    lambda r: r.strip().lower().startswith("true"),
                    False,
                ),
            },
            respond_conf={
                TomRespKey.NO_DATA: ResponseConfig(TOM_NO_DATA_RESP),
                TomRespKey.NO_INTENT: ResponseConfig(TOM_NO_INTENT_RESP, "Estou aqui para emitir notas fiscais. Me envie os dados do tomador do serviço."),
                TomRespKey.INCOMPLETE: ResponseConfig(TOM_INCOMPLETE_RESP),
                TomRespKey.INVALID: ResponseConfig(TOM_INVALID_RESP),
                TomRespKey.ONBOARD_INFO: ResponseConfig(ONBOARD_INFO_RESP),
                TomRespKey.ONBOARD_HISTORY: ResponseConfig(ONBOARD_HISTORY_RESP),
            },
        )