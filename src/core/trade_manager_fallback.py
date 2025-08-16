# -*- coding: utf-8 -*-
# Ścieżka: C:\Users\Msi\Desktop\investmentapp\src\core\trade_manager_fallback.py
import logging
import json
from pathlib import Path
import pandas as pd
from src.core.trade_manager_base import TradeManagerBase

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("C:\\Users\\Msi\\Desktop\\investmentapp\\logs\\app.log", encoding="utf-8"),
        logging.FileHandler("C:\\Users\\Msi\\Desktop\\investmentapp\\logs\\error.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

class TradeManagerFallback(TradeManagerBase):
    def __init__(self):
        super().__init__()

    def load_fallback_ohlcv(self, symbol, interval):
        try:
            fallback_file = Path(__file__).resolve().parents[2] / "data" / "fallback_ohlcv.json"
            if not fallback_file.exists():
                logging.warning(f"No fallback_ohlcv.json file found for {symbol} on {interval}")
                return None
            with open(fallback_file, "r", encoding="utf-8") as f:
                ohlcv_data = json.load(f)
            symbol_normalized = symbol.replace('/', '_')
            ohlcv_symbol_data = ohlcv_data.get(symbol_normalized, {}).get(interval, [])
            if not ohlcv_symbol_data:
                logging.warning(f"No OHLCV data for {symbol} on {interval} in fallback_ohlcv.json")
                return None
            df = pd.DataFrame(ohlcv_symbol_data, columns=["timestamp", "open", "high", "low", "close", "volume"])
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            if df.empty:
                logging.warning(f"Empty OHLCV data for {symbol} on {interval}")
                return None
            logging.info(f"Loaded fallback OHLCV data for {symbol} on {interval}")
            return df
        except Exception as e:
            logging.error(f"Error loading fallback OHLCV data for {symbol} on {interval}: {str(e)}", exc_info=True)
            return None