# -*- coding: utf-8 -*-
# Path: C:\Users\Msi\Desktop\investmentapp\strategies\utils\signals_adx.py
import pandas as pd
import logging

def calculate_adx(high, low, close, period):
    """
    Calculate the Average Directional Index (ADX) for given OHLCV data.
    
    Args:
        high (pd.Series): High prices
        low (pd.Series): Low prices
        close (pd.Series): Close prices
        period (int): Period for ADX calculation
    
    Returns:
        pd.Series: ADX values
    """
    try:
        logging.info(f"Calculating ADX with period {period}")
        
        # Calculate True Range (TR)
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # Calculate Directional Movement (DM)
        plus_dm = high - high.shift()
        minus_dm = low.shift() - low
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0
        
        # Smooth TR and DM
        tr_smooth = tr.ewm(span=period, adjust=False).mean()
        plus_dm_smooth = plus_dm.ewm(span=period, adjust=False).mean()
        minus_dm_smooth = minus_dm.ewm(span=period, adjust=False).mean()
        
        # Calculate Directional Indicators (DI)
        plus_di = (plus_dm_smooth / tr_smooth) * 100
        minus_di = (minus_dm_smooth / tr_smooth) * 100
        
        # Calculate DX
        dx = (abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
        
        # Calculate ADX
        adx = dx.ewm(span=period, adjust=False).mean()
        
        logging.info(f"Generated ADX for period {period}")
        return adx
    except Exception as e:
        logging.error(f"Error calculating ADX: {str(e)}")
        raise