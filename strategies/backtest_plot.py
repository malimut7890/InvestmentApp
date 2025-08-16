# -*- coding: utf-8 -*-
# Sciezka: C:\Users\Msi\Desktop\investmentapp\strategies\backtest_plot.py
import matplotlib.pyplot as plt
import pandas as pd
import logging

def plot_backtest_results(results):
    try:
        logging.info("Generowanie wykresu wyników backtestu")
        df = pd.DataFrame(results["data"])
        signals = results["signals"]
        parameters = results["parameters"]
        
        # Tworzenie wykresu
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True, gridspec_kw={'height_ratios': [3, 1]})
        
        # Wykres cenowy z linią ceny i wskaźnikami
        ax1.plot(df["timestamp"], df["close"], label="Cena zamknięcia", color="blue")
        
        # Dynamiczne rysowanie wskaźników
        for indicator in results["indicators"]:
            if indicator in df.columns and indicator != "adx":  # ADX na podwykresie
                ax1.plot(df["timestamp"], df[indicator], label=f"{indicator} ({parameters.get(indicator, '')})")
        
        # Sygnały buy/sell
        buy_signals = df[pd.Series(signals) == "buy"]
        sell_signals = df[pd.Series(signals) == "sell"]
        ax1.scatter(buy_signals["timestamp"], buy_signals["close"], marker="^", color="green", label="Buy", s=100)
        ax1.scatter(sell_signals["timestamp"], sell_signals["close"], marker="v", color="red", label="Sell", s=100)
        
        ax1.set_title(f"Backtest: {results['symbol']}")
        ax1.set_xlabel("Czas")
        ax1.set_ylabel("Cena")
        ax1.legend()
        ax1.grid(True)
        
        # Wykres ADX (jeśli istnieje)
        if "adx" in df.columns:
            ax2.plot(df["timestamp"], df["adx"], label=f"ADX ({parameters.get('adx_period', '')})", color="purple")
            if "adx_threshold" in parameters:
                ax2.axhline(y=parameters["adx_threshold"], color="gray", linestyle="--", label=f"Próg ADX ({parameters['adx_threshold']})")
        ax2.set_xlabel("Czas")
        ax2.set_ylabel("ADX")
        ax2.legend()
        ax2.grid(True)
        
        plt.tight_layout()
        logging.info("Wykres backtestu wygenerowany")
        return fig
    except Exception as e:
        logging.error(f"Błąd generowania wykresu backtestu: {str(e)}")
        raise