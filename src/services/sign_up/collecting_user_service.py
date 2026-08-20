import logging

from src.managers.msg_manager import MsgManager
from src.managers.user_manager import PrestadorManager
from src.services.ai import ai_client_factory
from src.services.ai.ai_service import AIService
from src.services.validators.validador_prestador import ValidatorPrestador, extrair_digitos
from src.types import (
    Address,
    ContextPrestador,
    PrestadorData,
    PrestExtractKey,
    PrestRespKey,
    Role,
    UserStatus,
)
from src.utils.get_cnpj import get_cnpj_info
from src.utils.get_endereco import get_endereco_by_cep

logger = logging.getLogger(__name__)

def notf_user(msg: str) -> None:
    #self.wpp.send_msg_text(self.msg.phone, msg)
    print(f"{msg}\n")

class ExtractionService:
    def __init__(self, ctx: ContextPrestador, prestador: PrestadorManager):
        self.ctx = ctx
        self.prestador = prestador
        self.ai = AIService(ai_client_factory.build_ai_client())

    def extract_e_merge(self) -> None:
        new_data = self.ai.prest.extract(PrestExtractKey.DATA, self.ctx.text)

        if new_data is not None:
            self.ctx.new_data = new_data                                 #type: ignore
        logger.debug("dados novos=%s", self.ctx.new_data)

        draft = self.prestador.get_db_data()
        logger.debug("draft=%s", draft)

        if draft is not None:
            self.ctx.db_data = PrestadorData.from_prestador(draft)
        logger.debug("dados draft=%s", self.ctx.db_data)

        self.ctx.merged = self.ctx.db_data.merge(self.ctx.new_data)
        logger.debug("merge=%s", self.ctx.merged)

class ValidationService:
    def __init__(self, ctx: ContextPrestador, prestador: PrestadorManager):
        self.ctx = ctx
        self.prestador = prestador
        self.msg = MsgManager(ctx)
        self.ai = AIService(ai_client_factory.build_ai_client())
        self.validador = ValidatorPrestador()
        
    def valido(self) -> bool:

        result = self.validador.validar(self.ctx.merged)
        self.ctx.valid = result.valid
        self.ctx.validation = result.result
        logger.debug("validation=%s", self.ctx.validation)

        if not self.ctx.validation.is_valid:
            if self.ctx.valid != PrestadorData():
                self._update_draft()
            self._invalidos()
            return False

        if self.ctx.valid != PrestadorData():
            self._update_draft()
            return True

        self._no_data()
        return False
    
    def completo(self) -> bool:
        if not self.ctx.validation.is_complete:
            self._incompleto()
            return False
        return True
    
    def _no_data(self):
        response = self.ai.prest.respond(PrestRespKey.NO_DATA, self.ctx.text)
        self.msg.save_msg(Role.AI, response)
        notf_user(response)

    def _incompleto(self):
        valid_missing_list = self.ctx.validation.missing
        valid_missing_list.insert(0, self.ctx.valid.to_str())

        response = self.ai.prest.respond(PrestRespKey.INCOMPLETE, self.ctx.text, valid_missing_list)
        self.msg.save_msg(Role.AI, response)
        notf_user(response)

    def _invalidos(self):
        response = self.ai.prest.respond(PrestRespKey.INVALID, self.ctx.text, self.ctx.validation.invalid)
        self.msg.save_msg(Role.AI, response)
        notf_user(response)

    def _update_draft(self):
        self.prestador.update_valid()

class AddressService:
    def __init__(self, ctx: ContextPrestador, prestador: PrestadorManager):
        self.ctx = ctx
        self.prestador = prestador

    def address(self):
        cep = self.ctx.valid.cep
        logger.debug("cep=%s", cep)

        if cep is None:
            return

        endereco = get_endereco_by_cep(cep)
        logger.debug("endereco=%s", endereco)

        if not endereco:
            notf_user(f"Não consegui encontrar o endereço para o CEP {cep}.\nPode verificar e enviar novamente?\n")
            self.prestador.update_state(UserStatus.ADDRESS)
            return

        self.prestador.update_state(UserStatus.ADDRESS)
        self.ctx.valid = endereco
        self.prestador.update_address()
        self._msg_falta_numero(endereco)

    def _msg_falta_numero(self, endereco: Address):
        notf_user(
            f"📍 Encontrei seu endereço:\n\n"
            f"{endereco.logradouro}\n"
            f"{endereco.bairro} — {endereco.cidade}/{endereco.uf}\n\n"
            f"Falta o número (e complemento, se houver). Pode enviar?\n"
        )

class CnpjService:
    def __init__(self, ctx: ContextPrestador, prestador: PrestadorManager):
        self.ctx = ctx
        self.prestador = prestador

    def verificar(self) -> bool:
        cnpj = extrair_digitos(self.ctx.valid.cnpj)
        logger.debug("cnpj=%s", cnpj)

        if cnpj is None:
            return True

        info = get_cnpj_info(cnpj)
        logger.debug("cnpj info=%s", info)

        if info is None:
            notf_user(
                f"Não consegui confirmar o CNPJ {cnpj} na Receita Federal.\n"
                f"Pode conferir e enviar novamente?\n"
            )
            return False

        situacao = info.get("descricao_situacao_cadastral")
        if situacao and situacao.upper() != "ATIVA":
            notf_user(
                f"O CNPJ {cnpj} está com situação cadastral \"{situacao}\" na Receita Federal.\n"
                f"Não é possível emitir notas fiscais para um CNPJ que não está ativo.\n"
            )
            return False

        return True

