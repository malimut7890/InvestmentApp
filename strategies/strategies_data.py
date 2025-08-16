# -*- coding: utf-8 -*-
# Path: C:\Users\Msi\Desktop\investmentapp\src\tabs\strategies\strategies_data.py
import tkinter as tk
from tkinter import ttk, messagebox
import json
import logging
from pathlib import Path
import os
import shutil
from src.core.trade_manager import TradeManager

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
error_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))

class StrategyData:
    def __init__(self):
        self.strategies_file = Path(__file__).resolve().parents[3] / "data" / "strategies.json"
        self.trade_manager = TradeManager()
        logging.info("Initializing StrategyData")

    def load_strategies(self):
        try:
            if not self.strategies_file.exists():
                logging.info("No strategies.json file, returning empty list")
                return []
            with open(self.strategies_file, "r", encoding="utf-8-sig") as f:
                strategies = json.load(f)
            logging.info("Loaded strategies: {}".format(', '.join(f"{s['name']}_{s['symbol']}" for s in strategies)))
            return strategies
        except Exception as e:
            logging.error(f"Error loading strategies: {str(e)}")
            tk.messagebox.showerror("Error", f"Błąd podczas wczytywania strategii: {str(e)}")
            return []

    def save_strategies(self, strategies):
        try:
            with open(self.strategies_file, "w", encoding="utf-8") as f:
                json.dump(strategies, f, indent=4, ensure_ascii=False)
            logging.info("Saved strategies to strategies.json")
        except Exception as e:
            logging.error(f"Error saving strategies: {str(e)}")
            tk.messagebox.showerror("Error", f"Błąd podczas zapisywania strategii: {str(e)}")
            raise

    def add_strategy(self, strategy_name, file_path, symbol="BTC/USDT", interval="1h", exchange="MEXC", mode="Symulacja", parameters=None):
        try:
            strategies = self.load_strategies()
            # Normalizacja symbolu i interwału
            normalized_symbol, normalized_interval = self.trade_manager.normalize_symbol_and_interval(symbol, interval)
            # Sprawdź, czy strategia już istnieje dla danego symbolu
            if any(s["name"] == strategy_name and s["symbol"] == normalized_symbol for s in strategies):
                logging.warning(f"Strategy {strategy_name} for {normalized_symbol} already exists")
                tk.messagebox.showwarning("Warning", f"Strategia {strategy_name} dla {normalized_symbol} już istnieje")
                return
            # Dodaj nową strategię
            new_strategy = {
                "name": strategy_name,
                "file_path": str(file_path),
                "symbol": normalized_symbol,
                "interval": normalized_interval,
                "exchange": exchange,
                "mode": mode,
                "parameters": parameters or {}
            }
            strategies.append(new_strategy)
            self.save_strategies(strategies)
            logging.info(f"Added strategy {strategy_name} for {normalized_symbol}")
            tk.messagebox.showinfo("Success", f"Dodano strategię {strategy_name} dla {normalized_symbol}")
        except Exception as e:
            logging.error(f"Error adding strategy {strategy_name}: {str(e)}")
            tk.messagebox.showerror("Error", f"Błąd podczas dodawania strategii: {str(e)}")
            raise

    def update_strategy_mode(self, strategy_name, symbol, mode):
        try:
            strategies = self.load_strategies()
            normalized_symbol, _ = self.trade_manager.normalize_symbol_and_interval(symbol, "1h")  # Interwał nieistotny dla aktualizacji trybu
            for strategy in strategies:
                if strategy["name"] == strategy_name and strategy["symbol"] == normalized_symbol:
                    strategy["mode"] = mode
                    self.save_strategies(strategies)
                    logging.info(f"Updated mode to {mode} for strategy {strategy_name} on {normalized_symbol}")
                    tk.messagebox.showinfo("Success", f"Zaktualizowano tryb strategii {strategy_name} na {mode}")
                    return
            logging.warning(f"Strategy {strategy_name} for {normalized_symbol} not found")
            tk.messagebox.showwarning("Warning", f"Strategia {strategy_name} dla {normalized_symbol} nie znaleziona")
        except Exception as e:
            logging.error(f"Error updating mode for {strategy_name} on {symbol}: {str(e)}")
            tk.messagebox.showerror("Error", f"Błąd podczas aktualizacji trybu strategii: {str(e)}")
            raise

    def clear_strategy_data(self, strategy_name, symbol, timeframe):
        try:
            logging.info(f"Clearing data for strategy {strategy_name} on {symbol} with timeframe {timeframe}")
            self.trade_manager.reset_for_new_strategy(strategy_name, symbol, timeframe)
            logging.info(f"Successfully cleared data for strategy {strategy_name} on {symbol}")
            tk.messagebox.showinfo("Success", f"Dane dla strategii {strategy_name} na {symbol} zostały wyczyszczone")
        except Exception as e:
            logging.error(f"Error clearing strategy data for {strategy_name} on {symbol}: {str(e)}")
            tk.messagebox.showerror("Error", f"Błąd podczas czyszczenia danych strategii: {str(e)}")
            raise

