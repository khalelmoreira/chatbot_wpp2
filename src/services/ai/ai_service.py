from src.integrations.ai_client import GemmaClient
from src.types import ContextTomador, DadosTomador, StatusResumo, IntentTipo
from src.utils.build_prompt import build_prompt
from chatbot_wpp2.src.services.ai.ai_extractors import (
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
)

class AIService:
    def __init__(self, ctx: ContextTomador):

        self.client = GemmaClient(model="google/gemma-4-e4b")
        self.extractor = AIExtractor
        self.ctx = ctx

    def extract_nfse_data(self) -> None:
        self.ctx.dados_novos = self.extractor(
            client=self.client,
            prompt=PROMPT_EXTRACT_NFSE_GEMMA,
            output_type=DadosTomador,
            parser=parse_tomador_data
        )

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
                system_prompt=str(PROMPT_NO_INTENT_RESPONSE),
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
                )
            )
            return response
        
        except Exception as e:
            print(f"Erro ao responder: {e}")
            return "Não pude entender sua mensagem, tente novamente em alguns minutos."
        
    def classificar_intent(self) -> IntentTipo:
        try:
            response = self.client.extract_text(
                system_prompt=PROMPT_CLASSIFICA_INTENT,
                user_msg=self.ctx.text
            )
            return IntentTipo(response.strip().upper())
        
        except (ValueError, Exception) as e:
            print(f"Erro ao classificar intencao: {e}")
            return IntentTipo.NENHUM
        
    def parece_pergunta(self) -> bool:
        try:
            response = self.client.extract_text(
                system_prompt=PROMPT_PARECE_PERGUNTA,
                user_msg=self.ctx.text
            )
            return response.strip().lower().startswith("true")
        
        except Exception as e:
            print(f"Erro ao classificar parece_pergunta: {e}")
            return False
        
    def _resumo_to_params(self, resumo: StatusResumo) -> dict:
        return [
            self.resumo.nf_status or "NENHUMA",
            self.resumo.erro_msg or "nenhum",
            self.resumo.created_at or "—",
            self.resumo.updated_at or "—",
            self.resumo.invoice_id or "—",
            self.resumo.draft or "_",
            self.resumo.requested_at or "_",
            self.resumo.cancelled_at or "_",
            self.resumo.emitido_em or "_",
            self.resumo.created_at or '—',
            self.resumo.erro_msg or 'erro desconhecido',
        ]