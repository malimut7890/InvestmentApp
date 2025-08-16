# -*- coding: utf-8 -*-
# Sciezka: C:\Users\Msi\Desktop\investmentapp\utils\normalization.py
import logging

def normalize_symbol(symbol):
    """Normalizuje symbole, np. BTC/USDT, BTC-USDT -> BTCUSDT"""
    try:
        normalized = symbol.replace("/", "").replace("-", "").upper()
        logging.debug(f"Normalizacja symbolu: {symbol} -> {normalized}")
        return normalized
    except Exception as e:
        logging.error(f"Blad normalizacji symbolu {symbol}: {str(e)}")
        return symbol

def normalize_interval(interval):
    """Normalizuje interwały, np. m1, 1m -> 1m; d1, 1d -> 1d"""
    try:
        interval = interval.lower().replace(" ", "")
        interval_map = {
            "m1": "1m", "1min": "1m", "min1": "1m",
            "m5": "5m", "5min": "5m", "min5": "5m",
            "m15": "15m", "15min": "15m", "min15": "15m",
            "m30": "30m", "30min": "30m", "min30": "30m",
            "h1": "1h", "1h": "1h", "hour1": "1h",
            "h4": "4h", "4h": "4h", "hour4": "4h",
            "d1": "1d", "1d": "1d", "day1": "1d",
            "w1": "1w", "1w": "1w", "week1": "1w",
            "mo1": "1mo", "1mo": "1mo", "month1": "1mo"
        }
        normalized = interval_map.get(interval, interval)
        logging.debug(f"Normalizacja interwalu: {interval} -> {normalized}")
        return normalized
    except Exception as e:
        logging.error(f"Blad normalizacji interwalu {interval}: {str(e)}")
        return interval