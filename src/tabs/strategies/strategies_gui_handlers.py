# -*- coding: utf-8 -*-
# Ścieżka: C:\Users\Msi\Desktop\investmentapp\src\tabs\strategies\strategies_gui_handlers.py

import tkinter as tk
from tkinter import ttk, filedialog
import logging
import json
from pathlib import Path
from src.tabs.strategies.strategies_data import StrategyData
from src.tabs.strategies.strategies_edit import edit_strategy
from src.tabs.strategies.strategies_backtest import run_backtest
from src.core.trade_manager_simulation import TradeManagerSimulation
from src.core.error_handler import ErrorHandler
import asyncio
import threading
import ccxt.async_support as ccxt
import shutil

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("C:\\Users\\Msi\\Desktop\\investmentapp\\logs\\app.log", encoding="utf-8"),
        logging.FileHandler("C:\\Users\\Msi\\Desktop\\investmentapp\\logs\\error.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

class StrategiesGuiHandlers:
    """Klasa obsługująca interakcje GUI dla zakładki Strategie."""

    def __init__(self, frame, tree, strategy_data, symbols_tab, simulation_tab, progress_label):
        try:
            logging.info("Initializing StrategiesGuiHandlers")
            self.frame = frame
            self.tree = tree
            self.strategy_data = strategy_data
            self.symbols_tab = symbols_tab
            self.simulation_tab = simulation_tab
            self.progress_label = progress_label
            self.strategies = self.strategy_data.load_strategies()
            self.loop = asyncio.get_event_loop()
            self.trade_manager = TradeManagerSimulation()
            self.simulation_tasks = {}
            self.exchanges = self.load_exchanges()
            self.error_handler = ErrorHandler()
            logging.info("StrategiesGuiHandlers initialized")
        except Exception as e:
            self.error_handler.log_and_show_error(self.frame, "Initializing StrategiesGuiHandlers", f"Błąd podczas inicjalizacji: {str(e)}")

    def load_exchanges(self):
        """Ładuje listę dostępnych giełd z api_keys.json."""
        try:
            api_keys_file = Path(__file__).resolve().parents[3] / "data" / "api_keys.json"
            if api_keys_file.exists():
                with open(api_keys_file, "r", encoding="utf-8-sig") as f:
                    api_keys = json.load(f)
                exchanges = [key["exchange"].upper() for key in api_keys if isinstance(key, dict) and "exchange" in key]
                exchanges = list(set(exchanges))
                logging.info(f"Loaded exchanges: {exchanges}")
                return exchanges if exchanges else ["MEXC"]
            logging.info("No api_keys.json file, default exchange: MEXC")
            return ["MEXC"]
        except Exception as e:
            self.error_handler.log_error("Loading exchanges", f"Error loading exchanges from api_keys.json: {str(e)}")
            return ["MEXC"]

    def update_strategies_display(self):
        """Aktualizuje tabelę strategii w GUI."""
        try:
            logging.info("Starting update of strategies table")
            for item in self.tree.get_children():
                self.tree.delete(item)
            self.strategies = self.strategy_data.load_strategies()
            logging.info(f"Loaded strategies for display: {[s['name'] for s in self.strategies]}")
            data_summary_file = Path(__file__).resolve().parents[3] / "data" / "summary.json"
            if data_summary_file.exists():
                try:
                    with open(data_summary_file, "r", encoding="utf-8-sig") as f:
                        summary_data = json.load(f)
                    if isinstance(summary_data, list):
                        valid_strategies = {f"{s['name']}_{s['symbol']}" for s in self.strategies}
                        summary_data = [s for s in summary_data if f"{s.get('strategy')}_{s.get('symbol')}" in valid_strategies]
                        with open(data_summary_file, "w", encoding="utf-8") as f:
                            json.dump(summary_data, f, indent=2)
                        logging.info("Updated summary.json to remove outdated strategy or symbol entries")
                    elif isinstance(summary_data, dict):
                        strategy_names = {s["name"] for s in self.strategies}
                        symbol_names = {s["symbol"] for s in self.strategies}
                        if summary_data.get("strategy") not in strategy_names or summary_data.get("symbol") not in symbol_names:
                            data_summary_file.unlink(missing_ok=True)
                            logging.info("Cleared outdated summary.json in data folder")
                except json.JSONDecodeError as e:
                    self.error_handler.log_error("Updating summary.json", f"Invalid JSON in summary.json: {str(e)}")
                    data_summary_file.unlink(missing_ok=True)
                    logging.info("Removed corrupted summary.json")
            for strategy in self.strategies:
                mode = strategy.get("mode", "Wylaczona")
                strategy_key = f"{strategy['name']}_{strategy['symbol']}"
                mode_display = f"{mode} (aktywna)" if mode in ["Paper", "Auto"] and strategy_key in self.simulation_tasks else mode
                tags = ("editable",) if self.tree["columns"].index("Tryb") in [1, 2, 3, 4] else ()
                self.tree.insert("", tk.END, values=(
                    strategy["name"],
                    mode_display,
                    strategy["symbol"],
                    strategy.get("interval", "1m"),
                    strategy.get("exchange", "MEXC").upper(),
                    "Edytuj",
                    "Backtest",
                    "Paper Trading",
                    "Usuń"
                ), tags=(strategy_key, tags))
            logging.info(f"Strategies table updated, strategies: {[s['name'] for s in self.strategies]}")
        except Exception as e:
            self.error_handler.log_and_show_error(self.frame, "Updating strategies table", f"Błąd podczas aktualizacji tabeli: {str(e)}")

    def clear_strategy_data(self):
        """Otwiera okno do czyszczenia danych strategii."""
        try:
            edit_window = tk.Toplevel(self.frame)
            edit_window.title("Wyczyść dane strategii")
            edit_window.geometry("300x150")
            
            tk.Label(edit_window, text="Wybierz strategię:").pack(pady=5)
            strategy_var = tk.StringVar(value=self.strategies[0]["name"] if self.strategies else "")
            strategy_combo = ttk.Combobox(edit_window, textvariable=strategy_var, values=[s["name"] for s in self.strategies], state="readonly")
            strategy_combo.pack(pady=5)
            
            def clear_action():
                try:
                    strategy_name = strategy_var.get()
                    if not strategy_name:
                        self.error_handler.log_and_show_error(self.frame, "Clearing strategy data", "Nie wybrano strategii")
                        return
                    for strategy in self.strategies:
                        if strategy["name"] == strategy_name:
                            strategy_key = f"{strategy['name']}_{strategy['symbol']}"
                            if strategy_key in self.simulation_tasks:
                                task = self.simulation_tasks.pop(strategy_key)
                                task.cancel()
                                logging.info(f"Cancelled simulation task for strategy {strategy_key}")
                    for mode in ["paper", "live"]:
                        strategy_dir = Path(__file__).resolve().parents[3] / mode / strategy_name
                        shutil.rmtree(strategy_dir, ignore_errors=True)
                        logging.info(f"Cleared {mode} data for strategy {strategy_name}")
                    data_summary_file = Path(__file__).resolve().parents[3] / "data" / "summary.json"
                    if data_summary_file.exists():
                        try:
                            with open(data_summary_file, "r", encoding="utf-8-sig") as f:
                                summary_data = json.load(f)
                            if isinstance(summary_data, dict) and summary_data.get("strategy") == strategy_name:
                                data_summary_file.unlink(missing_ok=True)
                                logging.info(f"Cleared summary.json for strategy {strategy_name} in data folder")
                            elif isinstance(summary_data, list):
                                summary_data = [s for s in summary_data if s.get("strategy") != strategy_name]
                                with open(data_summary_file, "w", encoding="utf-8") as f:
                                    json.dump(summary_data, f, indent=2)
                                logging.info(f"Updated summary.json by removing {strategy_name} in data folder")
                        except json.JSONDecodeError as e:
                            self.error_handler.log_error("Clearing summary.json", f"Invalid JSON in summary.json: {str(e)}")
                            data_summary_file.unlink(missing_ok=True)
                            logging.info(f"Removed corrupted summary.json for {strategy_name}")
                    self.simulation_tab.update_strategies_display()
                    self.update_strategies_display()
                    self.progress_label.config(text=f"Wyczyszczono dane dla strategii {strategy_name}")
                    edit_window.destroy()
                except Exception as e:
                    self.error_handler.log_and_show_error(self.frame, "Clearing strategy data", f"Błąd podczas czyszczenia danych: {str(e)}")
            
            ttk.Button(edit_window, text="Wyczyść dane", command=clear_action).pack(pady=10)
            ttk.Button(edit_window, text="Zamknij", command=edit_window.destroy).pack(pady=10)
            logging.info("Opened clear strategy data window")
        except Exception as e:
            self.error_handler.log_and_show_error(self.frame, "Opening clear strategy data window", f"Błąd podczas otwierania okna czyszczenia: {str(e)}")

    def on_tree_double_click(self, event):
        """Obsługuje podwójne kliknięcie w tabelę strategii."""
        try:
            logging.info("Double-click in StrategiesTab table")
            item = self.tree.selection()
            if not item:
                logging.info("No item selected in StrategiesTab table")
                return
            item = item[0]
            col = self.tree.identify_column(event.x)
            col_index = int(col.replace("#", "")) - 1
            col_name = self.tree["columns"][col_index]
            strategy_name = self.tree.item(item, "values")[0]
            symbol = self.tree.item(item, "values")[2]
            logging.info(f"Double-click on strategy {strategy_name}, symbol {symbol}, column {col}")
            
            strategy = next((s for s in self.strategies if s["name"] == strategy_name and s["symbol"] == symbol), None)
            file_path = strategy.get("file_path") if strategy else None
            
            edit_window = None
            if col_name == "Tryb":
                edit_window = tk.Toplevel(self.frame)
                edit_window.title(f"Edytuj tryb dla {strategy_name}")
                edit_window.geometry("300x200")
                tk.Label(edit_window, text="Tryb:").pack(pady=5)
                mode_var = tk.StringVar(value=self.tree.item(item, "values")[1].replace(" (aktywna)", ""))
                mode_combo = ttk.Combobox(edit_window, textvariable=mode_var, values=["Wylaczona", "Live", "Paper", "Auto"], state="readonly")
                mode_combo.pack(pady=5)
                
                def check_ohlc_data():
                    try:
                        if not strategy:
                            raise ValueError(f"Strategy {strategy_name} with symbol {symbol} not found")
                        exchange_name = strategy.get("exchange", "MEXC").lower()
                        interval = strategy.get("interval", "1m")
                        
                        api_keys = self.trade_manager.load_api_keys()
                        api_key_data = next((key for key in api_keys if key["exchange"].lower() == exchange_name), None)
                        if not api_key_data:
                            raise ValueError(f"No API key found for exchange {exchange_name}")
                        
                        exchange_class = getattr(ccxt, exchange_name)
                        exchange = exchange_class({
                            "apiKey": api_key_data["api_key"],
                            "secret": api_key_data["api_secret"],
                            "password": api_key_data.get("passphrase", ""),
                            "rateLimit": api_key_data.get("rate_limit_requests", 1800),
                            "timeout": api_key_data.get("timeout_seconds", 30) * 1000
                        })
                        
                        async def fetch_ohlc():
                            try:
                                await exchange.fetch_ohlcv(symbol, interval, limit=10)
                                await exchange.close()
                                self.progress_label.config(text=f"Pobrano 10 świec OHLCV dla {symbol} na {interval}")
                            except Exception as error:
                                await exchange.close()
                                self.error_handler.log_and_show_error(self.frame, "Checking OHLC data", f"Nie udało się pobrać OHLCV: {str(error)}")
                        
                        asyncio.run_coroutine_threadsafe(fetch_ohlc(), self.loop)
                    except Exception as error:
                        self.error_handler.log_and_show_error(self.frame, f"Checking OHLC data for {strategy_name}", str(error))
                
                ttk.Button(edit_window, text="Sprawdź dane OHLC", command=check_ohlc_data).pack(pady=5)
                mode_combo.bind("<<ComboboxSelected>>", lambda e: self._on_mode_selected(strategy_name, symbol, mode_var.get(), edit_window))
                ttk.Button(edit_window, text="Zapisz", command=lambda: self._on_mode_selected(strategy_name, symbol, mode_var.get(), edit_window)).pack(pady=10)
                ttk.Button(edit_window, text="Anuluj", command=edit_window.destroy).pack(pady=10)
            
            elif col_name == "Symbol":
                edit_window = tk.Toplevel(self.frame)
                edit_window.title(f"Edytuj symbol dla {strategy_name}")
                edit_window.geometry("300x150")
                tk.Label(edit_window, text="Symbol:").pack(pady=5)
                symbol_var = tk.StringVar(value=symbol)
                active_symbols = self.symbols_tab.get_active_symbols()
                if not active_symbols:
                    self.error_handler.log_and_show_error(self.frame, "Editing symbol", f"Brak dostępnych symboli")
                    edit_window.destroy()
                    return
                ttk.Combobox(edit_window, textvariable=symbol_var, values=active_symbols, state="readonly").pack(pady=5)
                
                def save_symbol():
                    try:
                        new_symbol = symbol_var.get()
                        self._on_symbol_selected(strategy_name, symbol, new_symbol, edit_window)
                    except Exception as e:
                        self.error_handler.log_and_show_error(self.frame, "Saving symbol", f"Błąd podczas zapisywania symbolu: {str(e)}")
                
                ttk.Button(edit_window, text="Zapisz", command=save_symbol).pack(pady=10)
                ttk.Button(edit_window, text="Anuluj", command=edit_window.destroy).pack(pady=10)
            
            elif col_name == "Interwał":
                edit_window = tk.Toplevel(self.frame)
                edit_window.title(f"Edytuj interwał dla {strategy_name}")
                edit_window.geometry("300x150")
                tk.Label(edit_window, text="Interwał:").pack(pady=5)
                interval_var = tk.StringVar(value=self.tree.item(item, "values")[3])
                ttk.Combobox(edit_window, textvariable=interval_var, values=["1m", "5m", "15m", "1h", "4h", "1d"], state="readonly").pack(pady=5)
                
                def save_interval():
                    try:
                        new_interval = interval_var.get()
                        self._on_interval_selected(strategy_name, new_interval, edit_window)
                    except Exception as e:
                        self.error_handler.log_and_show_error(self.frame, "Saving interval", f"Błąd podczas zapisywania interwału: {str(e)}")
                
                ttk.Button(edit_window, text="Zapisz", command=save_interval).pack(pady=10)
                ttk.Button(edit_window, text="Anuluj", command=edit_window.destroy).pack(pady=10)
            
            elif col_name == "Giełda":
                edit_window = tk.Toplevel(self.frame)
                edit_window.title(f"Edytuj giełdę dla {strategy_name}")
                edit_window.geometry("300x150")
                tk.Label(edit_window, text="Giełda:").pack(pady=5)
                exchange_var = tk.StringVar(value=self.tree.item(item, "values")[4])
                ttk.Combobox(edit_window, textvariable=exchange_var, values=self.exchanges, state="readonly").pack(pady=5)
                
                def save_exchange():
                    try:
                        new_exchange = exchange_var.get()
                        self._on_exchange_selected(strategy_name, new_exchange, edit_window)
                    except Exception as e:
                        self.error_handler.log_and_show_error(self.frame, "Saving exchange", f"Błąd podczas zapisywania giełdy: {str(e)}")
                
                ttk.Button(edit_window, text="Zapisz", command=save_exchange).pack(pady=10)
                ttk.Button(edit_window, text="Anuluj", command=edit_window.destroy).pack(pady=10)
            
            elif col_name == "Edytuj":
                if not strategy:
                    self.error_handler.log_and_show_error(self.frame, "Editing strategy", f"Strategia {strategy_name} z symbolem {symbol} nie znaleziona")
                    return
                if not file_path:
                    self.error_handler.log_and_show_error(self.frame, "Editing strategy", f"Brak ścieżki do pliku dla strategii {strategy_name}")
                    return
                for child in self.frame.winfo_children():
                    if isinstance(child, tk.Toplevel) and child.title().startswith("Edytuj strategię"):
                        child.destroy()
                edit_window = tk.Toplevel(self.frame)
                strategy_idx = next(i for i, s in enumerate(self.strategies) if s["name"] == strategy_name and s["symbol"] == symbol)
                edit_strategy(self, strategy_idx)
                logging.info(f"Opened configuration window for strategy {strategy_name}")
            
            elif col_name == "Backtest":
                if not strategy:
                    self.error_handler.log_and_show_error(self.frame, "Running backtest", f"Strategia {strategy_name} z symbolem {symbol} nie znaleziona")
                    return
                if not file_path:
                    self.error_handler.log_and_show_error(self.frame, "Running backtest", f"Brak ścieżki do pliku dla strategii {strategy_name}")
                    return
                edit_window = tk.Toplevel(self.frame)
                edit_window.title(f"Backtest dla {strategy_name}")
                edit_window.geometry("600x400")
                edit_window.transient(self.frame)
                edit_window.grab_set()
                
                tk.Label(edit_window, text="Symbol:").pack(pady=5)
                symbol_var = tk.StringVar(value=symbol)
                active_symbols = self.symbols_tab.get_active_symbols()
                symbol_combo = ttk.Combobox(edit_window, textvariable=symbol_var, values=["Wszystkie"] + active_symbols, state="readonly")
                symbol_combo.pack(pady=5)
                
                tk.Label(edit_window, text="Okres (liczba świec):").pack(pady=5)
                period_var = tk.StringVar(value="8760")
                period_entry = ttk.Entry(edit_window, textvariable=period_var)
                period_entry.pack(pady=5)
                
                tk.Label(edit_window, text=f"Interwał: {strategy.get('interval', '1m')}").pack(pady=5)
                
                def run_backtest_action():
                    try:
                        selected_symbol = symbol_var.get()
                        try:
                            period = int(period_var.get())
                            if period < 1:
                                raise ValueError("Okres musi być większy niż 0")
                        except ValueError:
                            self.error_handler.log_and_show_error(self.frame, "Running backtest", "Okres musi być liczbą większą niż 0")
                            return
                        
                        if selected_symbol == "Wszystkie":
                            results = []
                            for s in active_symbols:
                                result = asyncio.run(run_backtest(strategy_name, s, period=period, interval=strategy.get("interval", "1m")))
                                results.append(result)
                                logging.info(f"Ran backtest for strategy {strategy_name} on symbol {s} with period {period}")
                            self.progress_label.config(text=f"Backtest dla {strategy_name} na wszystkich symbolach zakończony")
                        else:
                            result = asyncio.run(run_backtest(strategy_name, selected_symbol, period=period, interval=strategy.get("interval", "1m")))
                            logging.info(f"Ran backtest for strategy {strategy_name} on symbol {selected_symbol} with period {period}")
                            self.progress_label.config(text=f"Backtest dla {strategy_name} na {selected_symbol} zakończony")
                        edit_window.destroy()
                    except Exception as e:
                        self.error_handler.log_and_show_error(self.frame, "Running backtest", f"Błąd podczas backtestu: {str(e)}")
                
                ttk.Button(edit_window, text="Uruchom backtest", command=run_backtest_action).pack(pady=10)
                ttk.Button(edit_window, text="Zamknij", command=edit_window.destroy).pack(pady=10)
            
            elif col_name == "Paper Trading":
                if not strategy:
                    self.error_handler.log_and_show_error(self.frame, "Running paper trading", f"Strategia {strategy_name} z symbolem {symbol} nie znaleziona")
                    return
                edit_window = tk.Toplevel(self.frame)
                edit_window.title(f"Paper Trading dla {strategy_name}")
                edit_window.geometry("300x150")
                tk.Label(edit_window, text="Interwał:").pack(pady=5)
                interval_var = tk.StringVar(value=strategy.get("interval", "1h"))
                ttk.Combobox(edit_window, textvariable=interval_var, values=["1m", "5m", "15m", "1h", "4h", "1d"], state="readonly").pack(pady=5)
                
                def run_simulation():
                    try:
                        interval = interval_var.get()
                        self.progress_label.config(text=f"Uruchamianie paper trading dla {strategy_name}...")
                        self.strategy_data.update_strategy_mode(strategy_name, symbol, "Paper")
                        asyncio.run_coroutine_threadsafe(self.run_simulation(strategy_name, symbol, interval), self.loop)
                        edit_window.destroy()
                    except Exception as e:
                        self.error_handler.log_and_show_error(self.frame, "Running paper trading", f"Błąd podczas uruchamiania paper trading: {str(e)}")
                
                ttk.Button(edit_window, text="Uruchom", command=run_simulation).pack(pady=10)
                ttk.Button(edit_window, text="Anuluj", command=edit_window.destroy).pack(pady=10)
            
            elif col_name == "Usuń":
                if not strategy:
                    self.error_handler.log_and_show_error(self.frame, "Deleting strategy", f"Strategia {strategy_name} z symbolem {symbol} nie znaleziona")
                    return
                self.strategy_data.delete_strategy(strategy_name, symbol)
                self.strategies = self.strategy_data.load_strategies()
                self.update_strategies_display()
                self.progress_label.config(text=f"Usunięto strategię {strategy_name}")
                logging.info(f"Deleted strategy {strategy_name} with symbol {symbol}")
        except Exception as e:
            self.error_handler.log_and_show_error(self.frame, "Editing StrategiesTab table", f"Błąd podczas edycji tabeli: {str(e)}")

    def run_backtest_thread(self, strategy_name: str, symbol: str, interval: str):
        """Uruchamia backtest w osobnym wątku."""
        try:
            result = asyncio.run_coroutine_threadsafe(run_backtest(strategy_name, symbol, interval=interval), self.loop).result()
            self.progress_label.config(text=f"Backtest zakończony dla {strategy_name}")
            logging.info(f"Backtest completed for {strategy_name} on {symbol}")
        except Exception as e:
            self.error_handler.log_and_show_error(self.frame, "Running backtest", f"Błąd podczas backtestu: {str(e)}")

    async def run_simulation(self, strategy_name: str, symbol: str, interval: str):
        """Uruchamia symulację Paper Trading."""
        try:
            logging.info(f"Task scheduled for paper trading: {strategy_name} on {symbol}")
            result = await self.trade_manager.paper_trade(strategy_name, symbol, interval, mode="paper")
            self.simulation_tab._refresh_results([result])
            self.progress_label.config(text=f"Paper trading zakończone dla {strategy_name}")
            logging.info(f"Paper trading completed for {strategy_name} on {symbol}, task id: {id(asyncio.current_task())}")
        except Exception as e:
            self.error_handler.log_and_show_error(self.frame, "Running paper trading", f"Błąd paper trading: {str(e)}")

    def import_strategy(self):
        """Importuje nową strategię z pliku Python."""
        try:
            logging.info("=== Called import strategy from GUI ===")
            file_path = filedialog.askopenfilename(
                title="Wybierz plik strategii",
                filetypes=[("Python files", "*.py")]
            )
            if not file_path:
                logging.info("No file selected for strategy import")
                return
            
            strategy_name = Path(file_path).stem
            edit_window = tk.Toplevel(self.frame)
            edit_window.title(f"Konfiguracja strategii {strategy_name}")
            edit_window.geometry("400x300")
            
            tk.Label(edit_window, text="Symbol:").pack(pady=5)
            symbol_var = tk.StringVar()
            active_symbols = self.symbols_tab.get_active_symbols()
            ttk.Combobox(edit_window, textvariable=symbol_var, values=active_symbols, state="readonly").pack(pady=5)
            
            tk.Label(edit_window, text="Interwał:").pack(pady=5)
            interval_var = tk.StringVar(value="1m")
            ttk.Combobox(edit_window, textvariable=interval_var, values=["1m", "5m", "15m", "1h", "4h", "1d"], state="readonly").pack(pady=5)
            
            tk.Label(edit_window, text="Giełda:").pack(pady=5)
            exchange_var = tk.StringVar(value="MEXC")
            ttk.Combobox(edit_window, textvariable=exchange_var, values=self.exchanges, state="readonly").pack(pady=5)
            
            tk.Label(edit_window, text="Parametry (JSON):").pack(pady=5)
            params_text = tk.Text(edit_window, height=4, width=30)
            params_text.pack(pady=5)
            
            def save_strategy():
                try:
                    symbol = symbol_var.get()
                    interval = interval_var.get()
                    exchange = exchange_var.get()
                    params_str = params_text.get("1.0", tk.END).strip()
                    parameters = json.loads(params_str) if params_str else {}
                    
                    strategies = self.strategy_data.load_strategies()
                    strategies.append({
                        "name": strategy_name,
                        "symbol": symbol,
                        "mode": "Wylaczona",
                        "interval": interval,
                        "exchange": exchange,
                        "parameters": parameters,
                        "file_path": file_path
                    })
                    self.strategy_data.save_strategies(strategies)
                    
                    self.strategies = self.strategy_data.load_strategies()
                    self.update_strategies_display()
                    self.progress_label.config(text=f"Zaimportowano strategię {strategy_name}")
                    edit_window.destroy()
                    logging.info(f"Imported strategy {strategy_name} with symbol {symbol}, interval {interval}, exchange {exchange}, parameters {parameters}")
                except json.JSONDecodeError as e:
                    self.error_handler.log_and_show_error(self.frame, "Saving strategy", f"Nieprawidłowy format parametrów JSON: {str(e)}")
                except Exception as e:
                    self.error_handler.log_and_show_error(self.frame, "Saving strategy", f"Błąd podczas importowania strategii: {str(e)}")
            
            ttk.Button(edit_window, text="Zapisz", command=save_strategy).pack(pady=10)
            ttk.Button(edit_window, text="Anuluj", command=edit_window.destroy).pack(pady=10)
            logging.info(f"Selected strategy file: {file_path}, strategy name: {strategy_name}")
        except Exception as e:
            self.error_handler.log_and_show_error(self.frame, "Opening import dialog", f"Błąd podczas otwierania okna importu: {str(e)}")

    def _on_mode_selected(self, strategy_name: str, symbol: str, new_mode: str, window):
        """Obsługuje zmianę trybu strategii."""
        try:
            logging.info(f"Saving mode {new_mode} for strategy {strategy_name} with symbol {symbol}")
            if not new_mode:
                logging.warning(f"No mode selected for strategy {strategy_name} with symbol {symbol}, defaulting to 'Wylaczona'")
                new_mode = "Wylaczona"
            strategy = next((s for s in self.strategies if s["name"] == strategy_name and s["symbol"] == symbol), None)
            if not strategy:
                self.error_handler.log_and_show_error(self.frame, "Saving mode", f"Strategia {strategy_name} z symbolem {symbol} nie znaleziona")
                window.destroy()
                return
            
            self.strategy_data.update_strategy_mode(strategy_name, symbol, new_mode)
            self.strategies = self.strategy_data.load_strategies()
            self.update_strategies_display()
            
            strategy_key = f"{strategy_name}_{symbol}"
            if new_mode in ["Paper", "Auto"]:
                interval = strategy.get("interval", "1m")
                mode = "paper" if new_mode == "Paper" else "auto"
                self.progress_label.config(text=f"Aktywowano {new_mode} dla {strategy_name} na {symbol}")
                
                if not self.loop.is_running():
                    loop_thread = threading.Thread(target=self.loop.run_forever, daemon=True)
                    loop_thread.start()
                    logging.info("Started asyncio event loop in separate thread")
                
                if strategy_key in self.simulation_tasks:
                    task = self.simulation_tasks.pop(strategy_key)
                    task.cancel()
                    logging.info(f"Cancelled existing paper trading task for strategy {strategy_key}")
                
                coro = self.run_simulation(strategy_name, symbol, interval)
                future = asyncio.run_coroutine_threadsafe(coro, self.loop)
                self.simulation_tasks[strategy_key] = future
                self.loop.call_soon_threadsafe(
                    lambda: logging.info(f"Task scheduled for {new_mode} paper trading: {strategy_name} on {symbol}, task id: {id(future)}")
                )
                
                def check_task():
                    if future.done():
                        try:
                            future.result()
                            self.progress_label.config(text="")
                            logging.info(f"Task completed successfully for {new_mode} paper trading: {strategy_name} on {symbol}")
                        except Exception as error:
                            self.progress_label.config(text="")
                            self.error_handler.log_and_show_error(self.frame, f"Running {new_mode} paper trading", f"Paper trading nieudane dla {strategy_name} na {symbol}: {str(error)}")
                    else:
                        self.frame.after(1000, check_task)
                self.frame.after(0, check_task)  # Natychmiastowe uruchomienie sprawdzania
            elif new_mode == "Wylaczona":
                if strategy_key in self.simulation_tasks:
                    task = self.simulation_tasks.pop(strategy_key)
                    task.cancel()
                    logging.info(f"Cancelled paper trading task for strategy {strategy_key} due to mode change to {new_mode}")
                self.progress_label.config(text=f"Dezaktywowano strategię {strategy_name}")
                self.simulation_tab.update_strategies_display()
            
            window.destroy()
            logging.info(f"Updated mode for strategy {strategy_name}: {new_mode}")
        except Exception as e:
            self.error_handler.log_and_show_error(self.frame, "Saving mode", f"Błąd podczas zapisywania trybu: {str(e)}")
            window.destroy()

    def _on_symbol_selected(self, strategy_name: str, old_symbol: str, new_symbol: str, window):
        """Obsługuje zmianę symbolu strategii."""
        try:
            logging.info(f"Saving symbol {new_symbol} for strategy {strategy_name}")
            if not new_symbol:
                self.error_handler.log_and_show_error(self.frame, "Saving symbol", "Nie wybrano symbolu")
                window.destroy()
                return
            
            strategy = next((s for s in self.strategies if s["name"] == strategy_name and s["symbol"] == old_symbol), None)
            if not strategy:
                self.error_handler.log_and_show_error(self.frame, "Saving symbol", f"Strategia {strategy_name} z symbolem {old_symbol} nie znaleziona")
                window.destroy()
                return
            
            active_symbols = self.symbols_tab.get_active_symbols()
            if new_symbol not in active_symbols:
                self.error_handler.log_and_show_error(self.frame, "Saving symbol", f"Symbol {new_symbol} nie jest dostępny")
                window.destroy()
                return
            
            if strategy.get("mode") in ["Paper", "Auto"]:
                logging.info(f"Disabling strategy {strategy_name} due to symbol change")
                strategy_key = f"{strategy_name}_{old_symbol}"
                if strategy_key in self.simulation_tasks:
                    task = self.simulation_tasks.pop(strategy_key)
                    task.cancel()
                    logging.info(f"Cancelled paper trading task for strategy {strategy_key} due to symbol change")
                self.strategy_data.update_strategy_mode(strategy_name, old_symbol, "Wylaczona")
                self.progress_label.config(text=f"Dezaktywowano strategię {strategy_name}")
            
            self.trade_manager.reset_for_new_symbol(strategy_name, old_symbol)
            self.strategy_data.update_strategy_symbol(strategy_name, new_symbol)
            self.strategies = self.strategy_data.load_strategies()
            self.update_strategies_display()
            window.destroy()
            logging.info(f"Updated symbol for strategy {strategy_name}: {new_symbol}")
            self.progress_label.config(text=f"Zaktualizowano symbol dla {strategy_name}")
        except Exception as e:
            self.error_handler.log_and_show_error(self.frame, "Saving symbol", f"Błąd podczas zapisywania symbolu: {str(e)}")
            window.destroy()

    def _on_interval_selected(self, strategy_name: str, new_interval: str, window):
        """Obsługuje zmianę interwału strategii."""
        try:
            logging.info(f"Saving interval {new_interval} for strategy {strategy_name}")
            valid_intervals = ["1m", "5m", "15m", "1h", "4h", "1d"]
            if new_interval not in valid_intervals:
                self.error_handler.log_and_show_error(self.frame, "Saving interval", f"Nieprawidłowy interwał {new_interval}")
                window.destroy()
                return
            self.strategy_data.update_strategy_interval(strategy_name, new_interval)
            self.strategies = self.strategy_data.load_strategies()
            self.update_strategies_display()
            window.destroy()
            logging.info(f"Updated interval for strategy {strategy_name}: {new_interval}")
            self.progress_label.config(text=f"Zaktualizowano interwał dla {strategy_name}")
        except Exception as e:
            self.error_handler.log_and_show_error(self.frame, "Saving interval", f"Błąd podczas zapisywania interwału: {str(e)}")
            window.destroy()

    def _on_exchange_selected(self, strategy_name: str, new_exchange: str, window):
        """Obsługuje zmianę giełdy strategii."""
        try:
            logging.info(f"Saving exchange {new_exchange} for strategy {strategy_name}")
            if new_exchange not in self.exchanges:
                self.error_handler.log_and_show_error(self.frame, "Saving exchange", f"Nieprawidłowa giełda {new_exchange}")
                window.destroy()
                return
            strategy = next((s for s in self.strategies if s["name"] == strategy_name), None)
            if not strategy:
                self.error_handler.log_and_show_error(self.frame, "Saving exchange", f"Strategia {strategy_name} nie znaleziona")
                window.destroy()
                return
            if strategy.get("mode") in ["Paper", "Auto"]:
                logging.info(f"Disabling strategy {strategy_name} due to exchange change")
                strategy_key = f"{strategy_name}_{strategy.get('symbol', '')}"
                if strategy_key in self.simulation_tasks:
                    task = self.simulation_tasks.pop(strategy_key)
                    task.cancel()
                    logging.info(f"Cancelled paper trading task for strategy {strategy_key} due to exchange change")
                self.strategy_data.update_strategy_mode(strategy_name, strategy.get("symbol", ""), "Wylaczona")
                self.progress_label.config(text=f"Dezaktywowano strategię {strategy_name}")
            self.strategy_data.update_strategy_exchange(strategy_name, new_exchange)
            self.strategies = self.strategy_data.load_strategies()
            self.update_strategies_display()
            window.destroy()
            logging.info(f"Updated exchange for strategy {strategy_name}: {new_exchange}")
            self.progress_label.config(text=f"Zaktualizowano giełdę dla {strategy_name}")
        except Exception as e:
            self.error_handler.log_and_show_error(self.frame, "Saving exchange", f"Błąd podczas zapisywania giełdy: {str(e)}")
            window.destroy()