from src.types import ContextPrestador, PrestadorData, Role
from src.managers.prestador_manager import PrestadorManager
from src.services.ai.ai_service import AIService
from chatbot_wpp2.src.managers.msg_manager import MsgManager
from src.services.validators.validador_prestador import ValidadorPrestador
from src.utils.debug import print_table

def notf_user(msg: str) -> None:
    #self.wpp.send_msg_text(self.msg.phone, msg)
    print(f"{msg}\n")

class ExtractionService:
    def __init__(self, ctx: ContextPrestador, prestador: PrestadorManager):
        self.ctx = ctx
        self.prestador = prestador
        self.ai = AIService()

    def extract_e_merge(self):
        self.ai.extract_address(self.ctx)
        print(f"DADOS NOVOS: {self.ctx.new_data}\n")

        draft = self.prestador.get_all()
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
    
    def msg_confirm(self):
        self.ctx.validated = PrestadorData.from_dict(self.ctx.validation.valid)
        # wpp.send_msg_botao(
        #     phone=ctx.user.phone,
        #     text=(
        #         f"📍 *Endereço encontrado:*\n\n"
        #         f"{address.logradouro}\n"
        #         f"{address.bairro} — {address.cidade}/{address.uf}\n"
        #         f"CEP: {address.cep}\n\n"
        #         f"Esse é o endereço correto?"
        #     ),
        #     botoes=[
        #         BotaoResponse(id=,"prestador_confirmado", title="✅ Confirmar"),
        #         BotaoResponse(id="prestador_corrigir", title="✏️ Corrigir"),
        #     ],
        # )

        print(
            f"Seus dados:*\n\n"
            f"Razão Social: {self.ctx.validated.razao_social}\n"
            f"CNPJ: {self.ctx.validated.cnpj}\n"
            f"Email: {self.ctx.validated.email}\n"
            f"Regime Tributário: {self.ctx.validated.regime_tributario}\n"
            f"Endereco: {self.ctx.validated.address.logradouro} — {self.ctx.validated.address.bairro} — {self.ctx.validated.address.cidade}/{self.ctx.validated.address.uf}\n"
            f"CEP: {self.ctx.validated.cep}\n\n"
            f"Esses dados estão corretos?\n"
        )
        print_table(table_name="users", where=self.ctx.user.phone)
        return
    
    def _no_data(self):
        response = self.ai.no_data_prest_response(self.ctx)
        self.msg.save_msg(Role.AI, response)
        notf_user(response)
    
    def _incompleto(self):
        response = self.ai.incomplete_prest_response(self.ctx)
        self.msg.save_msg(Role.AI, response)
        notf_user(response)
    
    def _invalidos(self):
        response = self.ai.invalidos_prest_response()
        self.msg.save_msg(Role.AI, response)
        notf_user(response)
    
    def _update_draft(self):
        self.prestador.update_validos()