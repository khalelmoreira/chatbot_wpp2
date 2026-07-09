from src.types import ContextPrestador, DadosPrestador, Role
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
        print(f"DADOS NOVOS: {self.ctx.dados_novos}\n")

        draft = self.prestador.get_all()
        self.ctx.dados_db = DadosPrestador.from_dict(draft)
        print(f"DADOS DARFT: {self.ctx.dados_db}\n")

        self.ctx.dados_completos = self.ctx.dados_db.merge(self.ctx.dados_novos)
        print(f"MERGE: {self.ctx.dados_completos}\n")

class ValidationService:
    def __init__(self, ctx: ContextPrestador, prestador: PrestadorManager):
        self.ctx = ctx
        self.prestador = prestador
        self.msg = MsgManager(ctx)
        self.ai = AIService()
        self.validador = ValidadorPrestador()
        
    def valido(self) -> bool:

        self.validador.validar(self.ctx)

        if self.ctx.validacao.validos:
            self._update_draft()
            return True
        
        if self.ctx.validacao.invalidos:
            self._invalidos()
            return False
        
        self._no_data()
        return False
    
    def completo(self) -> bool:
        if not self.ctx.validacao.is_complete:
            self._incompleto()
            return False
        return True
    
    def msg_confirm(self):
        self.ctx.dados_validados = DadosPrestador.from_dict(self.ctx.validacao.validos)
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
            f"Seus dados:*\n\n"
            f"Razão Social: {self.ctx.dados_validados.razao_social}\n"
            f"CNPJ: {self.ctx.dados_validados.cnpj}\n"
            f"Email: {self.ctx.dados_validados.email}\n"
            f"Regime Tributário: {self.ctx.dados_validados.regime_tributario}\n"
            f"Endereco: {self.ctx.dados_validados.endereco.logradouro} — {self.ctx.dados_validados.endereco.bairro} — {self.ctx.dados_validados.endereco.cidade}/{self.ctx.dados_validados.endereco.uf}\n"
            f"CEP: {self.ctx.dados_validados.cep}\n\n"
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