from src.utils.build_prompt import build_list_prompt


def test_build_list_prompt_supporta_placeholders_nomeados():
    template = "NOTAS:\n{notas}\n\nHISTORICO:\n{mensagens}"

    prompt = build_list_prompt(template, {"notas": "linha 1", "mensagens": "linha 2"})

    assert "NOTAS:" in prompt
    assert "linha 1" in prompt
    assert "HISTORICO:" in prompt
    assert "linha 2" in prompt
