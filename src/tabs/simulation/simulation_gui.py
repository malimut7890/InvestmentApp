# -*- coding: utf-8 -*-
# Ścieżka: C:\Users\Msi\Desktop\investmentapp\src\tabs\simulation\simulation_gui.py

import tkinter as tk
from tkinter import ttk
import json
import logging
from pathlib import Path
from src.core.error_handler import ErrorHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("C:\\Users\\Msi\\Desktop\\investmentapp\\logs\\app.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

class SimulationTab:
    """Klasa obsługująca zakładkę Symulacje w GUI."""

    def __init__(self, notebook):
        self.frame = ttk.Frame(notebook)
        self.strategies_file = Path(__file__).resolve().parents[3] / "data" / "strategies.json"
        self.error_handler = ErrorHandler()
        self.setup_ui()
        self.update_strategies_display()

    def setup_ui(self):
        """Konfiguruje interfejs użytkownika zakładki."""
        # Strategy results table
        self.tree = ttk.Treeview(self.frame, columns=(
            "Name", "Symbol", "Active Days", "Total Trades", "Total Transactions",
            "Win Rate %", "Avg Profit %", "Max DD %", "Profit Factor", "Profit %", "Total Profit"
        ), show="headings")
        self.tree.heading("Name", text="Strategia")
        self.tree.heading("Symbol", text="Symbol")
        self.tree.heading("Active Days", text="Dni aktywności")
        self.tree.heading("Total Trades", text="Liczba transakcji zamkniętych")
        self.tree.heading("Total Transactions", text="Liczba wszystkich pozycji")
        self.tree.heading("Win Rate %", text="Win Rate %")
        self.tree.heading("Avg Profit %", text="Śr. zysk %")
        self.tree.heading("Max DD %", text="Max DD %")
        self.tree.heading("Profit Factor", text="Profit Factor")
        self.tree.heading("Profit %", text="Zysk %")
        self.tree.heading("Total Profit", text="Całkowity zysk")
        for col in self.tree["columns"]:
            self.tree.column(col, width=100, anchor="center")
        self.tree.pack(pady=10, fill="both", expand=True)
        
        # Refresh button
        ttk.Button(self.frame, text="Odśwież", command=self.update_strategies_display).pack(pady=5)
        
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)
        
        # Schedule periodic refresh
        self.frame.after(5000, self.periodic_refresh)

    def load_strategies(self):
        """Ładuje strategie z pliku strategies.json."""
        try:
            if not self.strategies_file.exists():
                logging.info("No strategies.json file, returning empty list")
                return []
            with open(self.strategies_file, "r", encoding="utf-8-sig") as f:
                strategies = json.load(f)
            logging.info(f"Loaded strategies: {[s['name'] for s in strategies]}")
            return strategies
        except Exception as e:
            self.error_handler.log_and_show_error(self.frame, "Loading strategies", f"Error loading strategies: {str(e)}")
            return []

    def update_strategies_display(self):
        """Aktualizuje tabelę strategii w GUI."""
        try:
            logging.info("Starting update of simulation strategies table")
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            strategies = self.load_strategies()
            for strategy in strategies:
                strategy_name = strategy["name"]
                symbol = strategy.get("symbol", "")
                if not symbol:
                    continue
                
                for mode in ["paper", "live"]:
                    summary_file = Path(__file__).resolve().parents[3] / mode / strategy_name / symbol.replace('/', '_') / "summary.json"
                    if summary_file.exists():
                        try:
                            with open(summary_file, "r", encoding="utf-8-sig") as f:
                                summary = json.load(f)
                            self.tree.insert("", tk.END, values=(
                                strategy_name,
                                summary.get("symbol", symbol),
                                summary.get("days_active", 0),
                                summary.get("total_trades", 0),
                                summary.get("total_transactions", 0),
                                f"{summary.get('winrate_pct', 0):.2f}",
                                f"{summary.get('avg_profit_percentage', 0):.2f}",
                                f"{summary.get('max_drawdown_usd', 0):.2f}",
                                f"{summary.get('profit_factor', float('inf')):.2f}",
                                f"{summary.get('profit_percentage', 0):.2f}",
                                f"{summary.get('net_profit_usd', 0):.2f}"
                            ))
                            logging.info(f"Loaded summary data for {strategy_name} on {symbol} from {summary_file}")
                        except Exception as e:
                            self.error_handler.log_error("Loading summary.json", f"Error loading summary.json for {strategy_name} on {symbol}: {str(e)}")
                    else:
                        logging.info(f"No summary.json found for {strategy_name} on {symbol} in {mode}")
                        self.tree.insert("", tk.END, values=(
                            strategy_name,
                            symbol,
                            0, 0, 0, "0.00", "0.00", "0.00", "0.00", "0.00", "0.00"
                        ))
            
            logging.info("Simulation strategies table updated")
        except Exception as e:
            self.error_handler.log_and_show_error(self.frame, "Updating simulation strategies table", f"Error updating table: {str(e)}")

    def periodic_refresh(self):
        """Planuje okresowe odświeżanie tabeli."""
        try:
            self.update_strategies_display()
            self.frame.after(5000, self.periodic_refresh)
            logging.info("Scheduled periodic refresh for simulation table")
        except Exception as e:
            self.error_handler.log_and_show_error(self.frame, "Periodic refresh", f"Error in periodic refresh: {str(e)}")

    def _refresh_results(self, results):
        """Odświeża wyniki w tabeli."""
        try:
            logging.info("Refreshing simulation results")
            self.update_strategies_display()
        except Exception as e:
            self.error_handler.log_and_show_error(self.frame, "Refreshing simulation results", f"Error refreshing results: {str(e)}")