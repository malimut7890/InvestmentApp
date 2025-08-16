# -*- coding: utf-8 -*-
# Ścieżka: C:\Users\Msi\Desktop\investmentapp\src\tabs\simulation\simulation.py

import tkinter as tk
from tkinter import ttk
import logging
from pathlib import Path
import json
from src.tabs.strategies.strategies_data import StrategyData
from src.core.error_handler import ErrorHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("C:\\Users\\Msi\\Desktop\\investmentapp\\logs\\app.log", encoding="utf-8"),
        logging.FileHandler("C:\\Users\\Msi\\Desktop\\investmentapp\\logs\\error.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

class SimulationTab:
    """Klasa obsługująca zakładkę Symulacje w GUI."""

    def __init__(self, frame):
        try:
            logging.info("Initializing SimulationTab")
            self.frame = frame
            self.strategy_data = StrategyData()
            self.error_handler = ErrorHandler()
            self.progress_label = tk.Label(self.frame, text="")
            self.progress_label.pack(pady=5)
            
            self.tree = ttk.Treeview(self.frame, columns=(
                "Nazwa", "Symbol", "Profit", "Max DD%", "Liczba transakcji"
            ), show="headings")
            self.tree.heading("Nazwa", text="Nazwa")
            self.tree.heading("Symbol", text="Symbol")
            self.tree.heading("Profit", text="Profit")
            self.tree.heading("Max DD%", text="Max DD%")
            self.tree.heading("Liczba transakcji", text="Liczba transakcji")
            for col in self.tree["columns"]:
                self.tree.column(col, width=100, anchor="center")
            self.tree.pack(pady=10, fill="both", expand=True)
            
            self.update_strategies_display()
            self.frame.after(5000, self.periodic_refresh)
            logging.info("SimulationTab initialized")
        except Exception as e:
            self.error_handler.log_and_show_error(self.frame, "Initializing SimulationTab", f"Error initializing SimulationTab: {str(e)}")

    def update_strategies_display(self):
        """Aktualizuje tabelę strategii w zakładce Symulacje."""
        try:
            logging.info("Starting update of simulation strategies table")
            # Bezpieczne usuwanie elementów
            items = list(self.tree.get_children())
            for item in items:
                if self.tree.exists(item):
                    self.tree.delete(item)
            
            strategies = self.strategy_data.load_strategies()
            for strategy in strategies:
                if strategy["mode"] in ["Paper", "Auto"]:
                    summary_file = Path(__file__).resolve().parents[3] / "paper" / strategy["name"] / strategy["symbol"].replace("/", "_") / "summary.json"
                    if summary_file.exists():
                        try:
                            with open(summary_file, "r", encoding="utf-8") as f:
                                summary = json.load(f)
                            self.tree.insert("", tk.END, values=(
                                strategy["name"],
                                strategy["symbol"],
                                f"{summary.get('net_profit_usd', 0):.2f}",
                                f"{summary.get('max_drawdown_usd', 0):.2f}",
                                summary.get("total_trades", 0)
                            ))
                        except json.JSONDecodeError as e:
                            self.error_handler.log_and_show_error(self.frame, "Loading summary.json", f"Invalid JSON in {summary_file}: {str(e)}")
                    else:
                        logging.debug(f"No summary.json for strategy {strategy['name']} on {strategy['symbol']}, skipping")
                        self.tree.insert("", tk.END, values=(
                            strategy["name"],
                            strategy["symbol"],
                            "0.00",
                            "0.00",
                            0
                        ))
            logging.info(f"Simulation strategies table updated, strategies: {[s['name'] + '_' + s['symbol'] for s in strategies if s['mode'] in ['Paper', 'Auto']]}")
        except Exception as e:
            self.error_handler.log_and_show_error(self.frame, "Updating simulation strategies table", f"Error updating simulation strategies table: {str(e)}")

    def _refresh_results(self, results):
        """Odświeża wyniki w tabeli."""
        try:
            for result in results:
                strategy_name = result.get("strategy")
                symbol = result.get("symbol")
                summary_file = Path(__file__).resolve().parents[3] / "paper" / strategy_name / symbol.replace("/", "_") / "summary.json"
                summary_file.parent.mkdir(parents=True, exist_ok=True)
                with open(summary_file, "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=2)
                logging.info(f"Updated summary.json for strategy {strategy_name} on {symbol}")
            self.update_strategies_display()
        except Exception as e:
            self.error_handler.log_and_show_error(self.frame, "Refreshing simulation results", f"Error refreshing simulation results: {str(e)}")

    def periodic_refresh(self):
        """Planuje okresowe odświeżanie tabeli."""
        try:
            if not self.frame.winfo_exists():
                logging.debug("Simulation frame destroyed, stopping periodic refresh")
                return
            self.update_strategies_display()
            self.frame.after(5000, self.periodic_refresh)
            logging.debug("Scheduled periodic refresh for Simulation table")
        except Exception as e:
            self.error_handler.log_and_show_error(self.frame, "Scheduling periodic refresh", f"Error scheduling periodic refresh: {str(e)}")