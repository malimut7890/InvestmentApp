# -*- coding: utf-8 -*-
# Path: C:\Users\Msi\Desktop\investmentapp\src\core\trade_manager_base.py
import logging
import json
import ccxt.async_support as ccxt
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
import asyncio
from utils.normalization import normalize_symbol, normalize_interval

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("C:\\Users\\Msi\\Desktop\\investmentapp\\logs\\app.log", encoding="utf-8"),
        logging.FileHandler("C:\\Users\\Msi\\Desktop\\investmentapp\\logs\\error.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

class TradeManagerBase:
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        logging.info("TradeManagerBase initialized")

    def load_api_keys(self):
        try:
            api_keys_file = Path(__file__).resolve().parents[2] / "data" / "api_keys.json"
            if not api_keys_file.exists():
                logging.warning("No api_keys.json file found, using default settings")
                return [{"exchange": "mexc", "api_key": "", "api_secret": "", "passphrase": "", "rate_limit_requests": 1800, "timeout_seconds": 30}]
            with open(api_keys_file, "r", encoding="utf-8-sig") as f:
                api_keys = json.load(f)
            logging.info(f"Loaded API keys for exchanges: {[key['exchange'] for key in api_keys]}")
            return api_keys
        except Exception as e:
            logging.error(f"Error loading API keys: {str(e)}", exc_info=True)
            return [{"exchange": "mexc", "api_key": "", "api_secret": "", "passphrase": "", "rate_limit_requests": 1800, "timeout_seconds": 30}]

    async def synchronize_time(self, exchange, exchange_name, max_time_diff_ms=10000):
        try:
            server_time = await exchange.fetch_time()
            local_time = int(datetime.now(tz=ZoneInfo("Europe/Warsaw")).timestamp() * 1000)
            time_diff = server_time - local_time
            if abs(time_diff) > max_time_diff_ms:
                logging.error(f"Time difference with {exchange_name} server ({time_diff}ms) exceeds maximum allowed ({max_time_diff_ms}ms)")
                raise ValueError(f"Time difference with {exchange_name} server ({time_diff}ms) exceeds maximum allowed ({max_time_diff_ms}ms)")
            logging.info(f"Time synchronized with {exchange_name}, difference: {time_diff}ms")
            return time_diff
        except ValueError as e:
            logging.error(f"Error synchronizing time with {exchange_name}: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            logging.error(f"Error synchronizing time with {exchange_name}: {str(e)}", exc_info=True)
            raise

    async def validate_symbol_and_interval(self, exchange, symbol, interval):
        try:
            normalized_symbol = normalize_symbol(symbol)
            normalized_interval = normalize_interval(interval)
            markets = await exchange.load_markets()
            if normalized_symbol not in markets:
                logging.error(f"Symbol {normalized_symbol} not available on {exchange.id}")
                raise ValueError(f"Symbol {normalized_symbol} not available")
            if normalized_interval not in exchange.timeframes:
                logging.error(f"Interval {normalized_interval} not supported by {exchange.id}")
                raise ValueError(f"Interval {normalized_interval} not supported")
            logging.info(f"Validated symbol {normalized_symbol} and interval {normalized_interval} on {exchange.id}")
            return normalized_symbol
        except Exception as e:
            logging.error(f"Error validating symbol {symbol} and interval {interval}: {str(e)}", exc_info=True)
            raise