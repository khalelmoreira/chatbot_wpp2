import pytest

from src.services.telegram import msg_service as msg_service_module
from src.services.telegram.msg_service import TelegramService
from src.types import BotaoResponse


class FakeResponse:
    def __init__(self, status_code: int, json_data: dict | None = None, text: str = ""):
        self.status_code = status_code
        self._json = json_data or {}
        self.text = text

    def json(self) -> dict:
        return self._json


def test_format_msg_botao_lista_titulos_entre_colchetes():
    botoes = [BotaoResponse(id="a", title="Sim"), BotaoResponse(id="b", title="Não")]
    resultado = TelegramService().format_msg_botao("Confirma?", botoes)

    assert resultado == "Confirma?\n\nOpções: [Sim] / [Não]"


def test_formatar_lista_usa_um_traco_por_item():
    resultado = TelegramService().formatar_lista(["nome", "cnpj"])
    assert resultado == "- nome\n- cnpj"


def test_send_msg_botao_recusa_zero_botoes():
    with pytest.raises(ValueError):
        TelegramService().send_msg_botao("123456789", "texto", botoes=[])


def test_send_msg_botao_recusa_mais_de_tres_botoes():
    botoes = [BotaoResponse(id=str(i), title=str(i)) for i in range(4)]
    with pytest.raises(ValueError):
        TelegramService().send_msg_botao("123456789", "texto", botoes=botoes)


def test_send_msg_botao_monta_teclado_inline_e_envia(monkeypatch):
    captured = {}

    def fake_post(url, json, timeout):
        captured["payload"] = json
        return FakeResponse(200, {"ok": True})

    monkeypatch.setattr(msg_service_module.requests, "post", fake_post)

    botoes = [BotaoResponse(id="confirma", title="✅ Confirmar")]
    result = TelegramService().send_msg_botao("123456789", "Tudo certo?", botoes, rodape="rodapé")

    assert result == {"ok": True}
    payload = captured["payload"]
    assert "rodapé" in payload["text"]
    assert payload["reply_markup"]["inline_keyboard"][0][0]["callback_data"] == "confirma"


def test_send_msg_text_anexa_lista_formatada(monkeypatch):
    captured = {}

    def fake_post(url, json, timeout):
        captured["payload"] = json
        return FakeResponse(200, {"ok": True})

    monkeypatch.setattr(msg_service_module.requests, "post", fake_post)

    TelegramService().send_msg_text("123456789", "Faltam:", lista=["nome", "cnpj"])

    assert captured["payload"]["text"] == "Faltam:\n- nome\n- cnpj"


def test_post_telegram_retorna_none_em_status_de_erro(monkeypatch):
    monkeypatch.setattr(
        msg_service_module.requests, "post",
        lambda *a, **kw: FakeResponse(500, text="deu ruim"),
    )
    assert TelegramService().send_msg_text("123456789", "oi") is None


def test_post_telegram_retorna_none_em_erro_de_rede(monkeypatch):
    def fake_post(*a, **kw):
        raise msg_service_module.requests.RequestException("timeout")

    monkeypatch.setattr(msg_service_module.requests, "post", fake_post)
    assert TelegramService().send_msg_text("123456789", "oi") is None
