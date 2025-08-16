# -*- coding: utf-8 -*-
# Path: C:\Users\Msi\Desktop\investmentapp\src\tabs\simulation\simulation_core.py
import tkinter as tk
from tkinter import ttk, messagebox
import json
import logging
import os
from datetime import datetime
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from src.tabs.strategies.strategies_data import StrategyData
import traceback

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("C:\\Users\\Msi\\Desktop\\investmentapp\\logs\\app.log", encoding="utf-8"),
        logging.FileHandler("C:\\Users\\Msi\\Desktop\\investmentapp\\logs\\error.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

# Konfiguracja handlera dla error.log (tylko błędy)
error_handler = logging.getLogger('').handlers[1]
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(module)s | %(funcName)s | %(message)s | Traceback: %(exc_info)s"))

class SimulationCore:
    def __init__(self, frame):
        self.frame = frame
        self.strategy_data = StrategyData()
        self.refresh_id = None  # Store the after ID for periodic refresh

    def periodic_refresh(self):
        try:
            if not self.frame.winfo_exists():
                logging.debug("Simulation frame destroyed, stopping periodic refresh")
                return
            self.update_strategies_display()
            self.refresh_id = self.frame.after(5000, self.periodic_refresh)  # Refresh every 5 seconds
            logging.debug("Scheduled periodic refresh for simulation table")
        except Exception as e:
            logging.error(f"Error scheduling periodic refresh: {str(e)}", exc_info=True)
            tk.messagebox.showerror("Error", f"Błąd podczas planowania odświeżania: {str(e)}\nTraceback: {traceback.format_exc()}")

    def load_simulation_results(self, strategy_name, symbol):
        try:
            summary_file = Path(__file__).resolve().parents[3] / "simulations" / strategy_name / symbol.replace('/', '_') / "summary.json"
            if not summary_file.exists():
                logging.warning(f"No summary.json for strategy {strategy_name} on {symbol}")
                return {
                    "days": 0,
                    "profit": 0.0,
                    "profit_percentage": 0.0,
                    "max_dd_percentage": 0.0,
                    "total_trades": 0,
                    "total_transactions": 0,
                    "win_rate_percentage": 0.0,
                    "avg_profit_percentage": 0.0,
                    "profit_factor": "inf"
                }
            
            with open(summary_file, "r", encoding="utf-8") as f:
                summary_data = json.load(f)
            
            total_trades = int(summary_data.get("total_trades", 0))
            net_profit_usd = float(summary_data.get("net_profit_usd", 0.0))
            avg_profit_percentage = (net_profit_usd / total_trades / 10000 * 100) if total_trades > 0 else 0.0
            
            return {
                "days": int(summary_data.get("days_active", 0)),
                "profit": net_profit_usd,
                "profit_percentage": net_profit_usd / 10000 * 100,  # Zakładamy kapitał początkowy 10000
                "max_dd_percentage": float(summary_data.get("max_drawdown_usd", 0.0)) / 10000 * 100,  # Zakładamy kapitał początkowy 10000
                "total_trades": total_trades,
                "total_transactions": total_trades + len([t for t in summary_data.get("trades", []) if t.get("status") == "open"]),
                "win_rate_percentage": float(summary_data.get("winrate_pct", 0.0)),
                "avg_profit_percentage": avg_profit_percentage,
                "profit_factor": summary_data.get("profit_factor", "inf")
            }
        except Exception as e:
            logging.error(f"Error loading simulation results for {strategy_name} on {symbol}: {str(e)}", exc_info=True)
            return {
                "days": 0,
                "profit": 0.0,
                "profit_percentage": 0.0,
                "max_dd_percentage": 0.0,
                "total_trades": 0,
                "total_transactions": 0,
                "win_rate_percentage": 0.0,
                "avg_profit_percentage": 0.0,
                "profit_factor": "inf"
            }

    def show_price_chart(self, strategy_name, symbol):
        try:
            logging.info(f"Generating price chart for strategy {strategy_name} on {symbol}")
            fallback_file = Path(__file__).resolve().parents[3] / "data" / "fallback_ohlcv.json"
            if not fallback_file.exists():
                logging.warning(f"No fallback_ohlcv.json file found for {strategy_name} on {symbol}")
                tk.messagebox.showwarning("Warning", "Brak danych OHLCV do wyświetlenia wykresu")
                return
            
            trades_file = Path(__file__).resolve().parents[3] / "simulations" / strategy_name / symbol.replace('/', '_') / "trades.json"
            trades = []
            if trades_file.exists():
                with open(trades_file, "r", encoding="utf-8") as f:
                    trades = [json.loads(line) for line in f if line.strip()]
            
            with open(fallback_file, "r", encoding="utf-8") as f:
                ohlcv_data = json.load(f)
            
            # Poprawka: Upewniamy się, że używamy danych dla odpowiedniego symbolu
            symbol_normalized = symbol.replace('/', '_')
            ohlcv_symbol_data = ohlcv_data.get(symbol, {}).get("1h", [])  # Zakładamy domyślny interwał 1h
            if not ohlcv_symbol_data:
                logging.warning(f"No OHLCV data for {symbol} in fallback_ohlcv.json")
                tk.messagebox.showwarning("Warning", f"Brak danych OHLCV dla {symbol}")
                return
            
            df = pd.DataFrame(ohlcv_symbol_data, columns=["timestamp", "open", "high", "low", "close", "volume"])
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            
            plt.figure(figsize=(10, 6))
            plt.plot(df["timestamp"], df["close"], label="Cena zamknięcia", color="blue")
            
            buy_signals = [t for t in trades if t.get("side") == "long" and t.get("entry_time")]
            sell_signals = [t for t in trades if t.get("side") == "long" and t.get("exit_time")]
            
            if buy_signals:
                buy_times = [pd.to_datetime(t["entry_time"]) for t in buy_signals]
                buy_prices = [t["entry_price"] for t in buy_signals]
                plt.scatter(buy_times, buy_prices, marker="^", color="green", label="Kupno", s=100)
            
            if sell_signals:
                sell_times = [pd.to_datetime(t["exit_time"]) for t in sell_signals]
                sell_prices = [t["exit_price"] for t in sell_signals]
                plt.scatter(sell_times, sell_prices, marker="v", color="red", label="Sprzedaż", s=100)
            
            for buy, sell in zip(buy_signals, sell_signals):
                buy_time = pd.to_datetime(buy["entry_time"])
                sell_time = pd.to_datetime(sell["exit_time"])
                plt.plot([buy_time, sell_time], [buy["entry_price"], sell["exit_price"]], color="black", linestyle="--")
            
            plt.title(f"Wykres cenowy dla {strategy_name} na {symbol}")
            plt.xlabel("Czas")
            plt.ylabel("Cena")
            plt.legend()
            plt.grid(True)
            
            chart_window = tk.Toplevel(self.frame)
            chart_window.title(f"Wykres cenowy: {strategy_name} na {symbol}")
            chart_window.geometry("1000x600")
            
            canvas = FigureCanvasTkAgg(plt.gcf(), master=chart_window)
            canvas.get_tk_widget().pack(fill="both", expand=True)
            canvas.draw()
            
            ttk.Button(chart_window, text="Zamknij", command=chart_window.destroy).pack(pady=10)
            logging.info(f"Displayed price chart for {strategy_name} on {symbol}")
        except Exception as e:
            logging.error(f"Error generating price chart for {strategy_name} on {symbol}: {str(e)}", exc_info=True)
            tk.messagebox.showerror("Error", f"Błąd podczas generowania wykresu: {str(e)}\nTraceback: {traceback.format_exc()}")