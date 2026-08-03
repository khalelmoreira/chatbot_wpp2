from src.services.ai.ai_client import GemmaClient
from src.managers.user_manager import PrestadorManager
from src.services.wpp.msg_service import WhatsAppService
from src.services.validators.validador_prestador import ValidatorPrestador
from src.types import ContextPrestador, UserStatus, BotaoResponse, Role, PrestadorData, Address, PrestExtractKey, PrestRespKey
from src.services.ai.ai_service import AIService
from src.managers.msg_manager import MsgManager
from src.utils.debug import print_table
from src.utils.get_endereco import get_endereco_by_cep

def notf_user(msg: str) -> None:
    #self.wpp.send_msg_text(self.msg.phone, msg)
    print(f"{msg}\n")

class ExtractionService:
    def __init__(self, ctx: ContextPrestador, prestador: PrestadorManager):
        self.ctx = ctx
        self.prestador = prestador
        self.ai = AIService(GemmaClient())

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
        self.ai = AIService(GemmaClient())
        self.validador = ValidatorPrestador()
        
    def valido(self) -> bool:

        result = self.validador.validar(self.ctx.merged)
        self.ctx.valid = result.valid
        self.ctx.validation = result.result
        print(f"VALIDATION: {self.ctx.validation}\n")

        if self.ctx.valid != PrestadorData():
            self._update_draft()
            return True
        
        if not self.ctx.validation.is_valid:
            self._invalidos()
            return False
        
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

        self.prestador.update_state(UserStatus.CONFIRMING)
        self._msg_confirm(endereco)

    def _msg_confirm(self, endereco: Address):

        # wpp.send_msg_botao(
        #     phone=ctx.user.phone,
        #     text=(
        #         f"📍 *Endereço encontrado:*\n\n"
        #         f"{endereco.logradouro}\n"
        #         f"{endereco.bairro} — {endereco.cidade}/{endereco.uf}\n"
        #         f"CEP: {endereco.cep}\n\n"
        #         f"Esse é o endereço correto?"
        #     ),
        #     botoes=[
        #         BotaoResponse(id=,"prestador_confirmado", title="✅ Confirmar"),
        #         BotaoResponse(id="prestador_corrigir", title="✏️ Corrigir"),
        #     ],
        # )

        print(
            f"📍 *Endereço encontrado:*\n\n"
            f"{endereco.logradouro}\n"
            f"{endereco.bairro} — {endereco.cidade}/{endereco.uf}\n"
            f"CEP: {self.ctx.valid.cep}\n\n"
            f"Esse é o endereço correto?\n"
        )
        print(f"DADOS SALVOS NO DB:")
        print_table(
            table_name="prestador",
            columns=[
                "status",
                "email",
                "cnpj",
                "razao_social",
                "regime_tributario",
                "cep",
                "address_logradouro",
                "address_numero",
                "address_complemento",
                "address_bairro",
                "address_cidade",
                "address_uf",
            ],
            where=self.ctx.user.phone,
        )
        return