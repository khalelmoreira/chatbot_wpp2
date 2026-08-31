import logging
from dataclasses import asdict

from src.managers.conversations.conv_manager import ConvManager
from src.managers.msg_manager import MsgManager
from src.models.municipios import RJ_CODIGO_MUNICIPIO
from src.services.ai import ai_client_factory
from src.services.ai.ai_service import AIService
from src.services.iss.iss_resolution_service import IssResolutionService
from src.services.sender import get_sender
from src.services.validators.validador_tomador import ValidadorTomador
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
from src.utils.debug import log_table
from src.utils.get_cnpj import get_cnpj_info
from src.utils.nome_empresa import nome_confere_com_receita

logger = logging.getLogger(__name__)

class ExtractionService:
    def __init__(self, ctx: ContextTomador, conversation: ConvManager):
        self.ctx = ctx
        self.ai = AIService(ai_client_factory.build_ai_client())
        self.conversation = conversation

    def extract_e_merge(self):

        new_data = self.ai.tom.extract(TomExtractKey.NF, self.ctx.text)
        if new_data is not None:
            self.ctx.new_data = new_data

        draft = self.conversation.get_draft()
        if draft is not None:
            self.ctx.db_data = TomadorData.from_dict(draft)

        self.ctx.merged = self.ctx.db_data.merge(self.ctx.new_data)


