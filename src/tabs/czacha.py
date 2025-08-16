# -*- coding: utf-8 -*-
# Ścieżka: C:\Users\Msi\Desktop\investmentapp\src\tabs\czacha.py
import tkinter as tk
from tkinter import ttk
import logging
from pathlib import Path
import json
from src.tabs.czacha_data import CzachaData
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

class CzachaTab:
    """Class managing the Czacha tab in the GUI."""

    def __init__(self, frame):
        try:
            logging.info("Initializing CzachaTab")
            self.frame = frame
            self.czacha_data = CzachaData()
            self.strategy_data = StrategyData()
            self.error_handler = ErrorHandler()
            self.progress_label = None
            
            for widget in self.frame.winfo_children():
                widget.destroy()
            logging.debug("Czacha frame cleared")
            
            total_capital_frame = ttk.Frame(self.frame)
            total_capital_frame.pack(pady=10, padx=10, anchor="nw")
            ttk.Label(total_capital_frame, text="Total Capital:").pack(side="left")
            self.total_capital_var = tk.StringVar(value=str(self.czacha_data.load_data().get("total_capital", 10000.0)))
            total_capital_entry = ttk.Entry(total_capital_frame, textvariable=self.total_capital_var, width=15, state="normal")
            total_capital_entry.pack(side="left", padx=5)
            total_capital_entry.bind("<FocusOut>", self.update_total_capital)
            
            ttk.Button(self.frame, text="Save", command=self.save_total_capital).pack(pady=5)
            ttk.Button(self.frame, text="Export Data to CSV", command=self.export_to_csv).pack(pady=5)
            
            self.tree = ttk.Treeview(self.frame, columns=(
                "Mode", "Name", "Strategy Capital", "Position Percentage", "Position Value",
                "Total Capital Percentage", "Start Capital", "Days", "Max DD%", "Max Profit %",
                "Profit Live", "Total Profit", "Reinvestment", "Promotion"
            ), show="headings")
            
            self.tree.heading("Mode", text="Mode")
            self.tree.heading("Name", text="Name")
            self.tree.heading("Strategy Capital", text="Strategy Capital")
            self.tree.heading("Position Percentage", text="Position Percentage")
            self.tree.heading("Position Value", text="Position Value")
            self.tree.heading("Total Capital Percentage", text="Total Capital Percentage")
            self.tree.heading("Start Capital", text="Start Capital")
            self.tree.heading("Days", text="Days")
            self.tree.heading("Max DD%", text="Max DD%")
            self.tree.heading("Max Profit %", text="Max Profit %")
            self.tree.heading("Profit Live", text="Profit Live")
            self.tree.heading("Total Profit", text="Total Profit")
            self.tree.heading("Reinvestment", text="Reinvestment")
            self.tree.heading("Promotion", text="Promotion")
            
            for col in self.tree["columns"]:
                self.tree.column(col, width=100, anchor="center")
            
            self.tree.tag_configure("editable", background="#E0FFE0")
            editable_columns = ["Position Percentage", "Total Capital Percentage", "Reinvestment", "Promotion"]
            for col in editable_columns:
                self.tree.column(col, anchor="center")
            
            self.tree.pack(pady=10, fill="both", expand=True)
            self.tree.bind("<Double-1>", self.on_tree_double_click)
            
            self.progress_label = tk.Label(self.frame, text="", fg="red")
            self.progress_label.pack(pady=5)
            
            self.update_strategies_display()
            
            logging.info("CzachaTab initialized")
        except Exception as e:
            self.error_handler.log_and_show_error(self.frame, "Initializing CzachaTab", f"Error initializing tab: {str(e)}")

    def update_total_capital(self, event):
        """Updates the total capital after a change in the input field."""
        try:
            new_capital = float(self.total_capital_var.get())
            current_capital = self.czacha_data.load_data().get("total_capital", 10000.0)
            if new_capital < 0:
                raise ValueError("Total capital must be non-negative")
            if abs(new_capital - current_capital) < 0.01:  # Avoid redundant updates
                logging.debug(f"No change in total capital: {new_capital}")
                return
            self.czacha_data.update_total_capital(new_capital)
            self.update_strategies_display()
            logging.info(f"Updated total capital to {new_capital}")
            self.progress_label.config(text=f"Updated total capital: {new_capital}")
        except ValueError as e:
            self.error_handler.log_and_show_error(self.frame, "Updating total capital", f"Invalid capital value: {str(e)}")
        except Exception as e:
            self.error_handler.log_and_show_error(self.frame, "Updating total capital", f"Error updating capital: {str(e)}")

    def save_total_capital(self):
        """Saves the total capital."""
        try:
            new_capital = float(self.total_capital_var.get())
            current_capital = self.czacha_data.load_data().get("total_capital", 10000.0)
            if new_capital < 0:
                raise ValueError("Total capital must be non-negative")
            if abs(new_capital - current_capital) < 0.01:  # Avoid redundant updates
                logging.debug(f"No change in total capital: {new_capital}")
                return
            self.czacha_data.update_total_capital(new_capital)
            self.update_strategies_display()
            logging.info(f"Saved total capital: {new_capital}")
            self.progress_label.config(text=f"Saved total capital: {new_capital}")
        except ValueError as e:
            self.error_handler.log_and_show_error(self.frame, "Saving total capital", f"Invalid capital value: {str(e)}")
        except Exception as e:
            self.error_handler.log_and_show_error(self.frame, "Saving total capital", f"Error saving capital: {str(e)}")

    def export_to_csv(self):
        """Exports Czacha data to a CSV file."""
        try:
            import pandas as pd
            import os
            from datetime import datetime
            czacha_data = self.czacha_data.load_data()
            if not czacha_data["strategies"]:
                self.error_handler.log_and_show_error(self.frame, "Exporting to CSV", "No Czacha data to export")
                return
            df = pd.DataFrame(czacha_data["strategies"])
            df["total_capital"] = czacha_data["total_capital"]
            export_dir = "C:\\Users\\Msi\\Desktop\\investmentapp\\data\\exports"
            os.makedirs(export_dir, exist_ok=True)
            export_file = f"{export_dir}\\czacha_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df.to_csv(export_file, index=False, encoding="utf-8")
            logging.info(f"Exported Czacha data to {export_file}")
            self.progress_label.config(text=f"Data exported to {export_file}")
        except Exception as e:
            self.error_handler.log_and_show_error(self.frame, "Exporting to CSV", f"Error exporting data to CSV: {str(e)}")

    def update_strategies_display(self):
        """Updates the strategies table in the Czacha tab."""
        try:
            logging.info("Starting update of Czacha strategies table")
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            czacha_data = self.czacha_data.load_data()
            strategies = self.strategy_data.load_strategies()
            active_strategies = [s for s in strategies if s["mode"] in ["Live", "Paper", "Auto"]]
            czacha_strategies = czacha_data.get("strategies", [])
            
            for strategy in active_strategies:
                strategy_name = strategy["name"]
                symbol = strategy["symbol"]
                czacha_strategy = next((cs for cs in czacha_strategies if cs["name"] == strategy_name and cs["symbol"] == symbol), None)
                if not czacha_strategy:
                    logging.warning(f"Strategy {strategy_name} with symbol {symbol} not found in czacha.json, adding default")
                    self.czacha_data.update_strategy(strategy_name, symbol)
                    czacha_strategy = next((cs for cs in czacha_data.get("strategies", []) if cs["name"] == strategy_name and cs["symbol"] == symbol), None)
                
                if czacha_strategy:
                    tags = ("editable",)
                    self.tree.insert("", tk.END, values=(
                        strategy["mode"],
                        strategy_name,
                        f"{czacha_strategy['capital_current']:.2f}",
                        f"{czacha_strategy['trade_percentage']:.2f}",
                        f"{czacha_strategy['capital_current'] * (czacha_strategy['trade_percentage'] / 100):.2f}",
                        f"{czacha_strategy['capital_percentage']:.2f}",
                        f"{czacha_strategy['start_capital']:.2f}",
                        czacha_strategy["days"],
                        f"{czacha_strategy['max_dd']:.2f}",
                        f"{czacha_strategy['max_profit']:.2f}",
                        f"{czacha_strategy['profit_live']:.2f}",
                        f"{czacha_strategy['profit_total']:.2f}",
                        czacha_strategy["reinvest"],
                        czacha_strategy["promotion"]
                    ), tags=tags)
            
            logging.info(f"Czacha strategies table updated, strategies: {', '.join(s['name'] + '_' + s['symbol'] for s in active_strategies)}")
        except Exception as e:
            self.error_handler.log_and_show_error(self.frame, "Updating Czacha table", f"Error updating table: {str(e)}")

    def on_tree_double_click(self, event):
        """Handles double-click events in the table."""
        try:
            item = self.tree.selection()
            if not item:
                logging.info("No item selected in CzachaTab table")
                return
            item = item[0]
            col = self.tree.identify_column(event.x)
            strategy_name = self.tree.item(item, "values")[1]
            symbol = self.tree.item(item, "values")[2]
            logging.info(f"Double-click on strategy {strategy_name} with symbol {symbol}, column {col}")
            
            editable_columns = ["Position Percentage", "Total Capital Percentage", "Reinvestment", "Promotion"]
            col_index = int(col.replace("#", "")) - 1
            col_name = self.tree["columns"][col_index]
            
            if col_name not in editable_columns:
                logging.info(f"Column {col_name} is not editable")
                return
            
            edit_window = tk.Toplevel(self.frame)
            edit_window.title(f"Edit {col_name} for {strategy_name}")
            edit_window.geometry("300x150")
            
            tk.Label(edit_window, text=f"{col_name}:").pack(pady=5)
            current_value = self.tree.item(item, "values")[col_index]
            var = tk.StringVar(value=current_value)
            
            if col_name in ["Reinvestment", "Promotion"]:
                combo = ttk.Combobox(edit_window, textvariable=var, values=["Enabled", "Disabled"], state="readonly")
                combo.pack(pady=5)
            else:
                entry = ttk.Entry(edit_window, textvariable=var)
                entry.pack(pady=5)
            
            def save_changes():
                try:
                    new_value = var.get()
                    if col_name in ["Position Percentage", "Total Capital Percentage"]:
                        new_value = float(new_value)
                        if new_value < 0:
                            raise ValueError("Value must be non-negative")
                        if col_name == "Total Capital Percentage":
                            czacha_data = self.czacha_data.load_data()
                            current_total = sum(cs["capital_percentage"] for cs in czacha_data["strategies"] if cs["name"] != strategy_name or cs["symbol"] != symbol)
                            if current_total + new_value > 100:
                                raise ValueError("Sum of total capital percentage exceeds 100%")
                    self.czacha_data.update_strategy(
                        strategy_name,
                        symbol,
                        capital_percentage=new_value if col_name == "Total Capital Percentage" else None,
                        trade_percentage=new_value if col_name == "Position Percentage" else None,
                        reinvest=new_value if col_name == "Reinvestment" else None,
                        promotion=new_value if col_name == "Promotion" else None
                    )
                    self.update_strategies_display()
                    edit_window.destroy()
                    logging.info(f"Updated {col_name} for strategy {strategy_name} with symbol {symbol} to {new_value}")
                    self.progress_label.config(text=f"Updated {col_name} for {strategy_name}")
                except ValueError as e:
                    self.error_handler.log_and_show_error(self.frame, "Saving changes", f"Invalid value: {str(e)}")
                except Exception as e:
                    self.error_handler.log_and_show_error(self.frame, "Saving changes", f"Error saving changes: {str(e)}")
            
            ttk.Button(edit_window, text="Save", command=save_changes).pack(pady=10)
            ttk.Button(edit_window, text="Cancel", command=edit_window.destroy).pack(pady=10)
        except Exception as e:
            self.error_handler.log_and_show_error(self.frame, "Handling double-click", f"Error handling table: {str(e)}")