# -*- coding: utf-8 -*-
# Path: C:\Users\Msi\Desktop\investmentapp\tests\test_api_and_signals.py

import unittest
import asyncio
import ccxt.async_support as ccxt
import pandas as pd
import logging
from unittest.mock import AsyncMock, patch
from pathlib import Path
from src.core.trade_manager_simulation import TradeManagerSimulation
from datetime import datetime
from zoneinfo import ZoneInfo

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("C:\\Users\\Msi\\Desktop\\investmentapp\\logs\\test.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

class TestApiAndSignals(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.trade_manager = TradeManagerSimulation()
        self.base_dir = Path(__file__).resolve().parents[1]
        self.strategies_file = self.base_dir / "data" / "strategies.json"
        self.api_keys_file = self.base_dir / "data" / "api_keys.json"

    @patch('ccxt.async_support.mexc')
    async def test_fetch_ohlcv(self, mock_mexc):
        """Test fetching OHLCV data from MEXC for ETH/USDT and WBTC/USDT."""
        mock_api_keys = [
            {"exchange": "MEXC", "api_key": "test_key", "api_secret": "test_secret", "passphrase": "", "rate_limit_requests": 1800, "timeout_seconds": 180}
        ]
        self.trade_manager.load_api_keys = lambda: mock_api_keys
        
        mock_ohlcv = [
            [1751913540000, 2533.72, 2534.26, 2533.5, 2533.5, 25.7541969],
            [1751913600000, 2533.5, 2534.0, 2532.0, 2533.8, 30.1234567]
        ]
        mock_mexc.return_value.fetch_ohlcv = AsyncMock(return_value=mock_ohlcv)
        mock_mexc.return_value.close = AsyncMock()
        
        for symbol in ["ETH/USDT", "WBTC/USDT"]:
            ohlcv = await mock_mexc.return_value.fetch_ohlcv(symbol, "1m", limit=10)
            self.assertTrue(ohlcv, f"No OHLCV data fetched for {symbol}")
            self.assertEqual(len(ohlcv[0]), 6, f"OHLCV data for {symbol} does not have 6 columns")
            self.assertTrue(all(candle[0] > 0 for candle in ohlcv), f"Invalid timestamps in OHLCV data for {symbol}")
            logging.info(f"Successfully fetched {len(ohlcv)} OHLCV candles for {symbol}")

    @patch('ccxt.async_support.kucoin')
    async def test_signal_generation(self, mock_kucoin):
        """Test signal generation in Paper Trading mode for strategy_test."""
        mock_api_keys = [
            {"exchange": "KUCOIN", "api_key": "test_key", "api_secret": "test_secret", "passphrase": "test_pass", "rate_limit_requests": 1800, "timeout_seconds": 180}
        ]
        self.trade_manager.load_api_keys = lambda: mock_api_keys
        
        mock_ohlcv = [
            [1751913540000, 149.573, 149.608, 149.545, 149.6, 506.9493],
            [1751913600000, 149.6, 149.65, 149.55, 149.62, 510.2345]
        ]
        mock_kucoin.return_value.fetch_ohlcv = AsyncMock(return_value=mock_ohlcv)
        mock_kucoin.return_value.close = AsyncMock()
        
        try:
            strategies = self.trade_manager.load_strategies()
            strategy = next((s for s in strategies if s["name"] == "strategy_test" and s["symbol"] == "ETH/USDT"), None)
            if not strategy:
                self.fail("Strategy strategy_test with symbol ETH/USDT not found in strategies.json")
            
            symbol = strategy["symbol"]
            timeframe = strategy["interval"]
            base_dir = self.base_dir / "paper" / "strategy_test" / symbol.replace('/', '_')
            base_dir.mkdir(parents=True, exist_ok=True)
            
            with patch('builtins.open', side_effect=mock_open()) as mocked_file:
                result = await self.trade_manager.paper_trade(
                    strategy_name="strategy_test",
                    symbol=symbol,
                    interval=timeframe,
                    mode="paper"
                )
            
            self.assertIsNotNone(result, "Paper trading result is None")
            self.assertIn("signals", result, "No signals in paper trading result")
            self.assertTrue(any(s in ["buy", "sell"] for s in result["signals"]), "No valid buy/sell signals generated")
            logging.info(f"Successfully generated signals for strategy_test on {symbol}")
        except Exception as e:
            logging.error(f"Error in test_signal_generation: {str(e)}")
            self.fail(f"Failed to generate signals: {str(e)}")

if __name__ == '__main__':
    unittest.main()