class StrategiesTab:
    def __init__(self, frame):
        try:
            logging.info("=== Initializing StrategiesTab ===")
            self.frame = frame
            self.strategy_data = StrategyData()
            self.strategies = self.strategy_data.load_strategies()
            
            self.tree = ttk.Treeview(self.frame, columns=("Name", "Symbol", "Interval", "Exchange", "Mode"), show="headings")
            self.tree.heading("Name", text="Nazwa")
            self.tree.heading("Symbol", text="Symbol")
            self.tree.heading("Interval", text="Interwał")
            self.tree.heading("Exchange", text="Giełda")
            self.tree.heading("Mode", text="Tryb")
            
            for col in self.tree["columns"]:
                self.tree.column(col, width=100, anchor="center")
            
            self.tree.pack(pady=10, fill="both", expand=True)
            
            # Obsługa dwukrotnego kliknięcia w tabelę
            self.tree.bind("<Double-1>", self.on_tree_double_click)
            
            # Przyciski
            button_frame = tk.Frame(self.frame)
            button_frame.pack(pady=5)
            ttk.Button(button_frame, text="Dodaj strategię", command=self.add_strategy).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="Edytuj strategię", command=self.edit_strategy).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="Usuń strategię", command=self.delete_strategy).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="Wyczyść dane strategii", command=self.clear_strategy_data).pack(side=tk.LEFT, padx=5)
            
            self.update_strategies_display()
            logging.info("=== StrategiesTab initialized ===")
        except Exception as e:
            logging.error(f"Error initializing StrategiesTab: {str(e)}")
            tk.messagebox.showerror("Error", f"Błąd podczas inicjalizacji zakładki: {str(e)}")
            raise

    def update_strategies_display(self):
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)
            self.strategies = self.strategy_data.load_strategies()
            for strategy in self.strategies:
                self.tree.insert("", tk.END, values=(
                    strategy.get("name", ""),
                    strategy.get("symbol", ""),
                    strategy.get("interval", ""),
                    strategy.get("exchange", ""),
                    strategy.get("mode", "")
                ))
            logging.info("Strategies table updated, strategies: {}".format(', '.join(f"{s['name']}_{s['symbol']}" for s in self.strategies)))
        except Exception as e:
            logging.error(f"Error updating strategies table: {str(e)}")
            tk.messagebox.showerror("Error", f"Błąd podczas aktualizacji tabeli strategii: {str(e)}")
            raise

    def add_strategy(self):
        try:
            # Okno dialogowe do dodawania strategii
            add_window = tk.Toplevel(self.frame)
            add_window.title("Dodaj strategię")
            add_window.geometry("400x300")
            
            tk.Label(add_window, text="Nazwa strategii:").pack(pady=5)
            name_entry = tk.Entry(add_window)
            name_entry.pack(pady=5)
            
            tk.Label(add_window, text="Ścieżka do pliku strategii:").pack(pady=5)
            file_entry = tk.Entry(add_window)
            file_entry.pack(pady=5)
            
            tk.Label(add_window, text="Symbol:").pack(pady=5)
            symbol_entry = tk.Entry(add_window)
            symbol_entry.insert(0, "BTC/USDT")
            symbol_entry.pack(pady=5)
            
            tk.Label(add_window, text="Interwał:").pack(pady=5)
            interval_entry = tk.Entry(add_window)
            interval_entry.insert(0, "1h")
            interval_entry.pack(pady=5)
            
            tk.Label(add_window, text="Giełda:").pack(pady=5)
            exchange_entry = tk.Entry(add_window)
            exchange_entry.insert(0, "MEXC")
            exchange_entry.pack(pady=5)
            
            def save_strategy():
                try:
                    strategy_name = name_entry.get()
                    file_path = file_entry.get()
                    symbol = symbol_entry.get()
                    interval = interval_entry.get()
                    exchange = exchange_entry.get()
                    if not strategy_name or not file_path or not symbol or not interval or not exchange:
                        logging.warning("Incomplete strategy data provided")
                        tk.messagebox.showwarning("Warning", "Wypełnij wszystkie pola")
                        return
                    self.strategy_data.add_strategy(strategy_name, file_path, symbol, interval, exchange)
                    self.update_strategies_display()
                    add_window.destroy()
                    logging.info(f"Added strategy {strategy_name} via GUI")
                except Exception as e:
                    logging.error(f"Error saving new strategy: {str(e)}")
                    tk.messagebox.showerror("Error", f"Błąd podczas zapisywania strategii: {str(e)}")
            
            ttk.Button(add_window, text="Zapisz", command=save_strategy).pack(pady=10)
        except Exception as e:
            logging.error(f"Error adding strategy: {str(e)}")
            tk.messagebox.showerror("Error", f"Błąd podczas dodawania strategii: {str(e)}")
            raise

    def edit_strategy(self):
        try:
            # Placeholder dla edycji strategii
            logging.info("Editing strategy (placeholder)")
            tk.messagebox.showinfo("Info", "Edycja strategii - funkcja do wdrożenia")
        except Exception as e:
            logging.error(f"Error editing strategy: {str(e)}")
            tk.messagebox.showerror("Error", f"Błąd podczas edycji strategii: {str(e)}")
            raise

    def delete_strategy(self):
        try:
            selected_item = self.tree.selection()
            if not selected_item:
                logging.warning("No strategy selected for deletion")
                tk.messagebox.showwarning("Warning", "Wybierz strategię do usunięcia")
                return
            strategy_name = self.tree.item(selected_item)["values"][0]
            symbol = self.tree.item(selected_item)["values"][1]
            timeframe = self.tree.item(selected_item)["values"][2]
            self.strategies = [s for s in self.strategies if not (s["name"] == strategy_name and s["symbol"] == symbol)]
            self.strategy_data.save_strategies(self.strategies)
            self.strategy_data.clear_strategy_data(strategy_name, symbol, timeframe)  # Czyść dane przy usuwaniu
            self.update_strategies_display()
            logging.info(f"Deleted strategy {strategy_name} for {symbol}")
            tk.messagebox.showinfo("Success", f"Strategia {strategy_name} dla {symbol} usunięta")
        except Exception as e:
            logging.error(f"Error deleting strategy: {str(e)}")
            tk.messagebox.showerror("Error", f"Błąd podczas usuwania strategii: {str(e)}")
            raise

    def clear_strategy_data(self):
        try:
            selected_item = self.tree.selection()
            if not selected_item:
                logging.warning("No strategy selected for data clearing")
                tk.messagebox.showwarning("Warning", "Wybierz strategię do wyczyszczenia danych")
                return
            strategy_name = self.tree.item(selected_item)["values"][0]
            symbol = self.tree.item(selected_item)["values"][1]
            timeframe = self.tree.item(selected_item)["values"][2]
            if not symbol or not timeframe:
                logging.warning(f"No symbol or timeframe defined for strategy {strategy_name}, cannot clear data")
                tk.messagebox.showwarning("Warning", "Strategia nie ma zdefiniowanego symbolu lub interwału")
                return
            self.strategy_data.clear_strategy_data(strategy_name, symbol, timeframe)
            self.update_strategies_display()
            logging.info(f"Cleared data for strategy {strategy_name} on {symbol}")
        except Exception as e:
            logging.error(f"Error clearing strategy data: {str(e)}")
            tk.messagebox.showerror("Error", f"Błąd podczas czyszczenia danych strategii: {str(e)}")
            raise

    def on_tree_double_click(self, event):
        try:
            item = self.tree.selection()
            if not item:
                logging.info("No item selected in StrategiesTab table")
                return
            item = item[0]
            col = self.tree.identify_column(event.x)
            strategy_name = self.tree.item(item, "values")[0]
            symbol = self.tree.item(item, "values")[1]
            col_index = int(col.replace("#", "")) - 1
            col_name = self.tree["columns"][col_index]
            
            if col_name != "Mode":
                logging.info(f"Double-click on non-editable column {col_name} for strategy {strategy_name}")
                return
            
            logging.info(f"Double-click in StrategiesTab table on strategy {strategy_name}, column {col_name}")
            
            edit_window = tk.Toplevel(self.frame)
            edit_window.title("Zmień tryb strategii")
            edit_window.geometry("300x150")
            
            tk.Label(edit_window, text="Tryb:").pack(pady=5)
            mode_var = tk.StringVar(value=self.tree.item(item, "values")[col_index])
            ttk.Combobox(edit_window, textvariable=mode_var, values=["Symulacja", "Live", "Auto"], state="readonly").pack(pady=5)
            
            def save_mode():
                try:
                    new_mode = mode_var.get()
                    self.strategy_data.update_strategy_mode(strategy_name, symbol, new_mode)
                    self.update_strategies_display()
                    edit_window.destroy()
                    logging.info(f"Saving mode {new_mode} for strategy {strategy_name}")
                except Exception as e:
                    logging.error(f"Saving mode for {strategy_name}: Error saving mode: {str(e)}")
                    tk.messagebox.showerror("Error", f"Błąd podczas zapisywania trybu: {str(e)}")
            
            ttk.Button(edit_window, text="Zapisz", command=save_mode).pack(pady=10)
        except Exception as e:
            logging.error(f"Error handling double-click in StrategiesTab: {str(e)}")
            tk.messagebox.showerror("Error", f"Błąd podczas obsługi tabeli: {str(e)}")