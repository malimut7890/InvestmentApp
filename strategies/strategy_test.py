# -*- coding: utf-8 -*-
# Ścieżka: C:\Users\Msi\Desktop\investmentapp\strategies\strategy_test.py
import logging
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("C:\\Users\\Msi\\Desktop\\investmentapp\\logs\\app.log", encoding="utf-8"),
        logging.FileHandler("C:\\Users\\Msi\\Desktop\\investmentapp\\logs\\error.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

class Strategy:
    def __init__(self):
        self.indicators = {
            "ema_short": 10,
            "ema_long": 20,
            "adx_threshold": 25
        }
        logging.debug("Initialized Strategy with default indicators")

    def update_indicators(self, indicators):
        try:
            self.indicators.update(indicators)
            logging.debug(f"Updated indicators: {self.indicators}")
        except Exception as e:
            logging.error(f"Error updating indicators: {str(e)}", exc_info=True)
            raise

    def get_indicators(self, df):
        try:
            if df.empty:
                logging.warning("Empty DataFrame provided to get_indicators")
                return [{"ema_short": 0, "ema_long": 0, "adx": 0}]
            
            df = df.copy()
            df["ema_short"] = df["close"].ewm(span=self.indicators["ema_short"], adjust=False).mean()
            df["ema_long"] = df["close"].ewm(span=self.indicators["ema_long"], adjust=False).mean()
            
            dx = 100 * ((df["high"] - df["low"]) / df["close"]).abs()
            df["adx"] = dx.ewm(span=14, adjust=False).mean()
            
            logging.debug(f"Calculated indicators for DataFrame: {list(df.columns)}")
            return [df[["ema_short", "ema_long", "adx"]].to_dict(orient="records")[-1]]
        except Exception as e:
            logging.error(f"Error calculating indicators: {str(e)}", exc_info=True)
            return [{"ema_short": 0, "ema_long": 0, "adx": 0}]

    def get_signal(self, df):
        try:
            if df.empty:
                logging.warning("Empty DataFrame provided to get_signal")
                return None
            
            row = df.iloc[-1]
            ema_short = row.get("ema_short", 0)
            ema_long = row.get("ema_long", 0)
            adx = row.get("adx", 0)
            
            logging.debug(f"EMA Short: {ema_short}, EMA Long: {ema_long}, ADX: {adx}")
            
            if ema_short > ema_long and adx > self.indicators["adx_threshold"]:
                logging.info("Generated buy signal")
                return "buy"
            elif ema_short < ema_long and adx > self.indicators["adx_threshold"]:
                logging.info("Generated sell signal")
                return "sell"
            else:
                logging.debug("No signal generated")
                return None
        except Exception as e:
            logging.error(f"Error generating signal: {str(e)}", exc_info=True)
            return None