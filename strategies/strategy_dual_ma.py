# -*- coding: utf-8 -*-
# Ścieżka: C:\Users\Msi\Desktop\investmentapp\strategies\strategy_dual_ma.py

import logging
import pandas as pd
from typing import Dict, List, Optional

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
    """Strategia oparta na dwóch średnich kroczących (MA).

    Attributes:
        indicators (Dict[str, int]): Słownik z parametrami strategii (ma_short, ma_long).
    """

    def __init__(self):
        self.indicators = {
            "ma_short": 10,
            "ma_long": 20
        }
        logging.debug("Zainicjalizowano strategię Dual MA z domyślnymi wskaźnikami")

    def update_indicators(self, indicators: Dict[str, any]) -> None:
        """Aktualizuje parametry wskaźników strategii.

        Args:
            indicators (Dict[str, any]): Nowe wartości dla wskaźników (ma_short, ma_long).

        Raises:
            ValueError: Jeśli parametry nie są poprawnymi liczbami całkowitymi większymi od zera.
        """
        try:
            for key, value in indicators.items():
                if key in ["ma_short", "ma_long"]:
                    try:
                        value = int(value)
                        if value <= 0:
                            raise ValueError(f"Parametr {key} musi być liczbą całkowitą większą od 0, otrzymano: {value}")
                        self.indicators[key] = value
                    except (ValueError, TypeError):
                        logging.error(f"Niepoprawna wartość dla {key}: {value}, używam domyślnej wartości {self.indicators[key]}")
                        continue
            logging.debug(f"Zaktualizowano wskaźniki: {self.indicators}")
        except Exception as e:
            logging.error(f"Błąd aktualizacji wskaźników: {str(e)}", exc_info=True)
            raise

    def get_indicators(self, df: pd.DataFrame) -> List[Dict[str, float]]:
        """Oblicza wskaźniki dla podanego DataFrame.

        Args:
            df (pd.DataFrame): DataFrame z danymi OHLCV.

        Returns:
            List[Dict[str, float]]: Lista słowników z wartościami wskaźników (ma_short, ma_long).

        Example:
            >>> df = pd.DataFrame({"close": [100, 101, 102]})
            >>> strategy = Strategy()
            >>> strategy.get_indicators(df)
            [{"ma_short": 101.0, "ma_long": 101.0}]
        """
        try:
            if df.empty:
                logging.warning("Pusty DataFrame przekazany do get_indicators")
                return [{"ma_short": 0.0, "ma_long": 0.0}]
            
            df = df.copy()
            df["ma_short"] = df["close"].rolling(window=self.indicators["ma_short"]).mean()
            df["ma_long"] = df["close"].rolling(window=self.indicators["ma_long"]).mean()
            
            logging.debug(f"Obliczono wskaźniki dla DataFrame: {list(df.columns)}")
            return [df[["ma_short", "ma_long"]].to_dict(orient="records")[-1]]
        except Exception as e:
            logging.error(f"Błąd obliczania wskaźników: {str(e)}", exc_info=True)
            return [{"ma_short": 0.0, "ma_long": 0.0}]

    def get_signal(self, df: pd.DataFrame) -> Optional[str]:
        """Generuje sygnał handlowy na podstawie wskaźników.

        Args:
            df (pd.DataFrame): DataFrame z danymi OHLCV i wskaźnikami.

        Returns:
            Optional[str]: Sygnał handlowy ("buy", "sell") lub None.

        Example:
            >>> df = pd.DataFrame({"ma_short": [101], "ma_long": [100]})
            >>> strategy = Strategy()
            >>> strategy.get_signal(df)
            "buy"
        """
        try:
            if df.empty:
                logging.warning("Pusty DataFrame przekazany do get_signal")
                return None
            
            row = df.iloc[-1]
            ma_short = row.get("ma_short", 0)
            ma_long = row.get("ma_long", 0)
            
            logging.debug(f"MA Short: {ma_short}, MA Long: {ma_long}")
            
            if ma_short > ma_long:
                logging.info("Wygenerowano sygnał buy")
                return "buy"
            elif ma_short < ma_long:
                logging.info("Wygenerowano sygnał sell")
                return "sell"
            else:
                logging.debug("Nie wygenerowano sygnału")
                return None
        except Exception as e:
            logging.error(f"Błąd generowania sygnału: {str(e)}", exc_info=True)
            return None