from src.services.validators.validador_prestador import ValidatorPrestador
from src.types import PrestadorData

CNPJ_VALIDO = "11222333000181"


def test_dados_completos_e_validos():
    data = PrestadorData(
        razao_social="Empresa LTDA", cnpj=CNPJ_VALIDO, email="a@a.com",
        regime_tributario="1", cep="01310100",
    )

    output = ValidatorPrestador.validar(data)

    assert output.result.is_valid
    assert output.result.is_complete


def test_dados_incompletos_reportam_campos_faltantes():
    data = PrestadorData(razao_social="Empresa LTDA")

    output = ValidatorPrestador.validar(data)

    assert not output.result.is_complete
    assert "cnpj" in output.result.missing
    assert "email" in output.result.missing


def test_regime_tributario_invalido():
    data = PrestadorData(
        razao_social="Empresa LTDA", cnpj=CNPJ_VALIDO, email="a@a.com",
        regime_tributario="9", cep="01310100",
    )

    output = ValidatorPrestador.validar(data)

    assert not output.result.is_valid
    assert "regime_tributario" in output.result.invalid
