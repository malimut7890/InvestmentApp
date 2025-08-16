# -*- coding: utf-8 -*-
# Sciezka: C:\Users\Msi\Desktop\investmentapp\strategies\utils\signals_ema.py
import pandas as pd
import logging

def calculate_ema(data, period):
    """Oblicza wykładniczą średnią kroczącą (EMA) dla podanych danych."""
    try:
        logging.info(f"Obliczanie EMA z okresem {period}")
        ema = data.ewm(span=period, adjust=False).mean()
        logging.info(f"Wygenerowano EMA dla okresu {period}")
        return ema
    except Exception as e:
        logging.error(f"Błąd obliczania EMA: {str(e)}")
        raise