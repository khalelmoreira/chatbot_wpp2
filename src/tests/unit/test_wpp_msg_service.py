import pytest

from src.services.wpp import msg_service as msg_service_module
from src.services.wpp.msg_service import WhatsAppService
from src.types import Address, BotaoResponse


class FakeResponse:
    def __init__(self, status_code: int, json_data: dict | None = None, text: str = ""):
        self.status_code = status_code
        self._json = json_data or {}
        self.text = text

    def json(self) -> dict:
        return self._json


def test_format_msg_botao_lista_titulos_entre_colchetes():
    botoes = [BotaoResponse(id="a", title="Sim"), BotaoResponse(id="b", title="Não")]
    resultado = WhatsAppService().format_msg_botao("Confirma?", botoes)

    assert resultado == "Confirma?\n\nOpções: [Sim] / [Não]"


def test_formatar_lista_usa_um_traco_por_item():
    resultado = WhatsAppService().formatar_lista(["nome", "cnpj"])
    assert resultado == "- nome\n- cnpj"


def test_msg_build_endereco_monta_payload_com_dados_do_endereco():
    endereco = Address(logradouro="Av. Paulista", bairro="Bela Vista", cidade="São Paulo", uf="SP")
    payload = WhatsAppService().msg_build_endereco("5511999999999", endereco)

    assert payload["to"] == "5511999999999"
    texto = payload["interactive"]["body"]["text"]
    assert "Av. Paulista" in texto
    assert "Bela Vista — São Paulo/SP" in texto


def test_send_msg_botao_recusa_zero_botoes():
    with pytest.raises(ValueError):
        WhatsAppService().send_msg_botao("5511999999999", "texto", botoes=[])


def test_send_msg_botao_recusa_mais_de_tres_botoes():
    botoes = [BotaoResponse(id=str(i), title=str(i)) for i in range(4)]
    with pytest.raises(ValueError):
        WhatsAppService().send_msg_botao("5511999999999", "texto", botoes=botoes)


def test_send_msg_botao_monta_payload_interativo_e_envia(monkeypatch):
    captured = {}

    def fake_post(url, headers, json, timeout):
        captured["payload"] = json
        return FakeResponse(200, {"messages": [{"id": "wamid.1"}]})

    monkeypatch.setattr(msg_service_module.requests, "post", fake_post)

    botoes = [BotaoResponse(id="confirma", title="✅ Confirmar")]
    result = WhatsAppService().send_msg_botao("5511999999999", "Tudo certo?", botoes, rodape="rodapé")

    assert result == {"messages": [{"id": "wamid.1"}]}
    payload = captured["payload"]
    assert payload["interactive"]["type"] == "button"
    assert payload["interactive"]["footer"] == {"text": "rodapé"}
    assert payload["interactive"]["action"]["buttons"][0]["reply"]["id"] == "confirma"


def test_send_msg_text_anexa_lista_formatada(monkeypatch):
    captured = {}

    def fake_post(url, headers, json, timeout):
        captured["payload"] = json
        return FakeResponse(200, {"ok": True})

    monkeypatch.setattr(msg_service_module.requests, "post", fake_post)

    WhatsAppService().send_msg_text("5511999999999", "Faltam:", lista=["nome", "cnpj"])

    assert captured["payload"]["text"]["body"] == "Faltam:\n- nome\n- cnpj"


def test_post_wpp_retorna_none_em_status_de_erro(monkeypatch):
    monkeypatch.setattr(
        msg_service_module.requests, "post",
        lambda *a, **kw: FakeResponse(500, text="deu ruim"),
    )
    assert WhatsAppService().send_msg_text("5511999999999", "oi") is None


def test_post_wpp_retorna_none_em_erro_de_rede(monkeypatch):
    def fake_post(*a, **kw):
        raise msg_service_module.requests.RequestException("timeout")

    monkeypatch.setattr(msg_service_module.requests, "post", fake_post)
    assert WhatsAppService().send_msg_text("5511999999999", "oi") is None