class ValidationService:
    def __init__(self, ctx: ContextTomador, conversation: ConvManager):
        self.ctx = ctx
        self.conversation = conversation
        self.ai = AIService(ai_client_factory.build_ai_client())
        self.validador = ValidadorTomador()
        self.msg = MsgManager(ctx)
        self.wpp = get_sender(ctx.user.channel)
        self.iss_resolution = IssResolutionService(ai=self.ai)

    def _notf_user(self, msg: str) -> None:
        self.wpp.send_msg_text(self.ctx.user.phone, msg)

    def valido_e_completo(self):

        self.validador.validar(self.ctx)
        self._update_draft()

        # Um campo rejeitado (ex.: CNPJ com dígito verificador errado) não conta
        # como "faltante" — is_complete seria True e a nota avançava para
        # CONFIRMING com o campo em None. Barra aqui, antes de qualquer avanço.
        if self.ctx.validation.invalid:
            self._invalidos()
            return

        if self.ctx.valid == TomadorData():
            self._no_data()
            return

        if not self.ctx.validation.is_complete:
            self._incompleto()
            return

        if not self._iss_ok():
            return

        if not self._cnpj_ok():
            return

        self._update_draft()
        self._update_state()
        self._msg_confirm()

    def _iss_ok(self) -> bool:
        """Checkpoint pré-emissão: bloqueia a transição para CONFIRMING se a
        descrição não classificar em um código nacional conhecido, ou se o código
        classificado não tiver alíquota vigente na tabela local. Nunca deixa a nota
        avançar com uma alíquota chutada/zero — ver IssResolutionService.

        Em caso de sucesso, grava o cTribNac e a alíquota resolvidos em `ctx.valid`
        para o próximo _update_draft() persistir — daí seguem no draft_json até o
        TomadorManager e o payload da Notaas."""

        descricao = self.ctx.merged.servico.descricao

        try:
            resolution = self.iss_resolution.resolve(descricao, RJ_CODIGO_MUNICIPIO) # type: ignore[arg-type]
        except IssResolutionError:
            self._iss_sem_aliquota()
            return False

        if resolution.unclassified:
            self._iss_nao_classificado()
            return False

        self.ctx.valid.servico.codigo = resolution.codigo_tributacao_nacional
        self.ctx.valid.valores.aliquotaIss = resolution.aliquota
        return True

    def _iss_sem_aliquota(self):
        response = (
            "Não encontrei a alíquota de ISS vigente para esse serviço no Rio de Janeiro. "
            "Nossa equipe precisa atualizar essa informação antes de emitir a nota — "
            "por favor tente novamente mais tarde."
        )
        self.msg.save_msg(Role.AI, response)
        self._notf_user(response)

    def _iss_nao_classificado(self):
        response = (
            "Não consegui identificar com segurança o tipo de serviço prestado a partir "
            "da descrição. Pode detalhar um pouco mais o que foi feito?"
        )
        self.msg.save_msg(Role.AI, response)
        self._notf_user(response)
    
    def _cnpj_ok(self) -> bool:
        """Checkpoint pré-emissão: confirma o CNPJ do tomador na Receita Federal e
        checa se o nome informado bate com a razão social / nome fantasia de lá.

        Só roda depois de nome e CNPJ já validados (formato + dígito) e a nota
        completa — espelha o CnpjService do onboarding do prestador. Tomador por
        CPF (cnpj None) não passa por aqui: não há serviço público de CPF→nome."""

        cnpj = self.ctx.valid.tomador.cnpj
        if cnpj is None:
            return True

        info = get_cnpj_info(cnpj)
        if info is None:
            self._cnpj_nao_confirmado(cnpj)
            return False

        situacao = info.get("descricao_situacao_cadastral")
        if situacao and situacao.upper() != "ATIVA":
            self._cnpj_inativo(cnpj, situacao)
            return False

        nome = self.ctx.valid.tomador.nome
        if nome and not nome_confere_com_receita(nome, info):
            self._cnpj_nome_divergente(info)
            return False

        return True

    def _cnpj_nao_confirmado(self, cnpj: str):
        response = (
            f"Não consegui confirmar o CNPJ {cnpj} na Receita Federal. "
            "Pode conferir e enviar novamente?"
        )
        self.msg.save_msg(Role.AI, response)
        self._notf_user(response)

    def _cnpj_inativo(self, cnpj: str, situacao: str):
        response = (
            f"O CNPJ {cnpj} está com situação cadastral \"{situacao}\" na Receita Federal. "
            "Não é possível emitir uma nota para um CNPJ que não está ativo."
        )
        self.msg.save_msg(Role.AI, response)
        self._notf_user(response)

    def _cnpj_nome_divergente(self, info: dict):
        razao = info.get("razao_social") or info.get("nome_fantasia") or "outro"
        response = (
            "O nome informado não confere com o CNPJ na Receita Federal, que consta como "
            f"\"{razao}\". Pode enviar o nome correto do cliente (ou o CNPJ certo)?"
        )
        self.msg.save_msg(Role.AI, response)
        self._notf_user(response)

    def _update_draft(self):
        draft_dict = asdict(self.ctx.valid)
        self.conversation.update_draft(draft_dict)
        logger.debug("validacao=%s", self.ctx.validation)
    
    def _update_state(self):
        self.conversation.update_state(ConvStatus.CONFIRMING)

    def _msg_confirm(self):

        confirmar = BotaoResponse(id="tomador_confirmado", title="✅ Confirmar")
        corrigir = BotaoResponse(id="tomador_corrigir", title="✏️ Corrigir")
        cancelar = BotaoResponse(id="tomador_cancelar", title="❌ Cancelar")
        botoes = [confirmar, corrigir, cancelar]

        dados = self.ctx.valid
        valor = dados.valores.total or 0.0
        valor_fmt = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        aliquota_fmt = f"{dados.valores.aliquotaIss:g}%" if dados.valores.aliquotaIss is not None else "—"

        texto = (f"*Dados da nota:*\n\n"
            f"Nome: {dados.tomador.nome}\n"
            f"CNPJ: {dados.tomador.cnpj}\n"
            f"Serviço: {dados.servico.descricao}\n"
            f"Valor: R$ {valor_fmt}\n"
            f"Alíquota ISS: {aliquota_fmt}\n\n"
            f"Esses dados estão corretos?"
        )

        msg_button = self.wpp.format_msg_botao(text=texto, botoes=botoes)
        self.msg.save_msg(Role.AI, msg_button)

        self.wpp.send_msg_botao(
            phone=self.ctx.user.phone,
            text=texto,
            botoes=botoes,
        )
        log_table(table_name="conversations", where=self.ctx.user.phone)

    def _incompleto(self):
        faltantes = ", ".join(self.ctx.validation.missing)

        response = self.ai.tom.respond(TomRespKey.INCOMPLETE, self.ctx.text, [faltantes])
        self.msg.save_msg(Role.AI, response)
        self._notf_user(response)
    
    def _invalidos(self):
        response = self.ai.tom.respond(TomRespKey.INVALID, self.ctx.text, self.ctx.validation.invalid)
        self.msg.save_msg(Role.AI, response)
        self._notf_user(response)

    def _no_data(self):
        response = self.ai.tom.respond(TomRespKey.NO_DATA, self.ctx.text)
        self.msg.save_msg(Role.AI, response)
        self._notf_user(response)