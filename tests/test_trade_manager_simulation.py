# -*- coding: utf-8 -*-
# Ścieżka: C:\Users\Msi\Desktop\investmentapp\tests\test_trade_manager_simulation.py

import pytest
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
from unittest.mock import AsyncMock, patch, mock_open
from src.core.trade_manager_simulation import TradeManagerSimulation
import ccxt.async_support as ccxt
import asyncio

@pytest.fixture
def trade_manager():
    """Inicjalizuje instancję TradeManagerSimulation."""
    return TradeManagerSimulation()

@pytest.fixture
def sample_ohlcv():
    """Zwraca przykładowe dane OHLCV."""
    return [
        [1751913540000, 149.573, 149.608, 149.545, 149.6, 506.9493],
        [1751913600000, 149.6, 149.65, 149.55, 149.62, 510.2345]
    ]

@pytest.fixture
def sample_df():
    """Zwraca przykładowy DataFrame z danymi OHLCV."""
    return pd.DataFrame({
        "timestamp": [datetime(2025, 7, 1, 10, tzinfo=ZoneInfo("Europe/Warsaw")), datetime(2025, 7, 1, 11, tzinfo=ZoneInfo("Europe/Warsaw"))],
        "open": [149.573, 149.6],
        "high": [149.608, 149.65],
        "low": [149.545, 149.55],
        "close": [149.6, 149.62],
        "volume": [506.9493, 510.2345]
    })

@patch('ccxt.async_support.kucoin')
async def test_paper_trade_success(mock_kucoin, trade_manager, sample_ohlcv, sample_df):
    """Testuje paper trading z poprawnymi danymi."""
    mock_api_keys = [
        {"exchange": "KUCOIN", "api_key": "test_key", "api_secret": "test_secret", "passphrase": "test_pass", "rate_limit_requests": 1800, "timeout_seconds": 180}
    ]
    trade_manager.load_api_keys = lambda: mock_api_keys
    
    mock_kucoin.return_value.fetch_ohlcv = AsyncMock(return_value=sample_ohlcv)
    mock_kucoin.return_value.close = AsyncMock()
    
    mock_strategies = [
        {
            "name": "strategy_test",
            "symbol": "ETH/USDT",
            "mode": "Paper",
            "interval": "1m",
            "exchange": "KUCOIN",
            "parameters": {"ema_short": 5.0, "ema_long": 7.0, "adx": 4.0, "min_volatility": 0.1},
            "file_path": "C:\\Users\\Msi\\Desktop\\investmentapp\\strategies\\strategy_test.py"
        }
    ]
    trade_manager.load_strategies = lambda: mock_strategies
    
    with patch('builtins.open', mock_open()) as mocked_file, \
         patch('pathlib.Path.exists', return_value=True), \
         patch('importlib.util.spec_from_file_location') as mock_spec, \
         patch('importlib.util.module_from_spec') as mock_module:
        mock_strategy = AsyncMock()
        mock_strategy.get_indicators.return_value = [{"ema_short": 149.61, "ema_long": 149.59, "adx": 25.1}]
        mock_strategy.get_signal.return_value = "buy"
        mock_spec.return_value = MagicMock()
        mock_module.return_value = MagicMock(Strategy=mock_strategy)
        
        result = await trade_manager.paper_trade("strategy_test", "ETH/USDT", "1m", mode="paper")
        
        assert result is not None
        assert "signals" in result
        assert "buy" in result["signals"]
        mocked_file.assert_any_call(Path("C:\\Users\\Msi\\Desktop\\investmentapp\\data\\strategies.json"), "r", encoding="utf-8-sig")
        mocked_file.assert_any_call(Path("C:\\Users\\Msi\\Desktop\\investmentapp\\paper\\strategy_test\\ETH_USDT\\trades.json"), "w", encoding="utf-8")

async def test_paper_trade_no_data(mock_kucoin, trade_manager, sample_ohlcv):
    """Testuje paper trading przy braku danych OHLCV."""
    mock_api_keys = [
        {"exchange": "KUCOIN", "api_key": "test_key", "api_secret": "test_secret", "passphrase": "test_pass", "rate_limit_requests": 1800, "timeout_seconds": 180}
    ]
    trade_manager.load_api_keys = lambda: mock_api_keys
    
    mock_kucoin.return_value.fetch_ohlcv = AsyncMock(return_value=[])
    mock_kucoin.return_value.close = AsyncMock()
    
    mock_strategies = [
        {
            "name": "strategy_test",
            "symbol": "ETH/USDT",
            "mode": "Paper",
            "interval": "1m",
            "exchange": "KUCOIN",
            "parameters": {"ema_short": 5.0, "ema_long": 7.0, "adx": 4.0},
            "file_path": "C:\\Users\\Msi\\Desktop\\investmentapp\\strategies\\strategy_test.py"
        }
    ]
    trade_manager.load_strategies = lambda: mock_strategies
    
    trade_manager.load_fallback_ohlcv = lambda x, y: None
    
    with pytest.raises(asyncio.CancelledError):
        task = asyncio.create_task(trade_manager.paper_trade("strategy_test", "ETH/USDT", "1m", mode="paper"))
        await asyncio.sleep(0.1)
        task.cancel()
        await task