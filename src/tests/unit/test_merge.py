from src.types import Address, PrestadorData


def test_merge_novo_sobrescreve_quando_presente():
    atual = PrestadorData(razao_social="Antiga LTDA", cnpj="11222333000181", email=None)
    novo = PrestadorData(razao_social="Nova LTDA", cnpj=None, email="a@a.com")

    resultado = atual.merge(novo)

    assert resultado.razao_social == "Nova LTDA"
    assert resultado.cnpj == "11222333000181"
    assert resultado.email == "a@a.com"


def test_merge_mantem_atual_quando_novo_e_none():
    atual = PrestadorData(cep="01310100")
    novo = PrestadorData(cep=None)

    resultado = atual.merge(novo)

    assert resultado.cep == "01310100"


def test_merge_recursivo_em_address():
    atual = PrestadorData(address=Address(logradouro="Rua A", numero="10"))
    novo = PrestadorData(address=Address(logradouro="Rua B", numero=None))

    resultado = atual.merge(novo)

    assert resultado.address.logradouro == "Rua B"
    assert resultado.address.numero == "10"
