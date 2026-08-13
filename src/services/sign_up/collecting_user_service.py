from src.services.ai import ai_client_factory
from src.managers.user_manager import PrestadorManager
from src.services.wpp.msg_service import WhatsAppService
from src.services.validators.validador_prestador import ValidatorPrestador, extrair_digitos
from src.types import ContextPrestador, UserStatus, Role, PrestadorData, Address, PrestExtractKey, PrestRespKey
from src.services.ai.ai_service import AIService
from src.managers.msg_manager import MsgManager
from src.utils.get_endereco import get_endereco_by_cep
from src.utils.get_cnpj import get_cnpj_info

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
        print(f"DADOS NOVOS: {self.ctx.new_data}\n")

        draft = self.prestador.get_db_data()
        print(f"DRAFT: {draft}\n")

        if draft is not None: 
            self.ctx.db_data = PrestadorData.from_prestador(draft)
        print(f"DADOS DARFT: {self.ctx.db_data}\n")

        self.ctx.merged = self.ctx.db_data.merge(self.ctx.new_data)
        print(f"MERGE: {self.ctx.merged}\n")

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
        print(f"VALIDATION: {self.ctx.validation}\n")

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
        print(f"CEP: {cep}\n")

        if cep is None:
            return

        endereco = get_endereco_by_cep(cep)
        print(f"ENDERECO: {endereco}\n")

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
        print(f"CNPJ: {cnpj}\n")

        if cnpj is None:
            return True

        info = get_cnpj_info(cnpj)
        print(f"CNPJ INFO: {info}\n")

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

