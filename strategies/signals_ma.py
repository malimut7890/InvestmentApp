# -*- coding: utf-8 -*-
# Ścieżka: C:\Users\Msi\Desktop\investmentapp\strategies\signals_ma.py
import pandas as pd
import numpy as np
import logging

def calculate_ma_signals(data, fast_ma_period, slow_ma_period):
    try:
        df = data.copy()
        df['fast_ma'] = df['close'].rolling(window=int(fast_ma_period)).mean()
        df['slow_ma'] = df['close'].rolling(window=int(slow_ma_period)).mean()
        signals = ['hold'] * len(df)
        position_open = False
        
        for i in range(1, len(df)):
            if df['fast_ma'].iloc[i] > df['slow_ma'].iloc[i] and df['fast_ma'].iloc[i-1] <= df['slow_ma'].iloc[i-1] and not position_open:
                signals[i] = 'buy'
                position_open = True
                logging.debug(f"Sygnał buy na indeksie {i}: fast_ma={df['fast_ma'].iloc[i]}, slow_ma={df['slow_ma'].iloc[i]}")
            elif df['fast_ma'].iloc[i] < df['slow_ma'].iloc[i] and df['fast_ma'].iloc[i-1] >= df['slow_ma'].iloc[i-1] and position_open:
                signals[i] = 'sell'
                position_open = False
                logging.debug(f"Sygnał sell na indeksie {i}: fast_ma={df['fast_ma'].iloc[i]}, slow_ma={df['slow_ma'].iloc[i]}")
        
        return signals
    except Exception as e:
        logging.error(f"Błąd generowania sygnałów MA: {str(e)}")
        return ['hold'] * len(data)