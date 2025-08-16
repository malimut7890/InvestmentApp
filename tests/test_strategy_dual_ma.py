# -*- coding: utf-8 -*-
# Ścieżka: C:\Users\Msi\Desktop\investmentapp\tests\test_strategy_dual_ma.py

import pytest
import pandas as pd
from strategies.strategy_dual_ma import Strategy

@pytest.fixture
def strategy():
    """Inicjalizuje instancję strategii Dual MA."""
    return Strategy()

@pytest.fixture
def sample_df():
    """Zwraca przykładowy DataFrame z danymi OHLCV."""
    return pd.DataFrame({
        "timestamp": [1, 2, 3],
        "close": [100, 101, 102],
        "open": [99, 100, 101],
        "high": [101, 102, 103],
        "low": [98, 99, 100],
        "volume": [1000, 1100, 1200]
    })

def test_update_indicators_valid(strategy):
    """Testuje aktualizację poprawnych parametrów."""
    indicators = {"ma_short": 5, "ma_long": 10}
    strategy.update_indicators(indicators)
    assert strategy.indicators["ma_short"] == 5
    assert strategy.indicators["ma_long"] == 10

def test_update_indicators_invalid(strategy):
    """Testuje aktualizację niepoprawnych parametrów."""
    indicators = {"ma_short": -1, "ma_long": "invalid"}
    strategy.update_indicators(indicators)
    assert strategy.indicators["ma_short"] == 10  # Domyślna wartość
    assert strategy.indicators["ma_long"] == 20   # Domyślna wartość

def test_get_indicators_valid(strategy, sample_df):
    """Testuje obliczanie wskaźników dla poprawnych danych."""
    strategy.indicators = {"ma_short": 2, "ma_long": 3}
    indicators = strategy.get_indicators(sample_df)
    assert isinstance(indicators, list)
    assert len(indicators) == 1
    assert "ma_short" in indicators[0]
    assert "ma_long" in indicators[0]
    assert indicators[0]["ma_short"] > 0
    assert indicators[0]["ma_long"] > 0

def test_get_indicators_empty_df(strategy):
    """Testuje obliczanie wskaźników dla pustego DataFrame."""
    empty_df = pd.DataFrame()
    indicators = strategy.get_indicators(empty_df)
    assert indicators == [{"ma_short": 0.0, "ma_long": 0.0}]

def test_get_signal_buy(strategy, sample_df):
    """Testuje generowanie sygnału 'buy'."""
    sample_df["ma_short"] = [100, 101, 102]
    sample_df["ma_long"] = [99, 100, 101]
    signal = strategy.get_signal(sample_df)
    assert signal == "buy"

def test_get_signal_sell(strategy, sample_df):
    """Testuje generowanie sygnału 'sell'."""
    sample_df["ma_short"] = [100, 101, 100]
    sample_df["ma_long"] = [101, 102, 101]
    signal = strategy.get_signal(sample_df)
    assert signal == "sell"

def test_get_signal_none(strategy, sample_df):
    """Testuje brak sygnału dla równych średnich."""
    sample_df["ma_short"] = [100, 101, 101]
    sample_df["ma_long"] = [100, 101, 101]
    signal = strategy.get_signal(sample_df)
    assert signal is None

def test_get_signal_empty_df(strategy):
    """Testuje generowanie sygnału dla pustego DataFrame."""
    empty_df = pd.DataFrame()
    signal = strategy.get_signal(empty_df)
    assert signal is None