from src.managers.msg_manager import MsgManager
from src.managers.user_manager import PrestadorManager
from src.services.ai import ai_client_factory
from src.services.ai.ai_service import AIService
from src.services.validators.validador_prestador import ValidatorAddress
from src.types import Address, ContextPrestador, PrestExtractKey, PrestRespKey, Role
from src.utils.debug import print_table


def notf_user(msg: str) -> None:
    #self.wpp.send_msg_text(self.msg.phone, msg)
    print(f"{msg}\n")

class ExtractionService:
    def __init__(self, ctx: ContextPrestador, prestador: PrestadorManager):
        self.ctx = ctx
        self.prestador = prestador
        self.ai = AIService(ai_client_factory.build_ai_client())

    def extract_e_merge(self):
        new_data = self.ai.prest.extract(PrestExtractKey.ADDRESS, self.ctx.text)

        if new_data is not None:
            self.ctx.new_data = new_data                       #type: ignore
        print(f"DADOS NOVOS: {self.ctx.new_data}\n")

        draft = self.prestador.get_address()
        print(f"DARFT: {self.ctx.db_data}\n")

        if draft is not None:
            self.ctx.db_data = draft
        print(f"DADOS DARFT: {self.ctx.db_data}\n")

        self.ctx.merged = self.ctx.db_data.merge(self.ctx.new_data)
        print(f"MERGE: {self.ctx.merged}\n")

class ValidationService:
    def __init__(self, ctx: ContextPrestador, prestador: PrestadorManager):
        self.ctx = ctx
        self.prestador = prestador
        self.msg = MsgManager(ctx)
        self.ai = AIService(ai_client_factory.build_ai_client())
        self.validador = ValidatorAddress()
        
    def valido(self) -> bool:

        result = self.validador.validar(self.ctx.merged)
        self.ctx.valid = result.valid
        self.ctx.validation = result.result
        print(f"VALIDATION: {self.ctx.validation}\n")

        if not self.ctx.validation.is_valid:
            if self.ctx.valid != Address():
                self._update_draft()
            self._invalidos()
            return False

        if self.ctx.valid != Address():
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
        self.prestador.update_address()
    
    def msg_confirm(self):
        logradouro = self.ctx.valid.logradouro
        bairro = self.ctx.valid.bairro
        cidade = self.ctx.valid.cidade
        uf = self.ctx.valid.uf

        db_data = self.prestador.get_db_data()
        cep = db_data.cep if db_data is not None else None

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
            f"Seu Endereço:*\n\n"
            f"Logradouro: {logradouro}\n"
            f"bairro: {bairro}\n"
            f"cidade: {cidade}\n"
            f"uf: {uf}\n"
            f"CEP: {cep}\n\n"
            f"Esses dados estão corretos?\n"
        )
        print("DADOS SALVOS NO DB:")
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