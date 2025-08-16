# -*- coding: utf-8 -*-
# Ścieżka: C:\Users\Msi\Desktop\investmentapp\src\tabs\strategies\strategies_gui.py
import tkinter as tk
from tkinter import ttk
import logging
from src.tabs.strategies.strategies_data import StrategyData
from src.tabs.strategies.strategies_logic import import_strategy
from src.tabs.strategies.strategies_gui_simulation import StrategiesTabSimulation
from src.tabs.strategies.strategies_gui_backtest import StrategiesTabBacktest
from src.tabs.strategies.strategies_gui_handlers import StrategiesGuiHandlers
from src.core.trade_manager_simulation import TradeManagerSimulation
from src.core.trade_manager_live import TradeManagerLive
from src.tabs.symbols import SymbolsTab
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("C:\\Users\\Msi\\Desktop\\investmentapp\\logs\\app.log", encoding="utf-8"),
        logging.FileHandler("C:\\Users\\Msi\\Desktop\\investmentapp\\logs\\error.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

class StrategiesTab:
    def __init__(self, frame, symbols_tab: SymbolsTab, simulation_tab):
        try:
            logging.info("=== Initializing StrategiesTab ===")
            self.frame = frame
            self.symbols_tab = symbols_tab
            self.simulation_tab = simulation_tab
            self.strategy_data = StrategyData()
            self.trade_manager_simulation = TradeManagerSimulation()
            self.trade_manager_live = TradeManagerLive()
            
            # Progress label
            self.progress_label = tk.Label(self.frame, text="")
            self.progress_label.pack(pady=5)
            
            # Strategy table
            self.tree = ttk.Treeview(self.frame, columns=(
                "Nazwa", "Tryb", "Symbol", "Interwał", "Giełda", "Edytuj", "Backtest", "Symulacja", "Usuń"
            ), show="headings")
            self.tree.heading("Nazwa", text="Nazwa")
            self.tree.heading("Tryb", text="Tryb")
            self.tree.heading("Symbol", text="Symbol")
            self.tree.heading("Interwał", text="Interwał")
            self.tree.heading("Giełda", text="Giełda")
            self.tree.heading("Edytuj", text="Edytuj")
            self.tree.heading("Backtest", text="Backtest")
            self.tree.heading("Symulacja", text="Symulacja")
            self.tree.heading("Usuń", text="Usuń")
            for col in self.tree["columns"]:
                self.tree.column(col, width=100, anchor="center")
            
            # Style for editable fields
            style = ttk.Style()
            style.configure("Editable.Treeview", background="#E0FFE0")
            self.tree.pack(pady=10, fill="both", expand=True)
            
            # Initialize helper classes
            self.simulation_handler = StrategiesTabSimulation(self.frame, self.symbols_tab, self.simulation_tab, self.strategy_data, self.trade_manager_simulation)
            self.backtest_handler = StrategiesTabBacktest(self.frame, self.symbols_tab, self.strategy_data)
            self.handlers = StrategiesGuiHandlers(self.frame, self.tree, self.strategy_data, self.symbols_tab, self.simulation_tab, self.progress_label)
            
            # Import button
            ttk.Button(self.frame, text="Import", command=self.import_strategy_wrapper).pack(pady=5)
            
            # Export results button
            ttk.Button(self.frame, text="Eksportuj wyniki do CSV", command=self.backtest_handler.export_backtest_to_csv).pack(pady=5)
            
            # Historical simulation button
            ttk.Button(self.frame, text="Uruchom symulację historyczną", command=self.simulation_handler.run_historical_simulation).pack(pady=5)
            
            # Clear strategy data button
            ttk.Button(self.frame, text="Wyczyść dane strategii", command=self.handlers.clear_strategy_data).pack(pady=5)
            
            self.tree.bind("<Double-1>", self.handlers.on_tree_double_click)
            
            self.handlers.update_strategies_display()
            logging.info("=== StrategiesTab initialized ===")
        except Exception as e:
            logging.error(f"Error initializing StrategiesTab: {str(e)}", exc_info=True)
            self.progress_label.config(text=f"Błąd: {str(e)}")
            raise

    def import_strategy_wrapper(self):
        try:
            logging.info("=== Called import strategy from GUI ===")
            import_strategy(self)
            self.handlers.exchanges = self.handlers.load_exchanges()
            self.handlers.update_strategies_display()
            logging.info("=== Completed strategy import and refreshed table ===")
        except Exception as e:
            logging.error(f"Error importing strategy from GUI: {str(e)}", exc_info=True)
            self.progress_label.config(text=f"Błąd podczas importowania strategii: {str(e)}")
            raise