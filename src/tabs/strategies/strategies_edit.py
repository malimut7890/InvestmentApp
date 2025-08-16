# -*- coding: utf-8 -*-
# Ścieżka: C:\Users\Msi\Desktop\investmentapp\src\tabs\strategies\strategies_edit.py
import tkinter as tk
from tkinter import ttk
import importlib.util
import sys
import logging
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("C:\\Users\\Msi\\Desktop\\investmentapp\\logs\\app.log", encoding="utf-8"),
        logging.FileHandler("C:\\Users\\Msi\\Desktop\\investmentapp\\logs\\error.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

def edit_strategy(tab, strategy_idx):
    """Otwiera okno edycji podwskaźników strategii"""
    try:
        strategy = tab.strategies[strategy_idx]
        spec = importlib.util.spec_from_file_location(strategy["name"], strategy["file_path"])
        if spec is None:
            logging.error(f"Nieprawidłowy plik strategii: {strategy['file_path']}")
            tab.progress_label.config(text=f"Błąd: Nieprawidłowy plik strategii {strategy['name']}")
            return
        module = importlib.util.module_from_spec(spec)
        sys.modules[strategy["name"]] = module
        try:
            spec.loader.exec_module(module)
        except Exception as e:
            logging.error(f"Błąd kompilacji pliku strategii {strategy['file_path']}: {str(e)}")
            tab.progress_label.config(text=f"Błąd: Kompilacja pliku strategii {strategy['name']} nie powiodła się")
            return
        strategy_class = getattr(module, "Strategy", None)
        if not strategy_class:
            logging.error(f"Brak klasy Strategy w {strategy['file_path']}")
            tab.progress_label.config(text=f"Błąd: Brak klasy Strategy w {strategy['name']}")
            return
        
        strategy_instance = strategy_class()
        indicators = strategy_instance.get_indicators(pd.DataFrame())
        if not isinstance(indicators, list) or not indicators or not isinstance(indicators[0], dict):
            logging.error(f"Metoda get_indicators w {strategy['name']} nie zwraca listy słowników")
            tab.progress_label.config(text=f"Błąd: Nieprawidłowy format wskaźników dla {strategy['name']}")
            return
        
        edit_window = tk.Toplevel(tab.frame)
        edit_window.title(f"Edytuj strategię: {strategy['name']}")
        edit_window.geometry("400x500")
        edit_window.transient(tab.frame)
        edit_window.grab_set()
        
        canvas = tk.Canvas(edit_window)
        scrollbar = ttk.Scrollbar(edit_window, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        entries = {}
        current_parameters = strategy.get("parameters", {})
        for i, (ind_name, ind_value) in enumerate(indicators[0].items()):
            tk.Label(scrollable_frame, text=f"{ind_name}:").grid(row=i, column=0, padx=5, pady=5, sticky="e")
            entry = ttk.Entry(scrollable_frame)
            entry.insert(0, str(current_parameters.get(ind_name, ind_value)))
            entry.grid(row=i, column=1, padx=5, pady=5)
            entries[ind_name] = entry
        
        def save_changes():
            try:
                new_indicators = {}
                for name, entry in entries.items():
                    try:
                        value = entry.get()
                        new_indicators[name] = float(value) if value.replace(".", "").isdigit() else value
                    except ValueError:
                        logging.error(f"Invalid value for indicator {name}: {value}")
                        tab.progress_label.config(text=f"Błąd: Nieprawidłowa wartość dla {name}")
                        return
                strategy_instance.update_indicators(new_indicators)
                tab.strategy_data.update_strategy_parameters(strategy["name"], new_indicators, strategy["symbol"])
                logging.info(f"Podwskaźniki zapisane dla strategii {strategy['name']}: {new_indicators}")
                edit_window.destroy()
                tab.progress_label.config(text=f"Zapisano parametry dla strategii {strategy['name']}")
                tab.update_strategies_display()
            except Exception as e:
                logging.error(f"Błąd zapisu podwskaźników: {str(e)}")
                tab.progress_label.config(text=f"Błąd: Nie udało się zapisać parametrów strategii {strategy['name']}")
        
        ttk.Button(scrollable_frame, text="Zapisz", command=save_changes).grid(row=len(indicators[0]), column=0, columnspan=2, pady=10)
        ttk.Button(scrollable_frame, text="Anuluj", command=edit_window.destroy).grid(row=len(indicators[0]) + 1, column=0, columnspan=2, pady=10)
    except Exception as e:
        logging.error(f"Błąd edycji strategii {strategy['name'] if 'strategy' in locals() else 'unknown'}: {str(e)}")
        tab.progress_label.config(text=f"Błąd: Edycja strategii nie powiodła się")