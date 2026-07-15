from src.managers.prestador_manager import PrestadorManager
from src.services.wpp.msg_service import WhatsAppService
from src.services.validators.validador_prestador import ValidadorPrestador
from src.types import ContextPrestador, UserStatus, BotaoResponse, Role, PrestadorData, Address
from src.managers.prestador_manager import PrestadorManager
from src.services.ai.ai_service import AIService
from src.managers.msg_manager import MsgManager
from src.utils.debug import print_table
from src.utils.get_endereco import get_endereco_by_cep

def notf_user(msg: str) -> None:
    #self.wpp.send_msg_text(self.msg.phone, msg)
    print(f"{msg}\n")

class ExtractionService:
    def __init__(self, ctx: ContextPrestador):
        self.ctx = ctx
        self.ai = AIService()
        self.prestador = PrestadorManager(ctx)

    def extract_e_merge(self) -> None:
        self.ai.extract_prest_data(self.ctx)
        print(f"DADOS NOVOS: {self.ctx.new_data}\n")

        draft = self.prestador.get_db_data()
        self.ctx.db_data = PrestadorData.from_dict(draft)
        print(f"DADOS DARFT: {self.ctx.db_data}\n")

        self.ctx.merged = self.ctx.db_data.merge(self.ctx.new_data)
        print(f"MERGE: {self.ctx.merged}\n")

class ValidationService:
    def __init__(self, ctx: ContextPrestador, prestador: PrestadorManager):
        self.ctx = ctx
        self.prestador = prestador
        self.msg = MsgManager(ctx)
        self.ai = AIService()
        self.validador = ValidadorPrestador()
        
    def valido(self) -> bool:

        self.validador.validar(self.ctx)

        if self.ctx.validation.valid:
            self._update_draft()
            return True
        
        if self.ctx.validation.invalid:
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
        response = self.ai.no_data_prest_response(self.ctx)
        self.msg.save_msg(Role.AI, response)
        notf_user(response)

    def _incompleto(self):
        response = self.ai.incomplete_prest_response(self.ctx)
        self.msg.save_msg(Role.AI, response)
        notf_user(response)

    def _invalidos(self):
        response = self.ai.invalidos_prest_response(self.ctx)
        self.msg.save_msg(Role.AI, response)
        notf_user(response)

    def _update_draft(self):
        self.prestador.update_validos()

class AddressService:
    def __init__(self, ctx: ContextPrestador, prestador: PrestadorManager):
        self.ctx = ctx
        self.prestador = prestador

    def address(self):
        cep = self.ctx.validation.valid["cep"]
        print(f"CEP: {cep}\n")

        endereco = get_endereco_by_cep(cep)
        print(f"ENDERECO: {endereco}\n")
        
        if not endereco:
            notf_user(f"Não consegui encontrar o endereço para o CEP {self.ctx.validation.valid["cep"]}.\nPode verificar e enviar novamente?\n")
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
            f"CEP: {self.ctx.validation.valid["cep"]}\n\n"
            f"Esse é o endereço correto?\n"
        )
        print_table(table_name="users", where=self.ctx.user.phone)
        return