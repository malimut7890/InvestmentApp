# -*- coding: utf-8 -*-
# Ścieżka: C:\Users\Msi\Desktop\investmentapp\tests\test_ohlcv.py

import pytest
import ccxt.async_support as ccxt
import asyncio
import logging
from unittest.mock import AsyncMock, patch

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("C:\\Users\\Msi\\Desktop\\investmentapp\\logs\\test.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

@pytest.mark.asyncio
@patch('ccxt.async_support.mexc')
@patch('ccxt.async_support.kucoin')
async def test_ohlcv(mock_kucoin, mock_mexc):
    """Testuje pobieranie danych OHLCV dla MEXC i KuCoin."""
    try:
        # Mock API keys
        api_keys = [
            {"exchange": "MEXC", "api_key": "test_key", "api_secret": "test_secret", "passphrase": "", "timeout": 30000},
            {"exchange": "KUCOIN", "api_key": "test_key", "api_secret": "test_secret", "passphrase": "test_pass", "timeout": 30000}
        ]
        
        # Mock OHLCV data
        mock_ohlcv = [
            [1751913540000, 50000.0, 50500.0, 49500.0, 50000.0, 100.0],
            [1751913600000, 50000.0, 50500.0, 49500.0, 50000.0, 120.0]
        ]
        
        # Mock MEXC
        mock_mexc.return_value.load_markets = AsyncMock()
        mock_mexc.return_value.fetch_ohlcv = AsyncMock(return_value=mock_ohlcv)
        mock_mexc.return_value.close = AsyncMock()
        mexc = mock_mexc.return_value
        mexc_data = await mexc.fetch_ohlcv('BTC/USDT', '1m', limit=10)
        logging.info(f"MEXC OHLCV data: {mexc_data}")
        
        # Mock KuCoin
        mock_kucoin.return_value.load_markets = AsyncMock()
        mock_kucoin.return_value.fetch_ohlcv = AsyncMock(return_value=mock_ohlcv)
        mock_kucoin.return_value.close = AsyncMock()
        kucoin = mock_kucoin.return_value
        kucoin_data = await kucoin.fetch_ohlcv('BTC/USDT', '1m', limit=10)
        logging.info(f"KuCoin OHLCV data: {kucoin_data}")
        
        # Assertions
        assert mexc_data == mock_ohlcv, "MEXC OHLCV data does not match expected"
        assert kucoin_data == mock_ohlcv, "KuCoin OHLCV data does not match expected"
        assert len(mexc_data) == 2, "MEXC OHLCV data length incorrect"
        assert len(kucoin_data) == 2, "KuCoin OHLCV data length incorrect"
    except Exception as e:
        logging.error(f"Error fetching OHLCV: {str(e)}")
        pytest.fail(f"Error fetching OHLCV: {str(e)}")