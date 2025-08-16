# -*- coding: utf-8 -*-
# Path: C:\Users\Msi\Desktop\investmentapp\src\tabs\strategies\strategies_gui_backtest.py
import tkinter as tk
from tkinter import ttk, messagebox
import logging
import json
import pandas as pd
from datetime import datetime
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from strategies.backtest_plot import plot_backtest_results
from src.tabs.strategies.strategies_backtest import run_backtest
from src.tabs.symbols import SymbolsTab
from src.tabs.strategies.strategies_data import StrategyData
from pathlib import Path
import glob
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

class StrategiesTabBacktest:
    def __init__(self, frame, symbols_tab: SymbolsTab, strategy_data: StrategyData):
        self.frame = frame
        self.symbols_tab = symbols_tab
        self.strategy_data = strategy_data
        self.strategies = self.strategy_data.load_strategies()

    def show_backtest_results(self, results, strategy_name, symbol):
        try:
            window = tk.Toplevel(self.frame)
            window.title(f"Backtest: {strategy_name}")
            window.geometry("800x600")
            window.transient(self.frame)
            window.grab_set()
            
            tk.Label(window, text="Symbol:").pack(pady=5)
            tk.Label(window, text=symbol).pack(pady=5)
            
            tk.Label(window, text="Results:").pack(pady=5)
            results_frame = ttk.Frame(window)
            results_frame.pack(pady=5)
            
            days_label = tk.Label(results_frame, text=f"Days: {results['days']}")
            days_label.pack(pady=2)
            profit_label = tk.Label(results_frame, text=f"Profit: {results['profit']:.2f}")
            profit_label.pack(pady=2)
            profit_percentage_label = tk.Label(results_frame, text=f"Profit %: {results['profit_percentage']:.2f}%")
            profit_percentage_label.pack(pady=2)
            max_dd_label = tk.Label(results_frame, text=f"Max DD%: {results['max_dd_percentage']:.2f}%")
            max_dd_label.pack(pady=2)
            signals_label = tk.Label(results_frame, text=f"Number of signals: {len([s for s in results['signals'] if s in ['buy', 'sell']])}")
            signals_label.pack(pady=2)
            total_trades_label = tk.Label(results_frame, text=f"Total Trades: {results.get('total_trades', 0)}")
            total_trades_label.pack(pady=2)
            total_transactions_label = tk.Label(results_frame, text=f"Total Transactions: {results.get('total_transactions', 0)}")
            total_transactions_label.pack(pady=2)
            win_rate_label = tk.Label(results_frame, text=f"Win Rate %: {results.get('win_rate_percentage', 0):.2f}")
            win_rate_label.pack(pady=2)
            avg_profit_label = tk.Label(results_frame, text=f"Avg Profit %: {results.get('avg_profit_percentage', 0):.2f}")
            avg_profit_label.pack(pady=2)
            profit_factor_label = tk.Label(results_frame, text=f"Profit Factor: {results.get('profit_factor', 'inf')}")
            profit_factor_label.pack(pady=2)
            
            # Chart
            fig = plot_backtest_results(results)
            canvas = FigureCanvasTkAgg(fig, master=window)
            canvas.get_tk_widget().pack(pady=5, fill="both", expand=True)
            canvas.draw()
            
            ttk.Button(window, text="Close", command=window.destroy).pack(pady=10)
            logging.info(f"Displayed backtest results for strategy {strategy_name} on {symbol}")
        except Exception as e:
            logging.error(f"Error displaying backtest results for {strategy_name}: {str(e)}", exc_info=True)
            tk.messagebox.showerror("Error", f"Błąd podczas wyświetlania wyników: {str(e)}\nTraceback: {traceback.format_exc()}")

    def export_backtest_to_csv(self):
        try:
            results = []
            for strategy in self.strategies:
                backtest_files = glob.glob(str(Path(__file__).resolve().parents[3] / "backtests" / strategy["name"] / "*" / "*" / "*.json"))
                for file in backtest_files:
                    with open(file, "r", encoding="utf-8-sig") as f:
                        result = json.load(f)
                        for res in (result if isinstance(result, list) else [result]):
                            results.append({
                                "strategy": strategy["name"],
                                "symbol": res["symbol"],
                                "days": res["days"],
                                "profit": res["profit"],
                                "profit_percentage": res["profit_percentage"],
                                "max_dd_percentage": res["max_dd_percentage"],
                                "total_trades": res.get("total_trades", 0),
                                "total_transactions": res.get("total_transactions", 0),
                                "win_rate_percentage": res.get("win_rate_percentage", 0),
                                "avg_profit_percentage": res.get("avg_profit_percentage", 0),
                                "profit_factor": res.get("profit_factor", "inf")
                            })
            if not results:
                logging.warning("No backtest results to export")
                self.show_error("Exporting backtest", "No backtest results to export")
                return
            
            # Save to strategy folder
            for strategy in self.strategies:
                strategy_results = [r for r in results if r["strategy"] == strategy["name"]]
                if strategy_results:
                    df = pd.DataFrame(strategy_results)
                    backtest_dir = Path(__file__).resolve().parents[3] / "backtests" / strategy["name"] / str(datetime.now().year) / f"{datetime.now().month:02d}"
                    backtest_dir.mkdir(parents=True, exist_ok=True)
                    strategy_file = backtest_dir / f"backtest_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                    df.to_csv(strategy_file, index=False, encoding="utf-8")
                    logging.info(f"Exported results for strategy {strategy['name']} to {strategy_file}")
            
            # Save summary
            df_summary = pd.DataFrame(results)
            export_dir = Path(__file__).resolve().parents[3] / "data" / "exports"
            export_dir.mkdir(parents=True, exist_ok=True)
            summary_file = export_dir / f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df_summary.to_csv(summary_file, index=False, encoding="utf-8")
            logging.info(f"Exported backtest summary to {summary_file}")
            tk.messagebox.showinfo("Success", f"Exported results to {summary_file}")
        except Exception as e:
            logging.error(f"Error exporting backtests to CSV: {str(e)}", exc_info=True)
            tk.messagebox.showerror("Error", f"Błąd podczas eksportowania wyników: {str(e)}\nTraceback: {traceback.format_exc()}")

    def show_error(self, context, msg):
        """Unified error handling for GUI and logging."""
        logging.error(f"{context}: {msg}", exc_info=True)
        tk.messagebox.showerror("Error", msg)