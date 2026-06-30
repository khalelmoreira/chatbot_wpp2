from src.integrations.ai_client import GemmaClient
from src.types import ContextTomador, DadosTomador, StatusResumo, IntentTipo, HistoryResumo
from src.utils.build_prompt import build_prompt
from src.services.ai.ai_extractors import (
    AIExtractor,
    parse_tomador_data,
)
from src.models.prompts import (
    PROMPT_EXTRACT_NFSE_GEMMA,
    PROMPT_HAS_INTENT,
    PROMPT_NO_INTENT_RESPONSE,
    PROMPT_CONSULTA,
    PROMPT_CLASSIFICA_INTENT,
    PROMPT_PARECE_PERGUNTA,
    PROMPT_REF_PAST,
)

class AIService:
    def __init__(self, ctx: ContextTomador):

        self.client = GemmaClient(model="google/gemma-4-e4b")
        self.extractor = AIExtractor
        self.ctx = ctx

    def extract_nfse_data(self) -> None:
        extractor = self.extractor(
            client=self.client,
            prompt=PROMPT_EXTRACT_NFSE_GEMMA,
            output_type=DadosTomador,
            parser=parse_tomador_data
        )
        self.ctx.dados_novos = extractor.extract(self.ctx.text)

    def has_intent(self) -> bool:

        try:
            response = self.client.extract_text(
                system_prompt=str(PROMPT_HAS_INTENT),
                user_msg=self.ctx.text
            )
            return response.lower().startswith("true")
        
        except Exception as e:
            print(f"Erro ao responder: {e}")
            return False
        
    def no_intent_response(self) -> str:

        print(f"NO INTENT RESPONSE\n")

        try:
            return self.client.extract_text(
                system_prompt=str(PROMPT_NO_INTENT_RESPONSE.system),
                user_msg=self.ctx.text
            )
        except Exception as e:
            print(f"Erro ao responder: {e}")
            return "Estou aqui para emitir notas fiscais. Me envie os dados do tomador do serviço."
        
class AIAssitant(AIService):
    def __init__(self, ctx: ContextTomador):
        super().__init__(ctx)
        
    def status_response(self, resumo: StatusResumo):
        try:
            response = self.client.extract_text(
                system_prompt=build_prompt(
                    template=PROMPT_CONSULTA.system,
                    params=self._resumo_to_params(resumo)
                ),
                user_msg=self.ctx.text
            )
            return response
        
        except Exception as e:
            print(f"Erro ao responder: {e}")
            return "Não pude entender sua mensagem, tente novamente em alguns minutos."
        
    def classificar_intent(self) -> IntentTipo:
        try:
            response = self.client.extract_text(
                system_prompt=PROMPT_CLASSIFICA_INTENT.system,
                user_msg=self.ctx.text
            )
            return IntentTipo(response.strip().upper())
        
        except (ValueError, Exception) as e:
            print(f"Erro ao classificar intencao: {e}")
            return IntentTipo.NENHUM
        
    def parece_pergunta(self) -> bool:
        try:
            response = self.client.extract_text(
                system_prompt=PROMPT_PARECE_PERGUNTA.system,
                user_msg=self.ctx.text
            )
            return response.strip().lower().startswith("true")
        
        except Exception as e:
            print(f"Erro ao classificar parece_pergunta: {e}")
            return False
        
    def ref_past(self) -> bool:
        try:
            response = self.client.extract_text(
                system_prompt=PROMPT_REF_PAST.system,
                user_msg=self.ctx.text
            )
            return response.strip().lower().startswith("true")
        
        except Exception as e:
            print(f"Erro ao identificar referencia_passado: {e}")
            return False
        
    def history_response(self, resumo: HistoryResumo):
        try:
            response = self.client.extract_text(
                system_prompt=
            )
        
    def _resumo_to_params(self, resumo: StatusResumo) -> dict:
        return [
            resumo.nf_status or "NENHUMA",
            resumo.erro_msg or "nenhum",
            resumo.created_at or "—",
            resumo.updated_at or "—",
            resumo.invoice_id or "—",
            resumo.draft or "_",
            resumo.requested_at or "_",
            resumo.cancelled_at or "_",
            resumo.emitido_em or "_",
        ]