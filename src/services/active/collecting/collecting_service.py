from dataclasses import asdict

from src.managers.conversations.conv_manager import ConvManager
from src.managers.msg_manager import MsgManager
from src.models.municipios import RJ_CODIGO_MUNICIPIO
from src.services.ai import ai_client_factory
from src.services.ai.ai_service import AIService
from src.services.iss.iss_resolution_service import IssResolutionService
from src.services.validators.validador_tomador import ValidadorTomador
from src.services.wpp.msg_service import WhatsAppService
from src.types import (
    BotaoResponse,
    ContextTomador,
    ConvStatus,
    IssResolutionError,
    Role,
    TomadorData,
    TomExtractKey,
    TomRespKey,
)
from src.utils.debug import print_table


def notf_user(msg: str) -> None:
    #self.wpp.send_msg_text(self.msg.phone, msg)
    print(f"{msg}\n")
    
class ExtractionService:
    def __init__(self, ctx: ContextTomador, conversation: ConvManager):
        self.ctx = ctx
        self.ai = AIService(ai_client_factory.build_ai_client())
        self.conversation = conversation

    def extract_e_merge(self):

        new_data = self.ai.tom.extract(TomExtractKey.NF, self.ctx.text)
        if new_data is not None:
            self.ctx.new_data = new_data
        print(f"DADOS NOVOS: {self.ctx.new_data}\n")

        draft = self.conversation.get_draft()
        if draft is not None:
            self.ctx.db_data = TomadorData.from_dict(draft)
        print(f"DADOS DRAFT:{self.ctx.db_data}\n")

        self.ctx.merged = self.ctx.db_data.merge(self.ctx.new_data)
        print(f"MERGE: {self.ctx.merged}\n")


class ValidationService:
    def __init__(self, ctx: ContextTomador, conversation: ConvManager):
        self.ctx = ctx
        self.conversation = conversation
        self.ai = AIService(ai_client_factory.build_ai_client())
        self.validador = ValidadorTomador()
        self.msg = MsgManager(ctx)
        self.wpp = WhatsAppService()
        self.iss_resolution = IssResolutionService(ai=self.ai)

    def valido_e_completo(self):

        self.validador.validar(self.ctx)

        if self.ctx.valid:
            self._update_draft()

            if not self.ctx.validation.is_complete:
                self._incompleto()
                return

            # TODO: TomadorManager ainda usa a constante ALIQUOTA_ISS fixa ao montar
            # o payload da NF-e — resolved.aliquota ainda não é propagado até lá.
            if not self._iss_ok():
                return

            self._update_draft()
            self._update_state()
            self._msg_confirm()
            return

        if self.ctx.validation.invalid:
            self._invalidos()
            return

        self._no_data()
        return

    def _iss_ok(self) -> bool:
        """Checkpoint pré-emissão: bloqueia a transição para CONFIRMING se a
        descrição não classificar em um código nacional conhecido, ou se o código
        classificado não tiver alíquota vigente na tabela local. Nunca deixa a nota
        avançar com uma alíquota chutada/zero — ver IssResolutionService."""

        descricao = self.ctx.merged.servico.descricao

        try:
            resolution = self.iss_resolution.resolve(descricao, RJ_CODIGO_MUNICIPIO) # type: ignore[arg-type]
        except IssResolutionError:
            self._iss_sem_aliquota()
            return False

        if resolution.unclassified:
            self._iss_nao_classificado()
            return False

        return True

    def _iss_sem_aliquota(self):
        response = (
            "Não encontrei a alíquota de ISS vigente para esse serviço no Rio de Janeiro. "
            "Nossa equipe precisa atualizar essa informação antes de emitir a nota — "
            "por favor tente novamente mais tarde."
        )
        self.msg.save_msg(Role.AI, response)
        notf_user(response)

    def _iss_nao_classificado(self):
        response = (
            "Não consegui identificar com segurança o tipo de serviço prestado a partir "
            "da descrição. Pode detalhar um pouco mais o que foi feito?"
        )
        self.msg.save_msg(Role.AI, response)
        notf_user(response)
    
    def _update_draft(self):
        draft_dict = asdict(self.ctx.valid)
        self.conversation.update_draft(draft_dict)
        print(f"VALIDACAO: {self.ctx.validation}\n")
    
    def _update_state(self):
        self.conversation.update_state(ConvStatus.CONFIRMING)

    def _msg_confirm(self):

        confirmar = BotaoResponse(id="tomador_confirmado", title="✅ Confirmar")
        corrigir = BotaoResponse(id="tomador_corrigir", title="✏️ Corrigir")

        msg_button = self.wpp.format_msg_botao(
            text=(f"*Dados do tomador:*\n\n"
            f"{self.ctx.merged.tomador.nome}\n"
            f"{self.ctx.merged.tomador.cnpj}\n"
            f"{self.ctx.merged.servico.descricao}\n"
            f"{self.ctx.merged.valores.total}\n"
            f"Esses dados estão corretos?"
            ),
            botoes=[confirmar, corrigir],
        )
        self.msg.save_msg(Role.AI, msg_button)

        # send_msg_botao(
        #     phone=self.ctx.user.phone,
        #     text=(
        #         f"*Dados do tomador:*\n\n"
        #         f"{self.ctx.merged.tomador.nome}\n"
        #         f"{self.ctx.merged.tomador.cnpj}\n"
        #         f"{self.ctx.merged.servico.descricao}\n"
        #         f"{self.ctx.merged.valores.total}\n"
        #         f"Esses dados estão corretos?"
        #     ),
        #     botoes=[confirmar, corrigir],
        # )
        

        print(
            f"*Dados do tomador:*\n\n"
            f"{self.ctx.merged.tomador.nome}\n"
            f"{self.ctx.merged.tomador.cnpj}\n"
            f"{self.ctx.merged.servico.descricao}\n"
            f"{self.ctx.merged.valores.total}\n"
            f"Esses dados estão corretos?"
        )
        print_table(table_name="conversations", where=self.ctx.user.phone)

    def _incompleto(self):
        valid_missing_list = self.ctx.validation.missing
        valid_missing_list.insert(0, self.ctx.valid.to_str())

        response = self.ai.tom.respond(TomRespKey.INCOMPLETE, self.ctx.text, valid_missing_list)
        self.msg.save_msg(Role.AI, response)
        notf_user(response)
    
    def _invalidos(self):
        response = self.ai.tom.respond(TomRespKey.INVALID, self.ctx.text, self.ctx.validation.invalid)
        self.msg.save_msg(Role.AI, response)
        notf_user(response)

    def _no_data(self):
        response = self.ai.tom.respond(TomRespKey.NO_DATA, self.ctx.text)
        self.msg.save_msg(Role.AI, response)
        notf_user(response)