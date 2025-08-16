# -*- coding: utf-8 -*-
# Path: C:\Users\Msi\Desktop\investmentapp\src\tabs\strategies\strategies_logic.py
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import logging
import json
import importlib.util
from pathlib import Path
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

def import_strategy(strategies_tab):
    try:
        logging.info("Opening file dialog for strategy import")
        file_path = filedialog.askopenfilename(
            filetypes=[("Python files", "*.py")],
            initialdir=Path(__file__).resolve().parents[3] / "strategies"
        )
        if not file_path:
            logging.info("No file selected for strategy import")
            return
        
        file_path = Path(file_path)
        strategy_name = file_path.stem
        logging.info(f"Selected strategy file: {file_path}, strategy name: {strategy_name}")
        
        # Validate strategy file
        spec = importlib.util.spec_from_file_location(strategy_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        if not hasattr(module, "Strategy"):
            logging.error(f"Strategy file {file_path} does not contain a 'Strategy' class")
            messagebox.showerror("Error", "Wybrany plik nie zawiera klasy 'Strategy'")
            return
        
        strategy = module.Strategy()
        if not hasattr(strategy, "get_signal") or not hasattr(strategy, "get_indicators"):
            logging.error(f"Strategy class in {file_path} missing required methods: get_signal or get_indicators")
            messagebox.showerror("Error", "Klasa 'Strategy' musi zawierać metody 'get_signal' i 'get_indicators'")
            return
        
        # Create strategy configuration window
        config_window = tk.Toplevel(strategies_tab.frame)
        config_window.title(f"Configure Strategy: {strategy_name}")
        config_window.geometry("400x500")
        
        tk.Label(config_window, text="Symbol:").pack(pady=5)
        symbol_var = tk.StringVar(value=strategies_tab.symbols_tab.get_active_symbols()[0] if strategies_tab.symbols_tab.get_active_symbols() else "")
        symbol_combo = ttk.Combobox(config_window, textvariable=symbol_var, values=strategies_tab.symbols_tab.get_active_symbols(), state="readonly")
        symbol_combo.pack(pady=5)
        
        tk.Label(config_window, text="Interval:").pack(pady=5)
        interval_var = tk.StringVar(value="1m")
        interval_combo = ttk.Combobox(config_window, textvariable=interval_var, values=["1m", "5m", "15m", "30m", "1h", "4h", "1d", "1w", "1mo"], state="readonly")
        interval_combo.pack(pady=5)
        
        tk.Label(config_window, text="Exchange:").pack(pady=5)
        exchange_var = tk.StringVar(value=strategies_tab.handlers.exchanges[0] if strategies_tab.handlers.exchanges else "MEXC")
        exchange_combo = ttk.Combobox(config_window, textvariable=exchange_var, values=strategies_tab.handlers.exchanges, state="readonly")
        exchange_combo.pack(pady=5)
        
        tk.Label(config_window, text="Parameters:").pack(pady=5)
        params_frame = ttk.Frame(config_window)
        params_frame.pack(pady=5)
        
        # Get default parameters from strategy
        default_parameters = getattr(strategy, "default_parameters", {})
        param_vars = {}
        for param, value in default_parameters.items():
            tk.Label(params_frame, text=f"{param}:").pack(pady=2)
            var = tk.StringVar(value=str(value))
            tk.Entry(params_frame, textvariable=var).pack(pady=2)
            param_vars[param] = var
        
        def save_imported_strategy():
            try:
                symbol = symbol_var.get()
                interval = interval_var.get()
                exchange = exchange_var.get()
                parameters = {key: var.get() for key, var in param_vars.items()}
                
                # Validate inputs
                if not symbol:
                    logging.error("No symbol selected for strategy import")
                    messagebox.showerror("Error", "Wybierz symbol")
                    return
                
                # Update or add strategy in strategies.json
                strategies = strategies_tab.strategy_data.load_strategies()
                for strategy in strategies:
                    if strategy["name"] == strategy_name and strategy["symbol"] == symbol:
                        strategy["interval"] = interval
                        strategy["exchange"] = exchange
                        strategy["parameters"] = parameters
                        strategy["file_path"] = str(file_path)
                        break
                else:
                    strategies.append({
                        "name": strategy_name,
                        "symbol": symbol,
                        "mode": "Wylaczona",
                        "interval": interval,
                        "exchange": exchange,
                        "parameters": parameters,
                        "file_path": str(file_path)
                    })
                strategies_tab.strategy_data.save_strategies(strategies)
                
                strategies_tab.handlers.update_strategies_display()
                config_window.destroy()
                logging.info(f"Imported strategy {strategy_name} with symbol {symbol}, interval {interval}, exchange {exchange}, parameters {parameters}")
                messagebox.showinfo("Success", f"Zaimportowano strategię {strategy_name}")
            except Exception as e:
                logging.error(f"Error importing strategy {strategy_name}: {str(e)}", exc_info=True)
                messagebox.showerror("Error", f"Błąd podczas importowania strategii: {str(e)}\nTraceback: {traceback.format_exc()}")
        
        ttk.Button(config_window, text="Save", command=save_imported_strategy).pack(pady=10)
        ttk.Button(config_window, text="Cancel", command=config_window.destroy).pack(pady=10)
        logging.info(f"Opened configuration window for strategy {strategy_name}")
    except Exception as e:
        logging.error(f"Error opening strategy import dialog: {str(e)}", exc_info=True)
        messagebox.showerror("Error", f"Błąd podczas otwierania dialogu importu: {str(e)}\nTraceback: {traceback.format_exc()}")