# -*- coding: utf-8 -*-
# Ścieżka: C:\Users\Msi\Desktop\investmentapp\src\core\main.py
import tkinter as tk
from tkinter import ttk
import logging
import sys
import json
import traceback
from src.tabs.czacha import CzachaTab
from src.tabs.strategies.strategies_gui import StrategiesTab
from src.tabs.promotion import PromotionTab
from src.tabs.symbols import SymbolsTab
from src.tabs.api import ApiTab
from src.tabs.simulation.simulation import SimulationTab
from src.tabs.live.live_tab import LiveTab
from src.tabs.czacha_data import CzachaData
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(module)s | %(message)s",
    handlers=[
        logging.FileHandler("C:\\Users\\Msi\\Desktop\\investmentapp\\logs\\app.log", encoding="utf-8"),
        logging.FileHandler("C:\\Users\\Msi\\Desktop\\investmentapp\\logs\\error.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

class InvestmentApp:
    def __init__(self, root):
        try:
            logging.info("=== Initializing InvestmentApp ===")
            self.root = root
            self.root.title("Investment App")
            self.root.geometry("800x600")
            self.root.resizable(True, True)
            
            self.notebook = ttk.Notebook(self.root)
            self.notebook.pack(fill="both", expand=True)
            
            czacha_frame = tk.Frame(self.notebook)
            symbols_frame = tk.Frame(self.notebook)
            simulation_frame = tk.Frame(self.notebook)
            strategies_frame = tk.Frame(self.notebook)
            promotion_frame = tk.Frame(self.notebook)
            api_frame = tk.Frame(self.notebook)
            live_frame = tk.Frame(self.notebook)
            
            self.czacha_data = CzachaData()
            self.czacha_tab = CzachaTab(czacha_frame)
            self.symbols_tab = SymbolsTab(symbols_frame)
            self.simulation_tab = SimulationTab(simulation_frame)
            self.strategies_tab = StrategiesTab(strategies_frame, self.symbols_tab, self.simulation_tab)
            self.promotion_tab = PromotionTab(promotion_frame)
            self.api_tab = ApiTab(api_frame)
            self.live_tab = LiveTab(live_frame)
            
            self.notebook.add(czacha_frame, text="Czacha")
            self.notebook.add(strategies_frame, text="Strategie")
            self.notebook.add(promotion_frame, text="Awans")
            self.notebook.add(symbols_frame, text="Symbole")
            self.notebook.add(api_frame, text="API")
            self.notebook.add(simulation_frame, text="Symulacje")
            self.notebook.add(live_frame, text="Live")
            
            self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)
            
            self.check_promotion()
            
            logging.info("=== InvestmentApp initialized ===")
        except Exception as e:
            logging.error(f"Error initializing InvestmentApp: {str(e)}", exc_info=True)
            self.show_error("Error", f"Błąd podczas inicjalizacji aplikacji: {str(e)}\nTraceback: {traceback.format_exc()}")
            raise

    def show_error(self, title, message):
        logging.error(f"{title}: {message}", exc_info=True)
        tk.Label(self.root, text=f"Błąd: {message}", fg="red").pack()

    def on_tab_change(self, event):
        try:
            selected_tab = event.widget.tab(event.widget.select(), "text")
            logging.info(f"Tab changed to: {selected_tab}")
        except Exception as e:
            logging.error(f"Error changing tab: {str(e)}", exc_info=True)
            self.show_error("Error changing tab", f"Error changing tab: {str(e)}")

    def check_promotion(self):
        try:
            promotion_file = Path(__file__).resolve().parents[2] / "data" / "promotion.json"
            if promotion_file.exists():
                with open(promotion_file, "r", encoding="utf-8") as f:
                    promotion_data = json.load(f)
                days = promotion_data.get("days", 30.0)
                
                strategies_file = Path(__file__).resolve().parents[2] / "data" / "strategies.json"
                if strategies_file.exists():
                    with open(strategies_file, "r", encoding="utf-8") as f:
                        strategies = json.load(f)
                    for strategy in strategies:
                        if strategy["mode"] in ["Symulacja", "Auto"]:
                            self.czacha_data.update_simulation_results(strategy["name"], strategy.get("symbol", ""))
                
                self.root.after(int(days * 24 * 60 * 60 * 1000), self.check_promotion)
                logging.info(f"Scheduled promotion check in {days} days")
        except Exception as e:
            logging.error(f"Error in promotion check: {str(e)}", exc_info=True)
            self.show_error("Error in promotion check", f"Error in promotion check: {str(e)}")
            self.root.after(60000, self.check_promotion)

def main():
    try:
        logging.info("=== Starting application ===")
        root = tk.Tk()
        app = InvestmentApp(root)
        logging.info("=== Starting main application loop ===")
        root.mainloop()
        logging.info("=== Closing application ===")
        logging.info("=== Application closed ===")
    except Exception as e:
        logging.error(f"Error running application: {str(e)}", exc_info=True)
        logging.info("=== Application terminated ===")
        raise

if __name__ == "__main__":
    try:
        logging.info("=== Logging initialized ===")
        logging.info("Successfully imported all tabs")
        main()
    except Exception as e:
        logging.error(f"Error starting application: {str(e)}", exc_info=True)
        raise