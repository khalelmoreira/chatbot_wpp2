import json
import logging
from src.integrations.ai_client import GemmaClient
from src.types import (
    ContextTomador,
    ContextPrestador,
    DadosTomador,
    DadosPrestador,
    StatusResumo,
    IntentTipo,
    HistoryResumo,
    MsgResumo,
    IntentUserType,
)
from src.utils.build_prompt import build_list_prompt
from src.services.ai.ai_extractors import (
    AIExtractor,
    parse_tomador_data,
    parse_prestador_data,
)
from src.models.prompts import (
    PROMPT_EXTRACT_NFSE_GEMMA,
    PROMPT_HAS_INTENT,
    PROMPT_NO_INTENT_RESPONSE,
    PROMPT_CONSULTA,
    PROMPT_CLASSIFICA_INTENT,
    PROMPT_PARECE_PERGUNTA,
    PROMPT_REF_PAST,
    PROMPT_HISTORY_RESPONSE,
    PROMPT_INCOMPLETE_RESPONSE,
    PROMPT_INVALIDOS_RESPONSE,
    PROMPT_NO_DATA_RESPONSE,
    PROMPT_EXTRACT_PREST_DATA,
    PROMPT_INCOMPLETE_PREST_DATA_RESPONSE,
    PROMPT_INVALIDOS_PREST_RESPONSE,
    PROMPT_NO_DATA_PREST_RESPONSE,
    PROMTP_EXTRACT_ADDRESS,
    PROMPT_CLASSIFICA_INTENT_PREST,
    PROMPT_GENERAL_ASK,
    PROMPT_NO_INTENT_PREST,
)

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.client = GemmaClient(model="google/gemma-4-e4b")
        self.extractor = AIExtractor

    def extract_nfse_data(self, ctx: ContextTomador) -> None:
        extractor = self.extractor(
            client=self.client,
            prompt=PROMPT_EXTRACT_NFSE_GEMMA.system,
            output_type=DadosTomador,
            parser=parse_tomador_data
        )
        ctx.dados_novos = extractor.extract(ctx.text)

    def extract_prest_data(self, ctx: ContextPrestador):
        extractor = self.extractor(
            client=self.client,
            prompt=PROMPT_EXTRACT_PREST_DATA.system,
            output_type=DadosPrestador,
            parser=parse_prestador_data
        )
        ctx.dados_novos = extractor.extract(ctx.text)

    def extract_address(self, ctx: ContextPrestador) -> str:
        extractor = self.extractor(
            client=self.client,
            prompt=PROMTP_EXTRACT_ADDRESS.system,
            output_type=DadosPrestador,
            parser=parse_prestador_data
        )
        ctx.dados_novos = extractor.extract(ctx.text)

    def has_intent(self, ctx: ContextTomador) -> bool:

        try:
            response = self.client.extract_text(
                system_prompt=PROMPT_HAS_INTENT.system,
                user_msg=ctx.text
            )
            return response.lower().startswith("true")
        
        except Exception as e:
            print(f"Erro ao responder: {e}")
            return False
        
    def no_intent_response(self, ctx: ContextTomador) -> str:

        try:
            return self.client.extract_text(
                system_prompt=PROMPT_NO_INTENT_RESPONSE.system,
                user_msg=ctx.text
            )
        except Exception as e:
            print(f"Erro ao responder: {e}")
            return "Estou aqui para emitir notas fiscais. Me envie os dados do tomador do serviço."
        
    def no_intent_prest(self, ctx: ContextPrestador) -> str:
        try:
            return self.client.extract_text(
                system_prompt=PROMPT_NO_INTENT_PREST.system,
                user_msg=ctx.text
            )
        except Exception as e:
            print(f"Erro ao responder: {e}")
            return "Não pude entender sua mensagem, tente novamente em alguns minutos."
        
    def general_ask(self, ctx: ContextPrestador) -> str:
        try:
            return self.client.extract_text(
                system_prompt=PROMPT_GENERAL_ASK.system,
                user_msg=ctx.text
            )
        except Exception as e:
            print(f"Erro ao responder: {e}")
            return "Não pude entender sua mensagem, tente novamente em alguns minutos."
        
    def incomplete_response(self, ctx: ContextTomador) -> str:
        try:
            prompt = build_list_prompt(PROMPT_INCOMPLETE_RESPONSE.system, [ctx.validacao.validos, ctx.validacao.faltantes])
            return self.client.extract_text(
                system_prompt=prompt,
                user_msg=ctx.text
            )
        except Exception as e:
            print(f"Erro ao responder: {e}")
            return "Não pude entender sua mensagem, tente novamente em alguns minutos."
        
    def incomplete_prest_response(self, ctx: ContextPrestador) -> str:
        try:
            prompt = build_list_prompt(PROMPT_INCOMPLETE_PREST_DATA_RESPONSE.system, [ctx.validacao.validos, ctx.validacao.faltantes])
            return self.client.extract_text(
                system_prompt=prompt,
                user_msg=ctx.text
            )
        except Exception as e:
            print(f"Erro ao responder: {e}")
            return "Não pude entender sua mensagem, tente novamente em alguns minutos."
        
    def invalidos_response(self, ctx: ContextTomador) -> str:
        try:
            prompt = build_list_prompt(PROMPT_INVALIDOS_RESPONSE.system, (ctx.validacao.invalidos,))
            return self.client.extract_text(
                system_prompt=prompt,
                user_msg=ctx.text
            )
        except Exception as e:
            print(f"Erro ao responder: {e}")
            return "Não pude entender sua mensagem, tente novamente em alguns minutos."
        
    def invalidos_prest_response(self, ctx: ContextPrestador) -> str:
        try:
            prompt = build_list_prompt(PROMPT_INVALIDOS_PREST_RESPONSE.system, (ctx.validacao.invalidos,))
            return self.client.extract_text(
                system_prompt=prompt,
                user_msg=ctx.text
            )
        except Exception as e:
            print(f"Erro ao responder: {e}")
            return "Não pude entender sua mensagem, tente novamente em alguns minutos."
        
    def no_data_response(self, ctx: ContextTomador) -> str:
        try:
            return self.client.extract_text(
                system_prompt=PROMPT_NO_DATA_RESPONSE.system,
                user_msg=ctx.text
            )
        except Exception as e:
            print(f"Erro ao responder: {e}")
            return "Não pude entender sua mensagem, tente novamente em alguns minutos."
        
    def no_data_prest_response(self, ctx: ContextPrestador) -> str:
        try:
            return self.client.extract_text(
                system_prompt=PROMPT_NO_DATA_PREST_RESPONSE.system,
                user_msg=ctx.text
            )
        except Exception as e:
            print(f"Erro ao responder: {e}")
            return "Não pude entender sua mensagem, tente novamente em alguns minutos."

    def status_response(self, resumo: StatusResumo):
        try:
            response = self.client.extract_text(
                system_prompt=build_list_prompt(
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
        
    def classificar_intent_user(self, ctx: ContextPrestador) -> IntentUserType:
        try:
            response = self.client.extract_text(
                system_prompt=PROMPT_CLASSIFICA_INTENT_PREST.system,
                user_msg=ctx.text
            )
            return IntentUserType(response.strip().upper())
        
        except (ValueError, Exception) as e:
            print(f"Erro ao classificar intencao: {e}")
            return IntentUserType.NENHUM
        
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
        
    def history_response(self, nf_resumo: list[HistoryResumo] | None, msg_resumo: list[MsgResumo] | None):

        print(f"ENTROU EM HISTORY_RESPONSE\n")
        try:
            nf_history_str = self._nf_history_to_str(nf_resumo)
            msg_history_str = self._msg_history_to_str(msg_resumo)
            
            prompt = build_list_prompt(PROMPT_HISTORY_RESPONSE.system, [nf_history_str, msg_history_str])
            print(f"NF_HISTORY_STR: \n{nf_history_str}\n")
            print(f"MSG_HISTORY_STR: \n{msg_history_str}\n")

            response = self.client.extract_text(
                system_prompt=prompt,
                user_msg=self.ctx.text
                )
            return response
        
        except Exception as e:
            logger.warning(f"Erro ao responder: {e}")
            return "Não pude entender sua mensagem, tente novamente em alguns minutos."

    def _nf_history_to_str(self, nfs: list[HistoryResumo]) -> str:
        rows = []
        for i, nf in enumerate(nfs, 1):
            row = (
                f"{i}. Id: {nf.id} | "
                f"Status: {nf.status} | "
                f"Tentativas: {nf.tentativas} | "
                f"Nome tomador: {nf.nome} | "
                f"Cnpj tomador: {nf.cnpj} | "
                f"Descricao do serviço: {nf.descricao_servico} | "
                f"Valor total: {nf.valor_total} | "
                f"Invoice_id: {nf.invoice_id or 'não informado'} | "
                f"Criada em: {nf.created_at} | "
                f"Emitida em: {nf.emitido_em or 'não informado'} | "
                f"Codigo de erro: {nf.erro_code or 'não informado'} | "
                f"Mensagem de erro: {nf.erro_msg or 'não informado'} | "
                f"Cancelado em: {nf.cancelled_at or 'não informado'}"
            )
            rows.append(row)
        return "\n".join(rows)
        
    def _msg_history_to_str(self, msgs: list[MsgResumo]) -> str:
        rows = []
        for i, msg in enumerate(msgs, 1):
            row = (
                f"{i}. Role: {msg.role} | "
                f"Content: {msg.content} | "
            )
            rows.append(row)
        return "\n".join(rows)
        
    def _resumo_to_params(self, resumo: StatusResumo) -> list:
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