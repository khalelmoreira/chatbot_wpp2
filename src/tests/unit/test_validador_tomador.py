from src.services.validators.validador_tomador import ValidadorTomador
from src.types import ContextTomador, MsgType, TomadorData, User, UserStatus
from src.types.tomador import Servico, Tomador, Valores

CNPJ_VALIDO = "11222333000181"
CNPJ_INVALIDO = "11111111111111"  # dígitos verificadores errados, mesmo formato válido


def _ctx(cnpj: str | None) -> ContextTomador:
    merged = TomadorData(
        tomador=Tomador(nome="ABBa LTDA", cnpj=cnpj),
        servico=Servico(descricao="marcenaria"),
        valores=Valores(total=1500.0),
    )
    return ContextTomador(
        user=User(id=1, phone="5521991112222", status=UserStatus.ACTIVE),
        text="", new_data=TomadorData(), db_data=TomadorData(),
        merged=merged, valid=TomadorData(), msg_type=MsgType.TEXT,
    )


def test_cnpj_com_digito_verificador_invalido_e_marcado_invalido():
    ctx = _ctx(CNPJ_INVALIDO)

    ValidadorTomador().validar(ctx)

    assert "tomador.cnpj" in ctx.validation.invalid
    assert ctx.valid.tomador.cnpj is None


def test_cnpj_valido_e_aceito():
    ctx = _ctx(CNPJ_VALIDO)

    ValidadorTomador().validar(ctx)

    assert "tomador.cnpj" not in ctx.validation.invalid
    assert ctx.valid.tomador.cnpj == CNPJ_VALIDO
