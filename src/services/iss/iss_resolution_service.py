from typing import cast

from src.managers.iss.iss_rate_manager import IssRateManager
from src.models.national_service_codes import UNCLASSIFIED
from src.services.ai import ai_client_factory
from src.services.ai.ai_service import AIService
from src.types import IssClassKey, IssRate, IssResolution, IssResolutionError


class IssResolutionService:
    """Classifica uma descrição livre em um código nacional e resolve a alíquota vigente
    para o município. Nunca deixa uma classificação sem confiança virar um código
    'chutado', e nunca deixa a ausência de alíquota vigente passar como zero/None
    silencioso — ver IssResolutionError.

    TODO: fora de escopo do MVP — não considera as tabelas municipais de retenção/
    benefício fiscal do ISS do RJ (endpoints /parametros_municipais/.../retencoes e
    /beneficiomunicipal na mesma API). A alíquota resolvida aqui é a alíquota base."""

    def __init__(self, ai: AIService | None = None, rates: IssRateManager | None = None):
        self.ai = ai or AIService(ai_client_factory.build_ai_client())
        self.rates = rates or IssRateManager()

    def resolve(self, descricao: str, codigo_municipio: str) -> IssResolution:
        codigo = cast(str, self.ai.iss.classify(IssClassKey.SERVICE_CODE, descricao))

        if codigo == UNCLASSIFIED:
            return IssResolution(unclassified=True)

        rate: IssRate | None = self.rates.get_current_rate(codigo_municipio, codigo)
        if rate is None:
            raise IssResolutionError(
                f"Sem alíquota vigente para codigo_tributacao_nacional={codigo} "
                f"codigo_municipio={codigo_municipio}."
            )

        return IssResolution(
            unclassified=False,
            codigo_tributacao_nacional=codigo,
            aliquota=rate.aliquota,
        )
