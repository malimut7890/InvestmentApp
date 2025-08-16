# -*- coding: utf-8 -*-
# Ścieżka: C:\Users\Msi\Desktop\investmentapp\src\tabs\live\live_tab.py
import tkinter as tk
from tkinter import ttk
import logging
import json
from datetime import datetime
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from src.tabs.strategies.strategies_data import StrategyData
from src.core.trade_manager_live import TradeManagerLive

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("C:\\Users\\Msi\\Desktop\\investmentapp\\logs\\app.log", encoding="utf-8"),
        logging.FileHandler("C:\\Users\\Msi\\Desktop\\investmentapp\\logs\\error.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

class LiveTab:
    def __init__(self, frame):
        try:
            logging.info("Initializing LiveTab")
            self.frame = frame
            self.strategy_data = StrategyData()
            self.trade_manager_live = TradeManagerLive()
            self.progress_label = None
            self.refresh_id = None
            
            for widget in self.frame.winfo_children():
                widget.destroy()
            logging.debug("Live frame cleared")
            
            self.tree = ttk.Treeview(self.frame, columns=(
                "Strategy", "Symbol", "Days", "Profit", "Profit %", "Max DD%", "Total Trades",
                "Total Transactions", "Win Rate%", "Avg Profit%", "Profit Factor"
            ), show="headings")
            self.tree.heading("Strategy", text="Strategia")
            self.tree.heading("Symbol", text="Symbol")
            self.tree.heading("Days", text="Dni")
            self.tree.heading("Profit", text="Zysk")
            self.tree.heading("Profit %", text="Zysk %")
            self.tree.heading("Max DD%", text="Max DD%")
            self.tree.heading("Total Trades", text="Liczba Transakcji")
            self.tree.heading("Total Transactions", text="Liczba Operacji")
            self.tree.heading("Win Rate%", text="Win Rate%")
            self.tree.heading("Avg Profit%", text="Śr. Zysk%")
            self.tree.heading("Profit Factor", text="Profit Factor")
            for col in self.tree["columns"]:
                self.tree.column(col, width=100, anchor="center")
            
            self.tree.pack(pady=10, fill="both", expand=True)
            
            self.progress_label = tk.Label(self.frame, text="", fg="red")
            self.progress_label.pack(pady=5)
            
            self.tree.bind("<Double-1>", self.on_tree_double_click)
            
            self.update_strategies_display()
            self.periodic_refresh()
            
            logging.info("LiveTab initialized")
        except Exception as e:
            logging.error(f"Error initializing LiveTab: {str(e)}", exc_info=True)
            self.show_error("Error initializing LiveTab", f"Błąd podczas inicjalizacji zakładki: {str(e)}")
            raise

    def show_error(self, context, message):
        logging.error(f"{context}: {message}", exc_info=True)
        if self.progress_label:
            self.progress_label.config(text=f"Błąd: {message}")

    def periodic_refresh(self):
        try:
            if not self.frame.winfo_exists():
                logging.debug("Live frame destroyed, stopping periodic refresh")
                return
            self.update_strategies_display()
            self.refresh_id = self.frame.after(5000, self.periodic_refresh)
            logging.debug("Scheduled periodic refresh for live table")
        except Exception as e:
            logging.error(f"Error scheduling periodic refresh: {str(e)}", exc_info=True)
            self.show_error("Scheduling periodic refresh", f"Błąd podczas planowania odświeżania: {str(e)}")

    def load_live_results(self, strategy_name, symbol):
        try:
            summary_file = Path(__file__).resolve().parents[3] / "live" / strategy_name / symbol.replace('/', '_') / "summary.json"
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
            avg_profit_percentage = (net_profit_usd / total_trades / 1000.0 * 100) if total_trades > 0 else 0.0
            
            return {
                "days": int(summary_data.get("days_active", 0)),
                "profit": net_profit_usd,
                "profit_percentage": net_profit_usd / 1000.0 * 100,
                "max_dd_percentage": float(summary_data.get("max_drawdown_usd", 0.0)) / 1000.0 * 100,
                "total_trades": total_trades,
                "total_transactions": int(summary_data.get("total_transactions", 0)),
                "win_rate_percentage": float(summary_data.get("winrate_pct", 0.0)),
                "avg_profit_percentage": avg_profit_percentage,
                "profit_factor": summary_data.get("profit_factor", "inf")
            }
        except Exception as e:
            logging.error(f"Error loading live results for {strategy_name} on {symbol}: {str(e)}", exc_info=True)
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

    def update_strategies_display(self):
        try:
            logging.info("Starting update of live strategies table")
            if not hasattr(self, "tree") or not self.tree.winfo_exists():
                logging.warning("Treeview widget does not exist or was destroyed, skipping update")
                return
            
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            strategies = self.strategy_data.load_strategies()
            logging.info(f"Loaded strategies: {', '.join(s['name'] + '_' + s['symbol'] for s in strategies)}")
            active_strategies = [s for s in strategies if s["mode"] == "Live"]
            
            for strategy in active_strategies:
                strategy_name = strategy["name"]
                symbol = strategy["symbol"]
                results = self.load_live_results(strategy_name, symbol)
                self.tree.insert("", tk.END, values=(
                    strategy_name,
                    symbol,
                    results["days"],
                    f"{results['profit']:.2f}",
                    f"{results['profit_percentage']:.2f}",
                    f"{results['max_dd_percentage']:.2f}",
                    results["total_trades"],
                    results["total_transactions"],
                    f"{results['win_rate_percentage']:.2f}",
                    f"{results['avg_profit_percentage']:.2f}",
                    results["profit_factor"]
                ))
            
            logging.info(f"Live strategies table updated, strategies: {', '.join(s['name'] + '_' + s['symbol'] for s in active_strategies)}")
        except Exception as e:
            logging.error(f"Error updating live strategies table: {str(e)}", exc_info=True)
            self.show_error("Error updating live table", f"Błąd podczas aktualizacji tabeli live: {str(e)}")

    def show_price_chart(self, strategy_name, symbol):
        try:
            logging.info(f"Generating price chart for strategy {strategy_name} on {symbol}")
            fallback_file = Path(__file__).resolve().parents[3] / "data" / "fallback_ohlcv.json"
            if not fallback_file.exists():
                logging.warning(f"No fallback_ohlcv.json file found for {strategy_name} on {symbol}")
                self.show_error("Generating price chart", "Brak danych OHLCV do wyświetlenia wykresu")
                return
            
            trades_file = Path(__file__).resolve().parents[3] / "live" / strategy_name / symbol.replace('/', '_') / "trades.json"
            trades = []
            if trades_file.exists():
                with open(trades_file, "r", encoding="utf-8") as f:
                    trades = [json.loads(line) for line in f if line.strip()]
            
            with open(fallback_file, "r", encoding="utf-8") as f:
                ohlcv_data = json.load(f)
            
            symbol_normalized = symbol.replace('/', '_')
            ohlcv_symbol_data = ohlcv_data.get(symbol_normalized, {}).get("1h", [])
            if not ohlcv_symbol_data:
                logging.warning(f"No OHLCV data for {symbol} in fallback_ohlcv.json")
                self.show_error("Generating price chart", f"Brak danych OHLCV dla {symbol}")
                return
            
            df = pd.DataFrame(ohlcv_symbol_data, columns=["timestamp", "open", "high", "low", "close", "volume"])
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            
            plt.figure(figsize=(10, 6))
            plt.plot(df["timestamp"], df["close"], label="Cena zamknięcia", color="blue")
            
            buy_signals = [t for t in trades if t.get("type") == "buy" and t.get("timestamp")]
            sell_signals = [t for t in trades if t.get("type") == "sell" and t.get("timestamp")]
            
            if buy_signals:
                buy_times = [pd.to_datetime(t["timestamp"]) for t in buy_signals]
                buy_prices = [t["price"] for t in buy_signals]
                plt.scatter(buy_times, buy_prices, marker="^", color="green", label="Kupno", s=100)
            
            if sell_signals:
                sell_times = [pd.to_datetime(t["timestamp"]) for t in sell_signals]
                sell_prices = [t["price"] for t in sell_signals]
                plt.scatter(sell_times, sell_prices, marker="v", color="red", label="Sprzedaż", s=100)
            
            for buy, sell in zip(buy_signals, sell_signals):
                buy_time = pd.to_datetime(buy["timestamp"])
                sell_time = pd.to_datetime(sell["timestamp"])
                plt.plot([buy_time, sell_time], [buy["price"], sell["price"]], color="black", linestyle="--")
            
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
            self.show_error("Generating price chart", f"Błąd podczas generowania wykresu: {str(e)}")

    def on_tree_double_click(self, event):
        try:
            item = self.tree.selection()
            if not item:
                logging.info("No item selected in LiveTab table")
                return
            item = item[0]
            strategy_name = self.tree.item(item, "values")[0]
            symbol = self.tree.item(item, "values")[1]
            logging.info(f"Double-click on strategy {strategy_name} with symbol {symbol} in LiveTab")
            self.show_price_chart(strategy_name, symbol)
        except Exception as e:
            logging.error(f"Error handling double-click in LiveTab: {str(e)}", exc_info=True)
            self.show_error("Error handling double-click", f"Błąd podczas obsługi tabeli: {str(e)}")

    def destroy(self):
        try:
            if self.refresh_id:
                self.frame.after_cancel(self.refresh_id)
                logging.debug("Cancelled periodic refresh")
            self.frame.destroy()
            logging.debug("LiveTab destroyed")
        except Exception as e:
            logging.error(f"Error destroying LiveTab: {str(e)}", exc_info=True)
            self.show_error("Error destroying LiveTab", f"Błąd podczas niszczenia zakładki: {str(e)}")