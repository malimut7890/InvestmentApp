# -*- coding: utf-8 -*-
# Path: C:\Users\Msi\Desktop\investmentapp\src\tabs\symbols.py
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import logging

class SymbolsTab:
    def __init__(self, frame):
        try:
            logging.info("=== Initializing SymbolsTab ===")
            self.frame = frame
            self.symbols_file = "C:\\Users\\Msi\\Desktop\\investmentapp\\data\\symbols.json"
            self.symbols = self.load_symbols()
            
            # Input frame
            input_frame = ttk.Frame(self.frame)
            input_frame.pack(pady=5)
            
            # Symbol input
            tk.Label(input_frame, text="Symbol:").pack(side=tk.LEFT, padx=5)
            self.symbol_entry = ttk.Entry(input_frame)
            self.symbol_entry.pack(side=tk.LEFT, padx=5)
            
            # Active checkbox
            self.active_var = tk.BooleanVar(value=True)
            tk.Checkbutton(input_frame, text="Active", variable=self.active_var).pack(side=tk.LEFT, padx=5)
            
            # Add button
            ttk.Button(input_frame, text="Add", command=self.add_symbol).pack(side=tk.LEFT, padx=5)
            
            # Symbols table
            self.tree = ttk.Treeview(self.frame, columns=("Symbol", "Active", "Delete"), show="headings")
            self.tree.heading("Symbol", text="Symbol")
            self.tree.heading("Active", text="Active")
            self.tree.heading("Delete", text="Delete")
            for col in self.tree["columns"]:
                self.tree.column(col, width=100, anchor="center")
            
            self.tree.pack(pady=10, fill="both", expand=True)
            
            self.tree.bind("<Double-1>", self.on_tree_double_click)
            
            self.update_symbols_display()
            logging.info("=== SymbolsTab initialized ===")
        except Exception as e:
            logging.error(f"Error initializing SymbolsTab: {str(e)}")
            tk.messagebox.showerror("Error", f"Error initializing tab: {str(e)}")
            raise

    def load_symbols(self):
        try:
            if not os.path.exists(self.symbols_file):
                logging.info("No symbols.json file, returning empty list")
                return []
            with open(self.symbols_file, "r", encoding="utf-8-sig") as f:
                symbols = json.load(f)
            logging.info(f"Loaded symbols: {symbols}")
            return symbols
        except Exception as e:
            logging.error(f"Error loading symbols: {str(e)}")
            return []

    def get_active_symbols(self):
        """Returns list of active symbols"""
        try:
            symbols = self.load_symbols()
            active_symbols = [s["symbol"] for s in symbols if s.get("active", False)]
            logging.info(f"Retrieved active symbols: {active_symbols}")
            return active_symbols
        except Exception as e:
            logging.error(f"Error retrieving active symbols: {str(e)}")
            return []

    def add_symbol(self):
        try:
            symbol = self.symbol_entry.get().strip()
            if not symbol:
                logging.warning("No symbol entered")
                tk.messagebox.showerror("Error", "Please enter a symbol")
                return
            
            symbols = self.load_symbols()
            if any(s["symbol"] == symbol for s in symbols):
                logging.warning(f"Symbol {symbol} already exists")
                tk.messagebox.showerror("Error", f"Symbol {symbol} already exists")
                return
            
            symbols.append({
                "symbol": symbol,
                "active": self.active_var.get()
            })
            with open(self.symbols_file, "w", encoding="utf-8") as f:
                json.dump(symbols, f, ensure_ascii=False, indent=4)
            
            self.symbols = self.load_symbols()
            self.update_symbols_display()
            self.symbol_entry.delete(0, tk.END)
            logging.info(f"Added symbol {symbol}")
            tk.messagebox.showinfo("Success", f"Added symbol {symbol}")
        except Exception as e:
            logging.error(f"Error adding symbol: {str(e)}")
            tk.messagebox.showerror("Error", f"Error adding symbol: {str(e)}")

    def update_symbols_display(self):
        try:
            logging.info("Starting update of symbols table")
            for item in self.tree.get_children():
                self.tree.delete(item)
            self.symbols = self.load_symbols()
            for symbol in self.symbols:
                self.tree.insert("", tk.END, values=(
                    symbol["symbol"],
                    "Yes" if symbol.get("active", False) else "No",
                    "Delete"
                ), tags=(symbol["symbol"],))
            logging.info(f"Symbols table updated, symbols: {[s['symbol'] for s in self.symbols]}")
        except Exception as e:
            logging.error(f"Error updating symbols table: {str(e)}")
            tk.messagebox.showerror("Error", f"Error updating table: {str(e)}")
            raise

    def on_tree_double_click(self, event):
        try:
            logging.info("Double-click in SymbolsTab table")
            item = self.tree.selection()
            if not item:
                logging.info("No item selected in table")
                return
            item = item[0]
            col = self.tree.identify_column(event.x)
            symbol = self.tree.item(item, "tags")[0]
            logging.info(f"Double-click on symbol {symbol}, column {col}")
            
            if col == "#2":  # Active
                symbols = self.load_symbols()
                for s in symbols:
                    if s["symbol"] == symbol:
                        s["active"] = not s.get("active", False)
                        break
                with open(self.symbols_file, "w", encoding="utf-8") as f:
                    json.dump(symbols, f, ensure_ascii=False, indent=4)
                self.update_symbols_display()
                logging.info(f"Toggled active status for symbol {symbol}")
            
            elif col == "#3":  # Delete
                symbols = self.load_symbols()
                symbols = [s for s in symbols if s["symbol"] != symbol]
                with open(self.symbols_file, "w", encoding="utf-8") as f:
                    json.dump(symbols, f, ensure_ascii=False, indent=4)
                self.update_symbols_display()
                logging.info(f"Deleted symbol {symbol}")
                tk.messagebox.showinfo("Success", f"Deleted symbol {symbol}")
        except Exception as e:
            logging.error(f"Error editing SymbolsTab table: {str(e)}")
            tk.messagebox.showerror("Error", f"Error editing table: {str(e)}")