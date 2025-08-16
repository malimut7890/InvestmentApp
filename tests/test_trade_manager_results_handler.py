# -*- coding: utf-8 -*-
# Ścieżka: C:\Users\Msi\Desktop\investmentapp\tests\test_trade_manager_results_handler.py

import pytest
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
import json
from unittest.mock import patch, mock_open
from src.core.trade_manager_results_handler import TradeManagerResultsHandler

@pytest.fixture
def trade_manager_results():
    """Inicjalizuje instancję TradeManagerResultsHandler."""
    return TradeManagerResultsHandler()

@pytest.fixture
def sample_trades():
    """Zwraca przykładową listę transakcji."""
    return [
        {"type": "buy", "price": 50000, "timestamp": "2025-07-01T10:00:00+02:00", "profit_usd": 0, "duration_minutes": 0},
        {"type": "sell", "price": 51000, "timestamp": "2025-07-01T11:00:00+02:00", "profit_usd": 1000, "duration_minutes": 60},
        {"type": "buy", "price": 51000, "timestamp": "2025-07-01T12:00:00+02:00", "profit_usd": 0, "duration_minutes": 0},
        {"type": "sell", "price": 50000, "timestamp": "2025-07-01T13:00:00+02:00", "profit_usd": -1000, "duration_minutes": 60}
    ]

@pytest.fixture
def sample_df():
    """Zwraca przykładowy DataFrame z danymi OHLCV."""
    return pd.DataFrame({
        "timestamp": [datetime(2025, 7, 1, 10, tzinfo=ZoneInfo("Europe/Warsaw")), datetime(2025, 7, 1, 11, tzinfo=ZoneInfo("Europe/Warsaw"))],
        "open": [50000, 51000],
        "high": [50500, 51500],
        "low": [49500, 50500],
        "close": [50000, 51000],
        "volume": [100, 120]
    })

def test_save_simulation_results_success(trade_manager_results, sample_trades, sample_df, tmp_path):
    """Testuje zapis wyników symulacji przy poprawnych danych."""
    base_dir = tmp_path / "simulations" / "test_strategy" / "BTC_USDT"
    strategy_name = "test_strategy"
    symbol = "BTC/USDT"
    open_trades = []
    total_profit = 0
    total_trades = 2
    winning_trades = 1
    avg_max_dd = -500
    initial_capital = 1000
    start_time_sim = datetime(2025, 7, 1, tzinfo=ZoneInfo("Europe/Warsaw"))

    with patch("builtins.open", mock_open()) as mocked_file, patch("os.remove") as mocked_remove:
        trade_manager_results.save_simulation_results(
            base_dir, strategy_name, symbol, sample_trades, open_trades, total_profit,
            total_trades, winning_trades, avg_max_dd, initial_capital, start_time_sim, sample_df
        )

        assert mocked_file.call_count == 4  # test_write.txt, trades.json, open_trades.json, summary.json
        mocked_file.assert_any_call(base_dir / "trades.json", "w", encoding="utf-8")
        mocked_file.assert_any_call(base_dir / "open_trades.json", "w", encoding="utf-8")
        mocked_file.assert_any_call(base_dir / "summary.json", "w", encoding="utf-8")
        mocked_remove.assert_called_once_with(base_dir / "test_write.txt")

def test_save_simulation_results_empty_trades(trade_manager_results, sample_df, tmp_path):
    """Testuje zapis wyników symulacji przy pustej liście transakcji."""
    base_dir = tmp_path / "simulations" / "test_strategy" / "BTC_USDT"
    strategy_name = "test_strategy"
    symbol = "BTC/USDT"
    trades = []
    open_trades = []
    total_profit = 0
    total_trades = 0
    winning_trades = 0
    avg_max_dd = 0
    initial_capital = 1000
    start_time_sim = datetime(2025, 7, 1, tzinfo=ZoneInfo("Europe/Warsaw"))

    with patch("builtins.open", mock_open()) as mocked_file, patch("os.remove") as mocked_remove:
        trade_manager_results.save_simulation_results(
            base_dir, strategy_name, symbol, trades, open_trades, total_profit,
            total_trades, winning_trades, avg_max_dd, initial_capital, start_time_sim, sample_df
        )

        assert mocked_file.call_count == 4
        mocked_file.assert_any_call(base_dir / "trades.json", "w", encoding="utf-8")
        mocked_file.assert_any_call(base_dir / "open_trades.json", "w", encoding="utf-8")
        mocked_file.assert_any_call(base_dir / "summary.json", "w", encoding="utf-8")
        mocked_remove.assert_called_once_with(base_dir / "test_write.txt")

def test_save_simulation_results_file_error(trade_manager_results, sample_trades, sample_df, tmp_path):
    """Testuje obsługę błędu zapisu pliku."""
    base_dir = tmp_path / "simulations" / "test_strategy" / "BTC_USDT"
    strategy_name = "test_strategy"
    symbol = "BTC/USDT"
    open_trades = []
    total_profit = 0
    total_trades = 2
    winning_trades = 1
    avg_max_dd = -500
    initial_capital = 1000
    start_time_sim = datetime(2025, 7, 1, tzinfo=ZoneInfo("Europe/Warsaw"))

    with patch("builtins.open", side_effect=IOError("Błąd zapisu pliku")):
        with pytest.raises(IOError, match="Błąd zapisu pliku"):
            trade_manager_results.save_simulation_results(
                base_dir, strategy_name, symbol, sample_trades, open_trades, total_profit,
                total_trades, winning_trades, avg_max_dd, initial_capital, start_time_sim, sample_df
            )