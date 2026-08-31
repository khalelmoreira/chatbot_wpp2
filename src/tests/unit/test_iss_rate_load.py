from src.managers.iss.iss_rate_manager import IssRateManager
from src.models.iss_rates_rj import RJ_ISS_RATES, RJ_ISS_VIGENCIA_INICIO
from src.models.municipios import RJ_CODIGO_MUNICIPIO
from src.workers.iss_rate_load import clear_load, run_load

RJ = RJ_CODIGO_MUNICIPIO


def _rate(codigo: str):
    rate = IssRateManager().get_current_rate(RJ, codigo)
    assert rate is not None
    return rate


def test_run_load_popula_todos_os_codigos_da_tabela_rj(db):
    total = run_load()

    assert total == len(RJ_ISS_RATES)
    # spot-checks contra a fonte confirmada (contabilidade.com, tabela RJ)
    assert _rate("010601").aliquota == 5.0   # consultoria em informática
    assert _rate("040101").aliquota == 2.0   # medicina
    assert _rate("071601").aliquota == 3.0   # florestamento/reflorestamento


def test_codigo_fora_da_fonte_nao_recebe_linha(db):
    """990101 (item 99, sem incidência) não está na fonte — fica sem linha de
    propósito, para IssResolutionService falhar visível se o classificador o devolver."""
    run_load()

    assert IssRateManager().get_current_rate(RJ, "990101") is None


def test_clear_load_remove_as_linhas_da_carga(db):
    run_load()
    removed = clear_load()

    assert removed == len(RJ_ISS_RATES)
    assert IssRateManager().get_current_rate(RJ, "010601") is None


def test_vigencia_inicio_e_a_data_de_confirmacao_nao_a_da_execucao(db):
    run_load()

    assert _rate("010601").vigencia_inicio == RJ_ISS_VIGENCIA_INICIO
