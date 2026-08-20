from src.managers.iss.iss_rate_manager import IssRateManager
from src.types import IssRate


def test_get_current_rate_finds_open_ended_row(db):
    manager = IssRateManager()
    manager.upsert_rates([
        IssRate("3304557", "010601", 3.0, "2026-01-01", None),
    ])

    rate = manager.get_current_rate("3304557", "010601")

    assert rate is not None
    assert rate.aliquota == 3.0


def test_get_current_rate_excludes_expired_row(db):
    manager = IssRateManager()
    manager.upsert_rates([
        IssRate("3304557", "010601", 2.0, "2020-01-01", "2020-12-31"),
    ])

    rate = manager.get_current_rate("3304557", "010601")

    assert rate is None


def test_get_current_rate_returns_none_when_no_row_exists(db):
    manager = IssRateManager()

    rate = manager.get_current_rate("3304557", "999999")

    assert rate is None


def test_get_current_rate_prefers_most_recent_vigencia(db):
    manager = IssRateManager()
    manager.upsert_rates([
        IssRate("3304557", "010601", 2.0, "2024-01-01", "2025-12-31"),
        IssRate("3304557", "010601", 3.5, "2026-01-01", None),
    ])

    rate = manager.get_current_rate("3304557", "010601")

    assert rate is not None
    assert rate.aliquota == 3.5
